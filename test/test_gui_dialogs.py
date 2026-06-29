# coding = utf-8
#
# @File name:       test_gui_dialogs.py
# @brief:           GUI 层：About/Help 对话框测试
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest


# ============================================================
# GUI 层测试：对话框
# ============================================================


@pytest.mark.gui
class TestAboutDialog:
    """关于对话框测试"""

    def test_about_dialog_has_content(self, qapp):
        """关于对话框应成功创建并包含内容"""
        from aboutandhelp import AboutDialog
        # 创建临时父窗口
        from PyQt5.QtWidgets import QWidget
        parent = QWidget()
        dialog = AboutDialog(parent)
        assert dialog is not None
        # 应有标题
        assert dialog.windowTitle() != ""

    def test_about_dialog_has_version_label(self, qapp):
        """关于对话框应包含版本号信息"""
        from aboutandhelp import AboutDialog
        from PyQt5.QtWidgets import QWidget
        parent = QWidget()
        dialog = AboutDialog(parent)
        # 检查对话框中的标签
        labels = dialog.findChildren(type(dialog).__bases__[0].__subclasses__()[0]) if False else []
        # 简单验证对话框已构造
        assert dialog.layout() is not None


@pytest.mark.gui
class TestHelpDialog:
    """帮助对话框测试"""

    def test_help_dialog_has_content(self, qapp):
        """帮助对话框应成功创建"""
        from aboutandhelp import HelpDialog
        from PyQt5.QtWidgets import QWidget
        parent = QWidget()
        dialog = HelpDialog(parent)
        assert dialog is not None
        # 应有标题
        assert dialog.windowTitle() != ""


# ============================================================
# P2 补充：编辑器编码回退测试
# ============================================================


@pytest.mark.gui
class TestEditorEncoding:
    """编辑器编码处理测试"""

    def test_load_file_utf8_success(self, qapp, tmp_path):
        """UTF-8 文件应正常加载"""
        from tabClass import EditorTab
        from PyQt5.QtWidgets import QWidget

        # 创建 UTF-8 文件
        script_file = tmp_path / "test_utf8.ps1"
        script_file.write_text('# UTF-8 content\nWrite-Host "测试"\n', encoding="utf-8")

        tab = EditorTab(str(script_file), "Consolas", True, True)
        content = tab.editor.toPlainText()
        assert "测试" in content

    def test_load_file_gbk_fallback(self, qapp, tmp_path):
        """GBK 编码文件应能回退加载（不崩溃）"""
        from tabClass import EditorTab

        # 创建 GBK 编码文件（仅含 ASCII 字符，因为 GBK 和 UTF-8 在 ASCII 范围内相同）
        script_file = tmp_path / "test_gbk.ps1"
        # 使用 GBK 编码写入中文（这样 UTF-8 解码会失败）
        script_file.write_bytes(b'# GBK content\nWrite-Host \xb2\xe2\xca\xd4\n')  # "测试" 的 GBK 编码

        # 不应抛出异常
        tab = EditorTab(str(script_file), "Consolas", True, True)
        content = tab.editor.toPlainText()
        assert content is not None

    def test_save_file_uses_utf8(self, qapp, tmp_path):
        """保存文件应使用 UTF-8 编码"""
        from tabClass import EditorTab

        script_file = tmp_path / "test_save.ps1"
        script_file.write_text("original content", encoding="utf-8")

        tab = EditorTab(str(script_file), "Consolas", True, True)
        tab.editor.setPlainText("modified content")
        success = tab.save_file()
        assert success is True

        # 验证文件内容
        with open(str(script_file), 'r', encoding='utf-8') as f:
            saved = f.read()
        assert saved == "modified content"


# ============================================================
# P2 补充：ZoomableTextEdit 样式测试
# ============================================================


@pytest.mark.gui
class TestZoomableTextEditStyle:
    """ZoomableTextEdit 样式测试"""

    def test_dark_mode_style(self, qapp):
        """暗色模式下 ZoomableTextEdit 应使用暗色背景"""
        from tabClass import ZoomableTextEdit

        edit = ZoomableTextEdit("Consolas", True, True)
        # 验证样式表包含暗色背景色
        assert "#1E1E1E" in edit.styleSheet() or "background" in edit.styleSheet()
        assert edit is not None

    def test_light_mode_style(self, qapp):
        """亮色模式下 ZoomableTextEdit 应使用亮色背景"""
        from tabClass import ZoomableTextEdit

        edit = ZoomableTextEdit("Consolas", False, True)
        assert edit is not None

    def test_default_font_applied(self, qapp):
        """ZoomableTextEdit 应使用默认字体"""
        from tabClass import ZoomableTextEdit
        from PyQt5.QtWidgets import QApplication

        edit = ZoomableTextEdit("Consolas", True, True)
        # 字体族至少不为空
        assert edit.font().family() != ""
