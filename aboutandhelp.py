# coding = utf-8
# Arch   = manyArch
#
# @File name:       aboutandhelp.py
# @brief:           帮助页和关于页面
# @attention:       None
# @Author:          NGC13009
# @History:         2026-03-16		Create

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from source_help_page import html_content

__version__ = "1.0.0"
__devdate__ = "2026年3月16日"
__githublink__ = "https://github.com/NGC13009/PsLauncher.git"


class PsLauncherDiag(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    def _copy_to_clipboard(self):
        """复制文本信息到剪贴板"""
        # 注意：这里我们复制的是纯文本版本，如果需要复制HTML格式需要额外处理
        plain_text = self.text_browser.toPlainText()

        clipboard = QApplication.clipboard()
        clipboard.setText(plain_text)

        # 可选：给用户一个复制成功的提示（例如改变按钮文字一秒钟）
        original_text = self.btn_copy.text()
        self.btn_copy.setText("已复制 ✓")
        self.btn_copy.repaint()

        # 这里简单的使用单Shot定时器做一个UI反馈
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.btn_copy.setText(original_text))


class AboutDialog(PsLauncherDiag):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.resize(800, 600)

        # 1. 设置布局
        layout = QVBoxLayout(self)

        # 2. 创建支持 HTML 的文本浏览器
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False) # 我们手动处理链接点击，或者设为True自动打开
        self._populate_about_content()
        layout.addWidget(self.text_browser)

        # 3. 创建按钮
        btn_layout = QVBoxLayout() # 或者用 QHBoxLayout 横向排列

        self.btn_copy = QPushButton("复制信息到剪贴板")
        self.btn_github = QPushButton("GitHub/PsLauncher")
        self.btn_close = QPushButton("❎")

        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_github)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # 4. 连接信号与槽
        self.btn_close.clicked.connect(self.accept)
        self.btn_github.clicked.connect(self._open_github)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

    def _populate_about_content(self):
        html_content = f"""
        <h2 align="center">PsLauncher</h2>
        <p align="center">{__version__}</p>
        <hr>
        <p>在一个轻量化的界面中, 管理多个路径下的脚本, 随时查看他们, 并在统一的窗口内快速执行.</p>
        <p>NGC13009</p>
        <p>{__devdate__}</p>
        """
        self.text_browser.setHtml(html_content)

    def _open_github(self):
        """打开 GitHub 链接"""
        # 这里的链接也可以存放在成员变量中
        url = QUrl(__githublink__)
        QDesktopServices.openUrl(url)


class HelpDialog(PsLauncherDiag):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("帮助")
        self.resize(1366, 768)

        # 1. 设置布局
        layout = QVBoxLayout(self)

        # 2. 创建支持 HTML 的文本浏览器
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self._populate_about_content()
        layout.addWidget(self.text_browser)

        # 3. 创建按钮
        btn_layout = QVBoxLayout() # 或者用 QHBoxLayout 横向排列

        self.btn_copy = QPushButton("复制信息到剪贴板")
        self.btn_close = QPushButton("关闭")

        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # 4. 连接信号与槽
        self.btn_close.clicked.connect(self.accept)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

    def _populate_about_content(self):
        self.text_browser.setHtml(html_content)
