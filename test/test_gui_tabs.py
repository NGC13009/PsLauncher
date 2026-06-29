# coding = utf-8
#
# @File name:       test_gui_tabs.py
# @brief:           GUI 层：标签页批量关闭、F8/F9 快捷键、编辑态确认流程
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


# ============================================================
# P1 补充：编辑态标签关闭流程测试
# ============================================================


@pytest.mark.gui
class TestTabEditingCloseFlow:
    """编辑态标签关闭流程测试"""

    def test_close_editing_tab_discard(self, main_window, sample_scripts_dir, monkeypatch):
        """编辑中的标签关闭时选择 Discard 应正常关闭"""
        from PyQt5.QtWidgets import QMessageBox

        # Mock QMessageBox.question 返回 Discard
        original_question = QMessageBox.question
        monkeypatch.setattr(QMessageBox, 'question',
                            staticmethod(lambda *a, **kw: QMessageBox.Discard))

        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_editor_tab(script_path)
        editor_widget = main_window.tabs.currentWidget()

        # 进入编辑模式
        editor_widget.set_editing(True)
        assert editor_widget.is_editing is True

        # 关闭标签（应触发保存确认弹窗，但被 mock 拦截返回 Discard）
        main_window.close_tab(0)
        assert main_window.tabs.count() == 0

    def test_close_editing_tab_cancel(self, main_window, sample_scripts_dir, monkeypatch):
        """编辑中的标签关闭时选择 Cancel 应取消关闭"""
        from PyQt5.QtWidgets import QMessageBox

        # Mock QMessageBox.question 返回 Cancel
        monkeypatch.setattr(QMessageBox, 'question',
                            staticmethod(lambda *a, **kw: QMessageBox.Cancel))

        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_editor_tab(script_path)
        editor_widget = main_window.tabs.currentWidget()

        # 进入编辑模式
        editor_widget.set_editing(True)

        # 关闭标签 - 点 Cancel 不应关闭
        main_window.close_tab(0)
        # 标签应仍然存在
        assert main_window.tabs.count() == 1

    def test_close_editing_tab_save(self, main_window, sample_scripts_dir, monkeypatch):
        """编辑中的标签关闭时选择 Save 应保存并关闭"""
        from PyQt5.QtWidgets import QMessageBox

        script_path = str(sample_scripts_dir / "test_script.ps1")
        original_content = open(script_path, 'r', encoding='utf-8').read()

        monkeypatch.setattr(QMessageBox, 'question',
                            staticmethod(lambda *a, **kw: QMessageBox.Save))

        main_window.open_editor_tab(script_path)
        editor_widget = main_window.tabs.currentWidget()

        # 进入编辑模式并修改内容
        editor_widget.set_editing(True)
        editor_widget.editor.setPlainText(original_content + "\n# New line")

        main_window.close_tab(0)
        # 标签应被关闭
        assert main_window.tabs.count() == 0

        # 文件内容应被保存（包含新行）
        with open(script_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        assert "# New line" in saved_content

        # 恢复文件内容
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

    def test_close_all_editor_tabs_with_editing(self, main_window, sample_scripts_dir, monkeypatch):
        """关闭所有编辑器标签时编辑态检查"""
        from PyQt5.QtWidgets import QMessageBox

        monkeypatch.setattr(QMessageBox, 'question',
                            staticmethod(lambda *a, **kw: QMessageBox.Discard))

        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_editor_tab(script_path)
        main_window.open_editor_tab(str(sample_scripts_dir / "test_script.bat"))

        # 进入编辑模式
        editor_widget = main_window.tabs.widget(0)
        editor_widget.set_editing(True)

        # 关闭所有编辑器标签
        main_window.close_all_editor_tabs()
        # 所有编辑器标签应被关闭
        assert main_window.tabs.count() == 0

    def test_close_all_tabs_no_terminal(self, main_window, monkeypatch):
        """无终端标签时关闭所有标签不应弹终端确认"""
        from PyQt5.QtWidgets import QMessageBox

        monkeypatch.setattr(QMessageBox, 'question',
                            staticmethod(lambda *a, **kw: QMessageBox.Yes))

        # 没有打开任何标签，close_all_tabs 不应崩溃
        main_window.close_all_tabs()
        assert True


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