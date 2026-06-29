# coding = utf-8
# Arch   = manyArch
#
# @File name:       aboutandhelp.py
# @brief:           Help page and About page
# @attention:       None
# @Author:          NGC13009
# @History:         2026-03-16		Create

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from i18n import tr

__version__ = "v1.0.10"
__devdate__ = "JUNE 29, 2026"
__githublink__ = "https://github.com/NGC13009/PsLauncher.git"


class PsLauncherDiag(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    def _copy_to_clipboard(self):
        """Copy text information to clipboard"""
        # Note: Here we copy the plain text version. If you need to copy HTML format, additional processing is required
        plain_text = self.text_browser.toPlainText()

        clipboard = QApplication.clipboard()
        clipboard.setText(plain_text)

        # Optional: Give the user a copy success hint (e.g., change button text for one second)
        original_text = self.btn_copy.text()
        self.btn_copy.setText("Copied ✓")
        self.btn_copy.repaint()

        # Here we simply use a single-shot timer for UI feedback
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.btn_copy.setText(original_text))


class AboutDialog(PsLauncherDiag):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("about.title"))
        self.resize(800, 600)

        # 1. Set up the layout
        layout = QVBoxLayout(self)

        # 2. Create a text browser that supports HTML
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False) # We manually handle link clicks, or set to True for automatic opening
        self._populate_about_content()
        layout.addWidget(self.text_browser)

        # 3. Create buttons
        btn_layout = QVBoxLayout() # Or use QHBoxLayout for horizontal arrangement

        self.btn_copy = QPushButton(tr("about.copy_info"))
        self.btn_github = QPushButton(tr("about.github"))
        self.btn_close = QPushButton(tr("about.close_btn"))

        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_github)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # 4. Connect signals and slots
        self.btn_close.clicked.connect(self.accept)
        self.btn_github.clicked.connect(self._open_github)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

    def _populate_about_content(self):
        html_content = f"""
        <h2 align="center">PsLauncher</h2>
        <p align="center">{__version__}</p>
        <hr>
        <p>{tr("about.description")}</p>
        <p>{tr("about.author")}</p>
        <p>{__devdate__}</p>
        """
        self.text_browser.setHtml(html_content)

    def _open_github(self):
        """Open GitHub link"""
        # The link here can also be stored in member variables
        url = QUrl(__githublink__)
        QDesktopServices.openUrl(url)


class HelpDialog(PsLauncherDiag):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("help.title"))
        self.resize(1366, 768)

        # 1. Set up the layout
        layout = QVBoxLayout(self)

        # 2. Create a text browser that supports HTML
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self._populate_about_content()
        layout.addWidget(self.text_browser)

        # 3. Create buttons
        btn_layout = QVBoxLayout() # Or use QHBoxLayout for horizontal arrangement

        self.btn_copy = QPushButton(tr("help.copy_info"))
        self.btn_close = QPushButton(tr("help.close_btn"))

        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # 4. Connect signals and slots
        self.btn_close.clicked.connect(self.accept)
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

    def _populate_about_content(self):
        from i18n import get_language
        if get_language() == "zh_CN":
            from i18n.source_help_page_zh_CN import html_content as hc
        else:
            from i18n.source_help_page import html_content as hc
        self.text_browser.setHtml(hc)
