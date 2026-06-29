# coding = utf-8
#
# @File name:       test_autorun.py
# @brief:           功能层：启动时自动运行标记、蓝色高亮状态持久化
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest

# ============================================================
# 功能层测试：自动运行
# ============================================================


class TestAutoRunToggle:
    """自动运行切换逻辑测试"""

    def test_toggle_adds_to_list(self, main_window, sample_scripts_dir):
        """切换自动运行应将路径添加到列表"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.toggle_auto_run_script(script_path)
        assert script_path in main_window.config.get('auto_run_scripts', [])

    def test_toggle_removes_from_list(self, main_window, sample_scripts_dir):
        """再次切换应从列表中移除"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.toggle_auto_run_script(script_path)  # 添加
        main_window.toggle_auto_run_script(script_path)  # 移除
        assert script_path not in main_window.config.get('auto_run_scripts', [])

    def test_toggle_persists_to_config(self, main_window, sample_scripts_dir):
        """切换后配置中的 auto_run_scripts 应正确更新"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.toggle_auto_run_script(script_path)
        # 验证内存中的 config 已更新
        assert script_path in main_window.config.get('auto_run_scripts', [])

    def test_is_script_auto_run_true(self, main_window, sample_scripts_dir):
        """已标记的脚本应返回 True"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.toggle_auto_run_script(script_path)
        assert main_window.is_script_auto_run(script_path) is True

    def test_is_script_auto_run_false(self, main_window):
        """未标记的脚本应返回 False"""
        assert main_window.is_script_auto_run("nonexistent.ps1") is False

    def test_is_script_auto_run_empty_path(self, main_window):
        """空路径应返回 False"""
        assert main_window.is_script_auto_run("") is False
        assert main_window.is_script_auto_run(None) is False


class TestAutoRunHighlight:
    """自动运行高亮状态测试"""

    def test_auto_run_scripts_highlighted(self, main_window, sample_scripts_dir):
        """自动运行的脚本在树中应有蓝色高亮"""
        from PyQt5.QtCore import Qt
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.config["auto_run_scripts"] = [script_path]
        main_window.refresh_tree()

        # 找到脚本项并验证颜色
        folder_item = main_window.tree.topLevelItem(0)
        found_highlighted = False
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.data(0, Qt.UserRole) == script_path:
                foreground = child.foreground(0)
                assert foreground.style() == Qt.SolidPattern  # 有颜色设置
                found_highlighted = True
                break
        assert found_highlighted


class TestRunAutoStartScripts:
    """启动时自动运行脚本测试"""

    def test_run_auto_start_empty_list(self, main_window):
        """空自动运行列表不应崩溃"""
        main_window.config["auto_run_scripts"] = []
        # 不应抛出异常
        main_window.run_auto_start_scripts()

    def test_run_auto_start_nonexistent(self, main_window):
        """不存在的脚本应被跳过"""
        main_window.config["auto_run_scripts"] = [r"Z:\nonexistent.ps1"]
        # 不应崩溃
        main_window.run_auto_start_scripts()

    def test_run_auto_start_invalid_ext(self, main_window):
        """不支持的后缀应被跳过"""
        main_window.config["auto_run_scripts"] = ["dummy.txt"]
        main_window.config["runnable_extensions"] = [".ps1", ".bat", ".sh"]
        # 不应崩溃
        main_window.run_auto_start_scripts()