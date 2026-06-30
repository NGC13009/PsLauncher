# coding = utf-8
#
# @File name:       test_event_listener.py
# @brief:           手动测试脚本：连接到 PsLauncher TCP 事件服务器并显示变更信息
# @attention:       运行前请确保 PsLauncher 已启动
# @Author:          NGC13009
# @History:         2026-06-30		Create

"""
使用说明：
    默认连接 127.0.0.1:13026，监听所有事件。
    可通过命令行参数订阅特定事件类型，不支持的事件类型将被丢弃。

    python test_event_listener.py                           # 监听所有事件
    python test_event_listener.py --subscribe path_changed terminal_status  # 只监听路径变化和终端状态变化
    python test_event_listener.py --host 127.0.0.1 --port 13026   # 指定地址和端口

    支持的订阅事件类型：
        - path_changed       # 文件夹路径列表发生变化
        - script_changed     # 脚本列表发生变化
        - terminal_output    # 终端有新的输出（仅发送变化的 terminal_id）
        - terminal_status    # 终端运行状态变化（开始/停止/完成/关闭）
"""

import socket
import json
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="PsLauncher TCP 事件监听器")
    parser.add_argument("--host", default="127.0.0.1", help="PsLauncher TCP 事件服务器地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=13026, help="PsLauncher TCP 事件服务器端口 (默认: 13026)")
    parser.add_argument("--subscribe", nargs="*", default=None,
                        help="订阅的事件类型列表，不指定则监听所有事件")
    args = parser.parse_args()

    # 订阅列表（不指定或空列表 = 监听所有）
    subscribe_list = args.subscribe

    print(f"PsLauncher TCP 事件监听器")
    print(f"连接至: {args.host}:{args.port}")
    if subscribe_list:
        print(f"订阅事件: {', '.join(subscribe_list)}")
    else:
        print(f"订阅事件: 所有")
    print("等待接收事件... (按 Ctrl+C 退出)")
    print("-" * 60)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30.0)
        sock.connect((args.host, args.port))

        # 发送订阅消息（如果指定了订阅列表）
        if subscribe_list:
            sub_msg = json.dumps({"subscribe": subscribe_list}) + "\n"
            sock.sendall(sub_msg.encode("utf-8"))
            print(f"[系统] 已发送订阅请求: {subscribe_list}")

        buffer = b""
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    print("[系统] 服务器已断开连接")
                    break
                buffer += data

                # 处理所有完整的 JSON 行
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line.decode("utf-8"))
                        display_event(event)
                    except json.JSONDecodeError as e:
                        print(f"[错误] JSON 解析失败: {e}")
                        print(f"  原始数据: {line[:200]}")

            except socket.timeout:
                # 超时后继续等待，保持连接活跃
                continue

    except ConnectionRefusedError:
        print(f"[错误] 无法连接到 {args.host}:{args.port}")
        print("请确保 PsLauncher 已启动并开启了 TCP 事件服务器")
        print("（默认端口 13026，可在配置文件中修改）")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[系统] 用户中断，退出监听器")
    finally:
        try:
            sock.close()
        except Exception:
            pass


def display_event(event):
    """格式化显示接收到的 JSON 事件"""
    event_type = event.get("event", "未知")
    timestamp = event.get("timestamp", "无时间戳")
    data = event.get("data", {})

    print(f"\n[{timestamp}] 事件类型: {event_type}")

    if event_type == "path_changed":
        folders = data.get("folders", [])
        print(f"  文件夹列表 (共 {len(folders)} 个):")
        for folder in folders:
            print(f"    - {folder}")

    elif event_type == "script_changed":
        folder = data.get("folder", "")
        scripts = data.get("scripts", [])
        print(f"  文件夹: {folder}")
        print(f"  脚本列表 (共 {len(scripts)} 个):")
        for script in scripts:
            print(f"    - {script.get('name', '?')}: {script.get('path', '?')}")

    elif event_type == "terminal_output":
        terminal_id = data.get("terminal_id", "?")
        script = data.get("script", "?")
        text = data.get("text", "")
        print(f"  终端 ID: {terminal_id}")
        print(f"  脚本: {script}")
        # 截断过长的输出
        if len(text) > 500:
            print(f"  输出 (前 500 字符): {text[:500]}...")
        else:
            print(f"  输出: {text}")

    elif event_type == "terminal_status":
        terminal_id = data.get("terminal_id", "?")
        script = data.get("script", "?")
        status = data.get("status", "?")
        status_map = {
            "started": "🚀 已启动",
            "finished": "✅ 已正常结束",
            "stopped": "🛑 被终止",
            "closed": "🔒 标签页已关闭",
        }
        status_display = status_map.get(status, f"❓ {status}")
        print(f"  终端 ID: {terminal_id}")
        print(f"  脚本: {script}")
        print(f"  状态: {status_display}")

    else:
        print(f"  数据: {json.dumps(data, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()