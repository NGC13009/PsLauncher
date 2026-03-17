# coding = utf-8
# Arch   = manyArch
#
# @File name:       utils.py
# @brief:           Common utility functions
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


# Parse JSON with comments
def load_json_with_comments(filepath):
    if not os.path.exists(filepath):
        return {"folders": [], "font_scale": 1.0, "dark_mode": True}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL) # Remove block comments /* ... */
    content = re.sub(r'//.*', '', content)                       # Remove line comments // ...
    try:
        config = json.loads(content)
                                                                 # Backward compatibility: ensure necessary fields
        if "font_scale" not in config:
            config["font_scale"] = 1.0
        if "dark_mode" not in config:
            config["dark_mode"] = True
        return config
    except Exception as e:
        print(f"Configuration file parsing failed: {e}")
        return {"folders": [], "font_scale": 1.0, "dark_mode": True}


# Store configuration
def save_json_with_comments(filepath, data):
    if "font_scale" not in data:
        data["font_scale"] = 1.0
    if "dark_mode" not in data:
        data["dark_mode"] = True
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    comment = "// PsLauncher program configuration file: configuration file supports comments. You can manually add folder paths to scan here.\n" # Write with an explanatory comment
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(comment + json_str)


# Syntax highlighter
class ScriptHighlighter(QSyntaxHighlighter):

    def __init__(self, document, ext):
        super().__init__(document)
        self.rules = []

        # Define color scheme similar to VS Code Dark theme
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#569CD6")) # Blue
        keyword_fmt.setFontWeight(QFont.Bold)

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#CE9178")) # Orange

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#6A9955")) # Green

        var_fmt = QTextCharFormat()
        var_fmt.setForeground(QColor("#9CDCFE")) # Light blue

        # PowerShell syntax rules
        if ext == '.ps1':
            keywords = ["if", "else", "elseif", "switch", "while", "for", "foreach", "in", "return", "function", "param", "Write-Host", "Write-Output", "try", "catch"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'\$[A-Za-z0-9_]+'), var_fmt)) # Variables
            self.rules.append((QRegExp(r'".*"'), string_fmt))         # Double quoted strings
            self.rules.append((QRegExp(r"'.*'"), string_fmt))         # Single quoted strings
            self.rules.append((QRegExp(r'#.*'), comment_fmt))         # Single line comments

        # Batch syntax rules
        elif ext == '.bat' or ext == '.cmd':
            keywords = ["echo", "set", "if", "else", "exist", "goto", "call", "exit", "pause", "start"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'%[A-Za-z0-9_]+%'), var_fmt))   # Variables
            self.rules.append((QRegExp(r'".*"'), string_fmt))           # Strings
            self.rules.append((QRegExp(r'(?i)^::.*'), comment_fmt))     # :: comments
            self.rules.append((QRegExp(r'(?i)\brem\b.*'), comment_fmt)) # REM comments

        # Bash syntax rules
        elif ext == '.sh':
            # 1. Keywords (note: Bash keywords are typically lowercase, case-sensitive)
            keywords = [
                "if", "then", "else", "elif", "fi", "case", "esac", "for", "do", "done", "while", "until", "function", "return", "exit", "echo", "printf", "read", "set", "unset", "export", "source"
            ]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b'), keyword_fmt))

            # 2. Special symbol keywords (like [ ] [[ ]] (( )))
            # Note: use \s or line start/end anchors to avoid false matches inside strings
            self.rules.append((QRegExp(r'(^|\s)\[($|\s)'), keyword_fmt))   # [ command
            self.rules.append((QRegExp(r'(^|\s)\]($|\s)'), keyword_fmt))   # ] command
            self.rules.append((QRegExp(r'(^|\s)\[\[($|\s)'), keyword_fmt)) # [[ keyword
            self.rules.append((QRegExp(r'(^|\s)\]\]($|\s)'), keyword_fmt)) # ]] keyword
            self.rules.append((QRegExp(r'(^|\s)\(\(($|\s)'), keyword_fmt)) # (( arithmetic expansion
            self.rules.append((QRegExp(r'(^|\s)\)\)($|\s)'), keyword_fmt)) # )) arithmetic expansion

            # 3. Variables: $var or ${var}
            self.rules.append((QRegExp(r'\$[A-Za-z0-9_]+'), var_fmt))     # Regular variables $var
            self.rules.append((QRegExp(r'\$\{[A-Za-z0-9_]+\}'), var_fmt)) # Brace variables ${var}

            # 4. Strings
            self.rules.append((QRegExp(r'".*"'), string_fmt)) # Double quoted strings
            self.rules.append((QRegExp(r"'.*'"), string_fmt)) # Single quoted strings
            self.rules.append((QRegExp(r'`.*`'), string_fmt)) # Backtick command substitution

            # 5. Comments: # at start (note: Bash doesn't have multi-line comments, process only single line here)
            self.rules.append((QRegExp(r'#.*'), comment_fmt))

    def highlightBlock(self, text):
        for regex, fmt in self.rules:
            index = regex.indexIn(text)
            while index >= 0:
                length = regex.matchedLength()
                self.setFormat(index, length, fmt)
                index = regex.indexIn(text, index + length)