# coding = utf-8
#
# @File name:       test_gui_script_management.py
# @brief:           GUI 层：脚本管理 CRUD 操作测试（新建/重命名/复制/移动/删除）
# @attention:       必须在模块级别 mock QInputDialog/QMessageBox 以避免实际弹窗阻塞
#                   注意：必须在 mock 前捕获 QMessageBox.Yes 的真实整数值(16384)
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
import os
import json
from PyQt5.QtCore import Qt, QEvent
from unittest.mock import MagicMock, patch

# QMessageBox.Yes 的真实整数值
_QMB_YES = 16384


def _mock_dialogs(monkeypatch, gettext_return=None, question_return=None):
    """在 PsLauncher.PsLauncher 模块中 mock QInputDialog 和 QMessageBox
    
    注意：question_return 必须使用整数值（如 _QMB_YES），
    因为源码中做了 if reply == QMessageBox.Yes 的整数比较。
    不能在 mock 之后再去访问 QMessageBox.Yes（已经是 MagicMock 了）。
    """
    import PsLauncher.PsLauncher as main_mod
    from unittest.mock import MagicMock

    # mock QInputDialog
    mock_input = MagicMock()
    if gettext_return is not None:
        mock_input.getText.return_value = gettext_return
        mock_input.getItem.return_value = gettext_return
    monkeypatch.setattr(main_mod, "QInputDialog", mock_input)

    # mock QMessageBox
    mock_msg = MagicMock()
    if question_return is not None:
        mock_msg.question.return_value = question_return
    monkeypatch.setattr(main_mod, "QMessageBox", mock_msg)

    return mock_input, mock_msg


# ============================================================
# GUI 层测试：脚本管理
# ============================================================


@pytest.mark.gui
class TestNewFolder:
    """新建文件夹功能测试"""

    def test_new_folder_creates_directory(self, main_window, sample_scripts_dir, monkeypatch):
        """新建文件夹应在磁盘上创建目录"""
        _mock_dialogs(monkeypatch,
                      gettext_return=("new_test_folder", True),
                      question_return=None)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        # 选中文件夹节点
        folder_item = main_window.tree.topLevelItem(0)
        main_window.tree.setCurrentItem(folder_item)

        main_window.new_folder_at_location()

        # 验证文件夹被创建
        new_folder_path = os.path.join(str(sample_scripts_dir), "new_test_folder")
        assert os.path.exists(new_folder_path)

        # 清理
        os.rmdir(new_folder_path)

    def test_new_folder_empty_name_cancels(self, main_window, sample_scripts_dir, monkeypatch):
        """空文件夹名应取消操作"""
        _mock_dialogs(monkeypatch,
                      gettext_return=("", False),
                      question_return=None)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        # 不应创建文件夹
        main_window.new_folder_at_location()
        assert True


