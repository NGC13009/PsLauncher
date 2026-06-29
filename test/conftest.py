# coding = utf-8
#
# @File name:       conftest.py
# @brief:           PsLauncher 测试全局 fixtures
# @attention:       必须在任何 QApplication 创建之前设置环境变量
# @Author:          NGC13009
# @History:         2026-06-29		Create

import os
import sys
import json
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock

# ============================================================
# 关键：在 pytest-qt 导入之前设置 headless 环境变量
# ============================================================
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTEST_QT_API", "pyqt5")


# ============================================================
# 算法层 fixtures（无 Qt 依赖）
# ============================================================

@pytest.fixture
def tmp_config_file(tmp_path):
    """创建一个临时的 config.json 配置文件"""
    cfg = tmp_path / "launcher_config.json"
    cfg.write_text(
        json.dumps({
            "folders": [],
            "font_scale": 1.5,
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
        }, indent=2),
        encoding="utf-8"
    )
    return cfg


@pytest.fixture
def tmp_config_with_comments(tmp_path):
    """创建带注释的 config.json 测试文件"""
    cfg = tmp_path / "launcher_config.json"
    cfg.write_text(
        '// PsLauncher 配置文件\n'
        '{\n'
        '    // 监视的文件夹列表\n'
        '    "folders": ["C:\\\\scripts"],\n'
        '    "font_scale": 1.2,  /* 字体缩放 */\n'
        '    "dark_mode": true\n'
        '}\n',
        encoding="utf-8"
    )
    return cfg


@pytest.fixture
def tmp_empty_config(tmp_path):
    """创建一个空的配置文件（测试默认值回退）"""
    cfg = tmp_path / "launcher_config.json"
    cfg.write_text("{}", encoding="utf-8")
    return cfg


# ============================================================
# 功能层/GUI 层 fixtures
# ============================================================

@pytest.fixture
def sample_scripts_dir(tmp_path):
    """构造包含 .ps1/.bat/.sh 各一个的临时脚本目录"""
    scripts = tmp_path / "test_scripts"
    scripts.mkdir()

    # .ps1 脚本
    ps1_file = scripts / "test_script.ps1"
    ps1_file.write_text(
        '# PowerShell test script\n'
        'Write-Host "Hello from PS1"\n',
        encoding="utf-8"
    )

    # .bat 脚本
    bat_file = scripts / "test_script.bat"
    bat_file.write_text(
        '@echo off\n'
        'echo Hello from BAT\n',
        encoding="utf-8"
    )

    # .sh 脚本
    sh_file = scripts / "test_script.sh"
    sh_file.write_text(
        '#!/bin/bash\n'
        'echo "Hello from SH"\n',
        encoding="utf-8"
    )

    # 一个不应被扫描的 .txt 文件
    txt_file = scripts / "readme.txt"
    txt_file.write_text("This is a text file, not a script.", encoding="utf-8")

    # 一个子目录（不应递归扫描）
    sub_dir = scripts / "subdir"
    sub_dir.mkdir()
    sub_ps1 = sub_dir / "sub_script.ps1"
    sub_ps1.write_text("# Sub dir script", encoding="utf-8")

    return scripts


@pytest.fixture
def sample_scripts_mixed(tmp_path):
    """包含多种变体的脚本目录"""
    scripts = tmp_path / "mixed_scripts"
    scripts.mkdir()

    # 正常脚本
    (scripts / "normal.ps1").write_text("# normal", encoding="utf-8")
    (scripts / "normal.bat").write_text("@echo off\necho normal\n", encoding="utf-8")

    # 空文件（有扩展名但无内容）
    empty_file = scripts / "empty.ps1"
    empty_file.write_text("", encoding="utf-8")

    # 无扩展名文件
    no_ext_file = scripts / "no_extension"
    no_ext_file.write_text("some content", encoding="utf-8")

    # 隐藏文件（以点开头）
    hidden_file = scripts / ".hidden.ps1"
    hidden_file.write_text("# hidden", encoding="utf-8")

    return scripts


