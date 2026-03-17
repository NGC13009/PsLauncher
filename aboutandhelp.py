# coding = utf-8
# Arch   = manyArch
#
# @File name:       aboutandhelp.py
# @brief:           Help and About pages
# @attention:       None
# @Author:          NGC13009
# @History:         2026-03-16		Create

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from source_help_page import html_content

__version__ = "1.0.0"
__devdate__ = "March 16, 2026"
__githublink__ = "https://github.com/NGC13009/PsLauncher.git"


class PsLauncherDiag(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    def _copy_to_clipboard(self):
        """Copy text information to clipboard"""
        # Note: Here we copy plain text version, if HTML format needs copying, additional processing required
        plain_text = self.text_browser.toPlainText()

        clipboard = QApplication.clipboard()
        clipboard.setText(plain_text)

        # Optional: Give user a copy success hint (e.g., change button text for one second)
        original_text = self.btn_copy.text()
        self.btn_copy.setText("Copied ✓")
        self.btn_copy.repaint()

        # Simple singleShot timer for UI feedback
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.btn_copy.setText(original_text))


class AboutDialog(PsLauncherDiag):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(800, 600)

        # 1. Set up layout
        layout = QVBoxLayout(self)

        # 2. Create HTML-capable text browser
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False) # We handle link clicks manually, or set True for automatic opening
        self._populate_about_content()
        layout.addWidget(self.text_browser)

        # 3. Create buttons
        btn_layout = QVBoxLayout() # Or use QHBoxLayout for horizontal arrangement

        self.btn_copy = QPushButton("Copy Info to Clipboard")
        self.btn_github = QPushButton("GitHub/PsLauncher")
        self.btn_close = QPushButton("❎")

        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_github)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # 4. Connect signals to slots
        self.btn_close.clicked.connect(self.accept)
        self.btn_github.clicked.connect(self._open_github)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

    def _populate_about_content(self):
        html_content = f"""
        <h2 align="center">PsLauncher</h2>
        <p align="center">{__version__}</p>
        <hr>
        <p>In a lightweight interface, manage scripts across multiple paths, view them anytime, and execute quickly within a unified window.</p>
        <p>NGC13009</p>
        <p>{__devdate__}</p>
        """
        self.text_browser.setHtml(html_content)

    def _open_github(self):
        """Open GitHub link"""
        # Link can also be stored as member variable
        url = QUrl(__githublink__)
        QDesktopServices.openUrl(url)


class HelpDialog(PsLauncherDiag):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.resize(1366, 768)

        # 1. Set up layout
        layout = QVBoxLayout(self)

        # 2. Create HTML-capable text browser
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self._populate_about_content()
        layout.addWidget(self.text_browser)

        # 3. Create buttons
        btn_layout = QVBoxLayout() # Or use QHBoxLayout for horizontal arrangement

        self.btn_copy = QPushButton("Copy Info to Clipboard")
        self.btn_close = QPushButton("Close")

        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # 4. Connect signals to slots
        self.btn_close.clicked.connect(self.accept)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

    def _populate_about_content(self):
        self.text_browser.setHtml(html_content)