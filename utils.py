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

# Field comment map for self-documenting JSON config
_COMMENT_MAP = {
    "folders": "List of folder paths to scan for scripts",
    "font_scale": "Font size scaling factor (e.g., 1.5 = 150%)",
    "dark_mode": "Enable dark mode theme",
    "height_value": "Window height in pixels",
    "width_value": "Window width in pixels",
    "font_family": "Font family for editor and terminal",
    "line_wrap_mode": "Enable automatic line wrapping",
    "supported_extensions": "File extensions to display in the script tree",
    "runnable_extensions": "File extensions that can be executed",
    "syntax_highlight_mode": "Syntax highlighting mode: auto, ps1, bash, command, none",
    "auto_run_scripts": "List of script paths to auto-run on startup",
    "auto_minimize_to_tray": "Auto-minimize to system tray on startup",
    "language": "UI language code (e.g., en, zh_CN)",
    "api": "HTTP API server configuration",
    "api.enabled": "Whether to enable the HTTP API server",
    "api.bind_ip": "IP address to bind the API server (127.0.0.1 = localhost only)",
    "api.bind_port": "Port number for the API server",
    "api.auth_token": "Bearer token for API authentication (empty = no auth)",
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


def _add_inline_comments(json_str):
    """Add inline // comments to each JSON key-value line based on _COMMENT_MAP."""
    lines = json_str.split('\n')
    result_lines = []
    path_stack = []  # Track nested object path, e.g. ["api"]

    for line in lines:
        stripped = line.strip()

        # Track entering/leaving nested objects (only api dict at top level)
        # Match '"key": {' style lines for top-level objects
        obj_match = re.match(r'^(\s*)"(\w+)"\s*:\s*\{\s*$', line)
        if obj_match:
            indent = obj_match.group(1)
            key = obj_match.group(2)
            comment = _COMMENT_MAP.get(key, "")
            if comment:
                # Check if the next non-empty line exists (meaning there are children)
                rest_lines = lines[lines.index(line) + 1:]
                next_non_empty = next((l for l in rest_lines if l.strip()), None)
                if next_non_empty and next_non_empty.strip() != '}':
                    line = f"{indent}\"{key}\": {{  // {comment}"
                else:
                    line = f"{indent}\"{key}\": {{  // {comment}"
            path_stack.append(key)
            result_lines.append(line)
            continue

        # Match closing brace '}' - pop from path stack
        if stripped == '}' or stripped.startswith('}'):
            if path_stack:
                path_stack.pop()
            result_lines.append(line)
            continue

        # Match key-value lines: "key": value, (possibly at end or nested)
        kv_match = re.match(r'^(\s*)"(\w+)"\s*:\s*(.*)$', line)
        if kv_match:
            indent = kv_match.group(1)
            key = kv_match.group(2)
            rest = kv_match.group(3)

            # Build full path key for comment lookup
            full_key = key
            if path_stack:
                full_key = ".".join(path_stack) + "." + key

            comment = _COMMENT_MAP.get(full_key, "")
            if comment:
                # Only add comment if rest doesn't already end with one
                if '//' not in rest:
                    # Pad rest to align comments (rough alignment)
                    line = f"{indent}\"{key}\": {rest.rstrip()}  // {comment}"

        result_lines.append(line)

    return '\n'.join(result_lines)


# Store configuration
def save_json_with_comments(filepath, config):
    data = {**_default_config, **config}
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    comment = "// PsLauncher program configuration file\n" # Include a descriptive comment when writing
    json_str_with_comments = _add_inline_comments(json_str)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(comment + json_str_with_comments)


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