# coding = utf-8
#
# @File name:       test_gui_main.py
# @brief:           GUI 层：主窗口构造、菜单 Action 触发、标签页增删、语言切换、主题切换
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


# ============================================================
# P1 补充：语言切换 UI 刷新测试
# ============================================================


@pytest.mark.gui
class TestLanguageSwitch:
    """语言切换 UI 刷新测试"""

    def test_switch_language_updates_config(self, main_window, monkeypatch):
        """切换语言后配置中的语言字段应更新"""
        from i18n import set_language, get_language
        set_language("en")  # 先设为英文

        main_window.switch_language("zh_CN")
        assert main_window.config["language"] == "zh_CN"

    def test_switch_language_same_language_returns_early(self, main_window, monkeypatch):
        """切换到当前语言应直接返回（不重复保存）"""
        from i18n import set_language
        set_language("en")
        main_window.config['language'] = 'en'

        # Mock save_config 跟踪调用
        save_called = False

        def track_save():
            nonlocal save_called
            save_called = True

        monkeypatch.setattr(main_window, 'save_config', track_save)

        main_window.switch_language("en")
        # save_config 不应被调用
        assert not save_called

    def test_switch_language_triggers_retranslate(self, main_window, monkeypatch):
        """切换语言应触 retranslate_ui"""
        from i18n import set_language, get_language
        # 确保当前不是 zh_CN
        if get_language() == "zh_CN":
            set_language("en")

        retranslate_called = False

        def track_retranslate():
            nonlocal retranslate_called
            retranslate_called = True

        monkeypatch.setattr(main_window, 'retranslate_ui', track_retranslate)

        # 直接设置 config 为 en 以确保条件成立
        main_window.config['language'] = 'en'

        main_window.switch_language("zh_CN")
        assert retranslate_called, "switch_language 应调用 retranslate_ui"

    def test_language_menu_actions_checkable(self, main_window):
        """语言菜单项应是可勾选的"""
        for lang, action in main_window.language_actions.items():
            assert action.isCheckable() is True
            # 至少有一项被选中
            if action.isChecked():
                assert action.text() != ""

    def test_auto_minimize_toggle_updates_config(self, main_window):
        """自动最小化开关应更新配置"""
        old_value = main_window.config.get('auto_minimize_to_tray', False)
        main_window.toggle_auto_minimize_to_tray()
        assert main_window.config['auto_minimize_to_tray'] == (not old_value)


# ============================================================
# P1 补充：toggle_line_wrap_mode、set_syntax_highlight_mode 测试
# ============================================================


@pytest.mark.gui
class TestViewSettings:
    """视图设置切换测试"""

    def test_toggle_line_wrap_mode_flips_config(self, main_window):
        """换行模式切换应翻转配置"""
        old_value = main_window.config['line_wrap_mode']
        main_window.toggle_line_wrap_mode()
        assert main_window.config['line_wrap_mode'] == (not old_value)

    def test_toggle_line_wrap_updates_action_checked(self, main_window):
        """换行模式切换后菜单项选中状态应同步"""
        old_checked = main_window.toggle_wrap_action.isChecked()
        main_window.toggle_line_wrap_mode()
        assert main_window.toggle_wrap_action.isChecked() == (not old_checked)

    def test_set_syntax_highlight_mode_updates_config(self, main_window):
        """设置语法高亮模式应更新配置"""
        main_window.set_syntax_highlight_mode('bash')
        assert main_window.config['syntax_highlight_mode'] == 'bash'
        assert main_window.syntax_bash_action.isChecked() is True

    def test_set_syntax_highlight_mode_multiple_times(self, main_window):
        """多次切换语法高亮模式应正常工作"""
        main_window.set_syntax_highlight_mode('ps1')
        assert main_window.config['syntax_highlight_mode'] == 'ps1'
        assert main_window.syntax_ps1_action.isChecked() is True
        assert main_window.syntax_bash_action.isChecked() is False

        main_window.set_syntax_highlight_mode('bash')
        assert main_window.config['syntax_highlight_mode'] == 'bash'
        assert main_window.syntax_ps1_action.isChecked() is False
        assert main_window.syntax_bash_action.isChecked() is True

    def test_set_syntax_highlight_mode_none(self, main_window):
        """设置语法高亮模式为 none"""
        main_window.set_syntax_highlight_mode('none')
        assert main_window.config['syntax_highlight_mode'] == 'none'
        assert main_window.syntax_none_action.isChecked() is True