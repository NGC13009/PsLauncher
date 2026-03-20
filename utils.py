# coding = utf-8
# Arch   = manyArch
#
# @File name:       utils.py
# @brief:           通用函数
# @attention:       None
# @Author:          ngc13009
# @History:         2026-03-17		Create

import json
import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os

_default_config = {"folders": [], "font_scale": 1.0, "dark_mode": True, 'height_value': 768, 'width_value': 1366, 'font_family': 'Consolas'}


# 解析JSON中的注释
def load_json_with_comments(filepath):
    if not os.path.exists(filepath):
        return _default_config
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL) # 移除块注释 /* ... */
    content = re.sub(r'//.*', '', content)                       # 移除行注释 // ...
    try:
        config = json.loads(content)
        return {**_default_config, **config}
    except Exception as e:
        print(f"Configuration file parsing failed: {e}")
        return _default_config


# 存储配置
def save_json_with_comments(filepath, config):
    data = {**_default_config, **config}
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    comment = "// PsLauncher program configuration file.\n" # Write with an explanatory comment
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(comment + json_str)


# 语法着色器
class ScriptHighlighter(QSyntaxHighlighter):

    def __init__(self, document, ext, isdark):
        super().__init__(document)
        self.rules = []

        # 定义类似 VS Code Dark 主题的配色
        blue = "#569CD6" if isdark else "#008CFF"
        orange = "#CE9178" if isdark else "#893412"
        green = "#6A9955" if isdark else "#2F7D0A"
        lightblue = "#9CDCFE" if isdark else "#0B6B9F"

        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor(blue)) # 蓝色
        keyword_fmt.setFontWeight(QFont.Bold)

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor(orange)) # 橙色

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor(green)) # 绿色

        var_fmt = QTextCharFormat()
        var_fmt.setForeground(QColor(lightblue)) # 浅蓝

        # PowerShell 语法规则
        if ext == '.ps1':
            keywords = ["if", "else", "elseif", "switch", "while", "for", "foreach", "in", "return", "function", "param", "Write-Host", "Write-Output", "try", "catch"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'\$[A-Za-z0-9_]+'), var_fmt)) # 变量
            self.rules.append((QRegExp(r'".*"'), string_fmt))         # 双引号字符串
            self.rules.append((QRegExp(r"'.*'"), string_fmt))         # 单引号字符串
            self.rules.append((QRegExp(r'#.*'), comment_fmt))         # 单行注释

        # Batch 语法规则
        elif ext == '.bat' or ext == '.cmd':
            keywords = ["echo", "set", "if", "else", "exist", "goto", "call", "exit", "pause", "start"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'%[A-Za-z0-9_]+%'), var_fmt))   # 变量
            self.rules.append((QRegExp(r'".*"'), string_fmt))           # 字符串
            self.rules.append((QRegExp(r'(?i)^::.*'), comment_fmt))     # :: 注释
            self.rules.append((QRegExp(r'(?i)\brem\b.*'), comment_fmt)) # REM 注释

        # Bash 语法规则
        elif ext == '.sh':
            # 1. 关键字（注意：Bash 关键字通常为小写，区分大小写）
            keywords = [
                "if", "then", "else", "elif", "fi", "case", "esac", "for", "do", "done", "while", "until", "function", "return", "exit", "echo", "printf", "read", "set", "unset", "export", "source"
            ]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b'), keyword_fmt))

            # 2. 特殊符号关键字（如 [ ] [[ ]] (( ))）
            # 注意：使用 \s 或行首/行尾锚定，避免误匹配字符串中的符号
            self.rules.append((QRegExp(r'(^|\s)\[($|\s)'), keyword_fmt))   # [ 命令
            self.rules.append((QRegExp(r'(^|\s)\]($|\s)'), keyword_fmt))   # ] 命令
            self.rules.append((QRegExp(r'(^|\s)\[\[($|\s)'), keyword_fmt)) # [[ 关键字
            self.rules.append((QRegExp(r'(^|\s)\]\]($|\s)'), keyword_fmt)) # ]] 关键字
            self.rules.append((QRegExp(r'(^|\s)\(\(($|\s)'), keyword_fmt)) # (( 算术扩展
            self.rules.append((QRegExp(r'(^|\s)\)\)($|\s)'), keyword_fmt)) # )) 算术扩展

            # 3. 变量：$var 或 ${var}
            self.rules.append((QRegExp(r'\$[A-Za-z0-9_]+'), var_fmt))     # 普通变量 $var
            self.rules.append((QRegExp(r'\$\{[A-Za-z0-9_]+\}'), var_fmt)) # 花括号变量 ${var}

            # 4. 字符串
            self.rules.append((QRegExp(r'".*"'), string_fmt)) # 双引号字符串
            self.rules.append((QRegExp(r"'.*'"), string_fmt)) # 单引号字符串
            self.rules.append((QRegExp(r'`.*`'), string_fmt)) # 反引号命令替换

            # 5. 注释：# 开头（注意：Bash 没有多行注释，这里只处理单行）
            self.rules.append((QRegExp(r'#.*'), comment_fmt))

    def highlightBlock(self, text):
        for regex, fmt in self.rules:
            index = regex.indexIn(text)
            while index >= 0:
                length = regex.matchedLength()
                self.setFormat(index, length, fmt)
                index = regex.indexIn(text, index + length)
