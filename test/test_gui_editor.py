# coding = utf-8
#
# @File name:       test_gui_editor.py
# @brief:           GUI 层：源码标签只读/编辑切换、保存、编码处理
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
from PyQt5.QtCore import Qt

# ============================================================
# GUI 层测试：编辑器标签页
# ============================================================


@pytest.mark.gui
class TestEditorTab:
    """编辑器标签页测试"""

    def test_editor_tab_creation(self, editor_tab, sample_scripts_dir):
        """编辑器标签应成功创建"""
        assert editor_tab is not None
        assert editor_tab.is_editing is False
        assert editor_tab.editor.isReadOnly() is True

    def test_editor_loads_file_content(self, editor_tab):
        """编辑器应加载文件内容"""
        content = editor_tab.editor.toPlainText()
        assert len(content) > 0
        assert "PowerShell" in content or "Write-Host" in content

    def test_editor_readonly_by_default(self, editor_tab):
        """编辑器默认只读"""
        assert editor_tab.editor.isReadOnly() is True

    def test_set_editing_enables_write(self, editor_tab):
        """设置编辑模式后应可写"""
        editor_tab.set_editing(True)
        assert editor_tab.is_editing is True
        assert editor_tab.editor.isReadOnly() is False

    def test_set_editing_disables_write(self, editor_tab):
        """取消编辑模式后应只读"""
        editor_tab.set_editing(True)
        editor_tab.set_editing(False)
        assert editor_tab.is_editing is False
        assert editor_tab.editor.isReadOnly() is True

    def test_editor_toggle_editing_state(self, editor_tab):
        """编辑模式切换状态"""
        editor_tab.set_editing(True)
        assert editor_tab.is_editing is True
        editor_tab.set_editing(False)
        assert editor_tab.is_editing is False

    def test_editor_syntax_highlighter_exists(self, editor_tab):
        """编辑器应有语法高亮器"""
        assert editor_tab.highlighter is not None

    def test_editor_apply_syntax_mode_ps1(self, editor_tab):
        """切换语法高亮模式为 ps1"""
        editor_tab.apply_syntax_highlight_mode('ps1')
        assert editor_tab.current_syntax_mode == 'ps1'

    def test_editor_apply_syntax_mode_none(self, editor_tab):
        """切换语法高亮模式为 none"""
        editor_tab.apply_syntax_highlight_mode('none')
        assert editor_tab.current_syntax_mode == 'none'

    def test_editor_save_file_preserves_content(self, editor_tab, tmp_path):
        """保存文件应保留内容"""
        original_content = editor_tab.editor.toPlainText()
        success = editor_tab.save_file()
        # 保存后文件内容应与原始内容一致
        with open(editor_tab.script_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        assert saved_content == original_content

    def test_editor_line_wrap_toggle(self, editor_tab):
        """换行模式切换"""
        editor_tab.set_line_wrap_mode(True)
        editor_tab.set_line_wrap_mode(False)


@pytest.mark.gui
class TestZoomableTextEdit:
    """可缩放文本编辑控件测试"""

    def test_zoom_in(self, qapp, sample_scripts_dir):
        """Ctrl+滚轮上滚应放大"""
        from tabClass import ZoomableTextEdit
        edit = ZoomableTextEdit("Consolas", True, True)
        original_size = edit.font().pointSize()
        # 模拟滚轮事件
        from PyQt5.QtGui import QWheelEvent
        from PyQt5.QtCore import QPoint, QPointF
        event = QWheelEvent(
            QPointF(0, 0), QPoint(0, 0),
            QPoint(0, 120), QPoint(0, 120),
            Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False
        )
        edit.wheelEvent(event)
        # 缩放后字体大小应改变
        assert edit.font().pointSize() > original_size

    def test_zoom_out(self, qapp, sample_scripts_dir):
        """Ctrl+滚轮下滚应缩小"""
        from tabClass import ZoomableTextEdit
        edit = ZoomableTextEdit("Consolas", True, True)
        original_size = edit.font().pointSize()
        from PyQt5.QtGui import QWheelEvent
        from PyQt5.QtCore import QPoint, QPointF
        event = QWheelEvent(
            QPointF(0, 0), QPoint(0, 0),
            QPoint(0, -120), QPoint(0, -120),
            Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False
        )
        edit.wheelEvent(event)
        assert edit.font().pointSize() < original_size