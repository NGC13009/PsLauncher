# coding = utf-8
# Arch   = manyArch
#
# @File name:       check_i18n_coverage.py
# @brief:           i18n 双向覆盖率检查脚本
#
#                   检查项：
#                   1. 所有语言文件之间的键集合是否一致（互相覆盖）
#                   2. i18n 中定义的键是否在代码中使用了（前向覆盖）
#                   3. 代码中 tr() 调用的键是否在 i18n 中定义了（后向覆盖）
#
#                   用法：
#                       python check_i18n_coverage.py
#
# @attention:       None
# @Author:          wyb
# @History:         2026-06-30		Create

import os
import re
import sys


def color(text, code):
    return f"\033[{code}m{text}\033[0m"


def red(text):
    return color(text, 91)


def green(text):
    return color(text, 92)


def yellow(text):
    return color(text, 93)


def cyan(text):
    return color(text, 96)


# ============================================================
# 语言文件读取
# ============================================================


def get_language_keys():
    """导入所有语言模块并获取键集合"""
    import i18n.en as en_mod
    import i18n.zh_CN as zh_mod

    return {
        "en": set(en_mod.messages.keys()),
        "zh_CN": set(zh_mod.messages.keys()),
    }


# ============================================================
# 源代码扫描
# ============================================================


def get_source_files(root_dir="."):
    """获取需要扫描的 Python 源文件列表

    需要排除：
    - test/ 目录（测试代码，不是程序本体）
    - i18n/ 目录（语言定义文件，不是 tr() 的调用者）
    - 自动生成的脚本（source_ico.py, get_help_page.py, get_ico.py, code_translator.py）
    - 自身（check_i18n_coverage.py）
    """
    exclude_dirs = {"test", "__pycache__", ".git", ".github", "exe", "cn", ".vscode"}
    exclude_files = {
        "source_ico.py",
        "get_help_page.py",
        "get_ico.py",
        "code_translator.py",
        "check_i18n_coverage.py",
    }

    files = []
    for root, dirs, fnames in os.walk(root_dir):
        # 修改 dirs 就地过滤
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

        rel_root = os.path.relpath(root, root_dir)
        if rel_root.startswith("i18n"):
            # 跳过 i18n 目录及其子目录
            continue

        for fname in fnames:
            if fname.endswith(".py") and fname not in exclude_files:
                files.append(os.path.join(root, fname))

    return files


def extract_tr_keys(filepath):
    """从文件中提取所有 tr() 调用的键名字面量"""
    keys = set()
    # 匹配 tr("key") 或 tr('key')，双引号/单引号都支持
    pattern = re.compile(r'tr\s*\(\s*([\'"])(.+?)\1')

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        for match in pattern.finditer(content):
            keys.add(match.group(2))
    except Exception as e:
        print(f"  {red('ERROR')}: 无法读取 {filepath}: {e}")

    return keys


# ============================================================
# 主逻辑
# ============================================================


