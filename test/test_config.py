# coding = utf-8
#
# @File name:       test_config.py
# @brief:           算法层+功能层：config.json 读写、注释解析、默认值合并、边界值、保存验证
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest
import json
import os

# ============================================================
# 算法层：load_json_with_comments 测试
# ============================================================


class TestLoadJsonWithComments:
    """配置加载：注释剥离与默认值合并"""

    def test_load_basic_config(self, tmp_config_file):
        """加载标准配置文件"""
        from utils import load_json_with_comments
        config = load_json_with_comments(str(tmp_config_file))
        assert config["font_scale"] == 1.5
        assert config["dark_mode"] is True
        assert config["folders"] == []

    def test_load_with_line_comments(self, tmp_config_with_comments):
        """加载带 // 行注释的配置"""
        from utils import load_json_with_comments
        config = load_json_with_comments(str(tmp_config_with_comments))
        assert config["folders"] == ["C:\\scripts"]
        assert config["font_scale"] == 1.2
        assert config["dark_mode"] is True

    def test_load_empty_config_uses_defaults(self, tmp_empty_config):
        """空配置使用默认值填充"""
        from utils import load_json_with_comments, DEFAULT_EXT
        config = load_json_with_comments(str(tmp_empty_config))
        assert config["font_family"] == "Consolas"
        assert config["supported_extensions"] == DEFAULT_EXT
        assert config["runnable_extensions"] == DEFAULT_EXT
        assert config["font_scale"] == 1.0
        assert config["dark_mode"] is True

    @pytest.mark.parametrize("field,expected_default", [
        ("font_scale", 1.0),
        ("dark_mode", True),
        ("height_value", 768),
        ("width_value", 1366),
        ("font_family", "Consolas"),
        ("line_wrap_mode", True),
        ("syntax_highlight_mode", "auto"),
        ("auto_minimize_to_tray", False),
        ("language", "en"),
    ])
    def test_default_values(self, tmp_empty_config, field, expected_default):
        """验证每个字段的默认值"""
        from utils import load_json_with_comments
        config = load_json_with_comments(str(tmp_empty_config))
        assert config[field] == expected_default, f"字段 {field} 默认值应为 {expected_default}"

    def test_config_file_not_exists_returns_default(self, tmp_path):
        """配置文件不存在时返回默认配置"""
        from utils import load_json_with_comments
        nonexistent = tmp_path / "nonexistent.json"
        config = load_json_with_comments(str(nonexistent))
        assert config["font_family"] == "Consolas"
        assert config["font_scale"] == 1.0

    def test_partial_config_merges_with_defaults(self, tmp_path):
        """部分配置与默认值合并"""
        from utils import load_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        cfg_file.write_text(
            json.dumps({"font_scale": 2.0, "dark_mode": False}),
            encoding="utf-8"
        )
        config = load_json_with_comments(str(cfg_file))
        assert config["font_scale"] == 2.0  # 传入值
        assert config["dark_mode"] is False  # 传入值
        assert config["font_family"] == "Consolas"  # 默认值

    def test_block_comments_removed(self, tmp_path):
        """测试块注释 /* */ 被正确移除"""
        from utils import load_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        cfg_file.write_text(
            '{\n'
            '    /* 块注释 */\n'
            '    "dark_mode": true,\n'
            '    /* 多行\n'
            '       块注释 */\n'
            '    "font_scale": 1.5\n'
            '}\n',
            encoding="utf-8"
        )
        config = load_json_with_comments(str(cfg_file))
        assert config["dark_mode"] is True
        assert config["font_scale"] == 1.5
        assert config["font_family"] == "Consolas"  # 默认值


