# coding = utf-8
# Arch   = manyArch
#
# @File name:       code_translator.py
# @brief:           code_translator.py - 将 Python 源码中的用户可见字符串从中文翻译为英文
#                   使用 OpenAI 兼容格式的大模型 API
#
#                   用法:
#                       1. 修改下方【配置区】中的 API 地址、密钥、模型名、文件列表等
#                       2. 运行: python code_translator.py
# @attention:       None
# @Author:          wyb
# @History:         2026-04-18		Create

import os
import re
import sys
import time
from openai import OpenAI

# ================================================================
#                        【配置区 - 请按需修改】
# ================================================================

# --- API 配置 ---
API_BASE_URL = "http://127.0.0.1:13092/v1" # OpenAI 兼容 API 地址
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"    # API Key
MODEL_NAME = "llama.cpp"                   # 模型名称

# --- 翻译任务列表 ---
# 每项为 (源文件路径, 翻译后输出路径) 的元组
# 输出目录如果不存在会自动创建
TRANSLATION_TASKS = [
    ("PsLauncher/aboutandhelp.py", "PsLauncher/en/aboutandhelp.py"),
    ("PsLauncher/PsLauncher.py", "PsLauncher/en/PsLauncher.py"),
    ("PsLauncher/tabClass.py", "PsLauncher/en/tabClass.py"),
    # ("PsLauncher/utils.py", "PsLauncher/en/utils.py"),
]

# --- 翻译行为 ---
SOURCE_LANG = "中文" # 源语言
TARGET_LANG = "英文" # 目标语言

# --- 分块大小 ---
# 每次发给 AI 的行数。值越大越快但越耗 token，值越小越慢但越节省
CHUNK_SIZE = 40

# --- 请求间隔（秒），避免触发 API 限流 ---
REQUEST_INTERVAL = 1.0

# --- 最大重试次数 ---
MAX_RETRIES = 3

# --- 请求超时（秒）---
REQUEST_TIMEOUT = 120

# --- 是否在翻译前备份原文件 ---
BACKUP_ORIGINAL = False

# ================================================================
#                      【以下为程序逻辑，一般无需修改】
# ================================================================

SYSTEM_PROMPT = f"""\
你是一个专业的代码翻译助手。你的任务是将 Python 代码中 **给用户呈现的字符串** \
从{SOURCE_LANG}翻译为{TARGET_LANG}。

## 翻译规则
1. **只翻译**用户可见的字符串（如 print()、input()、raise、assert、logging、\
messagebox、UI 标签、错误提示、帮助文档字符串等中的文本内容）
2. **不要翻译**以下内容：
   - 注释（# 开头的内容）
   - 变量名、函数名、类名、模块名、属性名
   - import 语句和模块路径
   - 代码结构、缩进、标点符号风格
   
总之就是所有非代码，非注释的，给用户呈现的内容。

3. 对于 f-string / format 字符串，只翻译花括号 `{{}}` 外的中文部分，不要改动花括号内的表达式
4. 原始字符串前缀（r、f、u、b 等）保持不变
5. 如果某行没有任何需要翻译的内容，原样返回该行
6. **必须原样返回所有行**，不要省略、合并或拆分任何行
7. 保持缩进完全一致
8. 符号不需要更改。

## 输出格式
- 输入是带行号的代码（格式：行号: 代码内容）
- 输出必须是 **完全相同行号** 的代码（格式相同），只修改需要翻译的字符串
- 不要添加任何多余的解释、说明或 markdown 标记
"""


def create_client() -> OpenAI:
    """创建 OpenAI 兼容客户端"""
    return OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
        timeout=REQUEST_TIMEOUT,
    )


def translate_chunk(
    client: OpenAI,
    lines: list[str],
    start_line_num: int,
    chunk_index: int,
    total_chunks: int,
) -> list[str]:
    """
    将一批代码行发送给 AI 进行翻译。

    Args:
        client: OpenAI 客户端
        lines: 该批次的原始代码行列表
        start_line_num: 起始行号（从 1 开始）
        chunk_index: 当前批次索引（从 0 开始）
        total_chunks: 总批次数

    Returns:
        翻译后的代码行列表（长度应与输入相同）
    """
    # 构造带行号的内容
    numbered_lines = []
    for i, line in enumerate(lines):
        line_num = start_line_num + i
        # 去除行号后的冒号和空格，保留原始内容
        numbered_lines.append(f"{line_num}: {line}")
    content = "\n".join(numbered_lines)

    user_prompt = (f"以下是第 {chunk_index + 1}/{total_chunks} 批代码（共 {len(lines)} 行），"
                   f"行号范围 {start_line_num}~{start_line_num + len(lines) - 1}。\n"
                   f"请将其中{SOURCE_LANG}的用户可见字符串翻译为{TARGET_LANG}，"
                   f"按照相同格式（行号: 内容）逐行返回。\n\n{content}")

    # 带重试的请求
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(
                f"  [批次 {chunk_index + 1}/{total_chunks}] "
                f"第 {attempt} 次请求... ",
                end="",
                flush=True,
            )
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    },
                ],
                temperature=0.1,
            )
            print("成功 ✓")
            break
        except Exception as e:
            last_error = e
            print(f"失败 ✗ ({e})")
            if attempt < MAX_RETRIES:
                wait = REQUEST_INTERVAL * attempt
                print(f"  等待 {wait:.1f}s 后重试...")
                time.sleep(wait)
    else:
        print(f"  ⚠ 批次 {chunk_index + 1} 连续 {MAX_RETRIES} 次失败，保留原文！")
        print(f"  错误信息: {last_error}")
        return lines # 返回原始行作为兜底

    # 解析 AI 返回结果
    raw_output = response.choices[0].message.content.strip()

    # 移除可能的 markdown 代码块包裹
    if raw_output.startswith("```"):
        # 移除首行的 ```python 或 ``` 等
        lines_out = raw_output.split("\n")
        if lines_out[0].strip().startswith("```"):
            lines_out = lines_out[1:]
        if lines_out and lines_out[-1].strip() == "```":
            lines_out = lines_out[:-1]
        raw_output = "\n".join(lines_out)

    # 解析行号映射
    translated_map: dict[int, str] = {}
    for out_line in raw_output.split("\n"):
        m = re.match(r"^(\d+):\s?(.*)", out_line)
        if m:
            translated_map[int(m.group(1))] = m.group(2)

    # 按原始顺序重组，未匹配到的行保留原文
    result: list[str] = []
    missing_count = 0
    for i, orig_line in enumerate(lines):
        line_num = start_line_num + i
        if line_num in translated_map:
            result.append(translated_map[line_num])
        else:
            result.append(orig_line)
            missing_count += 1

    if missing_count > 0:
        print(f"  ⚠ 有 {missing_count} 行未在 AI 返回中匹配到行号，已保留原文")

    return result


