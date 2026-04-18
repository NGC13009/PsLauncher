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

DEFAULT_EXT = ['.ps1', '.bat', '.sh']
CONFIG_FILE = "launcher_config.json"

_default_config = {
    "folders": [],                       # list[str] 文件夹路径的列表
    "font_scale": 1.0,                   # float 字号缩放
    "dark_mode": True,                   # bool 是否黑夜模式
    'height_value': 768,                 # int
    'width_value': 1366,                 # int
    'font_family': 'Consolas',           # str
    'line_wrap_mode': True,              # bool
    'supported_extensions': DEFAULT_EXT, # list[str] 支持的文件后缀列表（在文件树中显示）, 必须至少包含 DEFAULT_EXT 的内容
    'runnable_extensions': DEFAULT_EXT,  # list[str] 可运行的文件后缀列表（可以执行）, 必须至少包含 DEFAULT_EXT 的内容
    'syntax_highlight_mode': 'auto'      # 语法着色模式：枚举 'auto', 'ps1', 'bash', 'command', 'none'
}


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
        print(f"配置文件解析失败: {e}")
        return _default_config


# 存储配置
def save_json_with_comments(filepath, config):
    data = {**_default_config, **config}
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    comment = "// PsLauncher 程序配置文件\n" # 写入时附带一条说明性注释
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(comment + json_str)


# 语法着色器
class ScriptHighlighter(QSyntaxHighlighter):

    def __init__(self, document, ext, isdark, syntax_mode='auto'):
        super().__init__(document)
        self.rules = []

        # 如果语法模式为'auto'，则根据文件后缀选择着色模式
        if syntax_mode == 'auto':
            # 根据文件后缀选择着色模式
            if ext == '.ps1':
                syntax_mode = 'ps1'
            elif ext == '.bat' or ext == '.cmd':
                syntax_mode = 'command'
            elif ext == '.sh':
                syntax_mode = 'bash'
            else:
                # 对于其他文件，尝试根据常见后缀选择最接近的着色模式
                if ext in ['.json', '.yaml', '.yml', '.xml', '.html', '.htm']:
                    # 这些文件有类似的结构，使用ps1着色作为近似
                    syntax_mode = 'ps1'
                elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']:
                    # 编程语言文件，使用bash着色作为近似（有类似的控制结构）
                    syntax_mode = 'bash'
                else:
                    # 其他未知文件类型，不着色
                    syntax_mode = 'none'

        # 如果语法模式为'none'，则不创建任何语法规则
        if syntax_mode == 'none':
            return

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
        if syntax_mode == 'ps1':
            keywords = ["if", "else", "elseif", "switch", "while", "for", "foreach", "in", "return", "function", "param", "Write-Host", "Write-Output", "try", "catch"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'\$[A-Za-z0-9_]+'), var_fmt)) # 变量
            self.rules.append((QRegExp(r'".*"'), string_fmt))         # 双引号字符串
            self.rules.append((QRegExp(r"'.*'"), string_fmt))         # 单引号字符串
            self.rules.append((QRegExp(r'#.*'), comment_fmt))         # 单行注释

        # Batch/Command 语法规则
        elif syntax_mode == 'command':
            keywords = ["echo", "set", "if", "else", "exist", "goto", "call", "exit", "pause", "start"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'%[A-Za-z0-9_]+%'), var_fmt))   # 变量
            self.rules.append((QRegExp(r'".*"'), string_fmt))           # 字符串
            self.rules.append((QRegExp(r'(?i)^::.*'), comment_fmt))     # :: 注释
            self.rules.append((QRegExp(r'(?i)\brem\b.*'), comment_fmt)) # REM 注释

        # Bash 语法规则
        elif syntax_mode == 'bash':
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
