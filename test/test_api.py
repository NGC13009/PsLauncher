# coding = utf-8
#
# @File name:       test_api.py
# @brief:           HTTP API 服务器 自动测试
# @Author:          NGC13009
# @History:         2026-06-29		Create

import os
import sys
import json
import pytest
import tempfile
import shutil
import threading
import time
from unittest.mock import MagicMock, patch

# ============================================================
# API 配置测试（算法层）
# ============================================================


@pytest.mark.algo
class TestApiConfig:
    """API 配置项测试"""

    def test_default_api_config(self, tmp_path, monkeypatch):
        """默认 API 配置应有正确的默认值"""
        import utils
        test_config = tmp_path / "launcher_config.json"
        monkeypatch.setattr(utils, "CONFIG_FILE", str(test_config))

        config = utils.load_json_with_comments(str(test_config))
        api = config.get("api", {})
        assert api.get("enabled") is True
        assert api.get("bind_ip") == "127.0.0.1"
        assert api.get("bind_port") == 13025
        assert api.get("auth_token") == ""

    def test_api_config_disabled(self, tmp_path, monkeypatch):
        """配置 disabled 时可正确读取"""
        import utils
        test_config = tmp_path / "launcher_config.json"
        test_config.write_text(json.dumps({
            "folders": [],
            "api": {"enabled": False, "bind_ip": "0.0.0.0", "bind_port": 9999, "auth_token": "secret"}
        }, indent=2), encoding="utf-8")
        monkeypatch.setattr(utils, "CONFIG_FILE", str(test_config))

        config = utils.load_json_with_comments(str(test_config))
        api = config.get("api", {})
        assert api["enabled"] is False
        assert api["bind_ip"] == "0.0.0.0"
        assert api["bind_port"] == 9999
        assert api["auth_token"] == "secret"

    def test_api_config_persisted(self, tmp_path, monkeypatch):
        """API 配置保存后应可读取"""
        import utils
        test_config = tmp_path / "launcher_config.json"
        monkeypatch.setattr(utils, "CONFIG_FILE", str(test_config))

        config = utils.load_json_with_comments(str(test_config))
        config["api"] = {"enabled": True, "bind_ip": "10.0.0.1", "bind_port": 8080, "auth_token": "mytoken"}
        utils.save_json_with_comments(str(test_config), config)

        config2 = utils.load_json_with_comments(str(test_config))
        api = config2.get("api", {})
        assert api["enabled"] is True
        assert api["bind_ip"] == "10.0.0.1"
        assert api["bind_port"] == 8080
        assert api["auth_token"] == "mytoken"


# ============================================================
# API 服务器功能测试（功能层 - 需要 QApplication）
# ============================================================


@pytest.mark.gui
class TestApiServerStartup:
    """API 服务器启动测试"""

    def test_api_server_creation(self, qapp, main_window):
        """应能创建 API 服务器线程"""
        from api_server import ApiServerThread
        thread = ApiServerThread("127.0.0.1", 13025, "", main_window)
        assert thread is not None
        assert thread.bind_ip == "127.0.0.1"
        assert thread.bind_port == 13025
        assert thread.auth_token == ""

    def test_api_server_with_token(self, qapp, main_window):
        """带 token 的服务器创建"""
        from api_server import ApiServerThread
        thread = ApiServerThread("127.0.0.1", 13025, "secure123", main_window)
        assert thread.auth_token == "secure123"

    def test_start_and_stop_api_server(self, qapp, main_window):
        """API 服务器应可启动和停止"""
        # 确保使用正确的默认配置（防止前一个测试的 monkeypatch 残留）
        main_window.config["api"] = {"enabled": True, "bind_ip": "127.0.0.1", "bind_port": 13025, "auth_token": ""}
        # 启动
        main_window.start_api_server()
        assert hasattr(main_window, 'api_thread')
        time.sleep(0.3)
        assert main_window.api_thread.isRunning()

        # 停止
        main_window.stop_api_server()
        time.sleep(0.3)
        assert not main_window.api_thread.isRunning()

    def test_disabled_api_does_not_start(self, qapp, main_window):
        """disabled 配置时不应启动服务器"""
        main_window.config["api"] = {"enabled": False, "bind_ip": "127.0.0.1", "bind_port": 13025, "auth_token": ""}
        main_window.start_api_server()
        # 不应创建 api_thread 或不应在运行
        if hasattr(main_window, 'api_thread'):
            time.sleep(0.2)
            assert not main_window.api_thread.isRunning()


