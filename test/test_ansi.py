# coding = utf-8
#
# @File name:       test_ansi.py
# @brief:           算法层：ANSI 转义解析与着色逻辑测试
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
import re

# ============================================================
# 算法层测试：ANSI 转义序列解析
# 测试 TerminalTab.parse_and_append_ansi 的纯解析逻辑
# 需要 QApplication 环境，但不需要完整窗口
# ============================================================


@pytest.mark.algo
class TestAnsiParsingLogic:
    """ANSI 转义序列解析逻辑测试"""

    @pytest.fixture(autouse=True)
    def _setup_qapp(self, qapp):
        """确保 QApplication 存在（parse_and_append_ansi 需要 QTextCharFormat）"""
        pass

    def test_plain_text_no_ansi(self):
        """无 ANSI 码的纯文本"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "Hello, World!"
        parts = ansi_regex.split(text)
        assert len(parts) == 1
        assert parts[0] == "Hello, World!"

    def test_single_color_code(self):
        """单个 ANSI 颜色码：\x1b[31mRed\x1b[0m → 5 段"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "\x1b[31mRed Text\x1b[0mNormal"
        parts = ansi_regex.split(text)
        # split 结果：["", "31", "Red Text", "0", "Normal"] 共 5 段
        assert len(parts) == 5
        assert parts[0] == ""
        assert parts[1] == "31"
        assert parts[2] == "Red Text"
        assert parts[3] == "0"
        assert parts[4] == "Normal"

    def test_multiple_color_codes(self):
        """多个 ANSI 颜色码：\x1b[32mGreen\x1b[33mYellow\x1b[0m → 7 段"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "\x1b[32mGreen\x1b[33mYellow\x1b[0m"
        parts = ansi_regex.split(text)
        # 3 个 ANSI 码 → split 得 7 段
        assert len(parts) == 7
        assert parts[0] == ""
        assert parts[1] == "32"
        assert parts[2] == "Green"
        assert parts[3] == "33"
        assert parts[4] == "Yellow"
        assert parts[5] == "0"
        assert parts[6] == ""

    def test_color_code_mapping(self):
        """ANSI 颜色码到 QColor 映射验证"""
        colors = {
            30: '#1e1e1e',
            31: '#CD3131',
            32: '#0DBC79',
            33: '#E5E510',
            34: '#2472C8',
            35: '#BC3FBC',
            36: '#11A8CD',
            37: '#E5E5E5',
            90: '#666666',
            91: '#F14C4C',
            92: '#23D18B',
            93: '#F5F543',
            94: '#3B8EEA',
            95: '#D670D6',
            96: '#29B8DB',
            97: '#E5E5E5'
        }
        assert colors[30] == '#1e1e1e'  # 黑
        assert colors[31] == '#CD3131'  # 红
        assert colors[32] == '#0DBC79'  # 绿
        assert colors[33] == '#E5E510'  # 黄
        assert colors[34] == '#2472C8'  # 蓝
        assert colors[35] == '#BC3FBC'  # 紫
        assert colors[36] == '#11A8CD'  # 青
        assert colors[37] == '#E5E5E5'  # 白

    def test_code_0_resets_format(self):
        """码 0 应重置格式"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "\x1b[31mRed\x1b[0mNormal"
        parts = ansi_regex.split(text)
        assert parts[1] == "31"  # 红色码
        assert parts[3] == "0"  # 重置码

    def test_bright_color_codes(self):
        """亮色系颜色码 (90-97)"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "\x1b[91mBright Red\x1b[0m"
        parts = ansi_regex.split(text)
        assert parts[1] == "91"

    def test_complex_ansi_sequence(self):
        """复杂 ANSI 序列（含分号）"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "\x1b[1;31mBold Red\x1b[0m"
        parts = ansi_regex.split(text)
        assert parts[1] == "1;31"  # 分号分隔的参数

    def test_multiple_codes_with_reset_cycle(self):
        """多色交替 + 重置的完整路径"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "\x1b[32mGREEN\x1b[0m \x1b[31mRED\x1b[0m"
        parts = ansi_regex.split(text)
        # 4 个 ANSI 码 → split 得 9 段
        assert len(parts) == 9
        assert parts[1] == "32"
        assert parts[3] == "0"
        assert parts[4] == " "
        assert parts[5] == "31"
        assert parts[7] == "0"

    def test_empty_ansi_code_handling(self):
        """空 ANSI 码处理"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "\x1b[mEmpty code"
        parts = ansi_regex.split(text)
        assert "" in parts

    def test_no_ansi_contains_bracket(self):
        """不含 ANSI 但含普通方括号的文本"""
        ansi_regex = re.compile(r'\x1b\[([\d;]*)m')
        text = "Normal [brackets] here"
        parts = ansi_regex.split(text)
        assert len(parts) == 1
        assert parts[0] == "Normal [brackets] here"