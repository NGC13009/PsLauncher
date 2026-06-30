# coding = utf-8
# Arch   = manyArch
#
# @File name:       tcp_event_server.py
# @brief:           TCP 长连接事件服务器，为 PsLauncher 提供状态变更推送服务
# @attention:       运行在独立 QThread 中，通过信号槽与主窗口通信
# @Author:          NGC13009
# @History:         2026-06-30		Create

import json
import socket
import threading
import datetime
from PyQt5.QtCore import QThread, pyqtSignal


class TcpEventServer(QThread):
    """在独立 QThread 中运行的 TCP 事件推送服务器"""

    def __init__(self, bind_ip="127.0.0.1", bind_port=13026):
        super().__init__()
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self._running = False
        self._server_socket = None
        # 线程安全的客户端集合
        self._clients_lock = threading.Lock()
        self._clients = set()

    def run(self):
        """启动 TCP 服务器（在子线程中运行）"""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.settimeout(1.0)

        try:
            self._server_socket.bind((self.bind_ip, self.bind_port))
            self._server_socket.listen(5)
            self._running = True
            print(f"[TcpEventServer] 已启动: {self.bind_ip}:{self.bind_port}")

            while self._running:
                try:
                    client_sock, addr = self._server_socket.accept()
                    # 每个客户端启动独立线程处理
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_sock, addr),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except OSError:
                    break

        except OSError as e:
            print(f"[TcpEventServer] 绑定失败 {self.bind_ip}:{self.bind_port} - {e}")
        except Exception as e:
            print(f"[TcpEventServer] 服务器异常: {e}")
        finally:
            self._cleanup()

    def stop(self):
        """停止 TCP 服务器"""
        self._running = False
        self._cleanup()
        print("[TcpEventServer] 已停止")

    def _cleanup(self):
        """清理服务器资源"""
        with self._clients_lock:
            for sock in self._clients:
                try:
                    sock.close()
                except Exception:
                    pass
            self._clients.clear()
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

    def _handle_client(self, client_sock, addr):
        """处理单个客户端连接：接收订阅消息并维护连接"""
        # 默认订阅所有事件（None 表示通配）
        subscriptions = None

        with self._clients_lock:
            self._clients.add(client_sock)

        print(f"[TcpEventServer] 新客户端已连接: {addr}")

        try:
            client_sock.settimeout(30.0)
            buffer = b""
            while self._running:
                try:
                    data = client_sock.recv(4096)
                    if not data:
                        break
                    buffer += data
                    # 按行处理（新行分隔 JSON）
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            msg = json.loads(line.decode("utf-8"))
                            if isinstance(msg, dict) and "subscribe" in msg:
                                sub_list = msg["subscribe"]
                                if sub_list == ["*"] or not sub_list:
                                    subscriptions = None
                                else:
                                    subscriptions = set(sub_list)
                        except json.JSONDecodeError:
                            pass
                except socket.timeout:
                    continue
        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            with self._clients_lock:
                self._clients.discard(client_sock)
            try:
                client_sock.close()
            except Exception:
                pass
            print(f"[TcpEventServer] 客户端已断开: {addr}")

    def broadcast(self, event_type, data):
        """向所有已连接的客户端广播事件"""
        payload = {
            "event": event_type,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }
        message = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")

        dead_clients = []
        with self._clients_lock:
            for sock in self._clients:
                try:
                    sock.sendall(message)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    dead_clients.append(sock)

        # 清理断开的客户端
        if dead_clients:
            with self._clients_lock:
                for sock in dead_clients:
                    self._clients.discard(sock)
                    try:
                        sock.close()
                    except Exception:
                        pass

    def broadcast_path_changed(self, folders):
        """广播路径列表变化"""
        self.broadcast("path_changed", {"folders": folders})

    def broadcast_script_changed(self, folder, scripts):
        """广播脚本列表变化"""
        self.broadcast("script_changed", {
            "folder": folder,
            "scripts": scripts
        })

    def broadcast_terminal_output(self, terminal_id, script_path, text):
        """广播终端输出变化"""
        self.broadcast("terminal_output", {
            "terminal_id": terminal_id,
            "script": script_path,
            "text": text
        })

    def broadcast_terminal_status(self, terminal_id, script_path, status):
        """广播终端运行状态变化（started/finished/stopped/closed）"""
        self.broadcast("terminal_status", {
            "terminal_id": terminal_id,
            "script": script_path,
            "status": status
        })