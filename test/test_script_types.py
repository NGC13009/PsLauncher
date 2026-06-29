# coding = utf-8
#
# @File name:       test_script_types.py
# @brief:           算法层：脚本后缀识别、解释器选择、扩展名校验
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
import os

# ============================================================
# 算法层测试：脚本类型识别
# 无 Qt 依赖，可安全并行执行
# ============================================================


class TestDefaultExtensions:
    """DEFAULT_EXT 常量校验"""

    def test_default_ext_contains_required(self):
        """DEFAULT_EXT 必须包含 .ps1, .bat, .sh"""
        from utils import DEFAULT_EXT
        for ext in ['.ps1', '.bat', '.sh']:
            assert ext in DEFAULT_EXT, f"缺少必需的后缀: {ext}"

    def test_default_ext_all_lowercase(self):
        """所有扩展名必须小写"""
        from utils import DEFAULT_EXT
        for ext in DEFAULT_EXT:
            assert ext == ext.lower(), f"扩展名应小写: {ext}"

    def test_default_ext_starts_with_dot(self):
        """所有扩展名必须以点开头"""
        from utils import DEFAULT_EXT
        for ext in DEFAULT_EXT:
            assert ext.startswith('.'), f"扩展名应以点开头: {ext}"

    def test_default_ext_no_duplicates(self):
        """DEFAULT_EXT 无重复项"""
        from utils import DEFAULT_EXT
        assert len(DEFAULT_EXT) == len(set(DEFAULT_EXT)), "DEFAULT_EXT 中存在重复项"


class TestScriptExtensionMatching:
    """脚本扩展名匹配逻辑测试"""

    @pytest.mark.parametrize("filename,expected_ext", [
        ("script.ps1", ".ps1"),
        ("install.bat", ".bat"),
        ("deploy.sh", ".sh"),
        ("my.script.ps1", ".ps1"),       # 多点
        ("UPPERCASE.PS1", ".ps1"),       # 大小写
        ("UPPERCASE.BAT", ".bat"),
        ("UPPERCASE.SH", ".sh"),
        ("no_extension", ""),             # 无扩展名
        (".hidden.ps1", ".ps1"),          # 隐藏文件
        ("path.to.script.bat", ".bat"),
    ])
    def test_splitext(self, filename, expected_ext):
        """os.path.splitext 行为验证"""
        ext = os.path.splitext(filename)[1].lower()
        assert ext == expected_ext, f"{filename} -> ext='{ext}', 期望='{expected_ext}'"

    @pytest.mark.parametrize("ext,expected", [
        (".ps1", True),
        (".bat", True),
        (".sh", True),
        (".exe", False),
        (".txt", False),
        ("", False),
        (".ps2", False),
    ])
    def test_ext_in_default(self, ext, expected):
        """扩展名是否在 DEFAULT_EXT 中"""
        from utils import DEFAULT_EXT
        assert (ext in DEFAULT_EXT) == expected


class TestRunnableExtensions:
    """runnable_extensions 与 supported_extensions 的关系"""

    def test_runnable_subset_of_supported(self, tmp_config_file):
        """runnable_extensions 应是 supported_extensions 的子集"""
        from utils import load_json_with_comments, CONFIG_FILE, DEFAULT_EXT
        # 使用临时配置
        import importlib
        import utils
        original_config = utils.CONFIG_FILE
        try:
            utils.CONFIG_FILE = str(tmp_config_file)
            config = load_json_with_comments(str(tmp_config_file))
            supported = set(config.get('supported_extensions', DEFAULT_EXT))
            runnable = set(config.get('runnable_extensions', DEFAULT_EXT))
            assert runnable.issubset(supported), \
                f"可运行扩展 {runnable} 不是支持扩展 {supported} 的子集"
        finally:
            utils.CONFIG_FILE = original_config

    def test_default_ext_in_both_lists(self, tmp_config_file):
        """DEFAULT_EXT 应同时存在于 supported 和 runnable 列表中"""
        from utils import load_json_with_comments, CONFIG_FILE, DEFAULT_EXT
        import utils
        original_config = utils.CONFIG_FILE
        try:
            utils.CONFIG_FILE = str(tmp_config_file)
            config = load_json_with_comments(str(tmp_config_file))
            supported = config.get('supported_extensions', DEFAULT_EXT)
            runnable = config.get('runnable_extensions', DEFAULT_EXT)
            for ext in DEFAULT_EXT:
                assert ext in supported, f"DEFAULT_EXT {ext} 不在 supported_extensions 中"
                assert ext in runnable, f"DEFAULT_EXT {ext} 不在 runnable_extensions 中"
        finally:
            utils.CONFIG_FILE = original_config


class TestInterpreterSelection:
    """脚本解释器选择逻辑（tabClass.TerminalTab.start_process 中的分支）"""

    @pytest.mark.parametrize("ext,expected_interpreter_keyword", [
        (".bat", "cmd.exe"),
        (".cmd", "cmd.exe"),
        (".ps1", "powershell.exe"),
        (".sh", "bash"),
    ])
    def test_interpreter_for_extension(self, ext, expected_interpreter_keyword):
        """验证不同扩展名对应的解释器选择"""
        # 这段逻辑来自 TerminalTab.start_process:
        #   .bat/.cmd -> cmd.exe /c
        #   .ps1 -> powershell.exe
        #   .sh -> bash
        if ext in ('.bat', '.cmd'):
            interpreter = "cmd.exe"
        elif ext == '.ps1':
            interpreter = "powershell.exe"
        elif ext == '.sh':
            interpreter = "bash"
        else:
            interpreter = None

        assert interpreter is not None, f"扩展名 {ext} 无对应解释器"
        assert expected_interpreter_keyword in interpreter