# coding = utf-8
# Arch   = manyArch
#
# @File name:       tabClass.py
# @brief:           Tab-related functionality
# @attention:       None
# @Author:          NGC13009
# @History:         2026-03-17		Create

import os
import re
import subprocess
import signal
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import datetime
import psutil

from utils import *


# Source code editor base class
class ZoomableTextEdit(QTextEdit):

    def __init__(self, font_family, isdark, line_wrap_mode=True):
        super().__init__()
        # Use application font, do not hardcode font size
        app_font = QApplication.font()
        backgroundcolor = '#1E1E1E' if isdark else '#efefef'
        color = '#efefef' if isdark else '#1e1e1e'
        self.setStyleSheet(f"background-color: {backgroundcolor}; color: {color}; font-family: {font_family};")
        # Set font
        self.setFont(app_font)
        # Set automatic line wrap mode
        self.set_line_wrap_mode(line_wrap_mode)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            event.accept()
        else:
            super().wheelEvent(event)

    def set_line_wrap_mode(self, enabled):
        """Set automatic line wrap mode"""
        if enabled:
            self.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.setLineWrapMode(QTextEdit.NoWrap)


# Source code view tab
class EditorTab(QWidget):

    def __init__(self, script_path, font_family, isdark, line_wrap_mode=True):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.script_path = script_path
        self.is_editing = False # Is editing mode

        self.editor = ZoomableTextEdit(font_family, isdark, line_wrap_mode)
        self.editor.setReadOnly(True)
        self.layout.addWidget(self.editor)

        # Mount syntax highlighting (use auto mode)
        self.ext = os.path.splitext(script_path)[1].lower()
        self.isdark = isdark
        self.highlighter = ScriptHighlighter(self.editor.document(), self.ext, self.isdark)

        self.load_file(script_path)
        self.font_family = font_family

        # Save current syntax mode (initially auto)
        self.current_syntax_mode = 'auto'

    def set_line_wrap_mode(self, enabled):
        """Set automatic line wrap mode"""
        self.editor.set_line_wrap_mode(enabled)

    def set_editing(self, editing):
        """Set editing mode"""
        self.is_editing = editing
        self.editor.setReadOnly(not editing)
        # Change background color in editing mode to prompt the user
        # Get current font settings
        current_font = self.editor.font()
        font_family = current_font.family() or "Consolas"
        backgroundcolor = '#1e1e1e' if self.isdark else '#efefef'
        backgroundcoloredit = '#3c3c3c' if self.isdark else '#c1c1c1'
        color = '#efefef' if self.isdark else '#1e1e1e'
        if editing:
            self.setStyleSheet(f"background-color: {backgroundcoloredit}; color: {color}; font-family: {font_family};")
        else:
            self.setStyleSheet(f"background-color: {backgroundcolor}; color: {color}; font-family: {font_family};")

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='gbk') as f:
                content = f.read()
        self.editor.setPlainText(content)

    def save_file(self):
        """Save file content"""
        try:
            # First attempt to save with UTF-8 encoding
            with open(self.script_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            return True
        except Exception as e:
            print(f"Failed to save file: {e}")
            return False

    def apply_syntax_highlight_mode(self, mode):
        """Apply syntax highlighting mode"""
        self.current_syntax_mode = mode

        # Create a new syntax highlighter
        self.highlighter = ScriptHighlighter(self.editor.document(), self.ext, self.isdark, syntax_mode=mode)

        # Re-highlight the entire document
        self.highlighter.rehighlight()


# Interactive terminal tab
class TerminalTab(QWidget):
    _next_id = 0  # 类级别计数器，用于给每个终端标签页分配唯一持久ID

    def __init__(self, script_path, font_family, isdark, line_wrap_mode=True):
        super().__init__()
        self.terminal_id = TerminalTab._next_id  # 唯一持久ID
        TerminalTab._next_id += 1
        self.script_path = script_path
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Terminal body
        self.terminal = ZoomableTextEdit(font_family, isdark, line_wrap_mode)
        self.terminal.setReadOnly(False) # Allow user direct input
                                         # Keyboard event capture proxy
        self.terminal.keyPressEvent = self.terminal_keyPressEvent
        self.layout.addWidget(self.terminal)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)

        self.ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        self.input_start_pos = 0 # Record the starting position where user input is allowed

    def set_line_wrap_mode(self, enabled):
        """Set automatic line wrap mode"""
        self.terminal.set_line_wrap_mode(enabled)

    def _terminate_process_tree(self, pid):
        """Terminate process tree (including all child processes). Use psutil if available, otherwise use platform-specific methods."""
        try:
            # Try to import psutil
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            # Terminate child processes first
            for child in children:
                try:
                    child.terminate()
                except:
                    pass
            # Wait for child processes to exit
            gone, alive = psutil.wait_procs(children, timeout=3)
            for child in alive:
                try:
                    child.kill()
                except:
                    pass
            # Terminate parent process
            try:
                parent.terminate()
                parent.wait(timeout=3)
            except:
                try:
                    parent.kill()
                    parent.wait(timeout=2)
                except:
                    pass
        except ImportError:
            # psutil not available, use platform-specific methods
            if os.name == 'nt':
                # Windows: Use taskkill to forcefully terminate process tree
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            else:
                # Linux/macOS: Terminate process group
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    time.sleep(0.5)
                    # If the process group still exists, send SIGKILL
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                except:
                    pass

    def start_process(self):
        ext = os.path.splitext(self.script_path)[1].lower()
        self.append_output(f"[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] start: {self.script_path}\n", color="#00FF00")

        # Set the working directory to the directory where the script is located to ensure relative paths work correctly
        script_dir = os.path.dirname(self.script_path)
        if script_dir: # If the script path contains a directory part
            self.process.setWorkingDirectory(script_dir)

        if ext == '.bat' or ext == '.cmd':
            self.process.start("cmd.exe", ["/c", self.script_path])
        elif ext == '.ps1':
            self.process.start("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", self.script_path])
        elif ext == '.sh':
            self.process.start("bash", [self.script_path])

    def stop_process(self):
        if self.process is None:
            return
        if self.process.state() != QProcess.Running:
            # Process not running, clean up state
            self.process = None
            self.append_output(f"\n^C\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process already stopped.\n", color="#F14C4C")
            return

        pid = self.process.processId()
        if pid > 0:
            try:
                # Use improved process tree termination method
                self._terminate_process_tree(pid)
            except Exception as e:
                print(f"Error terminating process tree: {e}")

        # Wait for process to finish (timeout 3 seconds)
        if not self.process.waitForFinished(3000):
            # If still not finished, use QProcess kill as a last resort
            self.process.kill()
            self.process.waitForFinished(2000)

        # Clean up process object
        self.process = None

        # Output stop message
        self.append_output(f"\n^C\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process terminated.\n", color="#F14C4C")

    def send_ctrl_c(self):
        """send Ctrl+C (0x03) to current progress"""
        if self.process is not None and self.process.state() == QProcess.Running:
            self.append_output(f"\n^C\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sending Ctrl+C interruption...\n", color="#F14C4C")
            # 向标准输入写入 Ctrl+C 字节 (0x03)
            self.process.write(b'\x03')
        else:
            self.append_output(f"\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No running process to interrupt.\n", color="#FFFF00")

    # 键盘事件拦截
    def terminal_keyPressEvent(self, event):

        # 1. 捕获 Ctrl + V 快捷键（始终粘贴）
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_V:
            # 从剪贴板获取文本
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                # 插入文本到当前光标位置
                cursor = self.terminal.textCursor()
                cursor.insertText(text)
                # 确保光标在输入区域内
                if cursor.position() < self.input_start_pos:
                    self.terminal.moveCursor(QTextCursor.End)
            return

        # 2. 其他 Ctrl+组合键（非纯修饰键本身）→ 发送给子进程
        if event.modifiers() & Qt.ControlModifier and event.key() not in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            if self.process is not None and self.process.state() == QProcess.Running:
                key = event.key()
                if Qt.Key_A <= key <= Qt.Key_Z:
                    # Ctrl+A~Z → 发送 0x01~0x1A 到子进程
                    ctrl_byte = bytes([key - Qt.Key_A + 1])
                    self.process.write(ctrl_byte)
                # 其他 Ctrl 组合键忽略
            # 即使进程未运行也不放行到文本控件（避免意外插入特殊字符）
            return

        # 3. 防止用户退格/左移删除以前的控制台输出
        if event.key() in (Qt.Key_Backspace, Qt.Key_Left):
            if self.terminal.textCursor().position() <= self.input_start_pos:
                return # 拦截掉

        # 4. 按下回车键时，发送指令给 QProcess
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.terminal.moveCursor(QTextCursor.End)
            # 获取用户敲击的命令文字
            user_cmd = self.terminal.toPlainText()[self.input_start_pos:]

            # 允许回车键自身在UI上换行
            super(ZoomableTextEdit, self.terminal).keyPressEvent(event)
            self.input_start_pos = self.terminal.textCursor().position()

            # 将输入发送给子进程
            if self.process.state() == QProcess.Running:
                self.process.write((user_cmd + '\n').encode('mbcs', errors='replace'))
            return

        # 5. 如果是纯修饰键（Ctrl/Shift/Alt 本身），不重新定位光标，不破坏选区
        if event.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            super(ZoomableTextEdit, self.terminal).keyPressEvent(event)
            return

        # 6. 如果用户乱点鼠标在历史输出区，强行拉回到最后输入区
        if self.terminal.textCursor().position() < self.input_start_pos:
            self.terminal.moveCursor(QTextCursor.End)

        # 7. 其他普通按键放行
        super(ZoomableTextEdit, self.terminal).keyPressEvent(event)

    # Output processing
    def handle_stdout(self):
        text = self.process.readAllStandardOutput().data().decode('mbcs', errors='replace')
        self.inject_output(text)

    def handle_stderr(self):
        text = self.process.readAllStandardError().data().decode('mbcs', errors='replace')
        self.inject_output(text, default_color="#F14C4C")

    def handle_finished(self):
        self.append_output(f"\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process terminal.", color="#FFFF00")

    def inject_output(self, text, default_color=None):
        """ Smart output injection: if the user is typing when output occurs, first store the typed text, then append it after the output is complete """
        cursor = self.terminal.textCursor()
        # Store unsent user input
        cursor.setPosition(self.input_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        user_typing = cursor.selectedText()
        cursor.removeSelectedText()

        # Parse ANSI and print program output
        self.parse_and_append_ansi(text, default_color)

        # Update new starting safe position
        self.input_start_pos = self.terminal.textCursor().position()

        # Return the characters the user hasn't sent yet to them
        if user_typing:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#efefef"))
            cursor.setCharFormat(fmt)
            cursor.insertText(user_typing)

        self.terminal.ensureCursorVisible()

    def parse_and_append_ansi(self, text, default_color=None):
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        parts = self.ansi_regex.split(text)
        fmt = QTextCharFormat()
        if default_color:
            fmt.setForeground(QColor(default_color))

        colors = {
            30: '#1e1e1e',
            31: '#CD3131',
            32: '#0DBC79',
            33: '#E5E510',
            34: '#2472C8',
            35: '#BC3FBC',
            36: '#11A8CD',
            37: '#E5E5E5',
            90: '#666666',
            91: '#F14C4C',
            92: '#23D18B',
            93: '#F5F543',
            94: '#3B8EEA',
            95: '#D670D6',
            96: '#29B8DB',
            97: '#E5E5E5'
        }

        for i, part in enumerate(parts):
            if i % 2 == 1:                      # ANSI color code processing
                codes = part.split(';')
                for code in codes:
                    if not code: continue
                    c = int(code)
                    if c == 0:
                        fmt = QTextCharFormat() # Reset font format
                        if default_color: fmt.setForeground(QColor(default_color))
                    elif c in colors: fmt.setForeground(QColor(colors[c]))
            else:                               # Text processing
                if part:
                    cursor.setCharFormat(fmt)
                    cursor.insertText(part)
        self.terminal.setTextCursor(cursor)

    def clear_screen(self):
        """清除终端屏幕的所有内容，重置输入起始位置"""
        self.terminal.clear()
        self.input_start_pos = 0

    def append_output(self, text, color=None):
        self.inject_output(text, default_color=color)
