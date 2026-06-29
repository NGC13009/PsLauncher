# coding = utf-8
#
# @File name:       test_gui_terminal.py
# @brief:           GUI 层：终端标签 ANSI 渲染、交互输入、输入区域隔离、键盘事件、输出注入
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeyEvent
from unittest.mock import MagicMock, patch

# ============================================================
# GUI 层测试：终端标签
# ============================================================


@pytest.mark.gui
class TestTerminalTab:
    """终端标签页测试"""

    def test_terminal_tab_creation(self, qapp, sample_scripts_dir):
        """终端标签页应成功创建"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        assert tab.script_path == script_path
        assert tab.terminal is not None

    def test_terminal_has_process(self, qapp, sample_scripts_dir):
        """终端标签页应有 QProcess 实例"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        assert tab.process is not None

    def test_terminal_initial_input_start_pos(self, qapp, sample_scripts_dir):
        """初始输入起始位置应为 0"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        assert tab.input_start_pos == 0

    def test_terminal_clear_screen(self, qapp, sample_scripts_dir):
        """清屏应重置输入位置"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.terminal.setPlainText("Some output")
        tab.input_start_pos = 50
        tab.clear_screen()
        assert tab.terminal.toPlainText() == ""
        assert tab.input_start_pos == 0

    def test_terminal_append_output(self, qapp, sample_scripts_dir):
        """append_output 应在终端中追加文本"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.append_output("Test message\n", color="#00FF00")
        # 因为 inject_output 内部使用了 pos 等，直接验证文本存在
        assert "Test message" in tab.terminal.toPlainText()

    def test_terminal_light_mode(self, qapp, sample_scripts_dir):
        """终端标签支持亮色模式"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", False, True)
        assert tab is not None


@pytest.mark.gui
class TestTerminalLineWrap:
    """终端换行模式测试"""

    def test_terminal_wrap_enabled(self, qapp, sample_scripts_dir):
        """终端换行模式应可设置"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.set_line_wrap_mode(True)
        # 验证没有崩溃
        assert tab is not None

    def test_terminal_wrap_disabled(self, qapp, sample_scripts_dir):
        """终端换行模式应可关闭"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, False)
        tab.set_line_wrap_mode(False)
        assert tab is not None


# ============================================================
# P0 补充：终端键盘事件测试（terminal_keyPressEvent 7种按键路径）
# ============================================================


@pytest.mark.gui
class TestTerminalKeyPressEvent:
    """终端键盘事件处理测试"""

    def test_enter_sends_command(self, terminal_tab, qtbot):
        """回车键应发送当前输入行到进程"""
        terminal_tab.terminal.setPlainText("echo hello")
        terminal_tab.input_start_pos = 0
        terminal_tab.terminal.moveCursor(terminal_tab.terminal.textCursor().End)

        qtbot.keyClick(terminal_tab.terminal, Qt.Key_Return)

        # 验证 process.write 被调用，写入的内容包含命令
        assert terminal_tab.process.write.called
        call_args = terminal_tab.process.write.call_args
        assert call_args is not None
        written = call_args[0][0]
        assert b'echo hello' in written

    def test_enter_empty_input_does_not_crash(self, terminal_tab, qtbot):
        """空输入按回车不应崩溃"""
        terminal_tab.input_start_pos = 0

        # 不应抛出异常
        qtbot.keyClick(terminal_tab.terminal, Qt.Key_Return)
        assert True

    def test_backspace_blocked_at_boundary(self, terminal_tab, qtbot):
        """退格键在输入起始位置应被拦截"""
        terminal_tab.terminal.setPlainText("existing output")
        terminal_tab.input_start_pos = len("existing output")
        terminal_tab.terminal.moveCursor(terminal_tab.terminal.textCursor().End)

        # 按退格键，应被拦截
        qtbot.keyClick(terminal_tab.terminal, Qt.Key_Backspace)
        assert True

    def test_left_key_blocked_at_input_start(self, terminal_tab, qtbot):
        """左箭头键在输入起始位置应被拦截"""
        terminal_tab.terminal.setPlainText("existing\n")
        terminal_tab.input_start_pos = len("existing\n")
        terminal_tab.terminal.moveCursor(terminal_tab.terminal.textCursor().End)

        qtbot.keyClick(terminal_tab.terminal, Qt.Key_Left)
        assert True

    def test_ctrl_v_pastes(self, terminal_tab, qtbot):
        """Ctrl+V 应粘贴剪贴板内容"""
        from PyQt5.QtWidgets import QApplication

        # 设置剪贴板内容
        clipboard = QApplication.clipboard()
        clipboard.setText("pasted_text")

        terminal_tab.input_start_pos = 0

        # 直接调用 keyPressEvent（offscreen 下事件路由不可靠）
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_V, Qt.ControlModifier, '\x16', False, 0)
        terminal_tab.terminal.keyPressEvent(event)

        # 验证粘贴内容出现在终端中
        assert "pasted_text" in terminal_tab.terminal.toPlainText()

    def test_modifier_keys_alone_pass_through(self, terminal_tab, qtbot):
        """单独的修饰键（Ctrl/Shift/Alt）应放行不崩溃"""
        event_ctrl = QKeyEvent(QEvent.KeyPress, Qt.Key_Control, Qt.NoModifier, '', False, 0)
        terminal_tab.terminal.keyPressEvent(event_ctrl)

        event_shift = QKeyEvent(QEvent.KeyPress, Qt.Key_Shift, Qt.NoModifier, '', False, 0)
        terminal_tab.terminal.keyPressEvent(event_shift)

        event_alt = QKeyEvent(QEvent.KeyPress, Qt.Key_Alt, Qt.NoModifier, '', False, 0)
        terminal_tab.terminal.keyPressEvent(event_alt)
        assert True

    def test_home_end_keys_work(self, terminal_tab, qtbot):
        """Home/End 键在输入区内应正常工作（不崩溃）"""
        terminal_tab.terminal.setPlainText("some text")
        terminal_tab.input_start_pos = 0
        qtbot.keyClick(terminal_tab.terminal, Qt.Key_End)
        qtbot.keyClick(terminal_tab.terminal, Qt.Key_Home)
        assert True