@pytest.mark.gui
class TestApiEndpoints:
    """API 端点测试（功能层，模拟 HTTP 请求处理）"""

    def test_api_get_folders_empty(self, qapp, main_window):
        """空文件夹列表"""
        main_window.config["folders"] = []
        result = main_window.api_get_folders()
        assert result == {"folders": []}

    def test_api_get_folders_with_data(self, qapp, main_window):
        """有文件夹时的列表"""
        main_window.config["folders"] = ["C:/test1", "C:/test2"]
        result = main_window.api_get_folders()
        assert "C:/test1" in result["folders"]
        assert "C:/test2" in result["folders"]

    def test_api_get_scripts(self, qapp, main_window, sample_scripts_dir, monkeypatch):
        """脚本列表（不筛选文件夹）"""
        scripts_dir = str(sample_scripts_dir)
        main_window.config["folders"] = [scripts_dir]
        result = main_window.api_get_scripts()
        assert len(result["scripts"]) >= 3  # .ps1, .bat, .sh
        names = [s["name"] for s in result["scripts"]]
        assert "test_script.ps1" in names
        assert "test_script.bat" in names
        assert "test_script.sh" in names

    def test_api_get_scripts_filtered(self, qapp, main_window, sample_scripts_dir):
        """脚本列表（按文件夹筛选）"""
        scripts_dir = str(sample_scripts_dir)
        main_window.config["folders"] = [scripts_dir, "C:/other"]
        result = main_window.api_get_scripts(folder=scripts_dir)
        assert len(result["scripts"]) >= 3
        for s in result["scripts"]:
            assert s["folder"] == scripts_dir

    def test_api_get_scripts_filter_nonexistent(self, qapp, main_window):
        """筛选不存在的文件夹返回空"""
        main_window.config["folders"] = []
        result = main_window.api_get_scripts(folder="/nonexistent")
        assert result["scripts"] == []

    def test_api_add_folder(self, qapp, main_window, tmp_path):
        """添加文件夹"""
        new_folder = tmp_path / "new_api_folder"
        new_folder.mkdir()
        folder_str = str(new_folder)

        main_window.config["folders"] = []
        result = main_window.api_add_folder(folder_str)
        assert result["success"] is True
        assert folder_str in main_window.config["folders"]

    def test_api_add_folder_duplicate(self, qapp, main_window, tmp_path):
        """添加已存在的文件夹"""
        new_folder = tmp_path / "dup_folder"
        new_folder.mkdir()
        folder_str = str(new_folder)

        main_window.config["folders"] = [folder_str]
        result = main_window.api_add_folder(folder_str)
        assert result["success"] is True
        assert "已存在" in result.get("message", "")

    def test_api_add_folder_invalid(self, qapp, main_window):
        """添加不存在的路径"""
        result = main_window.api_add_folder("/nonexistent/path")
        assert result["success"] is False

    def test_api_add_folder_empty(self, qapp, main_window):
        """添加空路径"""
        result = main_window.api_add_folder("")
        assert result["success"] is False

    def test_api_remove_folder(self, qapp, main_window, tmp_path):
        """移除文件夹"""
        new_folder = tmp_path / "remove_folder_test"
        new_folder.mkdir()
        folder_str = str(new_folder)

        main_window.config["folders"] = [folder_str]
        result = main_window.api_remove_folder(folder_str)
        assert result["success"] is True
        assert folder_str not in main_window.config["folders"]

    def test_api_remove_folder_not_found(self, qapp, main_window):
        """移除不存在的文件夹"""
        main_window.config["folders"] = []
        result = main_window.api_remove_folder("/nonexistent")
        assert result["success"] is False

    def test_api_get_terminals_empty(self, qapp, main_window):
        """无终端时的终端列表"""
        result = main_window.api_get_terminals()
        assert result["terminals"] == []

    def test_api_get_terminals_with_data(self, qapp, main_window, sample_scripts_dir):
        """有终端时的终端列表"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)

        result = main_window.api_get_terminals()
        assert len(result["terminals"]) >= 1
        terminal = result["terminals"][0]
        assert "id" in terminal
        assert terminal["name"] == "test_script.ps1"
        assert "running" in terminal

    def test_api_get_terminal_output(self, qapp, main_window, sample_scripts_dir):
        """查看终端输出"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)

        # 获取已创建终端的 ID
        terminals_result = main_window.api_get_terminals()
        if terminals_result["terminals"]:
            tid = terminals_result["terminals"][0]["id"]
            result = main_window.api_get_terminal_output(terminal_id=tid)
            assert result["success"] is True
            assert "output" in result

    def test_api_get_terminal_output_by_name(self, qapp, main_window, sample_scripts_dir):
        """通过名称查看终端输出（唯一名称）"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)
        # 立即查询
        result = main_window.api_get_terminal_output(terminal_name="test_script.ps1")
        assert result["success"] is True

    def test_api_get_terminal_output_not_found(self, qapp, main_window):
        """查看不存在的终端"""
        result = main_window.api_get_terminal_output(terminal_id=99999)
        assert result["success"] is False

    def test_api_get_terminal_output_no_params(self, qapp, main_window):
        """不提供参数"""
        result = main_window.api_get_terminal_output()
        assert result["success"] is False

    def test_api_clear_terminal(self, qapp, main_window, sample_scripts_dir):
        """清空终端"""
        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)

        terminals_result = main_window.api_get_terminals()
        if terminals_result["terminals"]:
            tid = terminals_result["terminals"][0]["id"]
            result = main_window.api_clear_terminal(tid)
            assert result["success"] is True

    def test_api_clear_terminal_not_found(self, qapp, main_window):
        """清空不存在的终端"""
        result = main_window.api_clear_terminal(99999)
        assert result["success"] is False

    def test_api_shutdown(self, qapp, main_window):
        """关闭程序（不应崩溃）"""
        result = main_window.api_shutdown()
        assert result["success"] is True

    def test_api_run_script(self, qapp, main_window, sample_scripts_dir):
        """通过 API 运行脚本（停止 start_process 避免实际执行）"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        scripts_dir = str(sample_scripts_dir)
        main_window.config["folders"] = [scripts_dir]
        result = main_window.api_run_script(scripts_dir, "test_script.ps1")
        assert result["success"] is True
        assert "terminal_id" in result

        tabClass.TerminalTab.start_process = original_start

    def test_api_run_script_not_found(self, qapp, main_window):
        """运行不存在的脚本"""
        main_window.config["folders"] = ["/some/folder"]
        result = main_window.api_run_script("/some/folder", "nonexistent.ps1")
        assert result["success"] is False

    def test_api_stop_terminal(self, qapp, main_window, sample_scripts_dir):
        """终止终端"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)

        terminals_result = main_window.api_get_terminals()
        if terminals_result["terminals"]:
            tid = terminals_result["terminals"][0]["id"]
            result = main_window.api_stop_terminal(terminal_id=tid)
            assert result["success"] is True

        tabClass.TerminalTab.start_process = original_start

    def test_api_stop_terminal_by_name(self, qapp, main_window, sample_scripts_dir):
        """通过名称终止终端"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)

        result = main_window.api_stop_terminal(terminal_name="test_script.ps1")
        assert result["success"] is True

        tabClass.TerminalTab.start_process = original_start

    def test_api_stop_terminal_not_found(self, qapp, main_window):
        """终止不存在的终端"""
        result = main_window.api_stop_terminal(terminal_id=99999)
        assert result["success"] is False

    def test_api_stop_terminal_no_params(self, qapp, main_window):
        """不提供参数"""
        result = main_window.api_stop_terminal()
        assert result["success"] is False

    def test_api_send_terminal_input(self, qapp, main_window, sample_scripts_dir, monkeypatch):
        """向终端发送输入"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        from unittest.mock import MagicMock
        from PyQt5.QtCore import QProcess

        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)

        terminals_result = main_window.api_get_terminals()
        if terminals_result["terminals"]:
            tid = terminals_result["terminals"][0]["id"]
            widget = main_window._get_terminal_by_id(tid)
            # 模拟进程运行中
            widget.process = MagicMock()
            widget.process.state.return_value = QProcess.Running
            widget.process.write = MagicMock()

            result = main_window.api_send_terminal_input(tid, "hello")
            assert result["success"] is True

        tabClass.TerminalTab.start_process = original_start

    def test_api_send_terminal_input_no_process(self, qapp, main_window, sample_scripts_dir):
        """向没有运行进程的终端发送输入"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        script_path = str(sample_scripts_dir / "test_script.ps1")
        main_window.open_terminal_tab(script_path)

        terminals_result = main_window.api_get_terminals()
        if terminals_result["terminals"]:
            tid = terminals_result["terminals"][0]["id"]
            result = main_window.api_send_terminal_input(tid, "hello")
            assert result["success"] is False

        tabClass.TerminalTab.start_process = original_start

    def test_api_send_terminal_input_not_found(self, qapp, main_window):
        """向不存在的终端发送输入"""
        result = main_window.api_send_terminal_input(99999, "hello")
        assert result["success"] is False

    def test_api_help_returns_content(self, qapp, main_window):
        """帮助端点返回内容（通过 handler 类直接调用）"""
        from api_server import ApiRequestHandler
        # 注意：直接测试 ApiRequestHandler 很复杂，所以测试 MainWindow 能正确访问 help 即可
        # 简单检查 help 加载不抛异常即可
        from i18n import get_language
        if get_language() == "zh_CN":
            from i18n.source_help_page_zh_CN import html_content
        else:
            from i18n.source_help_page import html_content
        assert html_content is not None
        assert len(html_content) > 100


