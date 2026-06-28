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


# Main window
class MainWindow(QMainWindow):

    def __init__(self, font_family, h, w, dark_mode, line_wrap_mode):
        super().__init__()
        self.setWindowTitle("PsLauncher")
        self.resize(w, h)
        self.config = load_json_with_comments(CONFIG_FILE)

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

        sys_menu = menubar.addMenu("System")

        save_action = QAction("Save current configuration", self)
        save_action.triggered.connect(self.save_config)
        sys_menu.addAction(save_action)

        sys_menu.addSeparator()
        hide_action = QAction("Hide window to system tray", self)
        hide_action.setShortcut("F10")
        hide_action.triggered.connect(self.hide_to_tray)
        sys_menu.addAction(hide_action)

        sys_menu.addSeparator()
        self.auto_minimize_action = QAction("Auto-minimize to tray on startup", self)
        self.auto_minimize_action.setCheckable(True)
        self.auto_minimize_action.setChecked(self.config.get('auto_minimize_to_tray', False))
        self.auto_minimize_action.triggered.connect(self.toggle_auto_minimize_to_tray)
        sys_menu.addAction(self.auto_minimize_action)

        # File menu
        file_menu = menubar.addMenu("File")

        addpath_action = QAction("Add folder path", self)
        addpath_action.setShortcut("F2")
        addpath_action.triggered.connect(self.add_folder)
        file_menu.addAction(addpath_action)
        removepath_action = QAction("Remove folder path", self)
        removepath_action.setShortcut("F3")
        removepath_action.triggered.connect(self.remove_folder)
        file_menu.addAction(removepath_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        copy_action = QAction("Copy selected content", self)
        copy_action.triggered.connect(self.copy_selected_text)
        copy_action.setShortcut("F11")
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste_text)
        paste_action.setShortcut("F12")
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()
        copy_all_action = QAction("Copy all tabs to clipboard", self)
        copy_all_action.triggered.connect(self.copy_all_text)
        edit_menu.addAction(copy_all_action)

        # Clear terminal screen menu item
        clear_screen_action = QAction("🧹Clear Terminal Screen", self)
        clear_screen_action.triggered.connect(self.clear_current_terminal)
        clear_screen_action.setShortcut("Ctrl+L")
        clear_screen_action.setToolTip("Clear all displayed content in the current terminal tab")
        edit_menu.addAction(clear_screen_action)

        edit_menu.addSeparator()
        # Edit/Save menu item
        self.edit_save_action = QAction("Edit script source code", self)
        self.edit_save_action.setShortcut("F4")
        self.edit_save_action.setToolTip("Enter/Exit edit mode, save script changes")
        self.edit_save_action.triggered.connect(self.toggle_edit_save)
        edit_menu.addAction(self.edit_save_action)

        # Run menu
        tools_menu = menubar.addMenu("Run")

        run_action = QAction("Start script", self)
        run_action.triggered.connect(self.run_selected_script)
        run_action.setShortcut("F5")
        tools_menu.addAction(run_action)

        stop_action = QAction("Stop script (force terminate)", self)
        stop_action.triggered.connect(self.stop_current_script)
        stop_action.setShortcut("F6")
        tools_menu.addAction(stop_action)

        # Send Ctrl+C interrupt
        send_ctrlc_action = QAction("Send Ctrl+C interrupt", self)
        send_ctrlc_action.triggered.connect(self.send_ctrl_c_to_current_terminal)
        send_ctrlc_action.setShortcut("F7")
        send_ctrlc_action.setToolTip("Send Ctrl+C interrupt signal (0x03) to the current terminal process")
        tools_menu.addAction(send_ctrlc_action)

        # View menu
        view_menu = menubar.addMenu("View")

        # Auto wrap toggle menu item
        self.toggle_wrap_action = QAction("Toggle auto wrap mode", self)
        self.toggle_wrap_action.setCheckable(True)
        self.toggle_wrap_action.setChecked(self.config['line_wrap_mode'])
        self.toggle_wrap_action.triggered.connect(self.toggle_line_wrap_mode)
        view_menu.addAction(self.toggle_wrap_action)

        # Syntax highlighting method submenu
        syntax_menu = view_menu.addMenu("Syntax highlighting method")

        # Auto mode
        self.syntax_auto_action = QAction("Auto (select by extension)", self)
        self.syntax_auto_action.setCheckable(True)
        self.syntax_auto_action.triggered.connect(lambda: self.set_syntax_highlight_mode('auto'))
        syntax_menu.addAction(self.syntax_auto_action)

        # PowerShell mode
        self.syntax_ps1_action = QAction("PowerShell (ps1)", self)
        self.syntax_ps1_action.setCheckable(True)
        self.syntax_ps1_action.triggered.connect(lambda: self.set_syntax_highlight_mode('ps1'))
        syntax_menu.addAction(self.syntax_ps1_action)

        # Bash mode
        self.syntax_bash_action = QAction("Bash (sh)", self)
        self.syntax_bash_action.setCheckable(True)
        self.syntax_bash_action.triggered.connect(lambda: self.set_syntax_highlight_mode('bash'))
        syntax_menu.addAction(self.syntax_bash_action)

        # Command mode
        self.syntax_command_action = QAction("Command (batch)", self)
        self.syntax_command_action.setCheckable(True)
        self.syntax_command_action.triggered.connect(lambda: self.set_syntax_highlight_mode('command'))
        syntax_menu.addAction(self.syntax_command_action)

        # No coloring mode
        self.syntax_none_action = QAction("No coloring", self)
        self.syntax_none_action.setCheckable(True)
        self.syntax_none_action.triggered.connect(lambda: self.set_syntax_highlight_mode('none'))
        syntax_menu.addAction(self.syntax_none_action)

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

        # Script management menu
        script_menu = menubar.addMenu("Script Management")

        new_folder_action = QAction("New Path", self)
        new_folder_action.triggered.connect(self.new_folder_at_location)
        script_menu.addAction(new_folder_action)

        new_script_action = QAction("New Script", self)
        new_script_action.triggered.connect(self.new_script_in_folder)
        script_menu.addAction(new_script_action)

        rename_script_action = QAction("Rename Script", self)
        rename_script_action.triggered.connect(self.rename_selected_script)
        script_menu.addAction(rename_script_action)

        copy_script_action = QAction("Copy Script", self)
        copy_script_action.triggered.connect(self.copy_selected_script)
        script_menu.addAction(copy_script_action)

        move_script_action = QAction("Move Script", self)
        move_script_action.triggered.connect(self.move_selected_script)
        script_menu.addAction(move_script_action)

        delete_script_action = QAction("Delete Script", self)
        delete_script_action.triggered.connect(self.delete_selected_script)
        script_menu.addAction(delete_script_action)

        # Tab management functionality
        tab_menu = menubar.addMenu("Tab")
        close_editor_tabs_action = QAction("Close all source code tabs", self)
        close_editor_tabs_action.triggered.connect(self.close_all_editor_tabs)
        close_editor_tabs_action.setShortcut("F8")
        tab_menu.addAction(close_editor_tabs_action)

        close_terminal_tabs_action = QAction("Close all terminal tabs", self)
        close_terminal_tabs_action.triggered.connect(self.close_all_terminal_tabs)
        close_terminal_tabs_action.setShortcut("F9")
        tab_menu.addAction(close_terminal_tabs_action)

        close_all_tabs_action = QAction("Close all tabs", self)
        close_all_tabs_action.triggered.connect(self.close_all_tabs)
        tab_menu.addAction(close_all_tabs_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.open_help)
        help_menu.addAction(help_action)
        help_action.setShortcut("F1")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.open_about)
        help_menu.addAction(about_action)

        # ======================== Toolbar ======================================

        toolbar = QToolBar("Main Toolbar")
        # Set toolbar to be movable and allow wrapping
        toolbar.setMovable(True)
        toolbar.setFloatable(False)
        # Set toolbar button style, using icons and text
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # Enable toolbar overflow menu functionality
        toolbar.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.addToolBar(toolbar)

        # System tray button
        self.tray_btn = QAction(self)
        self.tray_btn.setText("📌Hide")
        self.tray_btn.setToolTip("Hide window to system tray, restore window by clicking the tray icon")
        self.tray_btn.triggered.connect(self.hide_to_tray)
        toolbar.addAction(self.tray_btn)

        toolbar.addSeparator()
        self.run_btn = QAction(self)
        self.run_btn.setText("▶️Run")
        self.run_btn.setToolTip("Run the script of the currently focused tab")
        self.run_btn.triggered.connect(self.run_selected_script)
        toolbar.addAction(self.run_btn)

        self.stop_btn = QAction(self)
        self.stop_btn.setText("⏹️Stop")
        self.stop_btn.setToolTip("Stop the script of the currently focused tab (force terminate process tree)")
        self.stop_btn.triggered.connect(self.stop_current_script)
        toolbar.addAction(self.stop_btn)

        # Send Ctrl+C interrupt button
        self.send_ctrlc_btn = QAction(self)
        self.send_ctrlc_btn.setText("❌Interrupt")
        self.send_ctrlc_btn.setToolTip("Send Ctrl+C interrupt signal (0x03) to the current terminal process, used for graceful interruption of running scripts")
        self.send_ctrlc_btn.triggered.connect(self.send_ctrl_c_to_current_terminal)
        toolbar.addAction(self.send_ctrlc_btn)

        # 清除终端屏幕按钮
        self.clear_screen_btn = QAction(self)
        self.clear_screen_btn.setText("🧹Clear")
        self.clear_screen_btn.setToolTip("Clear all displayed content in the current terminal tab")
        self.clear_screen_btn.triggered.connect(self.clear_current_terminal)
        toolbar.addAction(self.clear_screen_btn)

        toolbar.addSeparator()

        # Copy/Paste function buttons
        self.copy_btn = QAction(self)
        self.copy_btn.setText("📋Copy")
        self.copy_btn.setToolTip("Copy the selected text to the clipboard. If no text is selected, copy all text from the current focused tab.")

        self.copy_btn.triggered.connect(self.copy_selected_text)
        toolbar.addAction(self.copy_btn)

        self.paste_btn = QAction(self)
        self.paste_btn.setText("📤Paste")
        self.paste_btn.setToolTip("Paste the clipboard content to the cursor position")
        self.paste_btn.triggered.connect(self.paste_text)
        toolbar.addAction(self.paste_btn)

        toolbar.addSeparator()
        self.close_editor_tabs_btn = QAction(self)
        self.close_editor_tabs_btn.setText("🗑️Close All Source Code")
        self.close_editor_tabs_btn.setToolTip("Close all read-only source code view tabs")
        self.close_editor_tabs_btn.triggered.connect(self.close_all_editor_tabs)
        toolbar.addAction(self.close_editor_tabs_btn)

        # Edit/Save Button
        self.edit_save_btn = QAction(self)
        self.edit_save_btn.setText("✏️Quick Edit")
        self.edit_save_btn.setToolTip("Enter/Exit edit mode, save script changes")
        self.edit_save_btn.triggered.connect(self.toggle_edit_save)
        toolbar.addAction(self.edit_save_btn)

        toolbar.addSeparator()

        # Quick Close Button

        self.close_terminal_tabs_btn = QAction(self)
        self.close_terminal_tabs_btn.setText("🚫Terminate All Terminals")
        self.close_terminal_tabs_btn.setToolTip("Close all terminal tabs, including running and finished ones")
        self.close_terminal_tabs_btn.triggered.connect(self.close_all_terminal_tabs)
        toolbar.addAction(self.close_terminal_tabs_btn)

        self.close_all_tabs_btn = QAction(self)
        self.close_all_tabs_btn.setText("💥Close All Tabs")
        self.close_all_tabs_btn.setToolTip(
            "Close all tabs. This will close all source code tabs and all terminal tabs. If a terminal is currently executing, it will be forcibly terminated. This may cause running programs or scripts to exit abnormally."
        )
        self.close_all_tabs_btn.triggered.connect(self.close_all_tabs)
        toolbar.addAction(self.close_all_tabs_btn)

        # ======================== Resource Explorer ======================================

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Resource Explorer")
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

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to scan")
        if folder and folder not in self.config["folders"]:
            self.config["folders"].append(folder)
            self.refresh_tree()
            self.save_config()

    def remove_folder(self):
        """Remove the selected folder or let the user choose which folder to remove"""
        if not self.config.get("folders"):
            QMessageBox.information(self, "Info", "No removable folders are available.")
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
            reply = QMessageBox.question(self, 'Confirm', f'Are you sure you want to remove folder "{folder_name}"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.config["folders"].remove(selected_folder)
                self.refresh_tree()
                self.save_config()
                return

        # If no folder is selected or the selected is not a folder, display a folder selection dialog
        folder, ok = QInputDialog.getItem(self, "Remove Folder", "Select folder to remove:", self.config["folders"], 0, False)
        if ok and folder:
            folder_name = os.path.basename(folder.rstrip(os.sep))
            reply = QMessageBox.question(self, 'Confirm', f'Are you sure you want to remove folder "{folder_name}"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
            warnings.append(f"Default suffixes are missing from the supported list: {', '.join(missing_in_supported)}")
        if missing_in_runnable:
            warnings.append(f"Default suffixes are missing from the runnable list: {', '.join(missing_in_runnable)}")

        if warnings:
            warning_message = "Warning:\n" + "\n".join(warnings)
            warning_message += "\n\nUnable to save your current configuration. This may cause some scripts to fail to display or run correctly."

            # Display the warning directly in a popup and return immediately without making any changes
            QMessageBox.warning(self, "Configuration Warning", warning_message)
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
                            script_item.setToolTip(0, full_path + "\n(Auto-run on startup)")

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
        tab_name = f"📝 {filename}"

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
                    QMessageBox.information(self, "Failed", f"Script file '{os.path.basename(script_path)}' extension {ext} is not in the list of runnable extensions.", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Failed", "The selected path is not a valid file.", QMessageBox.Ok)
            return

        # No script path provided, get script path based on current focused tab
        current_widget = self.tabs.currentWidget()
        if current_widget is None:
            # If no tabs are open, fallback to using the current item in the file tree
            item = self.tree.currentItem()
            if not item:
                QMessageBox.information(self, "Failed", "No focused tab. You must select a program first before clicking the Run button", QMessageBox.Ok)
                return
            script_path = item.data(0, Qt.UserRole)
            if script_path:
                if os.path.isfile(script_path):
                    ext = os.path.splitext(script_path)[1].lower()
                    if ext in self.config.get('runnable_extensions', DEFAULT_EXT):
                        self.open_terminal_tab(script_path)
                    else:
                        QMessageBox.information(self, "Failed", f"Script file '{os.path.basename(script_path)}' extension {ext} is not in the list of runnable extensions.", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Failed", "The selected path is not a valid file.", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Failed", "No focused tab. You must select a program first before clicking the Run button", QMessageBox.Ok)
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
            QMessageBox.information(self, "Failed", "The current tab is not a script tab, so it cannot be run.", QMessageBox.Ok)
            return

        # Run script
        if script_path and os.path.isfile(script_path):
            ext = os.path.splitext(script_path)[1].lower()
            if ext in self.config.get('runnable_extensions', DEFAULT_EXT):
                self.open_terminal_tab(script_path)
            else:
                QMessageBox.information(self, "Failed", f"The extension '{os.path.basename(script_path)}' of the script file is not in the list of runnable extensions.", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Failed", "Unable to retrieve a valid script path.", QMessageBox.Ok)

    def open_terminal_tab(self, script_path):
        filename = os.path.basename(script_path)
        # Create a separate tab for the running program, using different emojis for visual distinction
        tab_name = f"🖥️ {filename}"
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
            QMessageBox.information(self, "Prompt", "The current tab is not a terminal tab and cannot send Ctrl+C interrupt.", QMessageBox.Ok)

    def clear_current_terminal(self):
        """Clear all displayed content in the current terminal tab"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, TerminalTab):
            current_widget.clear_screen()
        else:
            QMessageBox.information(self, "Information", "The current tab is not a terminal tab and cannot clear the screen.", QMessageBox.Ok)

    def close_tab(self, index):
        widget = self.tabs.widget(index)

        # First check if it is a source code tab and is in editing mode
        if isinstance(widget, EditorTab) and widget.is_editing:
            filename = os.path.basename(widget.script_path)
            reply = QMessageBox.question(self, 'Close Tab', f'Tab "{filename}" is being edited. Do you want to save changes?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                         QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Save:
                success = widget.save_file()
                if not success:
                    QMessageBox.warning(self, "Save Failed", "File save failed. Please check file permissions or path.", QMessageBox.Ok)
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
                message = f'Tab "{filename}" is being edited. Do you want to save changes?'
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = f'There are {editing_count} tabs being edited:\n{files_list}\n\nDo you want to save changes?'

            reply = QMessageBox.question(self, 'Close All Source Code Tabs', message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # User cancelled closing

            # Process tabs that need to be saved
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, "Save Failed", f'Failed to save file: {os.path.basename(widget.script_path)}\nPlease check file permissions or path.', QMessageBox.Ok)
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
        reply = QMessageBox.question(self, 'Confirm', f'Sure you want to close all {terminal_count} running tabs? This will stop all running scripts.', QMessageBox.Yes | QMessageBox.No,
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
                message = f'Tab "{filename}" is being edited. Do you want to save changes?'
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = f'The following {editing_count} tabs are being edited:\n{files_list}\n\nDo you want to save changes?'

            reply = QMessageBox.question(self, 'Close All Tabs', message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # User cancelled closing

            # Process tabs that need to be saved
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, "Save Failed", f'Failed to save file: {os.path.basename(widget.script_path)}\nPlease check file permissions or path.', QMessageBox.Ok)
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
            reply = QMessageBox.question(self, 'Confirm', f'Are you sure you want to close all {total_tabs} tabs?\nThis includes {terminal_count} terminal tabs and will stop all running scripts.',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            reply = QMessageBox.question(self, 'Confirm', f'Are you sure you want to close all {total_tabs} tabs?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

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
            QMessageBox.information(self, "Notice", "The current tab is not the Source Code tab, so editing mode cannot be entered.", QMessageBox.Ok)
            return

        editor_tab = current_widget

        if not editor_tab.is_editing:
            # Not currently in edit mode, attempt to enter edit mode
            editor_tab.set_editing(True)
            # Update button and menu text
            self.edit_save_action.setText("💾Save")
            self.edit_save_btn.setText("💾Save")
            self.edit_save_action.setToolTip("Save script changes")
            self.edit_save_btn.setToolTip("Save script changes")
        else:
            # Currently in edit mode, attempt to save
            reply = QMessageBox.question(self, 'Confirm', 'Do you want to save changes?\nThis will overwrite the original file.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                success = editor_tab.save_file()
                if success:
                    editor_tab.set_editing(False)
                    # Update buttons and menu text
                    self.edit_save_action.setText("✏️Edit Mode")
                    self.edit_save_btn.setText("✏️Edit")
                    self.edit_save_action.setToolTip("Enter/Exit Edit Mode, Save Script Changes")
                    self.edit_save_btn.setToolTip("Enter/Exit Edit Mode, Save Script Changes")
                else:
                    QMessageBox.warning(self, "Failed", "File save failed, please check file permissions or path. If it's a system directory, you may need to run with administrator privileges.",
                                        QMessageBox.Ok)
            else:
                # User cancelled save, need to reload file content to restore original state
                editor_tab.set_editing(False)
                # Reload file content to discard user's modifications
                editor_tab.load_file(editor_tab.script_path)
                # Update buttons and menu text
                self.edit_save_action.setText("✏️Edit Mode")
                self.edit_save_btn.setText("✏️Edit")
                self.edit_save_action.setToolTip("Enter/Exit Edit Mode, Save Script Changes")
                self.edit_save_btn.setToolTip("Enter/Exit Edit Mode, Save Script Changes")

    def update_edit_save_state(self):
        """Update Edit/Save Button State Based on Current Tab Type"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, EditorTab):
            editor_tab = current_widget
            if editor_tab.is_editing:
                self.edit_save_action.setText("💾Save")
                self.edit_save_btn.setText("💾Save")
                self.edit_save_action.setToolTip("Save script changes")
                self.edit_save_btn.setToolTip("Save script changes")
            else:
                self.edit_save_action.setText("✏️Edit Mode")
                self.edit_save_btn.setText("✏️Edit")
                self.edit_save_action.setToolTip("Enter/Exit edit mode, save script changes")
                self.edit_save_btn.setToolTip("Enter/Exit edit mode, save script changes")
        else:
            # Not a source code tab, restore default text
            self.edit_save_action.setText("✏️Edit Mode")
            self.edit_save_btn.setText("✏️Edit")
            self.edit_save_action.setToolTip("Enter/Exit edit mode, save script changes")
            self.edit_save_btn.setToolTip("Enter/Exit edit mode, save script changes")

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
        self.tray_icon.setToolTip("PsLauncher - Script Manager")

        # Create tray menu
        self.tray_menu = QMenu(self)

        # Open window menu item
        show_action = QAction("Open Window", self)
        show_action.triggered.connect(self.show_from_tray)
        self.tray_menu.addAction(show_action)

        # Separator
        self.tray_menu.addSeparator()

        # Exit menu item
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_from_tray)
        self.tray_menu.addAction(exit_action)

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
            self.tray_icon.showMessage("PsLauncher", "Program minimized to system tray", QSystemTrayIcon.Information, 2000)

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
        reply = QMessageBox.question(self, 'Prompt', 'Are you sure you want to exit PsLauncher?\nThis will stop all running scripts.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

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
            reply = QMessageBox.Yes                                                                                                                                                       # Went through a round of all source code tabs, what's the point of confirming?
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit PsLauncher? This will stop all running scripts.', QMessageBox.Yes | QMessageBox.No,
                                                 QMessageBox.No)
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
                QMessageBox.warning(self, "Warning", "Please add a folder path to the program first.", QMessageBox.Ok)
                return

        # Pop up a dialog to let the user enter a new folder name
        folder_name, ok = QInputDialog.getText(self, "New Path", "Please enter the new folder name:\n(Will be created under the selected path)", QLineEdit.Normal, "")
        if not ok or not folder_name.strip():
            return

        # Construct the full path
        new_folder_path = os.path.join(selected_folder, folder_name.strip())

        # Check if the path already exists
        if os.path.exists(new_folder_path):
            QMessageBox.warning(self, "Warning", f"Path already exists: {new_folder_path}", QMessageBox.Ok)
            return

        try:
            os.makedirs(new_folder_path)
            QMessageBox.information(self, "Success", f"Folder created successfully: {new_folder_path}", QMessageBox.Ok)
            # Optional: Add the new folder to the configuration
            if new_folder_path not in self.config["folders"]:
                self.config["folders"].append(new_folder_path)
                self.save_config()
                self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create folder: {str(e)}. Sometimes this is due to permission issues, please check if the program is running with administrator privileges.",
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
                folder, ok = QInputDialog.getItem(self, "Select Folder", "Please select the folder where you want to create the script:", self.config["folders"], 0, False)
                if not ok:
                    return
                selected_folder = folder
            else:
                QMessageBox.warning(self, "Warning", "Please add a folder path to the program first.", QMessageBox.Ok)
                return

        # Show dialog to let user enter file name
        file_name, ok = QInputDialog.getText(
            self, "New Script", "Please enter the script file name (including extension, e.g., myscript.ps1):\n"
            "Note: The program will not automatically add the extension. If you do not enter an extension, the file will have no extension.\n"
            f"Note: PsLauncher only scans {DEFAULT_EXT} extensions. If the extension is incorrect, the created file will not be visible immediately here.", QLineEdit.Normal, "new_script.ps1")
        if not ok or not file_name.strip():
            return

        # Check if the extension has changed
        new_ext = os.path.splitext(file_name)[1].lower()

        # If the new extension is not a supported type, prompt for confirmation
        if new_ext and new_ext not in DEFAULT_EXT:
            reply = QMessageBox.question(
                self, "Extension Warning", f"The extension you entered {new_ext} is not a supported script type for PsLauncher ({DEFAULT_EXT}).\n"
                "This will cause the file to not appear in the list unless the file name extension is manually edited again.\n\n"
                "Do you confirm to continue naming?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # If there is no extension, prompt the user to confirm
        if not new_ext:
            reply = QMessageBox.question(
                self, "No Extension Warning", f"The file name you entered has no extension, which may cause the file to not appear in the list.\n"
                f"It is recommended to use supported extensions such as {DEFAULT_EXT}.\n\n"
                "Do you confirm to continue naming?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        file_name = file_name.strip()
        # Construct the full path
        new_file_path = os.path.join(selected_folder, file_name)

        # Check if the file already exists
        if os.path.exists(new_file_path):
            reply = QMessageBox.question(self, "Confirm", f"File already exists: {new_file_path}\nOverwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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

            QMessageBox.information(self, "Success", f"Script created successfully: {new_file_path}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create script: {str(e)}", QMessageBox.Ok)

    def rename_selected_script(self):
        """Rename the selected script name, check if the suffix is a supported script type"""
        # Get the currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Prompt", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Prompt", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        old_ext = os.path.splitext(old_file_name)[1].lower() # Original file extension

        # Pop up a dialog to let the user enter the new file name
        new_file_name, ok = QInputDialog.getText(
            self, "Rename Script", f"Please enter the new script file name:\n"
            f"Current file name: {old_file_name}\n"
            "Note: The program will not automatically add the suffix. If you do not enter a suffix, the file will have no extension.\n"
            f"Note: PsLauncher only scans {DEFAULT_EXT} these three suffixes. If the suffix is incorrect, the file will not be visible immediately after creation.", QLineEdit.Normal, old_file_name)
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
                self, "Suffix Warning", f"The suffix {new_ext} you entered is not a script type supported by PsLauncher ({DEFAULT_EXT}).\n"
                "This will cause the file to not appear in the list after renaming, unless you manually edit the file name suffix again.\n\n"
                "Do you confirm to continue renaming?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # If there is no suffix, prompt the user to confirm
        if not new_ext:
            reply = QMessageBox.question(
                self, "No Suffix Warning", f"The file name you entered has no suffix, which may cause the file to not appear in the list.\n"
                f"It is recommended to use supported suffixes such as {DEFAULT_EXT}.\n\n"
                "Do you confirm to continue renaming?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        new_file_path = os.path.join(folder_path, new_file_name)

        # Check if the new file already exists
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "Warning", f"File already exists: {new_file_path}", QMessageBox.Ok)
            return

        try:
            os.rename(script_path, new_file_path)
            QMessageBox.information(self, "Success", f"Renaming successful: {old_file_name} -> {new_file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Renaming failed: {str(e)}", QMessageBox.Ok)

    def copy_selected_script(self):
        """Copy the selected script (prompt the user to rename the file name)"""
        # Get the currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Prompt", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Prompt", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        name, ext = os.path.splitext(old_file_name)

        # Generate default new filename: original filename with _copy
        default_new_name = name + "_copy" + ext

        # Pop up dialog to prompt user to rename file
        new_file_name, ok = QInputDialog.getText(
            self, "Copy Script", f"Please enter the name for the copied script:\n"
            f"Original filename: {old_file_name}\n"
            "Note: The program will not automatically add an extension. If you do not enter an extension, the file will have no extension.\n"
            f"Note: PsLauncher only scans {DEFAULT_EXT} extensions. If the extension is incorrect, the file will not appear immediately after creation.", QLineEdit.Normal, default_new_name)

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
            QMessageBox.warning(self, "Warning", f"File '{new_file_name}' already exists in the target folder.\n"
                                "Please use a different filename. Copy operation canceled.", QMessageBox.Ok)
            return # Refuse to perform any copy operation

        # Execute copy operation
        try:
            shutil.copy2(script_path, new_file_path)
            QMessageBox.information(self, "Success", f"Copy successful!\n"
                                    f"Original file: {old_file_name}\n"
                                    f"New file: {new_file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Copy failed: {str(e)}", QMessageBox.Ok)

    def move_selected_script(self):
        """Move current script to a loaded path (requires confirmation)"""
        # Get currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Info", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Info", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)

        # If no available target folder, prompt user
        if not self.config.get("folders"):
            QMessageBox.warning(self, "Warning", "No available target folder. Please add folder path first.", QMessageBox.Ok)
            return

        # Pop up dialog to let user select target folder
        target_folder, ok = QInputDialog.getItem(self, "Move Script", f"Select folder to move script '{old_file_name}' to:", self.config["folders"], 0, False)
        if not ok:
            return

        # Check if target folder exists
        if not os.path.exists(target_folder):
            QMessageBox.warning(self, "Warning", f"Target folder does not exist: {target_folder}", QMessageBox.Ok)
            return

        # Construct target path
        target_path = os.path.join(target_folder, old_file_name)

        # Check if target file already exists
        if os.path.exists(target_path):
            reply = QMessageBox.question(self, "Confirm", f"Target folder already contains a file with the same name: {old_file_name}\nOverwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # Display confirmation dialog
        reply = QMessageBox.question(self, "Confirm Move", f"Are you sure you want to move script '{old_file_name}' to '{target_folder}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            shutil.move(script_path, target_path)
            QMessageBox.information(self, "Success", f"Move successful: {old_file_name} has been moved to {target_folder}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Move failed: {str(e)}", QMessageBox.Ok)

    def delete_selected_script(self):
        """Delete selected script (requires confirmation dialog)"""
        # Get currently selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Prompt", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Prompt", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        file_name = os.path.basename(script_path)

        # Display confirmation dialog
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete script '{file_name}'?\nThis operation is irreversible! Files are directly deleted, not moved to Recycle Bin or similar.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            os.remove(script_path)
            QMessageBox.information(self, "Success", f"Delete successful: {file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}", QMessageBox.Ok)

    def open_in_vsc(self, file_path):
        """Open the specified file in VSCode"""
        try:
            subprocess.run(['code', file_path], check=True)
        except FileNotFoundError:
            QMessageBox.warning(self, "Failed", "VSCode (code command) not found.\nPlease ensure VSCode is installed and added to the system environment variable PATH.", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Failed", f"Error calling VSCode:\n{str(e)}", QMessageBox.Ok)

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
                    open_folder_action = QAction("📂 Open in Explorer", self)
                    open_folder_action.triggered.connect(lambda: os.startfile(path))
                    menu.addAction(open_folder_action)

                elif os.path.isfile(path):
                    ext = os.path.splitext(path)[1].lower()
                    if ext in self.config.get('supported_extensions', DEFAULT_EXT):
                        # Script item: show script management menu
                        run_action = QAction("▶️ Run", self)
                        run_action.triggered.connect(lambda: self.run_selected_script(path))
                        menu.addAction(run_action)

                        menu.addSeparator()

                        edit_action = QAction("✏️ Edit/Save", self)
                        edit_action.triggered.connect(lambda: (self.open_editor_tab(path), self.toggle_edit_save()))
                        menu.addAction(edit_action)

                        # 启动时自动运行开关 (仅对可运行后缀的脚本显示)
                        runnable_ext = self.config.get('runnable_extensions', DEFAULT_EXT)
                        if ext in runnable_ext:
                            script_path = path # 捕获当前路径供 lambda 使用（闭包捕获）
                            if self.is_script_auto_run(path):
                                auto_run_action = QAction("🔄 Stop auto-starting this script on launch", self)
                            else:
                                auto_run_action = QAction("🔄 Auto-start this script on launch", self)
                                               # triggered 信号会传入 checked(bool) 参数，必须显式接收并忽略
                            auto_run_action.triggered.connect(lambda _checked=False, sp=script_path: self.toggle_auto_run_script(sp))
                            menu.addAction(auto_run_action)

                            menu.addSeparator()

                        # Edit with VSCode
                        vsc_action = QAction("💻 Edit with VSC", self)
                        vsc_action.setToolTip("Try calling VSCode to open the file for editing")
                        vsc_action.triggered.connect(lambda _checked=False, p=path: self.open_in_vsc(p))
                        menu.addAction(vsc_action)

                        menu.addSeparator()

                        rename_action = QAction("📝 Rename", self)
                        rename_action.triggered.connect(self.rename_selected_script)
                        menu.addAction(rename_action)

                        copy_action = QAction("📋 Copy", self)
                        copy_action.triggered.connect(self.copy_selected_script)
                        menu.addAction(copy_action)

                        move_action = QAction("🚚 Move", self)
                        move_action.triggered.connect(self.move_selected_script)
                        menu.addAction(move_action)

                        delete_action = QAction("🗑️ Delete", self)
                        delete_action.triggered.connect(self.delete_selected_script)
                        menu.addAction(delete_action)
                    else:
                        # Other file types, only show View menu
                        view_action = QAction("📄 View", self)
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
            add_action = QAction("📂 Add Folder Path", self)
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
        cut_action = QAction("✂️ Cut", self)
        cut_action.triggered.connect(self.cut_selected_text)
        menu.addAction(cut_action)

        copy_action = QAction("📋 Copy", self)
        copy_action.triggered.connect(self.copy_selected_text)
        menu.addAction(copy_action)

        paste_action = QAction("📤 Paste", self)
        paste_action.triggered.connect(self.paste_text)
        menu.addAction(paste_action)

        menu.addSeparator()

        # For source code tabs, support edit or save functionality
        current_widget = self.tabs.widget(tab_idx)
        if isinstance(current_widget, EditorTab):
            if current_widget.is_editing:
                save_action = QAction("💾 Save", self)
                save_action.triggered.connect(self.toggle_edit_save)
                menu.addAction(save_action)
            else:
                edit_action = QAction("✏️ Edit", self)
                edit_action.triggered.connect(self.toggle_edit_save)
                menu.addAction(edit_action)

        menu.addSeparator()

        # Close tab
        close_action = QAction("🗑️ Close Tab", self)
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
    window.show()

    # 启动时自动运行配置中标记的脚本
    window.run_auto_start_scripts()

    # 如果配置了启动时自动最小化到托盘，则在显示后立即隐藏
    if config.get('auto_minimize_to_tray', False):
        window.show()
        window.hide_to_tray()
    else:
        window.show()

    sys.exit(app.exec_())
