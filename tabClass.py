# coding = utf-8
# Arch   = manyArch
#
# @File name:       tabClass.py
# @brief:           标签页相关功能
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


# 源码编辑器基类
class ZoomableTextEdit(QTextEdit):

    def __init__(self, font_family, isdark):
        super().__init__()
        # 使用应用字体，不硬编码字体大小
        app_font = QApplication.font()
        backgroundcolor = '#1E1E1E' if isdark else '#efefef'
        color = '#efefef' if isdark else '#1e1e1e'
        self.setStyleSheet(f"background-color: {backgroundcolor}; color: {color}; font-family: {font_family};")
        # 设置字体
        self.setFont(app_font)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            event.accept()
        else:
            super().wheelEvent(event)


# 源码查看标签页
class EditorTab(QWidget):

    def __init__(self, script_path, font_family, isdark):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.script_path = script_path
        self.is_editing = False # 是否处于编辑模式

        self.editor = ZoomableTextEdit(font_family, isdark)
        self.editor.setReadOnly(True)
        self.layout.addWidget(self.editor)

        # 挂载语法高亮
        ext = os.path.splitext(script_path)[1].lower()
        self.highlighter = ScriptHighlighter(self.editor.document(), ext, isdark)

        self.load_file(script_path)
        self.font_family = font_family
        self.isdark = isdark

    def set_editing(self, editing):
        """设置编辑模式"""
        self.is_editing = editing
        self.editor.setReadOnly(not editing)
        # 编辑模式下改变背景色以提示用户
        # 获取当前字体设置
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
        """保存文件内容"""
        try:
            # 首先尝试UTF-8编码保存
            with open(self.script_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False


# 交互式终端标签页
class TerminalTab(QWidget):

    def __init__(self, script_path, font_family, isdark):
        super().__init__()
        self.script_path = script_path
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 终端本体
        self.terminal = ZoomableTextEdit(font_family, isdark)
        self.terminal.setReadOnly(False) # 允许用户直接输入
                                         # 捕获键盘事件代理
        self.terminal.keyPressEvent = self.terminal_keyPressEvent
        self.layout.addWidget(self.terminal)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)

        self.ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        self.input_start_pos = 0 # 记录允许用户输入的起点位置

    def _terminate_process_tree(self, pid):
        """终止进程树（包括所有子进程）。如果 psutil 可用则使用它，否则使用平台特定方法。"""
        try:
            # 尝试导入 psutil
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            # 先终止子进程
            for child in children:
                try:
                    child.terminate()
                except:
                    pass
            # 等待子进程退出
            gone, alive = psutil.wait_procs(children, timeout=3)
            for child in alive:
                try:
                    child.kill()
                except:
                    pass
            # 终止父进程
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
            # psutil 不可用，使用平台特定方法
            if os.name == 'nt':
                # Windows: 使用 taskkill 强制终止进程树
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            else:
                # Linux/macOS: 终止进程组
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    time.sleep(0.5)
                    # 如果进程组仍然存在，发送 SIGKILL
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                except:
                    pass

    def start_process(self):
        ext = os.path.splitext(self.script_path)[1].lower()
        self.append_output(f"[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] start: {self.script_path}\n", color="#00FF00")

        # 设置工作目录为脚本所在的目录，确保相对路径能正确工作
        script_dir = os.path.dirname(self.script_path)
        if script_dir: # 如果脚本路径包含目录部分
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
            # 进程未运行，清理状态
            self.process = None
            self.append_output(f"\n^C\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process already stopped.\n", color="#F14C4C")
            return

        pid = self.process.processId()
        if pid > 0:
            try:
                # 使用改进的进程树终止方法
                self._terminate_process_tree(pid)
            except Exception as e:
                print(f"Error terminating process tree: {e}")

        # 等待进程结束（超时3秒）
        if not self.process.waitForFinished(3000):
            # 如果仍未结束，使用 QProcess 的 kill 作为最后手段
            self.process.kill()
            self.process.waitForFinished(2000)

        # 清理进程对象
        self.process = None

        # 输出停止消息
        self.append_output(f"\n^C\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process terminated.\n", color="#F14C4C")

    # 键盘事件拦截
    def terminal_keyPressEvent(self, event):
        # 1. 捕获 Ctrl + C 快捷键
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_C:
            self.stop_process()
            return

        # 2. 捕获 Ctrl + V 快捷键
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

        # 5. 如果用户乱点鼠标在历史输出区，强行拉回到最后输入区
        if self.terminal.textCursor().position() < self.input_start_pos:
            self.terminal.moveCursor(QTextCursor.End)

        # 6. 其他普通按键放行
        super(ZoomableTextEdit, self.terminal).keyPressEvent(event)

    # 输出处理
    def handle_stdout(self):
        text = self.process.readAllStandardOutput().data().decode('mbcs', errors='replace')
        self.inject_output(text)

    def handle_stderr(self):
        text = self.process.readAllStandardError().data().decode('mbcs', errors='replace')
        self.inject_output(text, default_color="#F14C4C")

    def handle_finished(self):
        self.append_output(f"\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process terminal.", color="#FFFF00")

    def inject_output(self, text, default_color=None):
        """ 智能输出注入：如果在输出时用户正在敲字，会先暂存用户敲的字，输出完毕后再补在后面 """
        cursor = self.terminal.textCursor()
        # 暂存未发送的用户输入
        cursor.setPosition(self.input_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        user_typing = cursor.selectedText()
        cursor.removeSelectedText()

        # 解析ANSI并打印程序输出
        self.parse_and_append_ansi(text, default_color)

        # 更新新的起始安全位置
        self.input_start_pos = self.terminal.textCursor().position()

        # 把用户还没发出去的字还给他们
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
            if i % 2 == 1:                      # ANSI 色码处理
                codes = part.split(';')
                for code in codes:
                    if not code: continue
                    c = int(code)
                    if c == 0:
                        fmt = QTextCharFormat() # 重置字体格式
                        if default_color: fmt.setForeground(QColor(default_color))
                    elif c in colors: fmt.setForeground(QColor(colors[c]))
            else:                               # 文本处理
                if part:
                    cursor.setCharFormat(fmt)
                    cursor.insertText(part)
        self.terminal.setTextCursor(cursor)

    def append_output(self, text, color=None):
        self.inject_output(text, default_color=color)