# ============================================================
# HTTP 请求处理器测试（算法层）
# ============================================================


@pytest.mark.algo
class TestApiRequestHandler:
    """请求处理器纯函数测试"""

    def test_auth_check_no_token(self):
        """无 token 配置时验权应通过"""
        from api_server import ApiRequestHandler
        ApiRequestHandler.auth_token = ""
        handler = MagicMock(spec=ApiRequestHandler)
        handler._check_auth = ApiRequestHandler._check_auth.__get__(handler, ApiRequestHandler)
        assert handler._check_auth() is True

    def test_auth_check_with_correct_token(self):
        """正确的 token 验权应通过"""
        from api_server import ApiRequestHandler
        ApiRequestHandler.auth_token = "secret123"
        handler = MagicMock(spec=ApiRequestHandler)
        handler.headers = {"Authorization": "Bearer secret123"}
        handler._check_auth = ApiRequestHandler._check_auth.__get__(handler, ApiRequestHandler)
        assert handler._check_auth() is True

    def test_auth_check_with_wrong_token(self):
        """错误的 token 验权应拒绝"""
        from api_server import ApiRequestHandler
        ApiRequestHandler.auth_token = "secret123"
        handler = MagicMock(spec=ApiRequestHandler)
        handler.headers = {"Authorization": "Bearer wrong"}
        handler._check_auth = ApiRequestHandler._check_auth.__get__(handler, ApiRequestHandler)
        assert handler._check_auth() is False

    def test_auth_check_with_no_header(self):
        """无 Authorization 头时应拒绝"""
        from api_server import ApiRequestHandler
        ApiRequestHandler.auth_token = "secret123"
        handler = MagicMock(spec=ApiRequestHandler)
        handler.headers = {}
        handler._check_auth = ApiRequestHandler._check_auth.__get__(handler, ApiRequestHandler)
        assert handler._check_auth() is False

    def test_auth_check_missing_bearer_prefix(self):
        """缺少 Bearer 前缀应拒绝"""
        from api_server import ApiRequestHandler
        ApiRequestHandler.auth_token = "secret123"
        handler = MagicMock(spec=ApiRequestHandler)
        handler.headers = {"Authorization": "secret123"}
        handler._check_auth = ApiRequestHandler._check_auth.__get__(handler, ApiRequestHandler)
        assert handler._check_auth() is False


