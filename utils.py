# coding = utf-8
# Arch   = manyArch
#
# @File name:       utils.py
# @brief:           General functions
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
    "folders": [],                       # list[str] List of folder paths
    "font_scale": 1.0,                   # float Font size scaling
    "dark_mode": True,                   # bool Dark mode enabled
    'height_value': 768,                 # int
    'width_value': 1366,                 # int
    'font_family': 'Consolas',           # str
    'line_wrap_mode': True,              # bool
    'supported_extensions': DEFAULT_EXT, # list[str] List of supported file extensions (displayed in file tree), must include at least the content of DEFAULT_EXT
    'runnable_extensions': DEFAULT_EXT,  # list[str] List of runnable file extensions (can be executed), must include at least the content of DEFAULT_EXT
    'syntax_highlight_mode': 'auto',     # Syntax highlighting mode: enum 'auto', 'ps1', 'bash', 'command', 'none'
    'auto_run_scripts': [],              # list[str] List of script paths to auto-run on startup
    'auto_minimize_to_tray': False,      # bool Whether to auto-minimize to system tray on startup
    'language': 'en',                    # str UI language code
    'api': {                             # dict API server configuration
        'enabled': True,                 # bool Whether to enable the HTTP API server on startup
        'bind_ip': '127.0.0.1',          # str IP address to bind the API server
        'bind_port': 13025,              # int Port to bind the API server
        'auth_token': ''                 # str Bearer token for authentication (empty = no auth)
    }
}


# Parse comments in JSON
def load_json_with_comments(filepath):
    if not os.path.exists(filepath):
        return _default_config
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL) # Remove block comments /* ... */
    content = re.sub(r'//.*', '', content)                       # Remove line comments // ...
    try:
        config = json.loads(content)
        return {**_default_config, **config}
    except Exception as e:
        print(f"Configuration file parsing failed: {e}")
        return _default_config


# Store configuration
def save_json_with_comments(filepath, config):
    data = {**_default_config, **config}
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    comment = "// PsLauncher program configuration file\n" # Include a descriptive comment when writing
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(comment + json_str)


# Syntax highlighter
class ScriptHighlighter(QSyntaxHighlighter):

    def __init__(self, document, ext, isdark, syntax_mode='auto'):
        super().__init__(document)
        self.rules = []

        # If syntax mode is 'auto', select highlighting mode based on file extension
        if syntax_mode == 'auto':
            # Select highlighting mode based on file extension
            if ext == '.ps1':
                syntax_mode = 'ps1'
            elif ext == '.bat' or ext == '.cmd':
                syntax_mode = 'command'
            elif ext == '.sh':
                syntax_mode = 'bash'
            else:
                # For other files, attempt to select the closest highlighting mode based on common extensions
                if ext in ['.json', '.yaml', '.yml', '.xml', '.html', '.htm']:
                    # These files have similar structures, use ps1 highlighting as an approximation
                    syntax_mode = 'ps1'
                elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']:
                    # Programming language file, use bash coloring as an approximation (has similar control structures)
                    syntax_mode = 'bash'
                else:
                    # Unknown file type, no coloring
                    syntax_mode = 'none'

        # If syntax mode is 'none', do not create any syntax rules
        if syntax_mode == 'none':
            return

        # Define color scheme similar to VS Code Dark theme
        blue = "#569CD6" if isdark else "#008CFF"
        orange = "#CE9178" if isdark else "#893412"
        green = "#6A9955" if isdark else "#2F7D0A"
        lightblue = "#9CDCFE" if isdark else "#0B6B9F"

        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor(blue)) # Blue
        keyword_fmt.setFontWeight(QFont.Bold)

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor(orange)) # Orange

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor(green)) # Green

        var_fmt = QTextCharFormat()
        var_fmt.setForeground(QColor(lightblue)) # Light blue

        # PowerShell syntax rules
        if syntax_mode == 'ps1':
            keywords = ["if", "else", "elseif", "switch", "while", "for", "foreach", "in", "return", "function", "param", "Write-Host", "Write-Output", "try", "catch"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'\$[A-Za-z0-9_]+'), var_fmt)) # Variable
            self.rules.append((QRegExp(r'".*"'), string_fmt))         # Double-quoted string
            self.rules.append((QRegExp(r"'.*'"), string_fmt))         # Single-quoted string
            self.rules.append((QRegExp(r'#.*'), comment_fmt))         # Single-line comment

        # Batch/Command syntax rules
        elif syntax_mode == 'command':
            keywords = ["echo", "set", "if", "else", "exist", "goto", "call", "exit", "pause", "start"]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b', Qt.CaseInsensitive), keyword_fmt))
            self.rules.append((QRegExp(r'%[A-Za-z0-9_]+%'), var_fmt))   # Variable
            self.rules.append((QRegExp(r'".*"'), string_fmt))           # String
            self.rules.append((QRegExp(r'(?i)^::.*'), comment_fmt))     # :: Comment
            self.rules.append((QRegExp(r'(?i)\brem\b.*'), comment_fmt)) # REM Comment

        # Bash syntax rules
        elif syntax_mode == 'bash':
            # 1. Keywords (Note: Bash keywords are usually lowercase and case-sensitive)
            keywords = [
                "if", "then", "else", "elif", "fi", "case", "esac", "for", "do", "done", "while", "until", "function", "return", "exit", "echo", "printf", "read", "set", "unset", "export", "source"
            ]
            for kw in keywords:
                self.rules.append((QRegExp(r'\b' + kw + r'\b'), keyword_fmt))

            # 2. Special symbol keywords (e.g., [ ] [[ ]] (( )))
            # Note: Use \s or line start/end anchors to avoid matching symbols within strings
            self.rules.append((QRegExp(r'(^|\s)\[($|\s)'), keyword_fmt))   # [ Command
            self.rules.append((QRegExp(r'(^|\s)\]($|\s)'), keyword_fmt))   # ] Command
            self.rules.append((QRegExp(r'(^|\s)\[\[($|\s)'), keyword_fmt)) # [[ Keyword
            self.rules.append((QRegExp(r'(^|\s)\]\]($|\s)'), keyword_fmt)) # ]] Keyword
            self.rules.append((QRegExp(r'(^|\s)\(\(($|\s)'), keyword_fmt)) # (( Arithmetic expansion
            self.rules.append((QRegExp(r'(^|\s)\)\)($|\s)'), keyword_fmt)) # )) Arithmetic expansion

            # 3. Variables: $var or ${var}
            self.rules.append((QRegExp(r'\$[A-Za-z0-9_]+'), var_fmt))     # Plain variable $var
            self.rules.append((QRegExp(r'\$\{[A-Za-z0-9_]+\}'), var_fmt)) # Brace variable ${var}

            # 4. Strings
            self.rules.append((QRegExp(r'".*"'), string_fmt)) # Double-quoted string
            self.rules.append((QRegExp(r"'.*'"), string_fmt)) # Single-quoted string
            self.rules.append((QRegExp(r'`.*`'), string_fmt)) # Backtick command substitution

            # 5. Comments: # start (Note: Bash has no multi-line comments, only single-line here)
            self.rules.append((QRegExp(r'#.*'), comment_fmt))

    def highlightBlock(self, text):
        for regex, fmt in self.rules:
            index = regex.indexIn(text)
            while index >= 0:
                length = regex.matchedLength()
                self.setFormat(index, length, fmt)
                index = regex.indexIn(text, index + length)
