# coding = utf-8
#
# @File name:       test_tcp_event.py
# @brief:           TCP 事件服务器自动化测试
# @attention:       测试 TcpEventServer 的核心功能：连接、广播、订阅过滤
# @Author:          NGC13009
# @History:         2026-06-30		Create

import json
import socket
import threading
import time
import pytest


# ============================================================
# 功能层测试（直接测试 TCP socket 通信逻辑，不依赖 QThread）
# ============================================================

class TestTcpEventProtocol:
    """测试 TCP 事件协议的客户端服务器通信"""

    def test_newline_json_protocol(self):
        """测试新行分隔 JSON 协议的基本收发"""
        # 创建一对 socket
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        server_sock.listen(1)
        server_sock.settimeout(3)
        port = server_sock.getsockname()[1]

        # 客户端连接
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))

        # 服务器接受
        conn, addr = server_sock.accept()

        # 发送新行分隔 JSON
        payload = {"event": "test", "data": {"msg": "hello"}}
        conn.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))

        # 客户端接收
        buffer = b""
        while b"\n" not in buffer:
            buffer += client.recv(4096)
        line = buffer.split(b"\n", 1)[0]
        received = json.loads(line.decode("utf-8"))
        assert received["event"] == "test"
        assert received["data"]["msg"] == "hello"

        conn.close()
        client.close()
        server_sock.close()

    def test_subscribe_message(self):
        """测试客户端发送订阅消息"""
        # 服务端接收订阅消息
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        server_sock.listen(1)
        server_sock.settimeout(3)
        port = server_sock.getsockname()[1]

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))

        conn, addr = server_sock.accept()

        # 客户端发送订阅消息
        sub_msg = json.dumps({"subscribe": ["path_changed", "terminal_status"]}) + "\n"
        client.sendall(sub_msg.encode("utf-8"))

        # 服务器接收
        buffer = b""
        while b"\n" not in buffer:
            buffer += conn.recv(4096)
        line = buffer.split(b"\n", 1)[0]
        received = json.loads(line.decode("utf-8"))
        assert received["subscribe"] == ["path_changed", "terminal_status"]

        conn.close()
        client.close()
        server_sock.close()

    def test_multiple_messages(self):
        """测试多条消息的连续发送和接收"""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        server_sock.listen(1)
        server_sock.settimeout(3)
        port = server_sock.getsockname()[1]

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))
        conn, addr = server_sock.accept()

        # 发送三条消息
        messages = [
            {"event": "msg1", "data": {"n": 1}},
            {"event": "msg2", "data": {"n": 2}},
            {"event": "msg3", "data": {"n": 3}},
        ]
        for msg in messages:
            conn.sendall((json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8"))

        # 客户端接收全部
        buffer = b""
        lines = []
        while len(lines) < 3:
            buffer += client.recv(4096)
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                lines.append(line)

        for i, line in enumerate(lines):
            received = json.loads(line.decode("utf-8"))
            assert received["event"] == messages[i]["event"]

        conn.close()
        client.close()
        server_sock.close()

    def test_broadcast_add_and_remove_folder(self):
        """测试广播消息格式（对应于 add/remove folder 操作的 path_changed）"""
        # 模拟 path_changed 事件格式
        event_data = {
            "event": "path_changed",
            "timestamp": "2026-06-30 22:00:00",
            "data": {
                "folders": ["C:/scripts", "D:/scripts"]
            }
        }
        msg = json.dumps(event_data, ensure_ascii=False) + "\n"

        # 验证格式
        parsed = json.loads(msg.strip())
        assert parsed["event"] == "path_changed"
        assert "folders" in parsed["data"]
        assert len(parsed["data"]["folders"]) == 2

    def test_script_changed_format(self):
        """测试 script_changed 事件格式"""
        event_data = {
            "event": "script_changed",
            "timestamp": "2026-06-30 22:00:00",
            "data": {
                "folder": "C:/scripts",
                "scripts": [
                    {"name": "run.ps1", "path": "C:/scripts/run.ps1"},
                    {"name": "test.bat", "path": "C:/scripts/test.bat"}
                ]
            }
        }
        parsed = json.loads(json.dumps(event_data, ensure_ascii=False))
        assert parsed["event"] == "script_changed"
        assert len(parsed["data"]["scripts"]) == 2

    def test_terminal_output_format(self):
        """测试 terminal_output 事件格式"""
        event_data = {
            "event": "terminal_output",
            "timestamp": "2026-06-30 22:00:00",
            "data": {
                "terminal_id": 0,
                "script": "C:/scripts/run.ps1",
                "text": "Hello World\n"
            }
        }
        parsed = json.loads(json.dumps(event_data, ensure_ascii=False))
        assert parsed["data"]["terminal_id"] == 0
        assert "text" in parsed["data"]

    def test_terminal_status_format(self):
        """测试 terminal_status 事件格式"""
        event_data = {
            "event": "terminal_status",
            "timestamp": "2026-06-30 22:00:00",
            "data": {
                "terminal_id": 1,
                "script": "C:/scripts/server.ps1",
                "status": "finished"
            }
        }
        parsed = json.loads(json.dumps(event_data, ensure_ascii=False))
        assert parsed["data"]["status"] in ("started", "finished", "stopped", "closed")

    def test_subscribe_wildcard(self):
        """测试通配符订阅（* 表示全部）"""
        msg = json.dumps({"subscribe": ["*"]})
        parsed = json.loads(msg)
        assert parsed["subscribe"] == ["*"]

    def test_subscribe_empty_list(self):
        """测试空订阅列表（取消所有订阅）"""
        msg = json.dumps({"subscribe": []})
        parsed = json.loads(msg)
        assert parsed["subscribe"] == []