# ============================================================
# GUI 层 fixtures（需要 qtbot）
# ============================================================

@pytest.fixture
def main_window(qtbot, tmp_config_file, monkeypatch):
    """构造 MainWindow 实例，配置指向临时文件"""
    # 注意：PsLauncher/ 是一个包（有 __init__.py），
    # 主模块是 PsLauncher.PsLauncher，它通过 from utils import * 导入了 CONFIG_FILE
    # 因此只需 patch utils.CONFIG_FILE 即可
    import utils
    monkeypatch.setattr(utils, "CONFIG_FILE", str(tmp_config_file))

    # Patch QSystemTrayIcon.isSystemTrayAvailable 避免托盘问题
    monkeypatch.setattr(
        "PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable",
        staticmethod(lambda: False)
    )

    # 导入并创建主窗口（PsLauncher 是包，PsLauncher.PsLauncher 是主模块）
    from PsLauncher.PsLauncher import MainWindow

    win = MainWindow(
        font_family="Consolas",
        h=768,
        w=1366,
        dark_mode=True,
        line_wrap_mode=True
    )
    # 实例级别的 closeEvent patch，不受 monkeypatch 撤销影响
    original_close = win.closeEvent
    win.closeEvent = lambda event: event.accept()
    qtbot.addWidget(win)
    return win


@pytest.fixture
def main_window_light(qtbot, tmp_config_file, monkeypatch):
    """构造浅色主题的 MainWindow 实例"""
    import utils
    monkeypatch.setattr(utils, "CONFIG_FILE", str(tmp_config_file))

    monkeypatch.setattr(
        "PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable",
        staticmethod(lambda: False)
    )

    from PsLauncher.PsLauncher import MainWindow
    win = MainWindow(
        font_family="Consolas",
        h=768,
        w=1366,
        dark_mode=False,
        line_wrap_mode=False
    )
    qtbot.addWidget(win)
    return win


@pytest.fixture
def editor_tab(qtbot, tmp_path, sample_scripts_dir):
    """构造一个 EditorTab 实例"""
    script_path = sample_scripts_dir / "test_script.ps1"
    from tabClass import EditorTab
    tab = EditorTab(
        script_path=str(script_path),
        font_family="Consolas",
        isdark=True,
        line_wrap_mode=True
    )
    qtbot.addWidget(tab)
    return tab


@pytest.fixture
def terminal_tab(qtbot, sample_scripts_dir):
    """构造一个 TerminalTab 实例（mock 掉 QProcess）"""
    from tabClass import TerminalTab
    script_path = str(sample_scripts_dir / "test_script.ps1")
    tab = TerminalTab(script_path, "Consolas", True, True)
    # Mock process 以避免实际启动进程
    tab.process = MagicMock()
    tab.process.state.return_value = 2  # QProcess.Running
    tab.process.processId.return_value = 12345
    qtbot.addWidget(tab)
    return tab


@pytest.fixture
def main_window_with_tabs(qtbot, tmp_config_file, monkeypatch, sample_scripts_dir):
    """构造 MainWindow 并打开一个编辑标签和一个终端标签"""
    import utils
    monkeypatch.setattr(utils, "CONFIG_FILE", str(tmp_config_file))
    monkeypatch.setattr(
        "PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable",
        staticmethod(lambda: False)
    )
    from PsLauncher.PsLauncher import MainWindow
    import tabClass
    original_start = tabClass.TerminalTab.start_process
    tabClass.TerminalTab.start_process = lambda self: None

    win = MainWindow("Consolas", 768, 1366, True, True)
    win.closeEvent = lambda event: event.accept()
    qtbot.addWidget(win)

    # 打开一个编辑标签
    win.open_editor_tab(str(sample_scripts_dir / "test_script.ps1"))
    # 打开一个终端标签
    win.open_terminal_tab(str(sample_scripts_dir / "test_script.bat"))

    tabClass.TerminalTab.start_process = original_start
    return win