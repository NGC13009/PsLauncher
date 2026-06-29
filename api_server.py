# coding = utf-8
# Arch   = manyArch
#
# @File name:       api_server.py
# @brief:           HTTP API 服务器，为 PsLauncher 提供 RESTful API 接口
# @attention:       运行在独立 QThread 中，通过信号槽与主窗口通信
# @Author:          NGC13009
# @History:         2026-06-29		Create

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Qt, Q_ARG

from aboutandhelp import __version__
from i18n import tr


class ApiRequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器（每个请求在新线程中处理）"""

    # 类级别引用，由 ApiServerThread 在启动时设置
    main_window = None
    auth_token = ""

    def log_message(self, format, *args):
        """覆盖日志方法，同时输出到 stdout"""
        msg = f"[ApiServer] {format % args}"
        print(msg)

    def _check_auth(self):
        """验证 Bearer Token，若未配置 token 则跳过验证"""
        if not self.__class__.auth_token:
            return True
        auth_header = self.headers.get("Authorization", "")
        expected = f"Bearer {self.__class__.auth_token}"
        return auth_header == expected

    def _send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if self._is_pretty():
            json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        else:
            json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.wfile.write(json_bytes)

    def _send_error(self, message, status=400):
        """发送错误响应"""
        self._send_json({"success": False, "error": message}, status=status)

    def _is_pretty(self):
        """检查请求是否要求美化输出（?pretty=true/1/yes）"""
        query = self._parse_query()
        return query.get("pretty", "").lower() in ("true", "1", "yes")

    def _read_body(self):
        """读取请求体 JSON"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def _invoke_main(self, method_name, *args):
        """通过 QMetaObject.invokeMethod 安全地在主线程调用 MainWindow 方法（阻塞等待结果）"""
        result_holder = {"result": None, "error": None, "done": threading.Event()}

        def callback(ret_val):
            result_holder["result"] = ret_val
            result_holder["done"].set()

        def error_callback(err):
            result_holder["error"] = str(err)
            result_holder["done"].set()

        # 使用 invokeMethod 调用返回非 void 的方法比较困难，
        # 改用 signals 进行跨线程通信
        self.__class__.api_server._execute_on_main(method_name, args, result_holder)
        result_holder["done"].wait(timeout=10)
        if result_holder["error"]:
            raise RuntimeError(result_holder["error"])
        return result_holder["result"]

    # ==================== 路由处理 ====================

    def do_GET(self):
        """处理 GET 请求"""
        if not self._check_auth():
            self._send_error("Unauthorized", 401)
            return

        path = self.path.split("?")[0].rstrip("/")
        query = self._parse_query()

        if path == "/status" or path == "":
            self._handle_status()
        elif path == "/help":
            self._handle_help()
        elif path == "/folders":
            self._handle_folders()
        elif path == "/scripts":
            self._handle_scripts(query)
        elif path == "/terminals":
            self._handle_terminals()
        elif path == "/terminal/output":
            self._handle_terminal_output(query)
        elif path == "/shutdown":
            self._handle_shutdown()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        """处理 POST 请求"""
        if not self._check_auth():
            self._send_error("Unauthorized", 401)
            return

        path = self.path.split("?")[0].rstrip("/")

        if path == "/status" or path == "":
            self._handle_status()
        elif path == "/shutdown":
            self._handle_shutdown()
        elif path == "/folder/add":
            self._handle_folder_add()
        elif path == "/folder/remove":
            self._handle_folder_remove()
        elif path == "/script/run":
            self._handle_script_run()
        elif path == "/terminal/stop":
            self._handle_terminal_stop()
        elif path == "/terminal/stop_all":
            self._handle_terminal_stop_all()
        elif path == "/terminal/clear":
            self._handle_terminal_clear()
        elif path == "/terminal/input":
            self._handle_terminal_input()
        else:
            # 也支持 GET 端点通过 POST 访问
            if path == "/folders":
                self._handle_folders()
            elif path == "/scripts":
                self._handle_scripts(self._parse_query())
            elif path == "/terminals":
                self._handle_terminals()
            elif path == "/terminal/output":
                self._handle_terminal_output(self._parse_query())
            elif path == "/help":
                self._handle_help()
            else:
                self._send_error("Not Found", 404)

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _parse_query(self):
        """解析 URL 查询参数"""
        if "?" not in self.path:
            return {}
        query_str = self.path.split("?", 1)[1]
        result = {}
        for pair in query_str.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                result[k] = v
            else:
                result[pair] = ""
        return result

    # ==================== 端点处理 ====================

    def _handle_status(self):
        """返回服务状态"""
        self._send_json({
            "status": "ok",
            "version": __version__,
            "app": "PsLauncher"
        })

    def _handle_help(self):
        """返回帮助页面 HTML 字符串"""
        try:
            from i18n import get_language
            if get_language() == "zh_CN":
                from i18n.source_help_page_zh_CN import html_content as hc
            else:
                from i18n.source_help_page import html_content as hc
            self._send_json({"help": hc})
        except Exception as e:
            self._send_json({"help": tr("api.help_load_failed", error=str(e))})

    def _handle_folders(self):
        """枚举文件夹路径列表"""
        result = self._invoke_main("api_get_folders")
        self._send_json(result)

    def _handle_scripts(self, query):
        """枚举脚本列表（可选筛选文件夹）"""
        folder = query.get("folder", None)
        result = self._invoke_main("api_get_scripts", folder)
        self._send_json(result)

    def _handle_folder_add(self):
        """添加文件夹路径"""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON", 400)
            return
        path = body.get("path", "")
        if not path:
            self._send_error("Missing 'path' parameter", 400)
            return
        result = self._invoke_main("api_add_folder", path)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_error(result.get("error", "Failed"), 400)

    def _handle_folder_remove(self):
        """移除文件夹路径"""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON", 400)
            return
        path = body.get("path", "")
        if not path:
            self._send_error("Missing 'path' parameter", 400)
            return
        result = self._invoke_main("api_remove_folder", path)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_error(result.get("error", "Failed"), 400)

    def _handle_script_run(self):
        """运行指定脚本"""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON", 400)
            return
        folder = body.get("folder", "")
        script = body.get("script", "")
        if not folder or not script:
            self._send_error("Missing 'folder' or 'script' parameter", 400)
            return
        result = self._invoke_main("api_run_script", folder, script)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_error(result.get("error", "Failed"), 400)

    def _handle_terminals(self):
        """枚举打开的终端界面"""
        result = self._invoke_main("api_get_terminals")
        self._send_json(result)

    def _handle_terminal_stop(self):
        """终止终端"""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON", 400)
            return
        terminal_id = body.get("id", None)
        terminal_name = body.get("name", None)
        if terminal_id is None and terminal_name is None:
            self._send_error("Missing 'id' or 'name' parameter", 400)
            return
        result = self._invoke_main("api_stop_terminal", terminal_id, terminal_name)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_error(result.get("error", "Failed"), 400)

    def _handle_terminal_stop_all(self):
        """终止所有终端"""
        result = self._invoke_main("api_stop_all_terminals")
        self._send_json(result)

    def _handle_terminal_output(self, query):
        """查看终端输出记录"""
        terminal_id_str = query.get("id", None)
        terminal_name = query.get("name", None)
        if terminal_id_str is None and terminal_name is None:
            self._send_error("Missing 'id' or 'name' parameter", 400)
            return
        terminal_id = int(terminal_id_str) if terminal_id_str is not None else None
        result = self._invoke_main("api_get_terminal_output", terminal_id, terminal_name)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_error(result.get("error", "Failed"), 400)

    def _handle_terminal_clear(self):
        """清空终端输出"""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON", 400)
            return
        terminal_id = body.get("id", None)
        if terminal_id is None:
            self._send_error("Missing 'id' parameter", 400)
            return
        result = self._invoke_main("api_clear_terminal", terminal_id)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_error(result.get("error", "Failed"), 400)

    def _handle_terminal_input(self):
        """向终端发送字符串"""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON", 400)
            return
        terminal_id = body.get("id", None)
        text = body.get("text", "")
        if terminal_id is None:
            self._send_error("Missing 'id' parameter", 400)
            return
        if not text:
            self._send_error("Missing 'text' parameter", 400)
            return
        result = self._invoke_main("api_send_terminal_input", terminal_id, text)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_error(result.get("error", "Failed"), 400)

    def _handle_shutdown(self):
        """关闭 PsLauncher"""
        result = self._invoke_main("api_shutdown")
        self._send_json(result)


