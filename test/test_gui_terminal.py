# coding = utf-8
#
# @File name:       test_gui_terminal.py
# @brief:           GUI 层：终端标签 ANSI 渲染、交互输入、输入区域隔离
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
from PyQt5.QtCore import Qt

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