def main():
    print()
    print(cyan("=" * 60))
    print(cyan("  i18n 双向覆盖率检查"))
    print(cyan("=" * 60))
    print()

    # ----------------------------------------------------------
    # 1. 获取语言文件键集合
    # ----------------------------------------------------------
    print(cyan("▶ 第1步：加载语言文件..."))
    lang_keys = get_language_keys()

    for lang, keys in lang_keys.items():
        print(f"    {lang}: {len(keys)} 个键")
    print()

    # 并集 = 至少在某个语言中出现的键
    all_i18n_keys = set()
    for keys in lang_keys.values():
        all_i18n_keys.update(keys)

    # 交集 = 在所有语言中都出现的键
    all_keys_intersection = None
    for keys in lang_keys.values():
        if all_keys_intersection is None:
            all_keys_intersection = keys.copy()
        else:
            all_keys_intersection &= keys

    # ----------------------------------------------------------
    # 2. 语言间键一致性检查
    # ----------------------------------------------------------
    print(cyan("▶ 第2步：语言间键一致性检查..."))
    consistent = True
    for lang, keys in lang_keys.items():
        missing = all_i18n_keys - keys
        if missing:
            consistent = False
            print(f"    {red('✗')} [{lang}] 缺少以下键 ({len(missing)} 个):")
            for key in sorted(missing):
                print(f"        - {key}")

    if consistent:
        print(f"    {green('✓')} 所有语言文件的键集合完全一致 "
              f"(共 {len(all_keys_intersection)} 个公共键)")
    else:
        print(f"    {red('✗')} 存在不一致！")

    print()

    # ----------------------------------------------------------
    # 3. 扫描源代码中的 tr() 调用
    # ----------------------------------------------------------
    print(cyan("▶ 第3步：扫描源代码中的 tr() 调用..."))

    source_files = get_source_files()
    code_keys = set()
    file_key_map = {}

    for filepath in source_files:
        keys = extract_tr_keys(filepath)
        if keys:
            relpath = os.path.relpath(filepath, ".")
            file_key_map[relpath] = keys
            code_keys.update(keys)

    print(f"    共扫描 {len(source_files)} 个源文件")
    print(f"    其中 {len(file_key_map)} 个文件包含 tr() 调用")
    print(f"    代码中共使用了 {len(code_keys)} 个不同的键")
    print()

    if file_key_map:
        for fpath, keys in sorted(file_key_map.items()):
            print(f"      {fpath}: {len(keys)} 个键")
        print()

    # ----------------------------------------------------------
    # 4. 前向覆盖检查：i18n 定义的键 → 代码中是否使用
    # ----------------------------------------------------------
    print(cyan("▶ 第4步：前向覆盖检查 (i18n → 代码)"))

    i18n_in_code = all_i18n_keys & code_keys
    unused_keys = all_i18n_keys - code_keys

    if unused_keys:
        print(f"    {red('✗')} {len(unused_keys)} 个键在 i18n 中定义但未在代码中使用:")
        for key in sorted(unused_keys):
            print(f"        - {key}")
    else:
        print(f"    {green('✓')} 前向覆盖完全：所有 i18n 键均在代码中使用过")

    print()

    # ----------------------------------------------------------
    # 5. 后向覆盖检查：代码中使用的键 → i18n 是否有定义
    # ----------------------------------------------------------
    print(cyan("▶ 第5步：后向覆盖检查 (代码 → i18n)"))

    # 5a. 完全缺失：在任何语言中都没定义
    missing_in_all = code_keys - all_i18n_keys

    if missing_in_all:
        print(f"    {red('✗')} {len(missing_in_all)} 个键在代码中使用，"
              f"但未在任何语言文件中定义:")
        for key in sorted(missing_in_all):
            print(f"        - {key}")
    else:
        print(f"    {green('✓')} 所有代码中使用的键均在 i18n 中有定义")

    # 5b. 部分缺失：在某个语言中存在，但在另一个语言中不存在
    missing_in_some_lang = {}
    for lang, lang_key_set in lang_keys.items():
        # 只报告那些至少在某个语言中有定义的键
        missing = (code_keys - lang_key_set) & all_i18n_keys
        if missing:
            missing_in_some_lang[lang] = missing

    if missing_in_some_lang:
        print()
        print(f"    {yellow('⚠')} 以下语言缺少某些键 (已在其他语言中存在):")
        for lang, missing in sorted(missing_in_some_lang.items()):
            print(f"    [{lang}] 缺少 {len(missing)} 个:")
            for key in sorted(missing):
                print(f"        - {key}")
    else:
        # 兼容第2步结果：如果第2步已经查出语言间不一致，这里就不重复表扬了
        if consistent:
            print(f"    {green('✓')} 所有语言均包含代码中使用的全部键")

    print()

    # ----------------------------------------------------------
    # 6. 汇总
    # ----------------------------------------------------------
    print(cyan("=" * 60))
    print(cyan("  汇总"))
    print(cyan("=" * 60))
    print()

    total_i18n_keys = len(all_i18n_keys)
    total_code_keys = len(code_keys)
    forward_used = len(i18n_in_code)
    backward_covered = len(code_keys & all_i18n_keys)

    forward_ratio = forward_used / total_i18n_keys * 100 if total_i18n_keys else 0
    backward_ratio = backward_covered / total_code_keys * 100 if total_code_keys else 0

    print(f"    语言文件定义键数 (并集):     {total_i18n_keys}")
    print(f"    各语言公共键数:              {len(all_keys_intersection)}")
    for lang, keys in lang_keys.items():
        print(f"    {lang} 键数:                   {len(keys)}")
    print(f"    代码中使用的键数:            {total_code_keys}")
    print(f"    前向覆盖率 (i18n→代码):      {forward_ratio:.1f}%"
          f" ({forward_used}/{total_i18n_keys})")
    print(f"    后向覆盖率 (代码→i18n):      {backward_ratio:.1f}%"
          f" ({backward_covered}/{total_code_keys})")
    print()

    # 综合判断
    has_issues = (not consistent or bool(unused_keys) or bool(missing_in_all) or bool(missing_in_some_lang))

    if has_issues:
        print(f"    {red('✗')} 检查发现问题，请查看上方详情。")
        issues = []
        if not consistent:
            issues.append("语言间键不一致")
        if unused_keys:
            issues.append(f"未使用翻译键 ({len(unused_keys)} 个)")
        if missing_in_all:
            issues.append(f"代码中使用但未定义 ({len(missing_in_all)} 个)")
        if missing_in_some_lang:
            issues.append(f"部分语言缺少键 ({sum(len(v) for v in missing_in_some_lang.values())} 个)")
        for issue in issues:
            print(f"      - {issue}")
        print()
        return 1
    else:
        print(f"    {green('✓')} 检查通过！所有 i18n 键双向覆盖完整。")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
