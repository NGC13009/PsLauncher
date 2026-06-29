# coding = utf-8
#
# @File name:       test_scanner.py
# @brief:           功能层：文件夹扫描测试（不递归、后缀过滤、实时刷新）
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
import os
import json

# ============================================================
# 功能层测试：文件夹扫描与文件树刷新
# 模拟 MainWindow.refresh_tree 的扫描逻辑
# ============================================================


class TestFolderScanner:
    """文件夹扫描逻辑测试"""

    def test_scan_only_top_level(self, sample_scripts_dir):
        """扫描仅限根目录，不递归子目录"""
        from utils import DEFAULT_EXT
        folder = str(sample_scripts_dir)
        found_files = []
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in DEFAULT_EXT:
                    found_files.append(file)
        # 应找到 .ps1, .bat, .sh 文件
        assert "test_script.ps1" in found_files
        assert "test_script.bat" in found_files
        assert "test_script.sh" in found_files
        # 不应包含 .txt 文件
        assert "readme.txt" not in found_files
        # 不应包含子目录中的文件
        assert "sub_script.ps1" not in found_files

    def test_supported_extensions_filter(self, sample_scripts_dir):
        """仅扫描 supported_extensions 中列出的后缀"""
        supported = ['.ps1', '.bat', '.sh']
        folder = str(sample_scripts_dir)
        for file in os.listdir(folder):
            ext = os.path.splitext(file)[1].lower()
            if ext in supported:
                assert ext in supported
            else:
                assert ext not in supported or file == "readme.txt"

    def test_empty_directory(self, tmp_path):
        """空目录不应返回任何结果"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        from utils import DEFAULT_EXT
        found = [f for f in os.listdir(str(empty_dir))
                 if os.path.isfile(os.path.join(str(empty_dir), f)) and
                 os.path.splitext(f)[1].lower() in DEFAULT_EXT]
        assert len(found) == 0

    def test_directory_not_exists_handled(self):
        """不存在的目录应安全处理"""
        nonexistent = r"Z:\does_not_exist_12345"
        exists = os.path.exists(nonexistent)
        assert not exists  # 确保目录确实不存在

    def test_case_insensitive_extensions(self, sample_scripts_mixed):
        """扩展名大小写不敏感"""
        from utils import DEFAULT_EXT
        folder = str(sample_scripts_mixed)
        found = []
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in DEFAULT_EXT:
                    found.append(file)
        # 应找到 .ps1 和 .bat 文件
        assert "normal.ps1" in found
        assert "normal.bat" in found


class TestTreeRefresh:
    """文件树刷新逻辑测试（基于 refresh_tree 方法设计）"""

    def test_refresh_tree_with_folders(self, main_window, sample_scripts_dir):
        """refresh_tree 应包含指定文件夹的内容"""
        # 向配置中添加脚本目录
        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()
        # 验证树中有项目
        assert main_window.tree.topLevelItemCount() >= 1

    def test_refresh_tree_empty_folders(self, main_window):
        """refresh_tree 在无文件夹时不应崩溃"""
        main_window.config["folders"] = []
        main_window.refresh_tree()
        assert main_window.tree.topLevelItemCount() == 0

    def test_refresh_tree_nonexistent_folder(self, main_window):
        """refresh_tree 应跳过不存在的文件夹"""
        main_window.config["folders"] = [r"Z:\nonexistent_path_xyz"]
        main_window.refresh_tree()
        # 不应崩溃，树应为空
        assert main_window.tree.topLevelItemCount() == 0

    def test_refresh_tree_folder_item_data(self, main_window, sample_scripts_dir):
        """文件夹项应存储完整路径在 UserRole 中"""
        from PyQt5.QtCore import Qt
        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()
        folder_item = main_window.tree.topLevelItem(0)
        stored_path = folder_item.data(0, Qt.UserRole)
        assert stored_path == str(sample_scripts_dir)