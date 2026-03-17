# coding = utf-8
# Arch   = manyArch
#
# @File name:       tabClass.py
# @brief:           Tab related functionality
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

    def __init__(self):
        super().__init__()
        # Use application font, don't hardcode font size
        app_font = QApplication.font()
        font_family = app_font.family() or "Consolas"
        font_size = app_font.pointSize() or 14
        self.setStyleSheet(f"background-color: #1E1E1E; color: #D4D4D4; font-family: {font_family};")
        # Set font
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


# Source code viewing tab
class EditorTab(QWidget):

    def __init__(self, script_path):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.script_path = script_path
        self.is_editing = False # Whether in edit mode

        self.editor = ZoomableTextEdit()
        self.editor.setReadOnly(True)
        self.layout.addWidget(self.editor)

        # Mount syntax highlighting
        ext = os.path.splitext(script_path)[1].lower()
        self.highlighter = ScriptHighlighter(self.editor.document(), ext)

        self.load_file(script_path)

    def set_editing(self, editing):
        """Set edit mode"""
        self.is_editing = editing
        self.editor.setReadOnly(not editing)
        # Change background color in edit mode to alert user
        # Get current font settings
        current_font = self.editor.font()
        font_family = current_font.family() or "Consolas"
        if editing:
            self.editor.setStyleSheet(f"background-color: #2A2A2A; color: #D4D4D4; font-family: {font_family};")
        else:
            self.editor.setStyleSheet(f"background-color: #1E1E1E; color: #D4D4D4; font-family: {font_family};")

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
            # First try UTF-8 encoding to save
            with open(self.script_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            return True
        except Exception as e:
            print(f"Save file failed: {e}")
            return False


# Interactive terminal tab
class TerminalTab(QWidget):

    def __init__(self, script_path):
        super().__init__()
        self.script_path = script_path
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Terminal body
        self.terminal = ZoomableTextEdit()
        self.terminal.setReadOnly(False) # Allow user direct input
                                         # Capture keyboard event proxy
        self.terminal.keyPressEvent = self.terminal_keyPressEvent
        self.layout.addWidget(self.terminal)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)

        self.ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        self.input_start_pos = 0 # Record starting position allowing user input

    def _terminate_process_tree(self, pid):
        """Terminate process tree (including all child processes). Use psutil if available, otherwise platform-specific methods."""
        try:
            # Try importing psutil
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            # Terminate children first
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
                # Windows: use taskkill to force terminate process tree
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            else:
                # Linux/macOS: terminate process group
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    time.sleep(0.5)
                    # If process group still exists, send SIGKILL
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                except:
                    pass

    def start_process(self):
        ext = os.path.splitext(self.script_path)[1].lower()
        self.append_output(f"[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] start: {self.script_path}\n", color="#00FF00")
        
        # Set working directory to script directory to ensure relative paths work correctly
        script_dir = os.path.dirname(self.script_path)
        if script_dir:  # If script path includes directory part
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

        # Wait for process to end (timeout 3 seconds)
        if not self.process.waitForFinished(3000):
            # If still not ended, use QProcess kill as last resort
            self.process.kill()
            self.process.waitForFinished(2000)

        # Clean up process object
        self.process = None

        # Output stop message
        self.append_output(f"\n^C\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process terminated.\n", color="#F14C4C")

    # Keyboard event interception
    def terminal_keyPressEvent(self, event):
        # 1. Capture Ctrl + C shortcut
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_C:
            self.stop_process()
            return

        # 2. Capture Ctrl + V shortcut
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_V:
            # Get text from clipboard
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                # Insert text at current cursor position
                cursor = self.terminal.textCursor()
                cursor.insertText(text)
                # Ensure cursor is within input area
                if cursor.position() < self.input_start_pos:
                    self.terminal.moveCursor(QTextCursor.End)
            return

        # 3. Prevent user backspace/left from deleting previous console output
        if event.key() in (Qt.Key_Backspace, Qt.Key_Left):
            if self.terminal.textCursor().position() <= self.input_start_pos:
                return # Intercept

        # 4. When Enter key pressed, send command to QProcess
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.terminal.moveCursor(QTextCursor.End)
            # Get user typed command text
            user_cmd = self.terminal.toPlainText()[self.input_start_pos:]

            # Allow Enter key itself to create newline in UI
            super(ZoomableTextEdit, self.terminal).keyPressEvent(event)
            self.input_start_pos = self.terminal.textCursor().position()

            # Send input to child process
            if self.process.state() == QProcess.Running:
                self.process.write((user_cmd + '\n').encode('mbcs', errors='replace'))
            return

        # 5. If user clicks mouse in history output area, force return to last input area
        if self.terminal.textCursor().position() < self.input_start_pos:
            self.terminal.moveCursor(QTextCursor.End)

        # 6. Other normal keystrokes allowed
        super(ZoomableTextEdit, self.terminal).keyPressEvent(event)

    # Output processing
    def handle_stdout(self):
        text = self.process.readAllStandardOutput().data().decode('mbcs', errors='replace')
        self.inject_output(text)

    def handle_stderr(self):
        text = self.process.readAllStandardError().data().decode('mbcs', errors='replace')
        self.inject_output(text, default_color="#F14C4C")

    def handle_finished(self):
        self.append_output(f"\n[PsLauncher {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process finished.", color="#FFFF00")

    def inject_output(self, text, default_color=None):
        """ Intelligent output injection: if user is typing during output, temporarily store user input, append after output finished """
        cursor = self.terminal.textCursor()
        # Store unsent user input
        cursor.setPosition(self.input_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        user_typing = cursor.selectedText()
        cursor.removeSelectedText()

        # Parse ANSI and print program output
        self.parse_and_append_ansi(text, default_color)

        # Update new safe starting position
        self.input_start_pos = self.terminal.textCursor().position()

        # Return user's not-yet-sent typing to them
        if user_typing:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#D4D4D4"))
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

    def append_output(self, text, color=None):
        self.inject_output(text, default_color=color)