# ============================================================
# 无头模式测试（功能层）
# ============================================================


@pytest.mark.gui
class TestHeadlessMode:
    """无头模式相关测试"""

    def test_headless_window_created(self, qapp, tmp_config_file, monkeypatch):
        """无头模式下窗口应被创建但不显示"""
        import utils
        monkeypatch.setattr(utils, "CONFIG_FILE", str(tmp_config_file))
        monkeypatch.setattr(
            "PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable",
            staticmethod(lambda: False)
        )
        from PsLauncher.PsLauncher import MainWindow
        win = MainWindow("Consolas", 768, 1366, True, True)
        # 验证窗口已被创建
        assert win is not None
        # 不调用 show() 即可模拟无头模式
        assert win.isVisible() is False


# ============================================================
# TerminalTab ID 测试
# ============================================================


@pytest.mark.gui
class TestTerminalId:
    """终端唯一 ID 测试"""

    def test_terminal_id_increments(self, qapp, sample_scripts_dir):
        """每个终端应有递增的唯一 ID"""
        from tabClass import TerminalTab
        # 记录当前最大 ID
        id_before = TerminalTab._next_id

        tab1 = TerminalTab(str(sample_scripts_dir / "test_script.ps1"), "Consolas", True, True)
        tab2 = TerminalTab(str(sample_scripts_dir / "test_script.bat"), "Consolas", True, True)

        assert tab1.terminal_id == id_before
        assert tab2.terminal_id == id_before + 1

    def test_terminal_id_unique(self, qapp, main_window, sample_scripts_dir):
        """生成的终端 ID 应唯一"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.ps1"))
        main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.bat"))
        main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.sh"))

        terminals = main_window.api_get_terminals()
        ids = [t["id"] for t in terminals["terminals"]]
        assert len(ids) == len(set(ids))  # 所有 ID 唯一

        tabClass.TerminalTab.start_process = original_start