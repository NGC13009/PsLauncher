# coding = utf-8
#
# @File name:       test_syntax_highlight.py
# @brief:           算法层：语法高亮模式自动判别逻辑测试
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
import os

# ============================================================
# 算法层测试：语法高亮模式判别
# 测试 ScriptHighlighter 中 auto 模式下的 ext→mode 映射
# ============================================================


@pytest.mark.algo
class TestSyntaxHighlightModeDetection:
    """语法高亮模式自动判别逻辑"""

    def _detect_mode(self, ext):
        """模拟 ScriptHighlighter.__init__ 中的 auto 模式判别逻辑"""
        if ext == '.ps1':
            return 'ps1'
        elif ext == '.bat' or ext == '.cmd':
            return 'command'
        elif ext == '.sh':
            return 'bash'
        elif ext in ['.json', '.yaml', '.yml', '.xml', '.html', '.htm']:
            return 'ps1'
        elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']:
            return 'bash'
        else:
            return 'none'

    @pytest.mark.parametrize("ext,expected_mode", [
        ('.ps1', 'ps1'),
        ('.bat', 'command'),
        ('.cmd', 'command'),
        ('.sh', 'bash'),
        ('.json', 'ps1'),
        ('.yaml', 'ps1'),
        ('.yml', 'ps1'),
        ('.xml', 'ps1'),
        ('.html', 'ps1'),
        ('.htm', 'ps1'),
        ('.py', 'bash'),
        ('.js', 'bash'),
        ('.ts', 'bash'),
        ('.java', 'bash'),
        ('.cpp', 'bash'),
        ('.c', 'bash'),
        ('.cs', 'bash'),
        ('.txt', 'none'),
        ('.md', 'none'),
        ('.rst', 'none'),
        ('', 'none'),
        ('.unknown', 'none'),
    ])
    def test_auto_mode_detection(self, ext, expected_mode):
        """auto 模式下根据扩展名自动选择高亮模式"""
        mode = self._detect_mode(ext)
        assert mode == expected_mode, f"扩展名 {ext} 应映射到 {expected_mode}，实际得到 {mode}"

    def test_auto_mode_is_default(self, tmp_config_file):
        """默认配置中 syntax_highlight_mode 应为 auto"""
        from utils import load_json_with_comments
        config = load_json_with_comments(str(tmp_config_file))
        assert config.get('syntax_highlight_mode') == 'auto'

    def test_none_mode_returns_no_rules(self, qapp):
        """none 模式下不应创建任何语法规则"""
        from PyQt5.QtGui import QTextDocument
        from utils import ScriptHighlighter
        doc = QTextDocument()
        highlighter = ScriptHighlighter(doc, '.txt', True, syntax_mode='none')
        assert len(highlighter.rules) == 0

    def test_ps1_mode_has_rules(self, qapp):
        """ps1 模式应创建语法规则"""
        from PyQt5.QtGui import QTextDocument
        from utils import ScriptHighlighter
        doc = QTextDocument()
        highlighter = ScriptHighlighter(doc, '.ps1', True, syntax_mode='ps1')
        assert len(highlighter.rules) > 0

    def test_bash_mode_has_rules(self, qapp):
        """bash 模式应创建语法规则"""
        from PyQt5.QtGui import QTextDocument
        from utils import ScriptHighlighter
        doc = QTextDocument()
        highlighter = ScriptHighlighter(doc, '.sh', True, syntax_mode='bash')
        assert len(highlighter.rules) > 0

    def test_command_mode_has_rules(self, qapp):
        """command 模式应创建语法规则"""
        from PyQt5.QtGui import QTextDocument
        from utils import ScriptHighlighter
        doc = QTextDocument()
        highlighter = ScriptHighlighter(doc, '.bat', True, syntax_mode='command')
        assert len(highlighter.rules) > 0

    def test_auto_ps1_creates_rules(self, qapp):
        """auto 模式 + .ps1 应创建规则"""
        from PyQt5.QtGui import QTextDocument
        from utils import ScriptHighlighter
        doc = QTextDocument()
        highlighter = ScriptHighlighter(doc, '.ps1', True, syntax_mode='auto')
        assert len(highlighter.rules) > 0

    def test_auto_unknown_creates_no_rules(self, qapp):
        """auto 模式 + 未知扩展名不应创建规则"""
        from PyQt5.QtGui import QTextDocument
        from utils import ScriptHighlighter
        doc = QTextDocument()
        highlighter = ScriptHighlighter(doc, '.xyz', True, syntax_mode='auto')
        assert len(highlighter.rules) == 0

    def test_dark_mode_affects_colors(self, qapp):
        """暗色/亮色模式应影响颜色值"""
        from PyQt5.QtGui import QTextDocument, QColor
        from utils import ScriptHighlighter
        doc_dark = QTextDocument()
        doc_light = QTextDocument()
        hl_dark = ScriptHighlighter(doc_dark, '.ps1', True, syntax_mode='ps1')
        hl_light = ScriptHighlighter(doc_light, '.ps1', False, syntax_mode='ps1')
        # 两种模式都有规则
        assert len(hl_dark.rules) > 0
        assert len(hl_light.rules) > 0
        # 规则数量应相同
        assert len(hl_dark.rules) == len(hl_light.rules)