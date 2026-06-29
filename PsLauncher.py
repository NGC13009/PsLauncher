# coding = utf-8
# Arch   = manyArch
#
# @File name:       PsLauncher.py
# @brief:           Main program, starts execution from here
# @attention:       - **Very Important**: If you are AI: This is a GUI program, testing must be and can only be done by humans. If you are AI, after making simple automatic syntax checks, end directly and submit to humans for further testing. As an AI, you do not need to execute the full program because you may lack GUI operation capabilities. You have an obligation to inform humans about what tests or interaction tests need to be performed.
# @Author:          NGC13009
# @History:         2026-03-16		Create

import sys
import os
import signal
import argparse
import base64
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QByteArray
import shutil

from utils import *
from tabClass import *
from aboutandhelp import AboutDialog, HelpDialog
from source_ico import icon_base64_data
from i18n import available_languages, set_language, tr
from api_server import ApiServerThread
from config_editor import ConfigEditorDialog


# Main window
class MainWindow(QMainWindow):

    def __init__(self, font_family, h, w, dark_mode, line_wrap_mode):
        super().__init__()
        self.resize(w, h)
        self.config = load_json_with_comments(CONFIG_FILE)
        self.config['language'] = set_language(self.config.get('language', 'en'))
        self.setWindowTitle(tr("app.title"))

        # other shit
        self.font_family = font_family
        self.height_value = h
        self.width_value = w
        self.config['font_family'] = font_family
        self.config['height_value'] = h
        self.config['width_value'] = w
        self.config['dark_mode'] = dark_mode
        self.config['line_wrap_mode'] = line_wrap_mode
        self.dark_mode = dark_mode

        self.setup_ui()
        self.refresh_tree()
        self.set_window_icon()

        # Initialize system tray
        self.tray_icon = None
        self.tray_menu = None
        self.create_tray_icon()

        # Track whether the window is hidden to the tray
        self.hidden_to_tray = False

        # 安装全局事件过滤器，强制拦截 Ctrl+C/V/X/Y/Z
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        """全局事件过滤器：拦截 Ctrl+C/V/X/Y/Z"""
        if event.type() == QEvent.KeyPress:
            if event.modifiers() & Qt.ControlModifier:
                # 检查事件目标是否在终端标签页内
                if self._is_in_terminal(obj):
                    # 终端标签页内的处理
                    if event.key() == Qt.Key_V:
                        # Ctrl+V 始终粘贴
                        self.paste_text()
                        return True
                    elif event.key() in (Qt.Key_C, Qt.Key_X):
                        # 有选中文本时复制/剪切，否则不拦截（让终端发送给进程）
                        focused = QApplication.focusWidget()
                        if focused and hasattr(focused, 'textCursor') and focused.textCursor().hasSelection():
                            if event.key() == Qt.Key_C:
                                self.copy_selected_text()
                            else:
                                self.cut_selected_text()
                            return True
                        # 无选中文本：不拦截，让 terminal_keyPressEvent 发送给进程
                        return False
                    else:
                        # 其他 Ctrl+组合键均不拦截，直接发送给进程
                        return False
                else:
                    # 非终端标签页：保持原有拦截行为
                    if event.key() == Qt.Key_C:
                        self.copy_selected_text()
                        return True
                    elif event.key() == Qt.Key_V:
                        self.paste_text()
                        return True
                    elif event.key() == Qt.Key_X:
                        self.cut_selected_text()
                        return True
                    elif event.key() == Qt.Key_Z:
                        # 撤销操作
                        focused_widget = QApplication.focusWidget()
                        if isinstance(focused_widget, QTextEdit):
                            focused_widget.undo()
                        return True
                    elif event.key() == Qt.Key_Y:
                        # 重做操作
                        focused_widget = QApplication.focusWidget()
                        if isinstance(focused_widget, QTextEdit):
                            focused_widget.redo()
                        return True
        return super().eventFilter(obj, event)

    def _is_in_terminal(self, obj):
        """判断事件目标对象或其父级是否在终端标签页内"""
        widget = obj if isinstance(obj, QWidget) else QApplication.focusWidget()
        if widget is None:
            return False
        while widget is not None:
            if isinstance(widget, TerminalTab):
                return True
            try:
                widget = widget.parent()
            except RuntimeError:
                break
        return False

    def set_window_icon(self):
        """Set window icon"""
        try:
            try:
                # Import base64 data
                if icon_base64_data:
                    # Decode base64 data
                    icon_data = base64.b64decode(icon_base64_data)
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(icon_data))
                    icon = QIcon(pixmap)
                    self.setWindowIcon(icon)
                    icon_set = True
            except Exception as e:
                print(f"Failed to load icon from base64: {e}")

            if not icon_set:
                print("Unable to load program icon, using default icon")
        except Exception as e:
            print(f"Error setting window icon: {e}")

    def setup_ui(self):
        menubar = self.menuBar()

        # ======================== Menu ======================================
        # System menu

        self.sys_menu = menubar.addMenu(tr("menu.system"))

        self.save_action = QAction(tr("action.save_config"), self)
        self.save_action.triggered.connect(self.save_config)
        self.sys_menu.addAction(self.save_action)

        self.sys_menu.addSeparator()
        self.hide_action = QAction(tr("action.hide_to_tray"), self)
        self.hide_action.setShortcut("F10")
        self.hide_action.triggered.connect(self.hide_to_tray)
        self.sys_menu.addAction(self.hide_action)

        self.sys_menu.addSeparator()
        self.auto_minimize_action = QAction(tr("action.auto_minimize"), self)
        self.auto_minimize_action.setCheckable(True)
        self.auto_minimize_action.setChecked(self.config.get('auto_minimize_to_tray', False))
        self.auto_minimize_action.triggered.connect(self.toggle_auto_minimize_to_tray)
        self.sys_menu.addAction(self.auto_minimize_action)

        self.sys_menu.addSeparator()
        self.edit_config_action = QAction(tr("action.edit_config"), self)
        self.edit_config_action.triggered.connect(self.open_config_editor)
        self.sys_menu.addAction(self.edit_config_action)

        # File menu
        self.file_menu = menubar.addMenu(tr("menu.file"))

        self.addpath_action = QAction(tr("action.add_folder"), self)
        self.addpath_action.setShortcut("F2")
        self.addpath_action.triggered.connect(self.add_folder)
        self.file_menu.addAction(self.addpath_action)
        self.removepath_action = QAction(tr("action.remove_folder"), self)
        self.removepath_action.setShortcut("F3")
        self.removepath_action.triggered.connect(self.remove_folder)
        self.file_menu.addAction(self.removepath_action)

        # Edit menu
        self.edit_menu = menubar.addMenu(tr("menu.edit"))

        self.copy_action = QAction(tr("action.copy_selected"), self)
        self.copy_action.triggered.connect(self.copy_selected_text)
        self.copy_action.setShortcut("F11")
        self.edit_menu.addAction(self.copy_action)

        self.paste_action = QAction(tr("action.paste"), self)
        self.paste_action.triggered.connect(self.paste_text)
        self.paste_action.setShortcut("F12")
        self.edit_menu.addAction(self.paste_action)

        self.edit_menu.addSeparator()
        self.copy_all_action = QAction(tr("action.copy_all_tabs"), self)
        self.copy_all_action.triggered.connect(self.copy_all_text)
        self.edit_menu.addAction(self.copy_all_action)

        # Clear terminal screen menu item
        self.clear_screen_action = QAction(tr("action.clear_terminal"), self)
        self.clear_screen_action.triggered.connect(self.clear_current_terminal)
        self.clear_screen_action.setShortcut("Ctrl+L")
        self.clear_screen_action.setToolTip(tr("tooltip.clear_terminal"))
        self.edit_menu.addAction(self.clear_screen_action)

        self.edit_menu.addSeparator()
        # Edit/Save menu item
        self.edit_save_action = QAction(tr("action.edit_script_source"), self)
        self.edit_save_action.setShortcut("F4")
        self.edit_save_action.setToolTip(tr("tooltip.edit_save"))
        self.edit_save_action.triggered.connect(self.toggle_edit_save)
        self.edit_menu.addAction(self.edit_save_action)

        # Run menu
        self.tools_menu = menubar.addMenu(tr("menu.run"))

        self.run_action = QAction(tr("action.start_script"), self)
        self.run_action.triggered.connect(self.run_selected_script)
        self.run_action.setShortcut("F5")
        self.tools_menu.addAction(self.run_action)

        self.stop_action = QAction(tr("action.stop_script"), self)
        self.stop_action.triggered.connect(self.stop_current_script)
        self.stop_action.setShortcut("F6")
        self.tools_menu.addAction(self.stop_action)

        # Send Ctrl+C interrupt
        self.send_ctrlc_action = QAction(tr("action.send_ctrl_c"), self)
        self.send_ctrlc_action.triggered.connect(self.send_ctrl_c_to_current_terminal)
        self.send_ctrlc_action.setShortcut("F7")
        self.send_ctrlc_action.setToolTip(tr("tooltip.send_ctrl_c"))
        self.tools_menu.addAction(self.send_ctrlc_action)

        # View menu
        self.view_menu = menubar.addMenu(tr("menu.view"))

        # Auto wrap toggle menu item
        self.toggle_wrap_action = QAction(tr("action.toggle_wrap"), self)
        self.toggle_wrap_action.setCheckable(True)
        self.toggle_wrap_action.setChecked(self.config['line_wrap_mode'])
        self.toggle_wrap_action.triggered.connect(self.toggle_line_wrap_mode)
        self.view_menu.addAction(self.toggle_wrap_action)

        # Syntax highlighting method submenu
        self.syntax_menu = self.view_menu.addMenu(tr("menu.syntax"))

        # Auto mode
        self.syntax_auto_action = QAction(tr("action.syntax_auto"), self)
        self.syntax_auto_action.setCheckable(True)
        self.syntax_auto_action.triggered.connect(lambda: self.set_syntax_highlight_mode('auto'))
        self.syntax_menu.addAction(self.syntax_auto_action)

        # PowerShell mode
        self.syntax_ps1_action = QAction(tr("action.syntax_ps1"), self)
        self.syntax_ps1_action.setCheckable(True)
        self.syntax_ps1_action.triggered.connect(lambda: self.set_syntax_highlight_mode('ps1'))
        self.syntax_menu.addAction(self.syntax_ps1_action)

        # Bash mode
        self.syntax_bash_action = QAction(tr("action.syntax_bash"), self)
        self.syntax_bash_action.setCheckable(True)
        self.syntax_bash_action.triggered.connect(lambda: self.set_syntax_highlight_mode('bash'))
        self.syntax_menu.addAction(self.syntax_bash_action)

        # Command mode
        self.syntax_command_action = QAction(tr("action.syntax_command"), self)
        self.syntax_command_action.setCheckable(True)
        self.syntax_command_action.triggered.connect(lambda: self.set_syntax_highlight_mode('command'))
        self.syntax_menu.addAction(self.syntax_command_action)

        # No coloring mode
        self.syntax_none_action = QAction(tr("action.syntax_none"), self)
        self.syntax_none_action.setCheckable(True)
        self.syntax_none_action.triggered.connect(lambda: self.set_syntax_highlight_mode('none'))
        self.syntax_menu.addAction(self.syntax_none_action)

        # Create an exclusive action group to ensure only one option is selected
        self.syntax_action_group = QActionGroup(self)
        self.syntax_action_group.addAction(self.syntax_auto_action)
        self.syntax_action_group.addAction(self.syntax_ps1_action)
        self.syntax_action_group.addAction(self.syntax_bash_action)
        self.syntax_action_group.addAction(self.syntax_command_action)
        self.syntax_action_group.addAction(self.syntax_none_action)
        self.syntax_action_group.setExclusive(True)

        # Set the selected menu item based on configuration
        syntax_mode = self.config.get('syntax_highlight_mode', 'auto')
        if syntax_mode == 'auto':
            self.syntax_auto_action.setChecked(True)
        elif syntax_mode == 'ps1':
            self.syntax_ps1_action.setChecked(True)
        elif syntax_mode == 'bash':
            self.syntax_bash_action.setChecked(True)
        elif syntax_mode == 'command':
            self.syntax_command_action.setChecked(True)
        elif syntax_mode == 'none':
            self.syntax_none_action.setChecked(True)
        else:
            raise ValueError("How is this possible?? This should not be reached here.")

        self.language_menu = self.view_menu.addMenu(tr("menu.language"))
        self.language_action_group = QActionGroup(self)
        self.language_action_group.setExclusive(True)
        self.language_actions = {}
        current_language = self.config.get('language', 'en')
        for language, label in available_languages().items():
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(language == current_language)
            action.triggered.connect(lambda _checked=False, lang=language: self.switch_language(lang))
            self.language_action_group.addAction(action)
            self.language_menu.addAction(action)
            self.language_actions[language] = action

        # Script management menu
        self.script_menu = menubar.addMenu(tr("menu.script"))

        self.new_folder_action = QAction(tr("action.new_path"), self)
        self.new_folder_action.triggered.connect(self.new_folder_at_location)
        self.script_menu.addAction(self.new_folder_action)

        self.new_script_action = QAction(tr("action.new_script"), self)
        self.new_script_action.triggered.connect(self.new_script_in_folder)
        self.script_menu.addAction(self.new_script_action)

        self.rename_script_action = QAction(tr("action.rename_script"), self)
        self.rename_script_action.triggered.connect(self.rename_selected_script)
        self.script_menu.addAction(self.rename_script_action)

        self.copy_script_action = QAction(tr("action.copy_script"), self)
        self.copy_script_action.triggered.connect(self.copy_selected_script)
        self.script_menu.addAction(self.copy_script_action)

        self.move_script_action = QAction(tr("action.move_script"), self)
        self.move_script_action.triggered.connect(self.move_selected_script)
        self.script_menu.addAction(self.move_script_action)

        self.delete_script_action = QAction(tr("action.delete_script"), self)
        self.delete_script_action.triggered.connect(self.delete_selected_script)
        self.script_menu.addAction(self.delete_script_action)

        # Tab management functionality
        self.tab_menu = menubar.addMenu(tr("menu.tab"))
        self.close_editor_tabs_action = QAction(tr("action.close_source_tabs"), self)
        self.close_editor_tabs_action.triggered.connect(self.close_all_editor_tabs)
        self.close_editor_tabs_action.setShortcut("F8")
        self.tab_menu.addAction(self.close_editor_tabs_action)

        self.close_terminal_tabs_action = QAction(tr("action.close_terminal_tabs"), self)
        self.close_terminal_tabs_action.triggered.connect(self.close_all_terminal_tabs)
        self.close_terminal_tabs_action.setShortcut("F9")
        self.tab_menu.addAction(self.close_terminal_tabs_action)

        self.close_all_tabs_action = QAction(tr("action.close_all_tabs"), self)
        self.close_all_tabs_action.triggered.connect(self.close_all_tabs)
        self.tab_menu.addAction(self.close_all_tabs_action)

        # Help menu
        self.help_menu = menubar.addMenu(tr("menu.help"))

        self.help_action = QAction(tr("action.help"), self)
        self.help_action.triggered.connect(self.open_help)
        self.help_menu.addAction(self.help_action)
        self.help_action.setShortcut("F1")

        self.about_action = QAction(tr("action.about"), self)
        self.about_action.triggered.connect(self.open_about)
        self.help_menu.addAction(self.about_action)

        # ======================== Toolbar ======================================

        self.toolbar = QToolBar(tr("toolbar.name"))
        # Set toolbar to be movable and allow wrapping
        self.toolbar.setMovable(True)
        self.toolbar.setFloatable(False)
        # Set toolbar button style, using icons and text
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # Enable toolbar overflow menu functionality
        self.toolbar.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.addToolBar(self.toolbar)

        # System tray button
        self.tray_btn = QAction(self)
        self.tray_btn.setText(tr("toolbar.hide"))
        self.tray_btn.setToolTip(tr("tooltip.hide_to_tray"))
        self.tray_btn.triggered.connect(self.hide_to_tray)
        self.toolbar.addAction(self.tray_btn)

        self.toolbar.addSeparator()
        self.run_btn = QAction(self)
        self.run_btn.setText(tr("toolbar.run"))
        self.run_btn.setToolTip(tr("tooltip.run"))
        self.run_btn.triggered.connect(self.run_selected_script)
        self.toolbar.addAction(self.run_btn)

        self.stop_btn = QAction(self)
        self.stop_btn.setText(tr("toolbar.stop"))
        self.stop_btn.setToolTip(tr("tooltip.stop"))
        self.stop_btn.triggered.connect(self.stop_current_script)
        self.toolbar.addAction(self.stop_btn)

        # Send Ctrl+C interrupt button
        self.send_ctrlc_btn = QAction(self)
        self.send_ctrlc_btn.setText(tr("toolbar.interrupt"))
        self.send_ctrlc_btn.setToolTip(tr("tooltip.interrupt"))
        self.send_ctrlc_btn.triggered.connect(self.send_ctrl_c_to_current_terminal)
        self.toolbar.addAction(self.send_ctrlc_btn)

        # 清除终端屏幕按钮
        self.clear_screen_btn = QAction(self)
        self.clear_screen_btn.setText(tr("toolbar.clear"))
        self.clear_screen_btn.setToolTip(tr("tooltip.clear_terminal"))
        self.clear_screen_btn.triggered.connect(self.clear_current_terminal)
        self.toolbar.addAction(self.clear_screen_btn)

        self.toolbar.addSeparator()

        # Copy/Paste function buttons
        self.copy_btn = QAction(self)
        self.copy_btn.setText(tr("toolbar.copy"))
        self.copy_btn.setToolTip(tr("tooltip.copy"))

        self.copy_btn.triggered.connect(self.copy_selected_text)
        self.toolbar.addAction(self.copy_btn)

        self.paste_btn = QAction(self)
        self.paste_btn.setText(tr("toolbar.paste"))
        self.paste_btn.setToolTip(tr("tooltip.paste"))
        self.paste_btn.triggered.connect(self.paste_text)
        self.toolbar.addAction(self.paste_btn)

        self.toolbar.addSeparator()
        self.close_editor_tabs_btn = QAction(self)
        self.close_editor_tabs_btn.setText(tr("toolbar.close_source"))
        self.close_editor_tabs_btn.setToolTip(tr("tooltip.close_source"))
        self.close_editor_tabs_btn.triggered.connect(self.close_all_editor_tabs)
        self.toolbar.addAction(self.close_editor_tabs_btn)

        # Edit/Save Button
        self.edit_save_btn = QAction(self)
        self.edit_save_btn.setText(tr("toolbar.quick_edit"))
        self.edit_save_btn.setToolTip(tr("tooltip.edit_save"))
        self.edit_save_btn.triggered.connect(self.toggle_edit_save)
        self.toolbar.addAction(self.edit_save_btn)

        self.toolbar.addSeparator()

        # Quick Close Button

        self.close_terminal_tabs_btn = QAction(self)
        self.close_terminal_tabs_btn.setText(tr("toolbar.terminate_all"))
        self.close_terminal_tabs_btn.setToolTip(tr("tooltip.close_terminal"))
        self.close_terminal_tabs_btn.triggered.connect(self.close_all_terminal_tabs)
        self.toolbar.addAction(self.close_terminal_tabs_btn)

        self.close_all_tabs_btn = QAction(self)
        self.close_all_tabs_btn.setText(tr("toolbar.close_all"))
        self.close_all_tabs_btn.setToolTip(tr("tooltip.close_all"))
        self.close_all_tabs_btn.triggered.connect(self.close_all_tabs)
        self.toolbar.addAction(self.close_all_tabs_btn)

        # ======================== Resource Explorer ======================================

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(tr("tree.header"))
        font = QFont(self.font_family, 14) # Font family, font size
                                           # font.setBold(True) # Bold
        self.tree.setFont(font)            # Apply to entire tree widget
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
                                           # Set right-click menu
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
                                           # Set tooltip
        self.tree.setMouseTracking(True)
        self.tree.viewport().setMouseTracking(True)
        self.tree.itemEntered.connect(self.on_tree_item_hovered)
        splitter.addWidget(self.tree)

        # ======================== File Tree Styles ======================================
        backgroundcolor = '#1E1E1E' if self.dark_mode else '#efefef'
        backgroundcolor2 = '#3c3c3c' if self.dark_mode else '#d1d1d1'
        backgroundcolor3 = '#d4d4d4' if self.dark_mode else '#3c3c3c'
        color = '#efefef' if self.dark_mode else '#1e1e1e'

        # Styles
        dark_stylesheet = f"""
        /* Main window background */
        QMainWindow {{
            background-color: {backgroundcolor};
        }}
        
        /* Splitter background */
        QSplitter {{
            background-color: {backgroundcolor};
        }}
        QSplitter::handle {{
            background-color: {backgroundcolor2};
            width: 2px;
            height: 2px;
        }}
        
        /* Tree widget styles */
        QTreeWidget {{
            background-color: {backgroundcolor};
            color: {backgroundcolor3};
            border: none;
            outline: none;
        }}
        QTreeWidget::item {{
            padding: 5px;
            border: none;
        }}
        QTreeWidget::item:selected {{
            background-color: #264f78;  /* Selected item dark blue */
            color: #ffffff;
        }}
        QTreeWidget::item:hover {{
            background-color: {backgroundcolor2};  /* Hover slightly brighter */
        }}
        QTreeWidget::branch {{
            background-color: {backgroundcolor};  /* Branch arrow area background */
        }}
        
        /* Header styles */
        QHeaderView::section {{
            background-color: {backgroundcolor2};
            color: {backgroundcolor3};
            padding: 5px;
            border: none;
            border-right: 1px solid {backgroundcolor};
        }}
        """
        self.setStyleSheet(dark_stylesheet)

        # ======================== Tabs ======================================
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        # Connect tab switching signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
        # Set right-click menu
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tabs_context_menu)
        splitter.addWidget(self.tabs)
        splitter.setSizes([300, 750])

    def switch_language(self, language):
        """Switch UI language and persist it in config."""
        selected_language = set_language(language)
        if self.config.get('language') == selected_language:
            return
        self.config['language'] = selected_language
        if hasattr(self, 'language_actions'):
            for lang, action in self.language_actions.items():
                action.setChecked(lang == selected_language)
        self.retranslate_ui()
        self.save_config()

    def _set_edit_save_texts(self, saving=False):
        if saving:
            self.edit_save_action.setText(tr("toolbar.save"))
            self.edit_save_btn.setText(tr("toolbar.save"))
            self.edit_save_action.setToolTip(tr("tooltip.save_script"))
            self.edit_save_btn.setToolTip(tr("tooltip.save_script"))
        else:
            self.edit_save_action.setText(tr("toolbar.edit_mode"))
            self.edit_save_btn.setText(tr("toolbar.edit"))
            self.edit_save_action.setToolTip(tr("tooltip.edit_save"))
            self.edit_save_btn.setToolTip(tr("tooltip.edit_save"))

    def retranslate_ui(self):
        """Refresh currently visible static UI text after changing language."""
        self.setWindowTitle(tr("app.title"))
        self.sys_menu.setTitle(tr("menu.system"))
        self.file_menu.setTitle(tr("menu.file"))
        self.edit_menu.setTitle(tr("menu.edit"))
        self.tools_menu.setTitle(tr("menu.run"))
        self.view_menu.setTitle(tr("menu.view"))
        self.syntax_menu.setTitle(tr("menu.syntax"))
        self.language_menu.setTitle(tr("menu.language"))
        self.script_menu.setTitle(tr("menu.script"))
        self.tab_menu.setTitle(tr("menu.tab"))
        self.help_menu.setTitle(tr("menu.help"))

        self.save_action.setText(tr("action.save_config"))
        self.hide_action.setText(tr("action.hide_to_tray"))
        self.auto_minimize_action.setText(tr("action.auto_minimize"))
        self.edit_config_action.setText(tr("action.edit_config"))
        self.addpath_action.setText(tr("action.add_folder"))
        self.removepath_action.setText(tr("action.remove_folder"))
        self.copy_action.setText(tr("action.copy_selected"))
        self.paste_action.setText(tr("action.paste"))
        self.copy_all_action.setText(tr("action.copy_all_tabs"))
        self.clear_screen_action.setText(tr("action.clear_terminal"))
        self.clear_screen_action.setToolTip(tr("tooltip.clear_terminal"))
        self.run_action.setText(tr("action.start_script"))
        self.stop_action.setText(tr("action.stop_script"))
        self.send_ctrlc_action.setText(tr("action.send_ctrl_c"))
        self.send_ctrlc_action.setToolTip(tr("tooltip.send_ctrl_c"))
        self.toggle_wrap_action.setText(tr("action.toggle_wrap"))
        self.syntax_auto_action.setText(tr("action.syntax_auto"))
        self.syntax_ps1_action.setText(tr("action.syntax_ps1"))
        self.syntax_bash_action.setText(tr("action.syntax_bash"))
        self.syntax_command_action.setText(tr("action.syntax_command"))
        self.syntax_none_action.setText(tr("action.syntax_none"))
        self.new_folder_action.setText(tr("action.new_path"))
        self.new_script_action.setText(tr("action.new_script"))
        self.rename_script_action.setText(tr("action.rename_script"))
        self.copy_script_action.setText(tr("action.copy_script"))
        self.move_script_action.setText(tr("action.move_script"))
        self.delete_script_action.setText(tr("action.delete_script"))
        self.close_editor_tabs_action.setText(tr("action.close_source_tabs"))
        self.close_terminal_tabs_action.setText(tr("action.close_terminal_tabs"))
        self.close_all_tabs_action.setText(tr("action.close_all_tabs"))
        self.help_action.setText(tr("action.help"))
        self.about_action.setText(tr("action.about"))

        self.toolbar.setWindowTitle(tr("toolbar.name"))
        self.tray_btn.setText(tr("toolbar.hide"))
        self.tray_btn.setToolTip(tr("tooltip.hide_to_tray"))
        self.run_btn.setText(tr("toolbar.run"))
        self.run_btn.setToolTip(tr("tooltip.run"))
        self.stop_btn.setText(tr("toolbar.stop"))
        self.stop_btn.setToolTip(tr("tooltip.stop"))
        self.send_ctrlc_btn.setText(tr("toolbar.interrupt"))
        self.send_ctrlc_btn.setToolTip(tr("tooltip.interrupt"))
        self.clear_screen_btn.setText(tr("toolbar.clear"))
        self.clear_screen_btn.setToolTip(tr("tooltip.clear_terminal"))
        self.copy_btn.setText(tr("toolbar.copy"))
        self.copy_btn.setToolTip(tr("tooltip.copy"))
        self.paste_btn.setText(tr("toolbar.paste"))
        self.paste_btn.setToolTip(tr("tooltip.paste"))
        self.close_editor_tabs_btn.setText(tr("toolbar.close_source"))
        self.close_editor_tabs_btn.setToolTip(tr("tooltip.close_source"))
        self.close_terminal_tabs_btn.setText(tr("toolbar.terminate_all"))
        self.close_terminal_tabs_btn.setToolTip(tr("tooltip.close_terminal"))
        self.close_all_tabs_btn.setText(tr("toolbar.close_all"))
        self.close_all_tabs_btn.setToolTip(tr("tooltip.close_all"))
        self.tree.setHeaderLabel(tr("tree.header"))

        current_widget = self.tabs.currentWidget()
        self._set_edit_save_texts(isinstance(current_widget, EditorTab) and current_widget.is_editing)

        if self.tray_icon:
            self.tray_icon.setToolTip(tr("tray.tooltip"))
        if hasattr(self, 'tray_show_action'):
            self.tray_show_action.setText(tr("tray.open_window"))
        if hasattr(self, 'tray_exit_action'):
            self.tray_exit_action.setText(tr("tray.exit"))

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr("dialog.select_folder_scan"))
        if folder and folder not in self.config["folders"]:
            self.config["folders"].append(folder)
            self.refresh_tree()
            self.save_config()

    def remove_folder(self):
        """Remove the selected folder or let the user choose which folder to remove"""
        if not self.config.get("folders"):
            QMessageBox.information(self, tr("dialog.info"), tr("message.no_removable_folders"))
            return

        # Get the currently selected folder item
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            # Check whether it is a folder item or a script item
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # Selected is a script item, get its parent folder
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # Full path of the parent folder
            else:
                                                                    # Selected may be a folder item
                selected_folder = current_item.data(0, Qt.UserRole) # Full path of the folder

        # If a folder is selected, provide a confirmation dialog
        if selected_folder and selected_folder in self.config["folders"]:
            folder_name = os.path.basename(selected_folder.rstrip(os.sep))
            reply = QMessageBox.question(self, tr("dialog.confirm"), tr("message.confirm_remove_folder", folder_name=folder_name), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.config["folders"].remove(selected_folder)
                self.refresh_tree()
                self.save_config()
                return

        # If no folder is selected or the selected is not a folder, display a folder selection dialog
        folder, ok = QInputDialog.getItem(self, tr("dialog.remove_folder"), tr("dialog.select_folder_remove"), self.config["folders"], 0, False)
        if ok and folder:
            folder_name = os.path.basename(folder.rstrip(os.sep))
            reply = QMessageBox.question(self, tr("dialog.confirm"), tr("message.confirm_remove_folder", folder_name=folder_name), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.config["folders"].remove(folder)
                self.refresh_tree()
                self.save_config()

    def save_config(self):
        # Check if default suffix configurations were removed

        supported_extensions = self.config.get('supported_extensions', DEFAULT_EXT)
        missing_in_supported = [ext for ext in DEFAULT_EXT if ext not in supported_extensions]

        runnable_extensions = self.config.get('runnable_extensions', DEFAULT_EXT)
        missing_in_runnable = [ext for ext in DEFAULT_EXT if ext not in runnable_extensions]

        warnings = []
        if missing_in_supported:
            warnings.append(tr("message.missing_supported_exts", exts=', '.join(missing_in_supported)))
        if missing_in_runnable:
            warnings.append(tr("message.missing_runnable_exts", exts=', '.join(missing_in_runnable)))

        if warnings:
            warning_details = "\n".join(warnings)
            warning_message = tr("message.save_config_warning", details=warning_details)

            # Display the warning directly in a popup and return immediately without making any changes
            QMessageBox.warning(self, tr("dialog.config_warning"), warning_message)
        else:
            save_json_with_comments(CONFIG_FILE, self.config)

    def refresh_tree(self):
        self.tree.clear()
        auto_run_list = self.config.get('auto_run_scripts', [])
        # 自动启动脚本高亮颜色（兼容暗色/亮色主题）
        auto_run_highlight_color = QColor(78, 168, 222) if self.dark_mode else QColor(14, 99, 156) # 蓝色系
        for folder in self.config.get("folders", []):
            if not os.path.exists(folder):
                continue

            # Create parent node; display equally in UI regardless of physical hierarchy
            folder_item = QTreeWidgetItem(self.tree)
            # Display folder name (last part of the path)
            folder_name = os.path.basename(folder.rstrip(os.sep))
            folder_item.setText(0, folder_name)
            # Store full path in UserRole
            folder_item.setData(0, Qt.UserRole, folder)
            folder_item.setExpanded(True)

            # Scan supported file extensions in the current directory
            for file in os.listdir(folder):
                full_path = os.path.join(folder, file)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.config.get('supported_extensions', DEFAULT_EXT):
                        script_item = QTreeWidgetItem(folder_item)
                        script_item.setText(0, file)
                        script_item.setData(0, Qt.UserRole, full_path)
                        # 如果该脚本在自动启动列表中，应用高亮
                        if full_path in auto_run_list:
                            script_item.setForeground(0, QBrush(auto_run_highlight_color))
                            script_item.setToolTip(0, tr("message.auto_run_tooltip", path=full_path))

    def on_tree_item_clicked(self, item, column):
        script_path = item.data(0, Qt.UserRole)
        if script_path:
            # Check if it is a file and the extension is in the supported list
            if os.path.isfile(script_path):
                ext = os.path.splitext(script_path)[1].lower()
                if ext in self.config.get('supported_extensions', DEFAULT_EXT):
                    # Open the source code reader on the right when clicking a file
                    self.open_editor_tab(script_path)
            # Do nothing if the path is a folder or a non-script file (folders are handled by the tree control)

    def open_editor_tab(self, script_path):
        filename = os.path.basename(script_path)
        tab_name = tr("tab.editor_prefix") + filename

        # Avoid opening the same source code tab repeatedly
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                self.tabs.setCurrentIndex(i)
                return

        editor = EditorTab(script_path, self.font_family, self.dark_mode, self.config['line_wrap_mode'])
        idx = self.tabs.addTab(editor, tab_name)
        self.tabs.setCurrentIndex(idx)

    def run_selected_script(self, script_path=None):
        # If a script path is provided (e.g., called from the right-click menu), run that script directly
        if script_path:
            if os.path.isfile(script_path):
                ext = os.path.splitext(script_path)[1].lower()
                if ext in self.config.get('runnable_extensions', DEFAULT_EXT):
                    self.open_terminal_tab(script_path)
                else:
                    QMessageBox.information(self, tr("dialog.failed"), tr("message.unsupported_runnable_ext", filename=os.path.basename(script_path), ext=ext), QMessageBox.Ok)
            else:
                QMessageBox.information(self, tr("dialog.failed"), tr("message.invalid_file"), QMessageBox.Ok)
            return

        # No script path provided, get script path based on current focused tab
        current_widget = self.tabs.currentWidget()
        if current_widget is None:
            # If no tabs are open, fallback to using the current item in the file tree
            item = self.tree.currentItem()
            if not item:
                QMessageBox.information(self, tr("dialog.failed"), tr("message.no_focused_tab"), QMessageBox.Ok)
                return
            script_path = item.data(0, Qt.UserRole)
            if script_path:
                if os.path.isfile(script_path):
                    ext = os.path.splitext(script_path)[1].lower()
                    if ext in self.config.get('runnable_extensions', DEFAULT_EXT):
                        self.open_terminal_tab(script_path)
                    else:
                        QMessageBox.information(self, tr("dialog.failed"), tr("message.unsupported_runnable_ext", filename=os.path.basename(script_path), ext=ext), QMessageBox.Ok)
                else:
                    QMessageBox.information(self, tr("dialog.failed"), tr("message.invalid_file"), QMessageBox.Ok)
            else:
                QMessageBox.information(self, tr("dialog.failed"), tr("message.no_focused_tab"), QMessageBox.Ok)
            return

        # Get script path based on current tab type
        script_path = None
        if isinstance(current_widget, EditorTab):
            # Source code tab: run the corresponding script
            script_path = current_widget.script_path
        elif isinstance(current_widget, TerminalTab):
            # Terminal tab: always start a new terminal tab and run the same script
            script_path = current_widget.script_path
        else:
            QMessageBox.information(self, tr("dialog.failed"), tr("message.current_tab_not_script"), QMessageBox.Ok)
            return

        # Run script
        if script_path and os.path.isfile(script_path):
            ext = os.path.splitext(script_path)[1].lower()
            if ext in self.config.get('runnable_extensions', DEFAULT_EXT):
                self.open_terminal_tab(script_path)
            else:
                QMessageBox.information(self, tr("dialog.failed"), tr("message.unsupported_runnable_file", filename=os.path.basename(script_path)), QMessageBox.Ok)
        else:
            QMessageBox.information(self, tr("dialog.failed"), tr("message.invalid_script_path"), QMessageBox.Ok)

    def open_terminal_tab(self, script_path):
        filename = os.path.basename(script_path)
        # Create a separate tab for the running program, using different emojis for visual distinction
        tab_name = tr("tab.terminal_prefix") + filename
        terminal = TerminalTab(script_path, self.font_family, self.dark_mode, self.config['line_wrap_mode'])
        idx = self.tabs.addTab(terminal, tab_name)
        self.tabs.setCurrentIndex(idx)
        terminal.start_process()

    def stop_current_script(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, TerminalTab):
            current_widget.stop_process()

    def send_ctrl_c_to_current_terminal(self):
        """Send Ctrl+C interrupt signal to the current terminal tab's process"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, TerminalTab):
            current_widget.send_ctrl_c()
        else:
            QMessageBox.information(self, tr("dialog.prompt"), tr("message.current_tab_not_terminal_ctrlc"), QMessageBox.Ok)

    def clear_current_terminal(self):
        """Clear all displayed content in the current terminal tab"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, TerminalTab):
            current_widget.clear_screen()
        else:
            QMessageBox.information(self, tr("dialog.info"), tr("message.current_tab_not_terminal_clear"), QMessageBox.Ok)

    def close_tab(self, index):
        widget = self.tabs.widget(index)

        # First check if it is a source code tab and is in editing mode
        if isinstance(widget, EditorTab) and widget.is_editing:
            filename = os.path.basename(widget.script_path)
            reply = QMessageBox.question(self, tr("dialog.close_tab"), tr("message.tab_editing_save", filename=filename), QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Save:
                success = widget.save_file()
                if not success:
                    QMessageBox.warning(self, tr("dialog.save_failed"), tr("message.save_file_failed"), QMessageBox.Ok)
                    return
                else:
                    widget.set_editing(False)
                    self.update_edit_save_state()

        # If it's a terminal tab, stop the process
        if isinstance(widget, TerminalTab):
            widget.stop_process()

        self.tabs.removeTab(index)
        widget.deleteLater()

    def close_all_editor_tabs(self):
        """Close all source code tabs (check editing status)"""
        # First check if there are tabs being edited
        editing_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab) and widget.is_editing:
                editing_tabs.append((i, widget))

        if editing_tabs:
            # If there are tabs being edited, prompt the user
            editing_count = len(editing_tabs)
            if editing_count == 1:
                filename = os.path.basename(editing_tabs[0][1].script_path)
                message = tr("message.tab_editing_save_single", filename=filename)
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = tr("message.tabs_editing_save_multi", count=editing_count, files=files_list)

            reply = QMessageBox.question(self, tr("dialog.close_all_source_tabs"), message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # User cancelled closing

            # Process tabs that need to be saved
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, tr("dialog.save_failed"), tr("message.save_file_failed_with_path", path=os.path.basename(widget.script_path)), QMessageBox.Ok)
                        return # One save failed, cancel all close operations
                    else:
                        widget.set_editing(False)

            # If Discard is selected, continue closing directly

        # Close all source code tabs
        tabs_to_close = []
        for i in range(self.tabs.count() - 1, -1, -1):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab):
                tabs_to_close.append(i)

        for index in tabs_to_close:
            self.tabs.removeTab(index)
            widget = self.tabs.widget(index) # Note: Index changes after removal, but since we process from back to front, it's fine

        # Update button states
        self.update_edit_save_state()

    def close_all_terminal_tabs(self):
        """Close all running tabs (with confirmation dialog)"""
        terminal_count = 0
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                terminal_count += 1

        if terminal_count == 0:
            return

        # Show confirmation dialog
        reply = QMessageBox.question(self, tr("dialog.close_terminal_tabs"), tr("message.close_terminal_confirm", count=terminal_count), QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            tabs_to_close = []
            for i in range(self.tabs.count() - 1, -1, -1):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()
                    tabs_to_close.append(i)

            for index in tabs_to_close:
                self.tabs.removeTab(index)

    def close_all_tabs(self):
        """Close all tabs, including source and run tabs (check editing status)"""
        total_tabs = self.tabs.count()
        if total_tabs == 0:
            return

        # Check if there are tabs being edited first
        editing_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab) and widget.is_editing:
                editing_tabs.append((i, widget))

        if editing_tabs:
            # If there are tabs being edited, prompt the user
            editing_count = len(editing_tabs)
            if editing_count == 1:
                filename = os.path.basename(editing_tabs[0][1].script_path)
                message = tr("message.tab_editing_save_single", filename=filename)
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = tr("message.tabs_editing_save_multi", count=editing_count, files=files_list)

            reply = QMessageBox.question(self, tr("dialog.close_all_tabs"), message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # User cancelled closing

            # Process tabs that need to be saved
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, tr("dialog.save_failed"), tr("message.save_file_failed_with_path", path=os.path.basename(widget.script_path)), QMessageBox.Ok)
                        return # One save failed, cancel all close operations
                    else:
                        widget.set_editing(False)

            # If Discard is selected, continue with the close operations below

        # Display confirmation dialog (mainly for terminal tabs)
        terminal_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                terminal_tabs.append(i)

        if terminal_tabs:
            terminal_count = len(terminal_tabs)
            reply = QMessageBox.question(self, tr("dialog.confirm"), tr("message.close_all_confirm_with_terminal", total=total_tabs, terminal_count=terminal_count),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            reply = QMessageBox.question(self, tr("dialog.confirm"), tr("message.close_all_confirm", total=total_tabs), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Stop all terminal processes first
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()

            # Clear all tabs
            self.tabs.clear()
            # Update button states
            self.update_edit_save_state()

    def copy_selected_text(self):
        """Copy selected text of the currently focused control to the clipboard"""
        # Get the currently focused control
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            cursor = focused_widget.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                clipboard = QApplication.clipboard()
                clipboard.setText(selected_text)
                return

        # No text selected or the focused widget does not support selection: copy all content of the current tab
        current_widget = self.tabs.currentWidget()
        if current_widget:
            text = ""
            if isinstance(current_widget, EditorTab):
                text = current_widget.editor.toPlainText()
            elif isinstance(current_widget, TerminalTab):
                text = current_widget.terminal.toPlainText()
            else:
                return

            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)

    def paste_text(self):
        """Paste text from clipboard to the currently focused widget"""
        # Get the currently focused widget
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                cursor = focused_widget.textCursor()
                cursor.insertText(text)

    def copy_all_text(self):
        """Copy all text within the current tab to the clipboard"""
        current_widget = self.tabs.currentWidget()
        if current_widget:
            text = ""
            if isinstance(current_widget, EditorTab):
                text = current_widget.editor.toPlainText()
            elif isinstance(current_widget, TerminalTab):
                text = current_widget.terminal.toPlainText()
            else:
                # Other types of tabs
                return

            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)

    def open_help(self):
        """Open the help window"""
        dialog = HelpDialog(self)
        dialog.exec_()

    def open_about(self):
        """Open About Window"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def toggle_edit_save(self):
        """Toggle Edit/Save Mode"""
        current_widget = self.tabs.currentWidget()
        if not isinstance(current_widget, EditorTab):
            QMessageBox.information(self, tr("dialog.notice"), tr("message.current_tab_not_editor"), QMessageBox.Ok)
            return

        editor_tab = current_widget

        if not editor_tab.is_editing:
            # Not currently in edit mode, attempt to enter edit mode
            editor_tab.set_editing(True)
            # Update button and menu text
            self._set_edit_save_texts(saving=True)
        else:
            # Currently in edit mode, attempt to save
            reply = QMessageBox.question(self, tr("dialog.confirm"), tr("message.save_changes_overwrite"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                success = editor_tab.save_file()
                if success:
                    editor_tab.set_editing(False)
                    # Update buttons and menu text
                    self._set_edit_save_texts(saving=False)
                else:
                    QMessageBox.warning(self, tr("dialog.failed"), tr("message.save_file_failed_admin"), QMessageBox.Ok)
            else:
                # User cancelled save, need to reload file content to restore original state
                editor_tab.set_editing(False)
                # Reload file content to discard user's modifications
                editor_tab.load_file(editor_tab.script_path)
                # Update buttons and menu text
                self._set_edit_save_texts(saving=False)

    def update_edit_save_state(self):
        """Update Edit/Save Button State Based on Current Tab Type"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, EditorTab):
            editor_tab = current_widget
            self._set_edit_save_texts(saving=editor_tab.is_editing)
        else:
            # Not a source code tab, restore default text
            self._set_edit_save_texts(saving=False)

    def create_tray_icon(self):
        """Create system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available")
            return

        # Create tray icon
        icon = None

        try:
            # Import pre-stored Base64 data (source_ico.py must be generated in advance)
            from source_ico import icon_base64_data
            if icon_base64_data:
                # Decode Base64 to binary data
                icon_data = base64.b64decode(icon_base64_data)
                # Load into QPixmap
                pixmap = QPixmap()
                if pixmap.loadFromData(QByteArray(icon_data)):
                    icon = QIcon(pixmap)
        except ImportError:
            print("source_ico.py not found, skipping Base64 loading")
        except Exception as e:
            print(f"Failed to load icon from Base64: {e}")

        if icon is None:
            # Use default Qt icon
            icon = self.style().standardIcon(self.style().SP_ComputerIcon)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(tr("tray.tooltip"))

        # Create tray menu
        self.tray_menu = QMenu(self)

        # Open window menu item
        self.tray_show_action = QAction(tr("tray.open_window"), self)
        self.tray_show_action.triggered.connect(self.show_from_tray)
        self.tray_menu.addAction(self.tray_show_action)

        # Separator
        self.tray_menu.addSeparator()

        # Exit menu item
        self.tray_exit_action = QAction(tr("tray.exit"), self)
        self.tray_exit_action.triggered.connect(self.quit_from_tray)
        self.tray_menu.addAction(self.tray_exit_action)

        # Set tray menu
        self.tray_icon.setContextMenu(self.tray_menu)

        # Connect tray icon click event
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Show tray icon
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        """Handle when tray icon is activated"""
        if reason == QSystemTrayIcon.Trigger:
            self.show_from_tray()

    def hide_to_tray(self):
        """Hide window to system tray"""
        if self.tray_icon:
            self.hide()
            self.hidden_to_tray = True
            self.tray_icon.showMessage(tr("app.title"), tr("tray.minimized"), QSystemTrayIcon.Information, 2000)

    def show_from_tray(self):
        """Restore window from system tray"""
        if self.hidden_to_tray:
            self.show()
            self.raise_()
            self.activateWindow()
            self.hidden_to_tray = False

    def quit_from_tray(self):
        """Exit program from tray menu"""
        # Show confirmation dialog
        reply = QMessageBox.question(self, tr("dialog.prompt"), tr("message.confirm_exit"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Save configuration and stop all processes
            self.save_config()
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()

            # Hide tray icon
            if self.tray_icon:
                self.tray_icon.hide()

            # Exit application
            QApplication.quit()

    def closeEvent(self, event):
        """Override close event to support hiding to tray"""
        # Check if currently hiding to tray
        if self.hidden_to_tray:
            event.ignore() # Ignore close event, just hide to tray
            return

        if self.tabs.count() != 0:
            # Display confirmation dialog
            reply = QMessageBox.Yes # Went through a round of all source code tabs, what's the point of confirming?
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    reply = QMessageBox.question(self, tr("dialog.confirm_exit"), tr("message.confirm_exit_inline"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    break
        else:
            reply = QMessageBox.Yes

        if reply == QMessageBox.Yes:
            # Automatically save configuration and forcefully terminate all processes on close
            self.save_config()
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()

            # Hide tray icon
            if self.tray_icon:
                self.tray_icon.hide()

            event.accept()
        else:
            event.ignore()

    # ======================== Script Management Features ======================================

    def new_folder_at_location(self):
        """Create new path (create folder at specific location)"""
        # Get currently selected folder
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # Selected is a script item, get its parent folder path
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # Full path of the parent folder
            else:
                                                                    # Selected might be a folder item
                selected_folder = current_item.data(0, Qt.UserRole) # Full path of the folder

        # If no folder is selected, let the user choose a base path
        if not selected_folder:
            if self.config.get("folders"):
                # Use the first folder from the configuration as the default path
                selected_folder = self.config["folders"][0]
            else:
                QMessageBox.warning(self, tr("dialog.warning"), tr("message.add_folder_first"), QMessageBox.Ok)
                return

        # Pop up a dialog to let the user enter a new folder name
        folder_name, ok = QInputDialog.getText(self, tr("dialog.new_path"), tr("message.enter_new_folder_name"), QLineEdit.Normal, "")
        if not ok or not folder_name.strip():
            return

        # Construct the full path
        new_folder_path = os.path.join(selected_folder, folder_name.strip())

        # Check if the path already exists
        if os.path.exists(new_folder_path):
            QMessageBox.warning(self, tr("dialog.warning"), tr("message.path_already_exists", path=new_folder_path), QMessageBox.Ok)
            return

        try:
            os.makedirs(new_folder_path)
            QMessageBox.information(self, tr("dialog.success"), tr("message.folder_created_success", path=new_folder_path), QMessageBox.Ok)
            # Optional: Add the new folder to the configuration
            if new_folder_path not in self.config["folders"]:
                self.config["folders"].append(new_folder_path)
                self.save_config()
                self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), tr("message.folder_create_failed", error=str(e)),
                                 QMessageBox.Ok)

    def new_script_in_folder(self):
        """Create a new script in the currently selected folder path"""
        # Get the currently selected folder
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # The selected item is a script, get its parent folder path
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # Full path of the parent folder
            else:
                                                                    # The selected item might be a folder item
                selected_folder = current_item.data(0, Qt.UserRole) # Full path of the folder

        # If no folder is selected, ask the user to select one
        if not selected_folder:
            if self.config.get("folders"):
                # Show folder selection dialog
                folder, ok = QInputDialog.getItem(self, tr("dialog.select_folder"), tr("message.select_target_folder"), self.config["folders"], 0, False)
                if not ok:
                    return
                selected_folder = folder
            else:
                QMessageBox.warning(self, tr("dialog.warning"), tr("message.add_folder_first"), QMessageBox.Ok)
                return

        # Show dialog to let user enter file name
        exts_str = str(DEFAULT_EXT)
        file_name, ok = QInputDialog.getText(
            self, tr("dialog.new_script"), tr("message.enter_script_name", exts=exts_str), QLineEdit.Normal, "new_script.ps1")
        if not ok or not file_name.strip():
            return

        # Check if the extension has changed
        new_ext = os.path.splitext(file_name)[1].lower()

        # If the new extension is not a supported type, prompt for confirmation
        if new_ext and new_ext not in DEFAULT_EXT:
            reply = QMessageBox.question(
                self, tr("dialog.extension_warning"), tr("message.extension_not_supported", ext=new_ext, exts=exts_str), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # If there is no extension, prompt the user to confirm
        if not new_ext:
            reply = QMessageBox.question(
                self, tr("dialog.no_extension_warning"), tr("message.no_extension_warning", exts=exts_str), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        file_name = file_name.strip()
        # Construct the full path
        new_file_path = os.path.join(selected_folder, file_name)

        # Check if the file already exists
        if os.path.exists(new_file_path):
            reply = QMessageBox.question(self, tr("dialog.confirm_overwrite"), tr("message.file_already_exists", path=new_file_path), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        try:
            # Create an empty file
            with open(new_file_path, 'w', encoding='utf-8') as f:
                # Can add some template content based on the extension
                ext = os.path.splitext(file_name)[1].lower()
                if ext == '.ps1':
                    f.write("# PowerShell script\nWrite-Host \"This is .ps1 demo created by PsLauncher.\"\n")
                elif ext == '.bat':
                    f.write("@echo off\necho This is .bat demo created by PsLauncher.\n")
                elif ext == '.sh':
                    f.write("#!/bin/bash\necho \"This is .sh demo created by PsLauncher.\"\n")
                else:
                    f.write("")

            QMessageBox.information(self, tr("dialog.success"), tr("message.script_created_success", path=new_file_path), QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), tr("message.script_create_failed", error=str(e)), QMessageBox.Ok)

    def rename_selected_script(self):
        """Rename the selected script name, check if the suffix is a supported script type"""
        # Get the currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script"), QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script_file"), QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        old_ext = os.path.splitext(old_file_name)[1].lower() # Original file extension

        # Pop up a dialog to let the user enter the new file name
        exts_str = str(DEFAULT_EXT)
        new_file_name, ok = QInputDialog.getText(
            self, tr("dialog.rename_script"), tr("message.rename_script_hint", old_name=old_file_name, exts=exts_str), QLineEdit.Normal, old_file_name)
        if not ok or not new_file_name.strip():
            return

        new_file_name = new_file_name.strip()
        # If the new file name is the same as the old file name, return directly
        if new_file_name == old_file_name:
            return

        # Check if the suffix has changed
        new_ext = os.path.splitext(new_file_name)[1].lower()

        # If the new suffix is not a supported type, prompt for confirmation
        if new_ext and new_ext not in DEFAULT_EXT:
            reply = QMessageBox.question(
                self, tr("dialog.suffix_warning"), tr("message.suffix_warning_rename", ext=new_ext, exts=exts_str), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # If there is no suffix, prompt the user to confirm
        if not new_ext:
            reply = QMessageBox.question(
                self, tr("dialog.no_extension_warning"), tr("message.no_suffix_warning_rename", exts=exts_str), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        new_file_path = os.path.join(folder_path, new_file_name)

        # Check if the new file already exists
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, tr("dialog.warning"), tr("message.file_already_exists_path", path=new_file_path), QMessageBox.Ok)
            return

        try:
            os.rename(script_path, new_file_path)
            QMessageBox.information(self, tr("dialog.success"), tr("message.rename_success", old_name=old_file_name, new_name=new_file_name), QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), tr("message.rename_failed", error=str(e)), QMessageBox.Ok)

    def copy_selected_script(self):
        """Copy the selected script (prompt the user to rename the file name)"""
        # Get the currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script"), QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script_file"), QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        name, ext = os.path.splitext(old_file_name)

        # Generate default new filename: original filename with _copy
        default_new_name = name + "_copy" + ext

        # Pop up dialog to prompt user to rename file
        exts_str = str(DEFAULT_EXT)
        new_file_name, ok = QInputDialog.getText(
            self, tr("dialog.copy_script"), tr("message.copy_script_hint", old_name=old_file_name, exts=exts_str), QLineEdit.Normal, default_new_name)

        if not ok or not new_file_name.strip():
            return # User canceled or input is empty

        new_file_name = new_file_name.strip()

        # Check if new filename has an extension; if not, add the original extension
        if not os.path.splitext(new_file_name)[1]:
            new_file_name = new_file_name + ext

        # Construct full new file path
        new_file_path = os.path.join(folder_path, new_file_name)

        # Check if a file with the same name exists
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, tr("dialog.warning"), tr("message.copy_file_exists", name=new_file_name), QMessageBox.Ok)
            return # Refuse to perform any copy operation

        # Execute copy operation
        try:
            shutil.copy2(script_path, new_file_path)
            QMessageBox.information(self, tr("dialog.success"), tr("message.copy_success", old_name=old_file_name, new_name=new_file_name), QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), tr("message.copy_failed", error=str(e)), QMessageBox.Ok)

    def move_selected_script(self):
        """Move current script to a loaded path (requires confirmation)"""
        # Get currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script"), QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script_file"), QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)

        # If no available target folder, prompt user
        if not self.config.get("folders"):
            QMessageBox.warning(self, tr("dialog.warning"), "No available target folder. Please add folder path first.", QMessageBox.Ok)
            return

        # Pop up dialog to let user select target folder
        target_folder, ok = QInputDialog.getItem(self, tr("dialog.move_script"), tr("message.move_script_select", script_name=old_file_name), self.config["folders"], 0, False)
        if not ok:
            return

        # Check if target folder exists
        if not os.path.exists(target_folder):
            QMessageBox.warning(self, tr("dialog.warning"), tr("message.target_folder_not_exist", path=target_folder), QMessageBox.Ok)
            return

        # Construct target path
        target_path = os.path.join(target_folder, old_file_name)

        # Check if target file already exists
        if os.path.exists(target_path):
            reply = QMessageBox.question(self, tr("dialog.confirm"), tr("message.move_file_exists", name=old_file_name), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # Display confirmation dialog
        reply = QMessageBox.question(self, tr("dialog.confirm"), tr("message.confirm_move", script_name=old_file_name, target_folder=target_folder), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            shutil.move(script_path, target_path)
            QMessageBox.information(self, tr("dialog.success"), tr("message.move_success", script_name=old_file_name, target_folder=target_folder), QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), tr("message.move_failed", error=str(e)), QMessageBox.Ok)

    def delete_selected_script(self):
        """Delete selected script (requires confirmation dialog)"""
        # Get currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script"), QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, tr("dialog.info"), tr("message.please_select_script_file"), QMessageBox.Ok)
            return

        file_name = os.path.basename(script_path)

        # Display confirmation dialog
        reply = QMessageBox.question(self, tr("dialog.confirm_delete"),
                                     tr("message.confirm_delete_script", file_name=file_name),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            os.remove(script_path)
            QMessageBox.information(self, tr("dialog.success"), tr("message.delete_success", file_name=file_name), QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, tr("dialog.error"), tr("message.delete_failed", error=str(e)), QMessageBox.Ok)

    def open_in_vsc(self, file_path):
        """Open the specified file in VSCode"""
        try:
            subprocess.run(['code', file_path], check=True)
        except FileNotFoundError:
            QMessageBox.warning(self, tr("dialog.failed"), tr("message.vsc_not_found"), QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, tr("dialog.failed"), tr("message.vsc_call_error", error=str(e)), QMessageBox.Ok)

    def show_tree_context_menu(self, position):
        """Display the right-click menu for the tree widget"""
        item = self.tree.itemAt(position)
        menu = QMenu(self)
        self.menu = menu
        if item:
            # Get the path
            path = item.data(0, Qt.UserRole)
            if path:
                # Determine if it's a folder or a script file
                if os.path.isdir(path):
                    # Folder item: show folder-related menu
                    open_folder_action = QAction(tr("context.open_in_explorer"), self)
                    open_folder_action.triggered.connect(lambda: os.startfile(path))
                    menu.addAction(open_folder_action)

                    menu.addSeparator()

                    # Remove current folder path
                    remove_folder_action = QAction(tr("action.remove_folder"), self)
                    remove_folder_action.triggered.connect(self.remove_folder)
                    menu.addAction(remove_folder_action)

                    # Add folder path
                    add_folder_action = QAction(tr("action.add_folder"), self)
                    add_folder_action.triggered.connect(self.add_folder)
                    menu.addAction(add_folder_action)

                elif os.path.isfile(path):
                    ext = os.path.splitext(path)[1].lower()
                    if ext in self.config.get('supported_extensions', DEFAULT_EXT):
                        # Script item: show script management menu
                        run_action = QAction(tr("context.run"), self)
                        run_action.triggered.connect(lambda: self.run_selected_script(path))
                        menu.addAction(run_action)

                        menu.addSeparator()

                        edit_action = QAction(tr("context.edit_save"), self)
                        edit_action.triggered.connect(lambda: (self.open_editor_tab(path), self.toggle_edit_save()))
                        menu.addAction(edit_action)

                        # 启动时自动运行开关 (仅对可运行后缀的脚本显示)
                        runnable_ext = self.config.get('runnable_extensions', DEFAULT_EXT)
                        if ext in runnable_ext:
                            script_path = path # 捕获当前路径供 lambda 使用（闭包捕获）
                            if self.is_script_auto_run(path):
                                auto_run_action = QAction(tr("context.stop_auto_start"), self)
                            else:
                                auto_run_action = QAction(tr("context.auto_start"), self)
                                               # triggered 信号会传入 checked(bool) 参数，必须显式接收并忽略
                            auto_run_action.triggered.connect(lambda _checked=False, sp=script_path: self.toggle_auto_run_script(sp))
                            menu.addAction(auto_run_action)

                            menu.addSeparator()

                        # Edit with VSCode
                        vsc_action = QAction(tr("context.edit_with_vsc"), self)
                        vsc_action.setToolTip(tr("context.edit_with_vsc"))
                        vsc_action.triggered.connect(lambda _checked=False, p=path: self.open_in_vsc(p))
                        menu.addAction(vsc_action)

                        menu.addSeparator()

                        rename_action = QAction(tr("action.rename_script"), self)
                        rename_action.triggered.connect(self.rename_selected_script)
                        menu.addAction(rename_action)

                        copy_action = QAction(tr("action.copy_script"), self)
                        copy_action.triggered.connect(self.copy_selected_script)
                        menu.addAction(copy_action)

                        move_action = QAction(tr("action.move_script"), self)
                        move_action.triggered.connect(self.move_selected_script)
                        menu.addAction(move_action)

                        delete_action = QAction(tr("action.delete_script"), self)
                        delete_action.triggered.connect(self.delete_selected_script)
                        menu.addAction(delete_action)
                    else:
                        # Other file types, only show View menu
                        view_action = QAction(tr("context.view"), self)
                        view_action.triggered.connect(lambda: self.open_editor_tab(path))
                        menu.addAction(view_action)
                else:
                    # Other file types or unknown path, do not show menu items or show default items
                    pass
            else:
                # Items without stored path (e.g., root node?)
                pass
        else:
            # Blank area: show Add Folder
            add_action = QAction(tr("action.add_folder"), self)
            add_action.triggered.connect(self.add_folder)
            menu.addAction(add_action)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def on_tab_changed(self, index):
        """Handling when tabs are switched"""
        self.update_edit_save_state()
        self.sync_tree_selection()

    def sync_tree_selection(self):
        """Synchronize file tree selection based on current tab"""
        current_widget = self.tabs.currentWidget()
        if current_widget is None:
            # No tabs, clear file tree selection
            self.tree.setCurrentItem(None)
            return

        # Get script path
        script_path = None
        if isinstance(current_widget, EditorTab):
            script_path = current_widget.script_path
        elif isinstance(current_widget, TerminalTab):
            script_path = current_widget.script_path
        else:
            # Other types of tabs, do not clear selection
            return

        if not script_path or not os.path.exists(script_path):
            return

        # Find the corresponding item in the file tree
        self.find_and_select_tree_item(script_path)

    def find_and_select_tree_item(self, script_path):
        """Find and select the corresponding item in the file tree"""
        # Iterate over all top-level items (folders)
        for i in range(self.tree.topLevelItemCount()):
            folder_item = self.tree.topLevelItem(i)
            folder_path = folder_item.data(0, Qt.UserRole)
            if folder_path and script_path.startswith(folder_path):
                # Search for script items under this folder
                for j in range(folder_item.childCount()):
                    script_item = folder_item.child(j)
                    item_path = script_item.data(0, Qt.UserRole)
                    if item_path == script_path:
                        # Found the matching item, select it and ensure visibility
                        self.tree.setCurrentItem(script_item)
                        # Ensure the parent folder is expanded
                        folder_item.setExpanded(True)
                        # Scroll to the item
                        self.tree.scrollToItem(script_item)
                        return
                # If no script item is found, select the folder
                self.tree.setCurrentItem(folder_item)
                return

        # If no matching item is found, clear the selection
        self.tree.setCurrentItem(None)

    def on_tree_item_hovered(self, item, column):
        """Tree item hover event, display tooltip"""
        if item:
            script_path = item.data(0, Qt.UserRole)
            if script_path:
                # Script item: display full path
                item.setToolTip(column, script_path)
            else:
                # Folder item: display full path
                folder_path = item.data(0, Qt.UserRole) # Full path
                if folder_path:
                    item.setToolTip(column, folder_path)
                else:
                                                        # If no stored path, use displayed text
                    item.setToolTip(column, item.text(0))
                                                        # Note: If item is None, do not set tooltip

    def show_tabs_context_menu(self, position):
        """Display context menu for tab widget"""
        # Get tab index
        tab_idx = self.tabs.tabBar().tabAt(position)
        if tab_idx == -1:
            return # No tabs

        menu = QMenu(self)

        # Cut, copy, paste functions
        cut_action = QAction(tr("context.cut"), self)
        cut_action.triggered.connect(self.cut_selected_text)
        menu.addAction(cut_action)

        copy_action = QAction(tr("action.copy_selected"), self)
        copy_action.triggered.connect(self.copy_selected_text)
        menu.addAction(copy_action)

        paste_action = QAction(tr("action.paste"), self)
        paste_action.triggered.connect(self.paste_text)
        menu.addAction(paste_action)

        menu.addSeparator()

        # For source code tabs, support edit or save functionality
        current_widget = self.tabs.widget(tab_idx)
        if isinstance(current_widget, EditorTab):
            if current_widget.is_editing:
                save_action = QAction(tr("toolbar.save"), self)
                save_action.triggered.connect(self.toggle_edit_save)
                menu.addAction(save_action)
            else:
                edit_action = QAction(tr("toolbar.edit"), self)
                edit_action.triggered.connect(self.toggle_edit_save)
                menu.addAction(edit_action)

        menu.addSeparator()

        # Close tab
        close_action = QAction(tr("context.close_tab"), self)
        close_action.triggered.connect(lambda: self.close_tab(tab_idx))
        menu.addAction(close_action)

        # Show menu
        menu.exec_(self.tabs.mapToGlobal(position))

    def cut_selected_text(self):
        """Cut selected text from the focused widget to the clipboard"""
        # Get the currently focused control
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            cursor = focused_widget.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                clipboard = QApplication.clipboard()
                clipboard.setText(selected_text)
                # Delete selected text
                cursor.removeSelectedText()

    def toggle_line_wrap_mode(self):
        """Toggle line wrap mode"""
        # Toggle configuration state
        self.config['line_wrap_mode'] = not self.config['line_wrap_mode']
        self.toggle_wrap_action.setChecked(self.config['line_wrap_mode'])

        # Update all existing tabs
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab):
                widget.set_line_wrap_mode(self.config['line_wrap_mode'])
            elif isinstance(widget, TerminalTab):
                widget.set_line_wrap_mode(self.config['line_wrap_mode'])

        # Save configuration
        self.save_config()

    def toggle_auto_minimize_to_tray(self):
        """切换启动时自动最小化到托盘的设置"""
        self.config['auto_minimize_to_tray'] = not self.config.get('auto_minimize_to_tray', False)
        self.auto_minimize_action.setChecked(self.config['auto_minimize_to_tray'])
        self.save_config()

    def toggle_auto_run_script(self, script_path):
        """切换指定脚本的启动时自动运行状态"""
        if not script_path:
            return
        auto_run_list = self.config.get('auto_run_scripts', [])
        if script_path in auto_run_list:
            auto_run_list.remove(script_path)
        else:
            auto_run_list.append(script_path)
        self.config['auto_run_scripts'] = auto_run_list
        self.save_config()
        # 立即刷新文件树以更新高亮状态
        self.refresh_tree()

    def is_script_auto_run(self, script_path):
        """检查指定脚本是否被设置为启动时自动运行"""
        if not script_path:
            return False
        return script_path in self.config.get('auto_run_scripts', [])

    def run_auto_start_scripts(self):
        """启动时自动运行配置中标记为自动运行的脚本"""
        auto_run_list = self.config.get('auto_run_scripts', [])
        if not auto_run_list:
            return
        runnable_ext = self.config.get('runnable_extensions', DEFAULT_EXT)
        for script_path in auto_run_list:
            if os.path.isfile(script_path):
                ext = os.path.splitext(script_path)[1].lower()
                if ext in runnable_ext:
                    try:
                        self.open_terminal_tab(script_path)
                    except Exception as e:
                        print(f"Failed to auto-run script '{script_path}': {e}")
                else:
                    print(f"Auto-run skipped (unsupported extension): {script_path}")
            else:
                print(f"Auto-run skipped (file does not exist): {script_path}")

    # ======================== HTTP API 辅助方法 ======================================

    def _get_terminal_by_id(self, terminal_id):
        """通过 ID 查找终端标签页"""
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab) and widget.terminal_id == terminal_id:
                return widget
        return None

    def _get_terminal_by_name(self, name):
        """通过脚本名称查找终端标签页（若有多个同名则返回第一个）"""
        matches = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                script_name = os.path.basename(widget.script_path)
                if script_name == name:
                    matches.append(widget)
        return matches[0] if len(matches) == 1 else None

    def _find_script_by_folder_and_name(self, folder, script_name):
        """根据文件夹路径和脚本名查找完整脚本路径"""
        if not os.path.isdir(folder):
            return None
        full_path = os.path.join(folder, script_name)
        if os.path.isfile(full_path):
            ext = os.path.splitext(script_name)[1].lower()
            if ext in self.config.get('supported_extensions', DEFAULT_EXT):
                return full_path
        return None

    def open_config_editor(self):
        """打开配置文件编辑器"""
        # 确保 config 中包含所有默认键（缺失的用默认值填充）
        from utils import _default_config
        for key, value in _default_config.items():
            if key not in self.config:
                self.config[key] = value
        # api 字典特殊处理
        if 'api' not in self.config:
            self.config['api'] = dict(_default_config['api'])
        else:
            for api_key, api_value in _default_config['api'].items():
                if api_key not in self.config['api']:
                    self.config['api'][api_key] = api_value

        dialog = ConfigEditorDialog(self.config, self)
        if dialog.exec_():
            # 用户点击保存后，立即同步配置
            self.on_config_edited()

    def on_config_edited(self):
        """配置被编辑后同步 UI 状态"""
        # 更新自动换行菜单状态
        self.toggle_wrap_action.setChecked(self.config.get('line_wrap_mode', True))

        # 更新语法高亮菜单状态
        syntax_mode = self.config.get('syntax_highlight_mode', 'auto')
        self.syntax_auto_action.setChecked(syntax_mode == 'auto')
        self.syntax_ps1_action.setChecked(syntax_mode == 'ps1')
        self.syntax_bash_action.setChecked(syntax_mode == 'bash')
        self.syntax_command_action.setChecked(syntax_mode == 'command')
        self.syntax_none_action.setChecked(syntax_mode == 'none')

        # 更新启动时最小化到托盘
        self.auto_minimize_action.setChecked(self.config.get('auto_minimize_to_tray', False))

        # 刷新文件树以反映文件夹等变化
        self.refresh_tree()

        # 保存配置到文件
        self.save_config()

    def start_api_server(self):
        """启动 HTTP API 服务器"""
        api_config = self.config.get('api', {})
        enabled = api_config.get('enabled', True)
        if not enabled:
            print("[MainWindow] API 服务器已在配置中禁用，跳过启动")
            return

        bind_ip = api_config.get('bind_ip', '127.0.0.1')
        bind_port = api_config.get('bind_port', 13025)
        auth_token = api_config.get('auth_token', '')

        self.api_thread = ApiServerThread(bind_ip, bind_port, auth_token, self)
        # 连接信号处理
        self.api_thread.execute_signal.connect(self._handle_api_call)
        self.api_thread.start()

    def stop_api_server(self):
        """停止 HTTP API 服务器"""
        if hasattr(self, 'api_thread') and self.api_thread:
            self.api_thread.stop()
            self.api_thread.wait(3000)

    def _handle_api_call(self, method_name, args, result_holder):
        """在主线程中处理 API 调用（由信号触发）"""
        try:
            method = getattr(self, method_name, None)
            if method is None:
                result_holder["error"] = f"Unknown method: {method_name}"
            else:
                result = method(*args)
                result_holder["result"] = result
        except Exception as e:
            result_holder["error"] = str(e)
        finally:
            result_holder["done"].set()

    # ---------- 以下方法在 HTTP 线程被 _invoke_main 调用，实际在主线程执行 ----------

    def api_get_folders(self):
        """返回文件夹路径列表"""
        return {"folders": list(self.config.get("folders", []))}

    def api_get_scripts(self, folder=None):
        """返回脚本列表（可选按文件夹筛选）"""
        scripts = []
        runnable_ext = self.config.get('runnable_extensions', DEFAULT_EXT)
        for f in self.config.get("folders", []):
            if folder and f != folder:
                continue
            if not os.path.isdir(f):
                continue
            for file in sorted(os.listdir(f)):
                full_path = os.path.join(f, file)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in runnable_ext:
                        scripts.append({
                            "folder": f,
                            "name": file,
                            "path": full_path
                        })
        return {"scripts": scripts}

    def api_add_folder(self, path):
        """添加文件夹路径"""
        if not path:
            return {"success": False, "error": "路径不能为空"}
        if not os.path.isdir(path):
            return {"success": False, "error": f"路径不存在或不是文件夹: {path}"}
        if path in self.config["folders"]:
            return {"success": True, "message": "文件夹已存在"}
        self.config["folders"].append(path)
        self.refresh_tree()
        self.save_config()
        return {"success": True, "message": f"已添加文件夹: {path}"}

    def api_remove_folder(self, path):
        """移除文件夹路径"""
        if path not in self.config["folders"]:
            return {"success": False, "error": f"文件夹不在列表中: {path}"}
        self.config["folders"].remove(path)
        self.refresh_tree()
        self.save_config()
        return {"success": True, "message": f"已移除文件夹: {path}"}

    def api_run_script(self, folder, script):
        """运行指定脚本"""
        script_path = self._find_script_by_folder_and_name(folder, script)
        if not script_path:
            return {"success": False, "error": f"脚本未找到: {folder}/{script}"}
        ext = os.path.splitext(script_path)[1].lower()
        if ext not in self.config.get('runnable_extensions', DEFAULT_EXT):
            return {"success": False, "error": f"不支持运行该类型脚本: {ext}"}
        self.open_terminal_tab(script_path)
        # 找到刚创建的终端标签页
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab) and widget.script_path == script_path:
                return {"success": True, "terminal_id": widget.terminal_id, "message": f"已启动脚本: {script}"}
        return {"success": True, "terminal_id": None, "message": f"已启动脚本: {script}"}

    def api_get_terminals(self):
        """返回所有打开的终端信息"""
        terminals = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                script_name = os.path.basename(widget.script_path)
                running = widget.process is not None and widget.process.state() == QProcess.Running
                terminals.append({
                    "id": widget.terminal_id,
                    "name": script_name,
                    "script": widget.script_path,
                    "running": running
                })
        return {"terminals": terminals}

    def api_stop_terminal(self, terminal_id=None, terminal_name=None):
        """终止终端"""
        widget = None
        if terminal_id is not None:
            widget = self._get_terminal_by_id(terminal_id)
            if not widget:
                return {"success": False, "error": f"未找到 ID 为 {terminal_id} 的终端"}
        elif terminal_name:
            widget = self._get_terminal_by_name(terminal_name)
            if not widget:
                return {"success": False, "error": f"未找到唯一名称为 '{terminal_name}' 的终端（可能有多个同名或不存在）"}
        else:
            return {"success": False, "error": "必须提供 id 或 name 参数"}

        widget.stop_process()
        # 找到对应的标签页索引并关闭
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) is widget:
                self.tabs.removeTab(i)
                break
        return {"success": True, "message": f"已终止终端 ID={widget.terminal_id}"}

    def api_stop_all_terminals(self):
        """终止所有终端标签页"""
        count = 0
        # 从后往前遍历并关闭所有终端标签页
        for i in range(self.tabs.count() - 1, -1, -1):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                widget.stop_process()
                self.tabs.removeTab(i)
                count += 1
        return {"success": True, "message": f"已终止 {count} 个终端"}

    def api_get_terminal_output(self, terminal_id=None, terminal_name=None):
        """查看终端输出记录"""
        widget = None
        if terminal_id is not None:
            widget = self._get_terminal_by_id(terminal_id)
            if not widget:
                return {"success": False, "error": f"未找到 ID 为 {terminal_id} 的终端"}
        elif terminal_name:
            widget = self._get_terminal_by_name(terminal_name)
            if not widget:
                return {"success": False, "error": f"未找到唯一名称为 '{terminal_name}' 的终端（可能有多个同名或不存在）"}
        else:
            return {"success": False, "error": "必须提供 id 或 name 参数"}

        return {
            "success": True,
            "id": widget.terminal_id,
            "name": os.path.basename(widget.script_path),
            "output": widget.terminal.toPlainText()
        }

    def api_clear_terminal(self, terminal_id):
        """清空终端输出"""
        widget = self._get_terminal_by_id(terminal_id)
        if not widget:
            return {"success": False, "error": f"未找到 ID 为 {terminal_id} 的终端"}
        widget.clear_screen()
        return {"success": True, "message": f"已清空终端 ID={terminal_id} 的输出"}

    def api_send_terminal_input(self, terminal_id, text):
        """向终端发送字符串"""
        widget = self._get_terminal_by_id(terminal_id)
        if not widget:
            return {"success": False, "error": f"未找到 ID 为 {terminal_id} 的终端"}
        if widget.process is None or widget.process.state() != QProcess.Running:
            return {"success": False, "error": "终端进程未在运行"}
        # 如果文本不以换行结尾，自动追加换行
        if not text.endswith('\n'):
            text += '\n'
        widget.process.write(text.encode('mbcs', errors='replace'))
        return {"success": True, "message": f"已向终端 ID={terminal_id} 发送输入"}

    def api_shutdown(self):
        """关闭 PsLauncher"""
        self.save_config()
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                widget.stop_process()
        # 延迟退出，让响应先发送
        QTimer.singleShot(500, QApplication.quit)
        return {"success": True, "message": "PsLauncher 正在关闭..."}

    def set_syntax_highlight_mode(self, mode):
        """Set syntax highlighting mode"""
        self.config['syntax_highlight_mode'] = mode

        # Update all existing source code tabs
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab):
                # Reapply syntax highlighting
                widget.apply_syntax_highlight_mode(mode)

        # Save configuration
        self.save_config()

        # Update menu item selection state
        self.syntax_auto_action.setChecked(mode == 'auto')
        self.syntax_ps1_action.setChecked(mode == 'ps1')
        self.syntax_bash_action.setChecked(mode == 'bash')
        self.syntax_command_action.setChecked(mode == 'command')
        self.syntax_none_action.setChecked(mode == 'none')


def apply_dark_theme(app):
    """Apply dark theme to the entire application"""
    dark_palette = QPalette()

    # Basic colors
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    # Disabled state colors
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    app.setPalette(dark_palette)
    app.setStyle("Fusion")


def apply_font_scaling(app, scale_factor):
    """Apply global font scaling"""
    font = app.font()
    if scale_factor != 1.0:
        font.setPointSize(int(font.pointSize() * scale_factor))
        app.setFont(font)


# ================= Program Entry Point =================
if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PsLauncher - A general script launcher')
    parser.add_argument('--scale', type=float, help='window DPI scale')
    parser.add_argument('--light', action='store_true', help='use light theme')
    parser.add_argument('--dark', action='store_true', help='use dark theme')
    parser.add_argument('--font', type=str, help='set font family')
    parser.add_argument('--height', type=int, help='window height')
    parser.add_argument('--width', type=int, help='window width')
    parser.add_argument('--line_wrap_mode', action='store_true', help='set auto line wrap')
    parser.add_argument('--headless', action='store_true', help='headless mode: no GUI window, only API server')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Load configuration file
    config = load_json_with_comments(CONFIG_FILE)

    # Apply theme
    dark_mode = True
    if args.light:
        app.setStyle("Fusion")
        dark_mode = False
    else:
        if args.dark:
            apply_dark_theme(app)
            dark_mode = True
        else:
            if config.get("dark_mode", True):
                apply_dark_theme(app)
                dark_mode = True
            else:
                app.setStyle("Fusion")
                dark_mode = False

    # Apply font scaling (command-line arguments take precedence over configuration file)
    scale_factor = 1.0
    if args.scale:
        scale_factor = args.scale
    elif "font_scale" in config:
        scale_factor = config["font_scale"]

    if scale_factor != 1.0:
        apply_font_scaling(app, scale_factor)

    # Apply font
    font_family = config["font_family"]
    if args.font:
        font_family = args.font

    # Window size
    height = config["height_value"]
    if args.height:
        height = args.height

    width = config["width_value"]
    if args.width:
        width = args.width

    # Auto wrap
    line_wrap_mode = False
    if args.line_wrap_mode:
        line_wrap_mode = True
    else:
        if config.get("line_wrap_mode", True):
            line_wrap_mode = True
        else:
            line_wrap_mode = False

    window = MainWindow(font_family, height, width, dark_mode, line_wrap_mode)

    # 启动 HTTP API 服务器
    window.start_api_server()

    # 启动时自动运行配置中标记的脚本
    window.run_auto_start_scripts()

    if args.headless:
        # 无头模式：不显示 GUI 窗口，仅通过 API 服务
        print("[PsLauncher] 无头模式启动，GUI 窗口已隐藏")
        print("[PsLauncher] 请通过 HTTP API 操作: http://127.0.0.1:13025")
        # 不调用 show()
    else:
        window.show()
        # 如果配置了启动时自动最小化到托盘，则在显示后立即隐藏
        if config.get('auto_minimize_to_tray', False):
            window.hide_to_tray()

    # 注册 SIGINT（Ctrl+C）处理器，使终端可以正常终止程序
    def sigint_handler(signum, frame):
        """在终端中按下 Ctrl+C 时优雅退出 Qt 事件循环"""
        QApplication.quit()
    signal.signal(signal.SIGINT, sigint_handler)

    # 创建一个 200ms 定时器周期触发回调，确保 Python 信号处理器能被 Qt 事件循环处理
    signal_timer = QTimer()
    signal_timer.start(200)
    signal_timer.timeout.connect(lambda: None)

    exit_code = app.exec_()
    # 程序退出前停止 API 服务器
    window.stop_api_server()
    sys.exit(exit_code)