class ApiServerThread(QThread):
    """在独立 QThread 中运行的 HTTP 服务器"""

    # 信号：向主线程请求执行某个方法
    execute_signal = pyqtSignal(str, tuple, object)

    def __init__(self, bind_ip, bind_port, auth_token, main_window):
        super().__init__()
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.auth_token = auth_token
        self.main_window = main_window
        self.http_server = None
        self._running = False

    def run(self):
        """启动 HTTP 服务器（在子线程中运行）"""
        ApiRequestHandler.main_window = self.main_window
        ApiRequestHandler.auth_token = self.auth_token
        ApiRequestHandler.api_server = self

        try:
            self.http_server = HTTPServer((self.bind_ip, self.bind_port), ApiRequestHandler)
            self.http_server.timeout = 1  # 1秒超时以便检查停止标志
            self._running = True
            auth_status = tr("api.auth_enabled") if self.auth_token else tr("api.auth_disabled")
            print(tr("api.server_started", ip=self.bind_ip, port=self.bind_port))
            print(tr("api.auth_status", status=auth_status))

            while self._running:
                self.http_server.handle_request()
        except OSError as e:
            print(tr("api.bind_failed", ip=self.bind_ip, port=self.bind_port, error=str(e)))
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(tr("api.server_exception", error=str(e)))
            import traceback
            traceback.print_exc()

    def stop(self):
        """停止 HTTP 服务器"""
        self._running = False
        if self.http_server:
            try:
                self.http_server.server_close()
            except Exception:
                pass
        print(tr("api.server_stopped"))

    def _execute_on_main(self, method_name, args, result_holder):
        """在主线程中执行方法并获取结果（通过信号槽机制）"""
        self.execute_signal.emit(method_name, args, result_holder)