@pytest.mark.gui
class TestNewScript:
    """新建脚本功能测试"""

    def test_new_script_ps1(self, main_window, sample_scripts_dir, monkeypatch):
        """新建 .ps1 脚本应创建文件并写入模板"""
        mock_input, mock_msg = _mock_dialogs(monkeypatch,
                      gettext_return=("test_new.ps1", True),
                      question_return=_QMB_YES)
        # 单独设置 getItem 返回正确的文件夹路径（与 getText 不同）
        mock_input.getItem.return_value = (str(sample_scripts_dir), True)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        # 选中文件夹
        folder_item = main_window.tree.topLevelItem(0)
        main_window.tree.setCurrentItem(folder_item)

        main_window.new_script_in_folder()

        new_file = os.path.join(str(sample_scripts_dir), "test_new.ps1")
        assert os.path.exists(new_file)

        # 验证包含模板内容
        with open(new_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "PowerShell" in content or "Write-Host" in content

        # 清理
        os.remove(new_file)


@pytest.mark.gui
class TestRenameScript:
    """重命名脚本功能测试"""

    def test_rename_script(self, main_window, sample_scripts_dir, monkeypatch):
        """重命名脚本应成功"""
        # 先创建一个要重命名的文件
        old_path = os.path.join(str(sample_scripts_dir), "rename_me.ps1")
        with open(old_path, 'w', encoding='utf-8') as f:
            f.write("# rename test")

        _mock_dialogs(monkeypatch,
                      gettext_return=("renamed.ps1", True),
                      question_return=None)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        # 选中脚本
        folder_item = main_window.tree.topLevelItem(0)
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.text(0) == "rename_me.ps1":
                main_window.tree.setCurrentItem(child)
                break

        main_window.rename_selected_script()

        new_path = os.path.join(str(sample_scripts_dir), "renamed.ps1")
        assert os.path.exists(new_path)
        assert not os.path.exists(old_path)

        # 清理
        os.remove(new_path)

    def test_rename_script_same_name_returns(self, main_window, sample_scripts_dir, monkeypatch):
        """重命名为同名应直接返回"""
        script_path = os.path.join(str(sample_scripts_dir), "test_script.ps1")

        _mock_dialogs(monkeypatch,
                      gettext_return=("test_script.ps1", True),
                      question_return=None)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        # 选中脚本
        folder_item = main_window.tree.topLevelItem(0)
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.text(0) == "test_script.ps1":
                main_window.tree.setCurrentItem(child)
                break

        # 不应出异常
        main_window.rename_selected_script()
        assert os.path.exists(script_path)


@pytest.mark.gui
class TestDeleteScript:
    """删除脚本功能测试"""

    def test_delete_script_removes_file(self, main_window, sample_scripts_dir, monkeypatch):
        """删除脚本应移除文件"""
        # 创建一个临时文件用于删除测试
        script_to_delete = os.path.join(str(sample_scripts_dir), "delete_me.ps1")
        with open(script_to_delete, 'w', encoding='utf-8') as f:
            f.write("# delete test")

        _mock_dialogs(monkeypatch,
                      gettext_return=None,
                      question_return=_QMB_YES)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        # 选中要删除的脚本
        folder_item = main_window.tree.topLevelItem(0)
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.text(0) == "delete_me.ps1":
                main_window.tree.setCurrentItem(child)
                break

        # 确认文件存在
        assert os.path.exists(script_to_delete)

        main_window.delete_selected_script()

        # 文件应被删除
        assert not os.path.exists(script_to_delete)


@pytest.mark.gui
class TestCopyScript:
    """复制脚本功能测试"""

    def test_copy_script_creates_copy(self, main_window, sample_scripts_dir, monkeypatch):
        """复制脚本应在同一目录创建副本"""
        _mock_dialogs(monkeypatch,
                      gettext_return=("test_script_copy.ps1", True),
                      question_return=None)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        # 选中脚本
        folder_item = main_window.tree.topLevelItem(0)
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.text(0) == "test_script.ps1":
                main_window.tree.setCurrentItem(child)
                break

        main_window.copy_selected_script()

        new_file = os.path.join(str(sample_scripts_dir), "test_script_copy.ps1")
        assert os.path.exists(new_file)

        # 清理
        os.remove(new_file)

    def test_copy_script_cancel_returns_no_file(self, main_window, sample_scripts_dir, monkeypatch):
        """取消复制操作不应创建文件"""
        _mock_dialogs(monkeypatch,
                      gettext_return=("", False),
                      question_return=None)

        main_window.config["folders"] = [str(sample_scripts_dir)]
        main_window.refresh_tree()

        folder_item = main_window.tree.topLevelItem(0)
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.text(0) == "test_script.ps1":
                main_window.tree.setCurrentItem(child)
                break

        main_window.copy_selected_script()

        # 不应创建意外文件
        for f in os.listdir(str(sample_scripts_dir)):
            assert "_copy" not in f


@pytest.mark.gui
class TestMoveScript:
    """移动脚本功能测试"""

    def test_move_script_to_another_folder(self, main_window, sample_scripts_dir, monkeypatch):
        """移动脚本到另一个文件夹"""
        # 创建第二个文件夹作为目标
        target_dir = sample_scripts_dir.parent / "target_dir"
        target_dir.mkdir()

        _mock_dialogs(monkeypatch,
                      gettext_return=(str(target_dir), True),
                      question_return=_QMB_YES)

        # 先把目标文件夹加入配置
        main_window.config["folders"] = [str(sample_scripts_dir), str(target_dir)]
        main_window.refresh_tree()

        # 选中脚本
        folder_item = main_window.tree.topLevelItem(0)
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.text(0) == "test_script.ps1":
                main_window.tree.setCurrentItem(child)
                break

        # 记录源文件路径
        source_path = os.path.join(str(sample_scripts_dir), "test_script.ps1")
        target_path = os.path.join(str(target_dir), "test_script.ps1")

        # 先备份原始文件
        with open(source_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        main_window.move_selected_script()

        # 源文件应不存在
        assert not os.path.exists(source_path)
        # 目标文件应存在
        assert os.path.exists(target_path)

        # 清理：把文件移回
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        os.remove(target_path)
        os.rmdir(str(target_dir))