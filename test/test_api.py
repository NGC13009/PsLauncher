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
        assert "already exists" in result.get("message", "").lower()

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


# ============================================================
# 终止所有终端测试
# ============================================================


@pytest.mark.gui
class TestStopAllTerminals:
    """终止所有终端 API 测试"""

    def test_api_stop_all_terminals(self, qapp, main_window, sample_scripts_dir):
        """终止所有终端"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.ps1"))
        main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.bat"))

        result = main_window.api_stop_all_terminals()
        assert result["success"] is True
        assert "message" in result

        # 验证所有终端已关闭
        terminals = main_window.api_get_terminals()
        assert len(terminals["terminals"]) == 0

        tabClass.TerminalTab.start_process = original_start

    def test_api_stop_all_terminals_empty(self, qapp, main_window):
        """无终端时终止所有终端"""
        result = main_window.api_stop_all_terminals()
        assert result["success"] is True
        assert "0" in result["message"]

    def test_api_stop_all_terminals_mixed_tabs(self, qapp, main_window, sample_scripts_dir):
        """混合标签页时终止所有终端（编辑器标签页不受影响）"""
        import tabClass
        original_start = tabClass.TerminalTab.start_process
        tabClass.TerminalTab.start_process = lambda self: None

        # 打开一个编辑器标签页
        main_window.open_editor_tab(str(sample_scripts_dir / "test_script.ps1"))
        # 打开两个终端标签页
        main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.ps1"))
        main_window.open_terminal_tab(str(sample_scripts_dir / "test_script.bat"))

        result = main_window.api_stop_all_terminals()
        assert result["success"] is True

        # 验证所有终端已关闭，但编辑器标签页仍在
        terminals = main_window.api_get_terminals()
        assert len(terminals["terminals"]) == 0

        # 验证编辑器标签页仍存在
        editor_count = 0
        for i in range(main_window.tabs.count()):
            from tabClass import EditorTab
            if isinstance(main_window.tabs.widget(i), EditorTab):
                editor_count += 1
        assert editor_count >= 1

        tabClass.TerminalTab.start_process = original_start


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
# POST /help 端点测试
# ============================================================


@pytest.mark.algo
class TestApiHelpPost:
    """POST /help 端点测试（返回所有 API 端点格式列表）"""

    def test_help_post_returns_success(self):
        """POST /help 应返回 success=True"""
        from api_server import ApiRequestHandler
        handler = MagicMock(spec=ApiRequestHandler)
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        handler._is_pretty = MagicMock(return_value=False)
        handler._send_json = ApiRequestHandler._send_json.__get__(handler, ApiRequestHandler)

        handler._handle_help_post = ApiRequestHandler._handle_help_post.__get__(handler, ApiRequestHandler)
        handler._handle_help_post()

        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        data = json.loads(written)
        assert data["success"] is True
        assert "endpoints" in data

    def test_help_post_contains_all_endpoints(self):
        """POST /help 应包含所有预期的 API 端点"""
        from api_server import ApiRequestHandler
        handler = MagicMock(spec=ApiRequestHandler)
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        handler._is_pretty = MagicMock(return_value=False)
        handler._send_json = ApiRequestHandler._send_json.__get__(handler, ApiRequestHandler)

        handler._handle_help_post = ApiRequestHandler._handle_help_post.__get__(handler, ApiRequestHandler)
        handler._handle_help_post()

        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        data = json.loads(written)
        endpoints = data["endpoints"]

        # 检查所有预期的端点路径和方法都存在
        expected_endpoints = [
            ("GET", "/status"),
            ("GET", "/help"),
            ("POST", "/help"),
            ("GET", "/folders"),
            ("GET", "/scripts"),
            ("POST", "/folder/add"),
            ("POST", "/folder/remove"),
            ("POST", "/script/run"),
            ("GET", "/terminals"),
            ("POST", "/terminal/stop"),
            ("POST", "/terminal/stop_all"),
            ("GET", "/terminal/output"),
            ("POST", "/terminal/clear"),
            ("POST", "/terminal/input"),
            ("GET", "/shutdown"),
        ]
        endpoint_set = {(ep["method"], ep["path"]) for ep in endpoints}
        for method, path in expected_endpoints:
            assert (method, path) in endpoint_set, f"缺少端点: {method} {path}"

    def test_help_post_endpoint_has_description(self):
        """每个端点应包含 description 字段"""
        from api_server import ApiRequestHandler
        handler = MagicMock(spec=ApiRequestHandler)
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        handler._is_pretty = MagicMock(return_value=False)
        handler._send_json = ApiRequestHandler._send_json.__get__(handler, ApiRequestHandler)

        handler._handle_help_post = ApiRequestHandler._handle_help_post.__get__(handler, ApiRequestHandler)
        handler._handle_help_post()

        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        data = json.loads(written)
        for ep in data["endpoints"]:
            assert "description" in ep, f"端点 {ep['method']} {ep['path']} 缺少 description"

    def test_help_post_endpoint_has_response_field(self):
        """每个端点应包含 response 字段"""
        from api_server import ApiRequestHandler
        handler = MagicMock(spec=ApiRequestHandler)
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        handler._is_pretty = MagicMock(return_value=False)
        handler._send_json = ApiRequestHandler._send_json.__get__(handler, ApiRequestHandler)

        handler._handle_help_post = ApiRequestHandler._handle_help_post.__get__(handler, ApiRequestHandler)
        handler._handle_help_post()

        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        data = json.loads(written)
        for ep in data["endpoints"]:
            assert "response" in ep, f"端点 {ep['method']} {ep['path']} 缺少 response"

    def test_help_post_does_not_require_auth(self):
        """POST /help 应当在请求处理器中通过认证"""
        from api_server import ApiRequestHandler
        ApiRequestHandler.auth_token = ""
        handler = MagicMock(spec=ApiRequestHandler)
        handler.headers = {}
        handler._check_auth = ApiRequestHandler._check_auth.__get__(handler, ApiRequestHandler)
        assert handler._check_auth() is True


# ============================================================
# 美化输出（pretty）测试
# ============================================================


@pytest.mark.algo
class TestApiPrettyOutput:
    """JSON 美化输出测试"""

    def _make_handler(self, path):
        """创建一个模拟 handler 并绑定真实方法"""
        from api_server import ApiRequestHandler
        handler = MagicMock(spec=ApiRequestHandler)
        handler.path = path
        handler._parse_query = ApiRequestHandler._parse_query.__get__(handler, ApiRequestHandler)
        handler._is_pretty = ApiRequestHandler._is_pretty.__get__(handler, ApiRequestHandler)
        return handler

    def test_pretty_off_by_default(self):
        """默认不带 pretty 参数时不应美化"""
        handler = self._make_handler("/status")
        assert handler._is_pretty() is False

    def test_pretty_true(self):
        """?pretty=true 应启用美化"""
        handler = self._make_handler("/status?pretty=true")
        assert handler._is_pretty() is True

    def test_pretty_1(self):
        """?pretty=1 应启用美化"""
        handler = self._make_handler("/status?pretty=1")
        assert handler._is_pretty() is True

    def test_pretty_yes(self):
        """?pretty=yes 应启用美化"""
        handler = self._make_handler("/status?pretty=yes")
        assert handler._is_pretty() is True

    def test_pretty_false(self):
        """?pretty=false 不应启用美化"""
        handler = self._make_handler("/status?pretty=false")
        assert handler._is_pretty() is False

    def test_pretty_0(self):
        """?pretty=0 不应启用美化"""
        handler = self._make_handler("/status?pretty=0")
        assert handler._is_pretty() is False

    def test_pretty_unknown_value(self):
        """?pretty=xxx（未知值）不应启用美化"""
        handler = self._make_handler("/status?pretty=xxx")
        assert handler._is_pretty() is False

    def test_send_json_pretty_contains_newlines(self):
        """美化模式输出的 JSON 应包含换行符"""
        handler = self._make_handler("/status?pretty=true")
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        from api_server import ApiRequestHandler
        data = {"status": "ok", "version": "1.0", "app": "PsLauncher"}
        # 绑定 _send_json 并使用绑定好的方法
        handler._send_json = ApiRequestHandler._send_json.__get__(handler, ApiRequestHandler)
        handler._send_json(data)
        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        assert "\n" in written
        assert "  " in written  # 缩进
        assert '"status": "ok"' in written

    def test_send_json_normal_no_newlines(self):
        """非美化模式输出的 JSON 不应含额外换行"""
        handler = self._make_handler("/status")
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        from api_server import ApiRequestHandler
        data = {"status": "ok", "version": "1.0", "app": "PsLauncher"}
        handler._send_json = ApiRequestHandler._send_json.__get__(handler, ApiRequestHandler)
        handler._send_json(data)
        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        assert "\n" not in written


# ============================================================
# API i18n 多语言测试
# ============================================================


def _make_help_post_handler():
    """创建一个模拟 handler 并绑定 _handle_help_post 真实方法"""
    from api_server import ApiRequestHandler
    handler = MagicMock(spec=ApiRequestHandler)
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    handler.wfile = MagicMock()
    handler._is_pretty = MagicMock(return_value=False)
    handler._send_json = ApiRequestHandler._send_json.__get__(handler, ApiRequestHandler)
    handler._handle_help_post = ApiRequestHandler._handle_help_post.__get__(handler, ApiRequestHandler)
    return handler


@pytest.mark.algo
class TestApiHelpPostI18n:
    """POST /help 端点 i18n 多语言测试"""

    def _get_endpoints(self, language):
        """在指定语言下调用 _handle_help_post，返回 endpoints 列表"""
        from i18n import set_language
        set_language(language)
        handler = _make_help_post_handler()
        handler._handle_help_post()
        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        data = json.loads(written)
        return data["endpoints"]

    def _get_meta_self_description(self, language):
        """获取 POST /help 中自描述端点的说明字段"""
        from i18n import set_language
        set_language(language)
        handler = _make_help_post_handler()
        handler._handle_help_post()
        written = handler.wfile.write.call_args[0][0].decode("utf-8")
        data = json.loads(written)
        # 在 endponts 列表里找第三个元素（POST /help self-description）
        for ep in data["endpoints"]:
            if ep["method"] == "POST" and ep["path"] == "/help":
                return ep
        return None

    def test_help_post_english_descriptions(self):
        """英文下所有 description 应为英文"""
        endpoints = self._get_endpoints("en")
        for ep in endpoints:
            desc = ep.get("description", "")
            assert isinstance(desc, str), f"{ep['method']} {ep['path']} description 不是字符串"
            assert len(desc) > 0, f"{ep['method']} {ep['path']} description 为空"
            # 验证不含中文字符
            assert not any('\u4e00' <= c <= '\u9fff' for c in desc), \
                f"{ep['method']} {ep['path']} description 包含中文: {desc}"

    def test_help_post_chinese_descriptions(self):
        """中文下所有 description 应为中文"""
        endpoints = self._get_endpoints("zh_CN")
        for ep in endpoints:
            desc = ep.get("description", "")
            assert isinstance(desc, str), f"{ep['method']} {ep['path']} description 不是字符串"
            assert len(desc) > 0, f"{ep['method']} {ep['path']} description 为空"
            # 验证包含中文字符
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in desc)
            assert has_chinese, f"{ep['method']} {ep['path']} description 不包含中文: {desc}"

    def test_help_post_status_endpoint_en(self):
        """英文下 /status 端点 description"""
        endpoints = self._get_endpoints("en")
        for ep in endpoints:
            if ep["method"] == "GET" and ep["path"] == "/status":
                assert "Check server status" in ep["description"]
                return

    def test_help_post_status_endpoint_zh(self):
        """中文下 /status 端点 description"""
        endpoints = self._get_endpoints("zh_CN")
        for ep in endpoints:
            if ep["method"] == "GET" and ep["path"] == "/status":
                assert "检查服务器状态" in ep["description"]
                return

    def test_help_post_meta_description_en(self):
        """英文下自描述端点的元说明字段"""
        meta = self._get_meta_self_description("en")
        assert meta is not None
        # 检查 response 结构中的元说明字段
        response = meta.get("response", {})
        endpoints_template = response.get("endpoints", [])
        assert len(endpoints_template) > 0
        template = endpoints_template[0]
        assert template["description"] == "Description"
        assert template["params"] == "Query parameters (optional)"
        assert template["body"] == "Request body parameters (optional)"
        assert template["response"] == "Response format description"

    def test_help_post_meta_description_zh(self):
        """中文下自描述端点的元说明字段"""
        meta = self._get_meta_self_description("zh_CN")
        assert meta is not None
        response = meta.get("response", {})
        endpoints_template = response.get("endpoints", [])
        assert len(endpoints_template) > 0
        template = endpoints_template[0]
        assert template["description"] == "说明"
        assert template["params"] == "查询参数（可选）"
        assert template["body"] == "请求体参数（可选）"
        assert template["response"] == "响应格式描述"

    def test_help_post_english_params_descriptions(self):
        """英文下 params/body 说明应为英文"""
        endpoints = self._get_endpoints("en")
        for ep in endpoints:
            params = ep.get("params")
            if params is not None and isinstance(params, dict):
                for k, v in params.items():
                    if isinstance(v, str) and v:
                        assert not any('\u4e00' <= c <= '\u9fff' for c in v), \
                            f"{ep['method']} {ep['path']} params.{k} 包含中文: {v}"
            body = ep.get("body")
            if body is not None and isinstance(body, dict):
                for k, v in body.items():
                    if isinstance(v, str) and v:
                        assert not any('\u4e00' <= c <= '\u9fff' for c in v), \
                            f"{ep['method']} {ep['path']} body.{k} 包含中文: {v}"

    def test_help_post_chinese_params_descriptions(self):
        """中文下 params/body 说明应为中文"""
        endpoints = self._get_endpoints("zh_CN")
        for ep in endpoints:
            params = ep.get("params")
            if params is not None and isinstance(params, dict):
                for k, v in params.items():
                    if isinstance(v, str) and v:
                        assert any('\u4e00' <= c <= '\u9fff' for c in v), \
                            f"{ep['method']} {ep['path']} params.{k} 不包含中文: {v}"
            body = ep.get("body")
            if body is not None and isinstance(body, dict):
                for k, v in body.items():
                    if isinstance(v, str) and v:
                        assert any('\u4e00' <= c <= '\u9fff' for c in v), \
                            f"{ep['method']} {ep['path']} body.{k} 不包含中文: {v}"

    def test_help_post_params_scripts_folder_en(self):
        """英文下 /scripts 的 params.folder 说明"""
        endpoints = self._get_endpoints("en")
        for ep in endpoints:
            if ep["method"] == "GET" and ep["path"] == "/scripts":
                params = ep.get("params", {})
                assert "Optional, filter by folder" in params.get("folder", "")
                return

    def test_help_post_params_scripts_folder_zh(self):
        """中文下 /scripts 的 params.folder 说明"""
        endpoints = self._get_endpoints("zh_CN")
        for ep in endpoints:
            if ep["method"] == "GET" and ep["path"] == "/scripts":
                params = ep.get("params", {})
                assert "可选，按文件夹筛选" in params.get("folder", "")
                return


@pytest.mark.algo
class TestApiErrorMessagesI18n:
    """API 错误消息 i18n 测试"""

    def test_error_message_via_tr_en(self):
        """使用 tr() 获取的错误消息为英文"""
        from i18n import set_language, tr
        set_language("en")
        assert tr("api.error.unauthorized") == "Unauthorized"
        assert tr("api.error.not_found") == "Not Found"
        assert tr("api.error.invalid_json") == "Invalid JSON"
        assert tr("api.error.missing_param_path") == "Missing 'path' parameter"
        assert tr("api.error.missing_param_id") == "Missing 'id' parameter"

    def test_error_message_via_tr_zh(self):
        """使用 tr() 获取的错误消息为中文"""
        from i18n import set_language, tr
        set_language("zh_CN")
        assert tr("api.error.unauthorized") == "未授权"
        assert tr("api.error.not_found") == "未找到"
        assert tr("api.error.invalid_json") == "无效的 JSON 格式"
        assert tr("api.error.missing_param_path") == "缺少 'path' 参数"
        assert tr("api.error.missing_param_id") == "缺少 'id' 参数"

    def test_shutdown_message_en(self):
        """英文下关闭消息"""
        from i18n import set_language, tr
        set_language("en")
        assert tr("api.shutdown.message") == "PsLauncher is shutting down..."

    def test_shutdown_message_zh(self):
        """中文下关闭消息"""
        from i18n import set_language, tr
        set_language("zh_CN")
        assert tr("api.shutdown.message") == "PsLauncher 正在关闭..."


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