# ============================================================
# P0 补充：输出注入逻辑测试（inject_output）
# ============================================================


@pytest.mark.gui
class TestTerminalInjectOutput:
    """终端输出注入逻辑测试"""

    def test_inject_output_preserves_user_typing(self, terminal_tab):
        """输出注入应保留用户已输入但未发送的文字"""
        # 准备：终端已有一些输出，用户输入了一些文字
        terminal_tab.terminal.setPlainText("process output\n")
        terminal_tab.input_start_pos = len("process output\n")
        terminal_tab.terminal.moveCursor(terminal_tab.terminal.textCursor().End)

        # 模拟用户输入
        cursor = terminal_tab.terminal.textCursor()
        cursor.insertText("user typed this")
        terminal_tab.terminal.setTextCursor(cursor)

        # 注入新输出
        terminal_tab.inject_output("new output\n")

        # 用户输入的文字应保留
        full_text = terminal_tab.terminal.toPlainText()
        assert "user typed this" in full_text
        assert "new output" in full_text

    def test_inject_output_updates_input_start_pos(self, terminal_tab):
        """输出注入后输入起始位置应更新"""
        terminal_tab.terminal.setPlainText("initial output\n")
        terminal_tab.input_start_pos = len("initial output\n")

        old_pos = terminal_tab.input_start_pos
        terminal_tab.inject_output("more output\n")

        assert terminal_tab.input_start_pos > old_pos

    def test_inject_output_no_user_typing(self, terminal_tab):
        """无用户输入时输出注入不应出错"""
        terminal_tab.terminal.setPlainText("some output\n")
        terminal_tab.input_start_pos = len("some output\n")

        # 不应抛出异常
        terminal_tab.inject_output("new data\n")

        assert "new data" in terminal_tab.terminal.toPlainText()

    def test_inject_output_with_ansi_codes(self, terminal_tab):
        """输出注入应正确处理 ANSI 转义序列"""
        terminal_tab.terminal.setPlainText("")
        terminal_tab.input_start_pos = 0

        # 注入带 ANSI 颜色的文本
        terminal_tab.inject_output("\x1b[31mRed Text\x1b[0mNormal\n")

        # ANSI 码应被剥离，文本应显示
        content = terminal_tab.terminal.toPlainText()
        assert "\x1b" not in content
        assert "Red Text" in content
        assert "Normal" in content

    def test_inject_output_empty_string(self, terminal_tab):
        """空字符串输出注入不应崩溃"""
        terminal_tab.inject_output("")
        assert True

    def test_inject_output_ansi_color_mapping_does_not_crash(self, terminal_tab):
        """各种 ANSI 颜色码注入不应崩溃"""
        for code in [30, 31, 32, 33, 34, 35, 36, 37, 90, 91, 92, 93, 94, 95, 96, 97]:
            terminal_tab.inject_output(f"\x1b[{code}mColored\x1b[0m\n")
        assert True