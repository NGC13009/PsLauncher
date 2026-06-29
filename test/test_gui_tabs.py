# coding = utf-8
#
# @File name:       test_gui_tabs.py
# @brief:           GUI 层：标签页批量关闭、F8/F9 快捷键、运行中进程终止
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
from PyQt5.QtCore import Qt
from unittest.mock import MagicMock

# ============================================================
# GUI 层测试：标签页管理
# ============================================================


@pytest.mark.gui
class TestTabCloseOperations:
    """标签页关闭操作测试"""

    def test_close_editor_tabs(self, main_window, sample_scripts_dir):
        """关闭所有编辑器标签页"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_editor_tab(script_path)
        main_window.open_editor_tab(str(sample_scripts_dir / "test_script.bat"))
        assert main_window.tabs.count() == 2
        main_window.close_all_editor_tabs()
        assert main_window.tabs.count() == 0

    def test_close_terminal_tabs(self, main_window, sample_scripts_dir, monkeypatch):
        """关闭所有终端标签页"""
        # 避免 QMessageBox.question 弹窗（offscreen 下崩溃）
        # PsLauncher 使用 from PyQt5.QtWidgets import *，需 patch 模块级别的引用
        import PsLauncher.PsLauncher as main_mod
        monkeypatch.setattr(main_mod, "QMessageBox", MagicMock())
        main_mod.QMessageBox.question.return_value = main_mod.QMessageBox.Yes
        from tabClass import TerminalTab
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None
        try:
            script_path = str(sample_scripts_dir / "test_script.ps1")
            main_window.open_terminal_tab(script_path)
            main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.bat"))
            assert main_window.tabs.count() == 2
            main_window.close_all_terminal_tabs()
            assert main_window.tabs.count() == 0
        finally:
            tabClass.TerminalTab.start_process = original_start

    def test_close_all_tabs(self, main_window, sample_scripts_dir, monkeypatch):
        """关闭所有标签页"""
        # 避免 QMessageBox.question 弹窗（offscreen 下崩溃）
        monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.question",
                            staticmethod(lambda *a, **kw: 16384))  # QMessageBox.Yes
        from tabClass import TerminalTab
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None
        try:
            script_path = str(sample_scripts_dir / "test_script.ps1")
            main_window.open_editor_tab(script_path)
            main_window.open_terminal_tab(script_path)
            assert main_window.tabs.count() == 2
            main_window.close_all_tabs()
            assert main_window.tabs.count() == 0
        finally:
            tabClass.TerminalTab.start_process = original_start

    def test_close_tab_stops_process(self, main_window, sample_scripts_dir):
        """关闭终端标签应停止进程"""
        from tabClass import TerminalTab
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None
        try:
            script_path = str(sample_scripts_dir / "test_script.ps1")
            main_window.open_terminal_tab(script_path)
            # 获取终端标签并 mock stop_process
            terminal_widget = main_window.tabs.currentWidget()
            assert isinstance(terminal_widget, TerminalTab)
            terminal_widget.stop_process = lambda: None
            main_window.close_tab(0)
            assert main_window.tabs.count() == 0
        finally:
            tabClass.TerminalTab.start_process = original_start


@pytest.mark.gui
class TestTabShortcuts:
    """标签页快捷键测试"""

    def test_f8_shortcut_exists(self, main_window):
        """F8 快捷键应存在"""
        assert main_window.close_editor_tabs_action.shortcut() == "F8"

    def test_f9_shortcut_exists(self, main_window):
        """F9 快捷键应存在"""
        assert main_window.close_terminal_tabs_action.shortcut() == "F9"

    def test_f5_shortcut_exists(self, main_window):
        """F5 快捷键应存在"""
        assert main_window.run_action.shortcut() == "F5"

    def test_f6_shortcut_exists(self, main_window):
        """F6 快捷键应存在"""
        assert main_window.stop_action.shortcut() == "F6"

    def test_f7_shortcut_exists(self, main_window):
        """F7 快捷键应存在"""
        assert main_window.send_ctrlc_action.shortcut() == "F7"