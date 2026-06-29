# coding = utf-8
#
# @File name:       config_factory.py
# @brief:           构造不同 config.json 场景的工厂函数
# @Author:          NGC13009
# @History:         2026-06-29		Create

import json


def make_config(tmp_path, overrides=None):
    """创建一个标准配置，支持覆盖特定字段"""
    config = {
        "folders": [],
        "font_scale": 1.0,
        "dark_mode": True,
        "height_value": 768,
        "width_value": 1366,
        "font_family": "Consolas",
        "line_wrap_mode": True,
        "supported_extensions": [".ps1", ".bat", ".sh"],
        "runnable_extensions": [".ps1", ".bat", ".sh"],
        "syntax_highlight_mode": "auto",
        "auto_run_scripts": [],
        "auto_minimize_to_tray": False,
        "language": "en"
    }
    if overrides:
        config.update(overrides)

    cfg_file = tmp_path / "launcher_config.json"
    cfg_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return cfg_file


def make_config_with_folders(tmp_path, folder_paths):
    """创建包含指定文件夹列表的配置"""
    return make_config(tmp_path, {"folders": list(folder_paths)})


def make_config_with_auto_run(tmp_path, script_paths):
    """创建包含自动运行脚本列表的配置"""
    return make_config(tmp_path, {"auto_run_scripts": list(script_paths)})


def make_config_missing_fields(tmp_path):
    """创建缺少部分字段的配置（测试默认值回退）"""
    cfg_file = tmp_path / "launcher_config.json"
    cfg_file.write_text(
        json.dumps({
            "folders": ["D:\\scripts"],
            "dark_mode": False
        }, indent=2),
        encoding="utf-8"
    )
    return cfg_file


def make_config_invalid_json(tmp_path):
    """创建非法 JSON 配置（测试容错）"""
    cfg_file = tmp_path / "launcher_config.json"
    cfg_file.write_text(
        '{ this is not valid json }',
        encoding="utf-8"
    )
    return cfg_file