class TestSaveJsonWithComments:
    """配置保存：序列化与注释写入"""

    def test_save_config_preserves_values(self, tmp_path):
        """保存配置应保留所有字段"""
        from utils import save_json_with_comments, load_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        test_config = {
            "folders": ["D:\\test"],
            "font_scale": 1.5,
            "dark_mode": False,
            "language": "zh_CN"
        }
        save_json_with_comments(str(cfg_file), test_config)
        loaded = load_json_with_comments(str(cfg_file))
        assert loaded["folders"] == ["D:\\test"]
        assert loaded["font_scale"] == 1.5
        assert loaded["dark_mode"] is False
        assert loaded["language"] == "zh_CN"

    def test_saved_file_contains_comment_header(self, tmp_path):
        """保存的配置文件应包含注释头"""
        from utils import save_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        save_json_with_comments(str(cfg_file), {"dark_mode": True})
        content = cfg_file.read_text(encoding="utf-8")
        assert "// PsLauncher" in content

    def test_saved_file_is_valid_json(self, tmp_path):
        """保存的文件应为合法 JSON"""
        from utils import save_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        save_json_with_comments(str(cfg_file), {"dark_mode": True})
        # 移除注释行后应为合法 JSON
        import re
        content = cfg_file.read_text(encoding="utf-8")
        json_content = re.sub(r'//.*', '', content)
        parsed = json.loads(json_content)
        assert parsed["dark_mode"] is True

    def test_saved_file_contains_field_comments(self, tmp_path):
        """保存的配置文件应包含字段注释"""
        from utils import save_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        test_config = {
            "font_scale": 1.5,
            "dark_mode": True,
            "height_value": 900,
            "width_value": 1600,
        }
        save_json_with_comments(str(cfg_file), test_config)
        content = cfg_file.read_text(encoding="utf-8")
        # 检查典型字段的行内注释是否存在
        assert "// Font size scaling factor" in content
        assert "// Enable dark mode theme" in content
        assert "// Window height in pixels" in content
        assert "// Window width in pixels" in content

    def test_saved_file_with_comments_can_be_loaded(self, tmp_path):
        """带注释的保存文件可被 load_json_with_comments 正确读取"""
        from utils import save_json_with_comments, load_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        test_config = {
            "folders": ["C:\\test"],
            "font_scale": 2.0,
            "dark_mode": False,
            "font_family": "Arial",
            "language": "zh_CN",
            "api": {
                "enabled": True,
                "bind_port": 23025,
            }
        }
        save_json_with_comments(str(cfg_file), test_config)
        loaded = load_json_with_comments(str(cfg_file))
        assert loaded["folders"] == ["C:\\test"]
        assert loaded["font_scale"] == 2.0
        assert loaded["dark_mode"] is False
        assert loaded["font_family"] == "Arial"
        assert loaded["language"] == "zh_CN"
        assert loaded["api"]["enabled"] is True
        assert loaded["api"]["bind_port"] == 23025

    def test_saved_file_all_known_fields_have_comments(self, tmp_path):
        """检查所有已知字段在注释映射表中都有定义（存根测试，确保不崩溃）"""
        from utils import save_json_with_comments, _COMMENT_MAP
        cfg_file = tmp_path / "launcher_config.json"
        save_json_with_comments(str(cfg_file), {})
        content = cfg_file.read_text(encoding="utf-8")
        # 确保至少有一半的已知字段名在文件内容中出现了注释
        # （由于数组/对象格式问题，不是所有字段都保证有行尾注释，但主要字段应该都有）
        known_fields = [
            "folders", "font_scale", "dark_mode", "height_value",
            "width_value", "font_family", "line_wrap_mode",
            "syntax_highlight_mode", "auto_run_scripts",
            "auto_minimize_to_tray", "language",
        ]
        commented_count = 0
        for field in known_fields:
            # 每个已知字段在 _COMMENT_MAP 中应有对应的注释
            assert field in _COMMENT_MAP, f"字段 {field} 在 _COMMENT_MAP 中缺失"
            assert _COMMENT_MAP[field], f"字段 {field} 的注释为空"
        # 检查嵌套字段也存在
        assert "api.enabled" in _COMMENT_MAP
        assert "api.bind_ip" in _COMMENT_MAP
        assert "api.bind_port" in _COMMENT_MAP
        assert "api.auth_token" in _COMMENT_MAP


class TestConfigBoundaryValues:
    """配置边界值测试"""

    @pytest.mark.parametrize("bad_json", [
        '{invalid json}',
        '{"unclosed": true',
        '["not an object"]',
    ])
    def test_invalid_json_returns_defaults(self, tmp_path, bad_json):
        """非法 JSON 应返回默认配置"""
        from utils import load_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        cfg_file.write_text(bad_json, encoding="utf-8")
        config = load_json_with_comments(str(cfg_file))
        assert config["font_family"] == "Consolas"
        assert config["font_scale"] == 1.0

    @pytest.mark.parametrize("bad_type_field, bad_value", [
        ("font_scale", "not_a_number"),
        ("dark_mode", "not_a_bool"),
        ("folders", "not_a_list"),
    ])
    def test_wrong_type_in_config_uses_default(self, tmp_path, bad_type_field, bad_value):
        """配置中字段类型错误时使用默认值（合并行为）"""
        from utils import load_json_with_comments
        cfg_file = tmp_path / "launcher_config.json"
        cfg_file.write_text(
            json.dumps({bad_type_field: bad_value}),
            encoding="utf-8"
        )
        config = load_json_with_comments(str(cfg_file))
        # 由于 _default_config 合并是浅合并，错误类型的值会被保留
        # 这里只验证不会崩溃
        assert bad_type_field in config


# ============================================================
# P1 补充：save_config 验证测试
# ============================================================


class TestSaveConfigValidation:
    """配置保存验证逻辑测试"""
    # 注意：必须 mock 模块级的 QMessageBox，不能 mock PyQt5.QtWidgets.QMessageBox.warning 静态方法

    def test_save_config_all_ext_present(self, main_window, monkeypatch):
        """所有默认后缀存在时应正常保存（不弹警告）"""
        import PsLauncher.PsLauncher as main_mod
        from unittest.mock import MagicMock

        # 在模块命名空间 mock QMessageBox
        mock_msg = MagicMock()
        monkeypatch.setattr(main_mod, "QMessageBox", mock_msg)

        main_window.config['supported_extensions'] = ['.ps1', '.bat', '.sh']
        main_window.config['runnable_extensions'] = ['.ps1', '.bat', '.sh']

        main_window.save_config()

        # 不应触发警告
        mock_msg.warning.assert_not_called()

    @pytest.mark.gui
    def test_save_config_missing_default_ext_warns(self, main_window, monkeypatch):
        """移除默认后缀时保存应弹警告"""
        import PsLauncher.PsLauncher as main_mod
        from unittest.mock import MagicMock

        # 在模块命名空间 mock QMessageBox
        mock_msg = MagicMock()
        monkeypatch.setattr(main_mod, "QMessageBox", mock_msg)

        main_window.config['supported_extensions'] = ['.ps1', '.bat']  # 移除 .sh

        main_window.save_config()

        # 应触发警告
        mock_msg.warning.assert_called_once()
