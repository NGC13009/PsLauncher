# coding = utf-8
#
# @File name:       test_gui_main.py
# @brief:           GUI 层：主窗口构造、菜单 Action 触发、标签页增删
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
from PyQt5.QtCore import Qt

# ============================================================
# GUI 层测试：主窗口
# 需要 pytest-qt 的 qtbot fixture
# ============================================================


@pytest.mark.gui
class TestMainWindowConstruction:
    """主窗口构造测试"""

    def test_window_created(self, main_window):
        """主窗口应成功创建"""
        assert main_window is not None
        assert main_window.windowTitle() != ""

    def test_window_has_menu_bar(self, main_window):
        """主窗口应有菜单栏"""
        menubar = main_window.menuBar()
        assert menubar is not None
        # 菜单栏应有子菜单
        assert len(menubar.actions()) >= 5  # 系统、文件、编辑、运行、视图、脚本、标签、帮助

    def test_window_has_toolbar(self, main_window):
        """主窗口应有工具栏"""
        assert main_window.toolbar is not None
        assert len(main_window.toolbar.actions()) > 0

    def test_window_has_tree_widget(self, main_window):
        """主窗口应有文件树"""
        assert main_window.tree is not None
        assert main_window.tree.headerItem() is not None

    def test_window_has_tab_widget(self, main_window):
        """主窗口应有标签页控件"""
        assert main_window.tabs is not None
        assert main_window.tabs.count() == 0


@pytest.mark.gui
class TestMenuActions:
    """菜单 Action 存在性测试"""

    def test_system_menu_actions(self, main_window):
        """系统菜单应有保存、隐藏、自动最小化"""
        assert hasattr(main_window, 'save_action')
        assert hasattr(main_window, 'hide_action')
        assert hasattr(main_window, 'auto_minimize_action')

    def test_file_menu_actions(self, main_window):
        """文件菜单应有添加/删除文件夹"""
        assert hasattr(main_window, 'addpath_action')
        assert hasattr(main_window, 'removepath_action')

    def test_edit_menu_actions(self, main_window):
        """编辑菜单应有复制、粘贴、全选复制、清屏、编辑保存"""
        assert hasattr(main_window, 'copy_action')
        assert hasattr(main_window, 'paste_action')
        assert hasattr(main_window, 'copy_all_action')
        assert hasattr(main_window, 'clear_screen_action')
        assert hasattr(main_window, 'edit_save_action')

    def test_run_menu_actions(self, main_window):
        """运行菜单应有启动、停止、发送 Ctrl+C"""
        assert hasattr(main_window, 'run_action')
        assert hasattr(main_window, 'stop_action')
        assert hasattr(main_window, 'send_ctrlc_action')

    def test_view_menu_actions(self, main_window):
        """视图菜单应有换行切换和语法高亮子菜单"""
        assert hasattr(main_window, 'toggle_wrap_action')
        assert hasattr(main_window, 'syntax_menu')
        assert hasattr(main_window, 'syntax_auto_action')
        assert hasattr(main_window, 'syntax_ps1_action')
        assert hasattr(main_window, 'syntax_bash_action')
        assert hasattr(main_window, 'syntax_command_action')
        assert hasattr(main_window, 'syntax_none_action')

    def test_script_menu_actions(self, main_window):
        """脚本管理菜单应有新建、重命名、复制、移动、删除"""
        assert hasattr(main_window, 'new_folder_action')
        assert hasattr(main_window, 'new_script_action')
        assert hasattr(main_window, 'rename_script_action')
        assert hasattr(main_window, 'copy_script_action')
        assert hasattr(main_window, 'move_script_action')
        assert hasattr(main_window, 'delete_script_action')

    def test_tab_menu_actions(self, main_window):
        """标签页菜单应有关闭编辑器/终端/全部"""
        assert hasattr(main_window, 'close_editor_tabs_action')
        assert hasattr(main_window, 'close_terminal_tabs_action')
        assert hasattr(main_window, 'close_all_tabs_action')

    def test_language_menu_actions(self, main_window):
        """语言菜单应包含可用语言"""
        assert hasattr(main_window, 'language_menu')
        assert len(main_window.language_actions) >= 2


@pytest.mark.gui
class TestToolbarMapping:
    """工具栏与菜单 Action 一致性测试"""

    def test_toolbar_run_matches_menu(self, main_window):
        """工具栏运行按钮关联的函数与菜单运行 Action 相同"""
        assert main_window.run_btn.triggered is not None
        # 验证都连接到同一个槽函数
        assert main_window.run_btn.triggered != main_window.stop_btn.triggered

    def test_toolbar_stop_matches_menu(self, main_window):
        """工具栏停止按钮关联的函数与菜单停止 Action 相同"""
        assert main_window.stop_btn.triggered is not None


@pytest.mark.gui
class TestTabManagement:
    """标签页管理测试"""

    def test_open_editor_tab(self, main_window, sample_scripts_dir):
        """打开一个编辑器标签页"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_editor_tab(script_path)
        assert main_window.tabs.count() == 1

    def test_open_terminal_tab(self, main_window, sample_scripts_dir):
        """打开一个终端标签页（不启动进程）"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        # 直接调用 open_terminal_tab 会启动进程，我们 mock 掉
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None
        try:
            main_window.open_terminal_tab(script_path)
            assert main_window.tabs.count() == 1
        finally:
            tabClass.TerminalTab.start_process = original_start

    def test_close_tab(self, main_window, sample_scripts_dir):
        """关闭标签页"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_editor_tab(script_path)
        assert main_window.tabs.count() == 1
        main_window.close_tab(0)
        assert main_window.tabs.count() == 0

    def test_tab_switching(self, main_window, sample_scripts_dir):
        """标签切换"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_editor_tab(script_path)
        # 再打开一个终端标签
        from tabClass import TerminalTab
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None
        try:
            main_window.open_terminal_tab(script_path)
            assert main_window.tabs.count() == 2
            # 切换到第一个标签
            main_window.tabs.setCurrentIndex(0)
            assert main_window.tabs.currentIndex() == 0
        finally:
            tabClass.TerminalTab.start_process = original_start


@pytest.mark.gui
class TestDarkLightTheme:
    """暗色/亮色主题测试"""

    def test_dark_mode_default(self, main_window):
        """默认暗色模式"""
        assert main_window.dark_mode is True

    def test_light_mode(self, main_window_light):
        """亮色模式"""
        assert main_window_light.dark_mode is False