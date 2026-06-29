# coding = utf-8
# Arch   = manyArch
#
# @File name:       generate_test_coverage_doc.py
# @brief:           扫描 test/ 目录下所有 test_*.py 文件，
#                   提取每个测试类和测试方法的 docstring，
#                   生成 TEST_COVERAGE.md 文档
# @attention:       可在任意位置执行，默认输出到同目录的 TEST_COVERAGE.md
# @Authors:         wyb
# @History:         2026-06-10   Create

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def extract_test_info_from_file(filepath: str) -> Optional[Dict]:
    """
    从单个测试文件中提取测试类信息

    :param filepath: .py 文件路径
    :return: {
        "filename": str,
        "brief": str,          # 文件级 @brief 说明
        "classes": [
            {
                "name": str,
                "doc": str,
                "methods": [
                    {"name": str, "doc": str},
                    ...
                ]
            },
            ...
        ]
    } 或 None
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return None

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    # 从文件头注释提取 @brief
    file_brief = ""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            doc = node.value.value
            if isinstance(doc, str):
                # 查找 @brief: 行
                for line in doc.split("\n"):
                    if "@brief:" in line and "ignore" not in line.lower():
                        file_brief = line.split("@brief:", 1)[1].strip()
                        break
        break      # 只看第一个节点（模块 docstring）

    classes = []
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # 跳过非测试辅助类（不以 Test 开头）
        if not node.name.startswith("Test"):
            continue

        class_doc = ast.get_docstring(node) or ""
        # 取 docstring 第一行作为摘要
        class_doc_first_line = class_doc.split("\n")[0].strip()

        methods = []
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            # 跳过非测试方法 (setup/teardown/私有方法)
            if not item.name.startswith("test_"):
                continue
            method_doc = ast.get_docstring(item) or ""
            method_doc_first_line = method_doc.split("\n")[0].strip()
            methods.append({
                "name": item.name,
                "doc": method_doc_first_line,
            })

        if methods:
            classes.append({
                "name": node.name,
                "doc": class_doc_first_line,
                "methods": methods,
            })

    if not classes:
        return None

    return {
        "filename": os.path.basename(filepath),
        "brief": file_brief,
        "classes": classes,
    }


def generate_markdown(test_dir: str, output_path: str) -> None:
    """
    扫描 test_dir 下所有 test_*.py，生成 Markdown 文档

    :param test_dir: 测试文件目录
    :param output_path: 输出 .md 文件路径
    """
    test_files = sorted([f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")])

    results = []
    for fname in test_files:
        fpath = os.path.join(test_dir, fname)
        info = extract_test_info_from_file(fpath)
        if info:
            results.append(info)

    # 统计总用例数
    total_methods = sum(len(c["methods"]) for r in results for c in r["classes"])
    total_classes = sum(len(r["classes"]) for r in results)

    # 生成 Markdown
    lines: List[str] = []
    lines.append("# TrkGUI 自动测试覆盖文档")
    lines.append("")
    lines.append("> 由 `generate_test_coverage_doc.py` 自动生成，请勿编辑本文件，应该使用脚本从自动测试直接生成本说明文档。如需修改，请修改测试样例的对应说明。")
    lines.append(f"编译日期：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")        # 类似于 2025-01-15 14:30:25
    lines.append("重新生成：执行 `python app/TrkGUI/test/generate_test_coverage_doc.py`")
    lines.append("")
    lines.append(f"**测试文件数**：{len(results)} | **测试类数**：{total_classes} | **测试用例数**：{total_methods}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 目录
    lines.append("## 目录")
    lines.append("")
    # for r in results:
    #     fname = r["filename"]
    #     brief = r["brief"]
    #     lines.append(f"- [{fname}](#{_anchor(fname)}) — {brief}")
    lines.append("> [TOC]")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 各文件详情
    total_test_num = 0
    for r in results:
        fname = r["filename"]
        brief = r["brief"]
        lines.append(f"## {fname}")
        lines.append("")
        if brief:
            lines.append(f"> {brief}")
            lines.append("")

        for cls in r["classes"]:
            lines.append(f"### {cls['name']}")
            if cls["doc"]:
                lines.append(f"\n{cls['doc']}")
                lines.append("")
            for i, m in enumerate(cls["methods"], 1):
                doc_text = m["doc"] if m["doc"] else "（无说明）"
                lines.append(f"{i}. `{m['name']}` — {doc_text}")
                total_test_num +=1
            lines.append("")

        # lines.append("---")
        # lines.append("")

    # 脚注
    lines.append(f"共 {total_methods} 个**测试用例**，{total_classes} 个**测试类**，生成了 {total_test_num} 行的测试任务说明。")
    lines.append("")
    lines.append("> 重新生成：`python app/TrkGUI/test/generate_test_coverage_doc.py`")
    lines.append("> 注意⚠：统计方法基于Python的AST分析，不一定完全精确。总数目可能和pytest的pass数目略有不同。")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[OK] 已生成 {output_path}")
    print(f"     文件数: {len(results)}  类数: {total_classes}  用例数: {total_methods}")


def _anchor(text: str) -> str:
    """生成 Markdown 锚点（简化版）"""
    return text.replace(".py", "").replace("_", "-").lower()


if __name__ == "__main__":
    # 自动定位 test 目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "TEST_COVERAGE.md")
    generate_markdown(script_dir, output_path)