def translate_file(client: OpenAI, src_path: str, dst_path: str) -> None:
    """
    翻译单个源文件。

    读取文件 → 分块翻译 → 写入目标文件。
    """
    print(f"\n{'='*60}")
    print(f"📖 源文件: {src_path}")
    print(f"📝 目标文件: {dst_path}")

    # 读取源文件
    with open(src_path, "r", encoding="utf-8") as f:
        original_lines = f.readlines()

    # 去除末尾可能的空行尾符，保留每行末尾的换行符信息
    # 翻译时以 "内容" 发送，最后补回换行符
    stripped_lines = [line.rstrip("\n").rstrip("\r") for line in original_lines]
    total_lines = len(stripped_lines)
    print(f"📊 总行数: {total_lines}")

    if total_lines == 0:
        print("⚠ 文件为空，跳过。")
        return

    # 分块
    chunks: list[tuple[int, int]] = [] # (start_index, end_index)
    for start in range(0, total_lines, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE, total_lines)
        chunks.append((start, end))

    total_chunks = len(chunks)
    print(f"📦 分为 {total_chunks} 个批次（每批最多 {CHUNK_SIZE} 行）")

    # 逐块翻译，结果存入 buffer
    buffer: list[str] = []
    for chunk_idx, (start, end) in enumerate(chunks):
        chunk_lines = stripped_lines[start:end]
        start_line_num = start + 1 # 行号从 1 开始

        translated_chunk = translate_chunk(
            client=client,
            lines=chunk_lines,
            start_line_num=start_line_num,
            chunk_index=chunk_idx,
            total_chunks=total_chunks,
        )

        # 拼接回 buffer
        buffer.extend(translated_chunk)

        # 请求间隔
        if chunk_idx < total_chunks - 1:
            time.sleep(REQUEST_INTERVAL)

    # 确保行数一致
    if len(buffer) != total_lines:
        print(f"⚠ 行数不一致！原始 {total_lines} 行，翻译后 {len(buffer)} 行。"
              f"将使用原始行数截断或填充。")
        if len(buffer) > total_lines:
            buffer = buffer[:total_lines]
        else:
            buffer.extend(original_lines[len(buffer):])

    # 补回换行符：保持与原文件一致
    final_lines = []
    for i, line in enumerate(buffer):
        if i < len(original_lines) and original_lines[i].endswith("\n"):
            final_lines.append(line + "\n")
        else:
            final_lines.append(line)

    # 创建输出目录
    dst_dir = os.path.dirname(dst_path)
    if dst_dir:
        os.makedirs(dst_dir, exist_ok=True)

    # 备份原文件（可选）
    if BACKUP_ORIGINAL:
        backup_path = dst_path + ".bak"
        if os.path.exists(dst_path):
            import shutil
            shutil.copy2(dst_path, backup_path)
            print(f"💾 已备份原文件到: {backup_path}")

    # 写入目标文件
    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(final_lines)

    print(f"✅ 翻译完成！已写入: {dst_path}")


def main():
    """主入口"""
    if not TRANSLATION_TASKS:
        print("❌ TRANSLATION_TASKS 列表为空，请配置要翻译的文件。")
        sys.exit(1)

    print("=" * 60)
    print("🔧 代码翻译工具 - Code Translator")
    print(f"🌐 API: {API_BASE_URL}")
    print(f"🤖 模型: {MODEL_NAME}")
    print(f"🔀 方向: {SOURCE_LANG} → {TARGET_LANG}")
    print(f"📋 任务数: {len(TRANSLATION_TASKS)}")
    print(f"📦 批次大小: {CHUNK_SIZE} 行/次")
    print("=" * 60)

    client = create_client()

    success_count = 0
    fail_count = 0

    for idx, (src, dst) in enumerate(TRANSLATION_TASKS, 1):
        if not os.path.isfile(src):
            print(f"\n❌ [任务 {idx}/{len(TRANSLATION_TASKS)}] "
                  f"源文件不存在: {src}")
            fail_count += 1
            continue

        try:
            translate_file(client, src, dst)
            success_count += 1
        except Exception as e:
            print(f"\n❌ [任务 {idx}] 翻译失败: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print(f"\n{'='*60}")
    print(f"🏁 全部完成！成功: {success_count}, 失败: {fail_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
