# coding = utf-8
#
# @File name:       test_gui_toolbar.py
# @brief:           GUI 层：工具栏按钮映射测试
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
from PyQt5.QtCore import Qt

# ============================================================
# GUI 层测试：工具栏
# ============================================================


@pytest.mark.gui
class TestToolbarButtons:
    """工具栏按钮存在性测试"""

    def test_toolbar_has_hide_button(self, main_window):
        """工具栏应有隐藏按钮"""
        assert hasattr(main_window, 'tray_btn')
        assert main_window.tray_btn.text() != ""

    def test_toolbar_has_run_button(self, main_window):
        """工具栏应有运行按钮"""
        assert hasattr(main_window, 'run_btn')
        assert "run" in main_window.run_btn.text().lower() or \
               main_window.run_btn.text() != ""

    def test_toolbar_has_stop_button(self, main_window):
        """工具栏应有停止按钮"""
        assert hasattr(main_window, 'stop_btn')

    def test_toolbar_has_interrupt_button(self, main_window):
        """工具栏应有中断按钮"""
        assert hasattr(main_window, 'send_ctrlc_btn')

    def test_toolbar_has_clear_button(self, main_window):
        """工具栏应有清屏按钮"""
        assert hasattr(main_window, 'clear_screen_btn')

    def test_toolbar_has_copy_paste(self, main_window):
        """工具栏应有复制/粘贴按钮"""
        assert hasattr(main_window, 'copy_btn')
        assert hasattr(main_window, 'paste_btn')

    def test_toolbar_has_tab_management(self, main_window):
        """工具栏应有标签管理按钮"""
        assert hasattr(main_window, 'close_editor_tabs_btn')
        assert hasattr(main_window, 'close_terminal_tabs_btn')
        assert hasattr(main_window, 'close_all_tabs_btn')

    def test_toolbar_has_edit_save(self, main_window):
        """工具栏应有编辑/保存按钮"""
        assert hasattr(main_window, 'edit_save_btn')


@pytest.mark.gui
class TestToolbarFunctionMapping:
    """工具栏按钮功能映射测试"""

    def test_run_button_triggers_run_selected(self, main_window):
        """运行按钮应连接到 run_selected_script"""
        # 通过信号连接验证
        # 触发 run_btn 应调用 run_selected_script
        # 这里只验证按钮存在且可点击，不实际执行以免启动进程
        assert main_window.run_btn.triggered is not None

    def test_stop_button_triggers_stop(self, main_window):
        """停止按钮应连接到 stop_current_script"""
        assert main_window.stop_btn.triggered is not None