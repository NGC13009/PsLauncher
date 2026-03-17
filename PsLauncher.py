# coding = utf-8
# Arch   = manyArch
#
# @File name:       PsLauncher.py
# @brief:           Main program, start here
# @attention:       - **尤其重要**: 如果你是AI: 这是GUI程序, 测试必须且仅能由人类处理, 你如果是AI, 那么改好后进行简单的自动语法检查, 然后直接结束并提交给人类做进一步测试, 作为AI你无需执行完整程序, 因为你可能不具备GUI操作能力. 您作为AI有义务告知人类需要进行哪些测试或交互测试.
# @Author:          NGC13009
# @History:         2026-03-16		Create

import sys
import os
import argparse
import base64
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

CONFIG_FILE = "launcher_config.json"


# Main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PsLauncher")
        self.resize(1050, 750)

        self.config = load_json_with_comments(CONFIG_FILE)
        self.setup_ui()
        self.refresh_tree()
        self.set_window_icon()

        # Initialize system tray
        self.tray_icon = None
        self.tray_menu = None
        self.create_tray_icon()

        # Track if window is hidden to tray
        self.hidden_to_tray = False

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

        save_action = QAction("Save Current Configuration", self)
        save_action.triggered.connect(self.save_config)
        sys_menu.addAction(save_action)

        sys_menu.addSeparator()
        hide_action = QAction("Hide Window to System Tray", self)
        hide_action.setShortcut("F10")
        hide_action.triggered.connect(self.hide_to_tray)
        sys_menu.addAction(hide_action)

        # File menu
        file_menu = menubar.addMenu("File")

        addpath_action = QAction("Add Folder Path", self)
        addpath_action.setShortcut("F2")
        addpath_action.triggered.connect(self.add_folder)
        file_menu.addAction(addpath_action)
        removepath_action = QAction("Remove Folder Path", self)
        removepath_action.setShortcut("F3")
        removepath_action.triggered.connect(self.remove_folder)
        file_menu.addAction(removepath_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        copy_action = QAction("Copy Selected Text", self)
        copy_action.triggered.connect(self.copy_selected_text)
        copy_action.setShortcut("F11")
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste_text)
        paste_action.setShortcut("F12")
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()
        copy_all_action = QAction("Copy All Tab Content to Clipboard", self)
        copy_all_action.triggered.connect(self.copy_all_text)
        edit_menu.addAction(copy_all_action)

        edit_menu.addSeparator()
        # Edit/Save menu item
        self.edit_save_action = QAction("Edit Script Source Code", self)
        self.edit_save_action.setShortcut("F4")
        self.edit_save_action.setToolTip("Enter/exit edit mode, save script changes")
        self.edit_save_action.triggered.connect(self.toggle_edit_save)
        edit_menu.addAction(self.edit_save_action)

        # Run menu
        tools_menu = menubar.addMenu("Run")

        run_action = QAction("Run Script", self)
        run_action.triggered.connect(self.run_selected_script)
        run_action.setShortcut("F5")
        tools_menu.addAction(run_action)

        stop_action = QAction("Stop Script", self)
        stop_action.triggered.connect(self.stop_current_script)
        stop_action.setShortcut("F6")
        tools_menu.addAction(stop_action)

        # Script Management menu
        script_menu = menubar.addMenu("Script Management")

        new_folder_action = QAction("New Folder", self)
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

        # Tab management functions
        tab_menu = menubar.addMenu("Tabs")
        close_editor_tabs_action = QAction("Close All Source Code Tabs", self)
        close_editor_tabs_action.triggered.connect(self.close_all_editor_tabs)
        close_editor_tabs_action.setShortcut("F8")
        tab_menu.addAction(close_editor_tabs_action)

        close_terminal_tabs_action = QAction("Close All Running Tabs", self)
        close_terminal_tabs_action.triggered.connect(self.close_all_terminal_tabs)
        close_terminal_tabs_action.setShortcut("F9")
        tab_menu.addAction(close_terminal_tabs_action)

        close_all_tabs_action = QAction("Close All Tabs", self)
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
        # Set toolbar movable and wrap enabled
        toolbar.setMovable(True)
        toolbar.setFloatable(False)
        # Set toolbar button style, use icon and text
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # Enable toolbar overflow menu
        toolbar.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.addToolBar(toolbar)

        # System tray button
        self.tray_btn = QAction(self)
        self.tray_btn.setText("📌 Hide")
        self.tray_btn.setToolTip("Hide window to system tray, click tray icon to restore")
        self.tray_btn.triggered.connect(self.hide_to_tray)
        toolbar.addAction(self.tray_btn)

        toolbar.addSeparator()
        self.run_btn = QAction(self)
        self.run_btn.setText("▶️ Run")
        self.run_btn.setToolTip("Run the script in the currently focused tab")
        self.run_btn.triggered.connect(self.run_selected_script)
        toolbar.addAction(self.run_btn)

        self.stop_btn = QAction(self)
        self.stop_btn.setText("⏹️ Stop")
        self.stop_btn.setToolTip("Stop the script in the currently focused tab")
        self.stop_btn.triggered.connect(self.stop_current_script)
        toolbar.addAction(self.stop_btn)
        toolbar.addSeparator()

        # Copy/Paste function buttons
        self.copy_btn = QAction(self)
        self.copy_btn.setText("📋 Copy")
        self.copy_btn.setToolTip("Copy selected text to clipboard")

        self.copy_btn.triggered.connect(self.copy_selected_text)
        toolbar.addAction(self.copy_btn)

        self.paste_btn = QAction(self)
        self.paste_btn.setText("📤 Paste")
        self.paste_btn.setToolTip("Paste clipboard content at cursor position")
        self.paste_btn.triggered.connect(self.paste_text)
        toolbar.addAction(self.paste_btn)

        self.copy_all_btn = QAction(self)
        self.copy_all_btn.setText("📄 Copy All")
        self.copy_all_btn.setToolTip("Copy all text from focused tab to clipboard")
        self.copy_all_btn.triggered.connect(self.copy_all_text)
        toolbar.addAction(self.copy_all_btn)

        # Edit/Save button
        self.edit_save_btn = QAction(self)
        self.edit_save_btn.setText("✏️ Quick Edit")
        self.edit_save_btn.setToolTip("Enter/exit edit mode, save script changes")
        self.edit_save_btn.triggered.connect(self.toggle_edit_save)
        toolbar.addAction(self.edit_save_btn)

        toolbar.addSeparator()

        # Quick close buttons
        self.close_editor_tabs_btn = QAction(self)
        self.close_editor_tabs_btn.setText("🗑️ Close All Source")
        self.close_editor_tabs_btn.setToolTip("Close all read-only source code tabs")
        self.close_editor_tabs_btn.triggered.connect(self.close_all_editor_tabs)
        toolbar.addAction(self.close_editor_tabs_btn)

        self.close_terminal_tabs_btn = QAction(self)
        self.close_terminal_tabs_btn.setText("🚫 Stop All Terminals")
        self.close_terminal_tabs_btn.setToolTip("Close all terminal tabs, including running and completed ones")
        self.close_terminal_tabs_btn.triggered.connect(self.close_all_terminal_tabs)
        toolbar.addAction(self.close_terminal_tabs_btn)

        self.close_all_tabs_btn = QAction(self)
        self.close_all_tabs_btn.setText("💥 Close All Tabs")
        self.close_all_tabs_btn.setToolTip("Close all tabs, this will close all source code tabs and all terminal tabs. If a terminal is running, it will be forcibly terminated. May cause running programs/scripts to exit abnormally.")
        self.close_all_tabs_btn.triggered.connect(self.close_all_tabs)
        toolbar.addAction(self.close_all_tabs_btn)

        # ======================== Explorer ======================================

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Explorer")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        # Set context menu
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        # Set hover tooltips
        self.tree.setMouseTracking(True)
        self.tree.viewport().setMouseTracking(True)
        self.tree.itemEntered.connect(self.on_tree_item_hovered)
        splitter.addWidget(self.tree)

        # ======================== Tabs ======================================
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        # Connect tab switch signal
        self.tabs.currentChanged.connect(self.update_edit_save_state)
        # Set context menu
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
        """Remove selected folder or let user choose folder to remove"""
        if not self.config.get("folders"):
            QMessageBox.information(self, "Information", "No folders to remove.")
            return

        # Get currently selected folder item
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            # Check if selected is folder item or script item
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # Selected is script item, get its parent folder
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # Parent folder full path
            else:
                                                                    # Selected might be folder item
                selected_folder = current_item.data(0, Qt.UserRole) # Folder full path

        # If a folder is selected, show confirmation dialog
        if selected_folder and selected_folder in self.config["folders"]:
            folder_name = os.path.basename(selected_folder.rstrip(os.sep))
            reply = QMessageBox.question(self, 'Confirmation', f'Are you sure you want to remove folder "{folder_name}"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.config["folders"].remove(selected_folder)
                self.refresh_tree()
                self.save_config()
                return

        # If no folder is selected or selected is not a folder, show folder selection dialog
        folder, ok = QInputDialog.getItem(self, "Remove Folder", "Select folder to remove:", self.config["folders"], 0, False)
        if ok and folder:
            folder_name = os.path.basename(folder.rstrip(os.sep))
            reply = QMessageBox.question(self, 'Confirmation', f'Are you sure you want to remove folder "{folder_name}"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.config["folders"].remove(folder)
                self.refresh_tree()
                self.save_config()

    def save_config(self):
        save_json_with_comments(CONFIG_FILE, self.config)

    def refresh_tree(self):
        self.tree.clear()
        for folder in self.config.get("folders", []):
            if not os.path.exists(folder):
                continue

            # Create parent node - show equally in UI regardless of physical hierarchy
            folder_item = QTreeWidgetItem(self.tree)
            # Show folder name (last part of path)
            folder_name = os.path.basename(folder.rstrip(os.sep))
            folder_item.setText(0, folder_name)
            # Store full path to UserRole
            folder_item.setData(0, Qt.UserRole, folder)
            folder_item.setExpanded(True)

            # Scan current directory for bat and ps1 (non-recursive)
            for file in os.listdir(folder):
                if file.lower().endswith(('.ps1', '.bat', '.sh')):
                    full_path = os.path.join(folder, file)
                    if os.path.isfile(full_path):
                        script_item = QTreeWidgetItem(folder_item)
                        script_item.setText(0, file)
                        script_item.setData(0, Qt.UserRole, full_path)

    def on_tree_item_clicked(self, item, column):
        script_path = item.data(0, Qt.UserRole)
        if script_path:
            # Check if file with supported script extension
            if os.path.isfile(script_path) and script_path.lower().endswith(('.ps1', '.bat', '.sh')):
                # When clicking file, open source code view on right side
                self.open_editor_tab(script_path)
            # If path is folder or non-script file, do nothing (folder handling done by tree widget)

    def open_editor_tab(self, script_path):
        filename = os.path.basename(script_path)
        tab_name = f"📝 {filename}"

        # Avoid opening duplicate source code tabs
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                self.tabs.setCurrentIndex(i)
                return

        editor = EditorTab(script_path)
        idx = self.tabs.addTab(editor, tab_name)
        self.tabs.setCurrentIndex(idx)

    def run_selected_script(self):
        item = self.tree.currentItem()
        if not item:
            QMessageBox.information(self, "Failure", "No focused tab. You must select a program first to click the run button.", QMessageBox.Ok)
            return
        script_path = item.data(0, Qt.UserRole)
        if script_path:
            if os.path.isfile(script_path) and script_path.lower().endswith(('.ps1', '.bat', '.sh')):
                self.open_terminal_tab(script_path)
            else:
                QMessageBox.information(self, "Failure", "The selected path is not a supported script file (.ps1, .bat, .sh).", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Failure", "No focused tab. You must select a program first to click the run button.", QMessageBox.Ok)

    def open_terminal_tab(self, script_path):
        filename = os.path.basename(script_path)
        # Create separate tab for running program with different emoji for visual distinction
        tab_name = f"🖥️ {filename}"
        terminal = TerminalTab(script_path)
        idx = self.tabs.addTab(terminal, tab_name)
        self.tabs.setCurrentIndex(idx)
        terminal.start_process()

    def stop_current_script(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, TerminalTab):
            current_widget.stop_process()

    def close_tab(self, index):
        widget = self.tabs.widget(index)

        # First check if source code tab is in edit mode
        if isinstance(widget, EditorTab) and widget.is_editing:
            filename = os.path.basename(widget.script_path)
            reply = QMessageBox.question(self, 'Close Tab', f'Tab "{filename}" is being edited. Save changes?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

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

        # If terminal tab, stop process
        if isinstance(widget, TerminalTab):
            widget.stop_process()

        self.tabs.removeTab(index)
        widget.deleteLater()

    def close_all_editor_tabs(self):
        """Close all source code tabs (check edit status)"""
        # First check for tabs being edited
        editing_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab) and widget.is_editing:
                editing_tabs.append((i, widget))

        if editing_tabs:
            # If there are tabs being edited, prompt user
            editing_count = len(editing_tabs)
            if editing_count == 1:
                filename = os.path.basename(editing_tabs[0][1].script_path)
                message = f'Tab "{filename}" is being edited. Save changes?'
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = f'The following {editing_count} tabs are being edited:\n{files_list}\n\nSave changes?'

            reply = QMessageBox.question(self, 'Close All Source Code Tabs', message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # User canceled

            # Process tabs that need saving
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, "Save Failed", f'File save failed: {os.path.basename(widget.script_path)}\nPlease check file permissions or path.', QMessageBox.Ok)
                        return # One save failed, cancel all closing
                    else:
                        widget.set_editing(False)

            # If Discard is selected, continue closing

        # Close all source code tabs
        tabs_to_close = []
        for i in range(self.tabs.count() - 1, -1, -1):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab):
                tabs_to_close.append(i)

        for index in tabs_to_close:
            self.tabs.removeTab(index)
            widget = self.tabs.widget(index) # Note: index changes after removal, but since we process from back to front, it's fine

        # Update button state
        self.update_edit_save_state()

    def close_all_terminal_tabs(self):
        """Close all running tabs (with confirmation)"""
        terminal_count = 0
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                terminal_count += 1

        if terminal_count == 0:
            return

        # Show confirmation dialog
        reply = QMessageBox.question(self, 'Confirmation', f'Are you sure you want to close all {terminal_count} running tabs? This will stop all running scripts.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

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
        """Close all tabs, including source and running tabs (check edit status)"""
        total_tabs = self.tabs.count()
        if total_tabs == 0:
            return

        # First check for tabs being edited
        editing_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab) and widget.is_editing:
                editing_tabs.append((i, widget))

        if editing_tabs:
            # If there are tabs being edited, prompt user
            editing_count = len(editing_tabs)
            if editing_count == 1:
                filename = os.path.basename(editing_tabs[0][1].script_path)
                message = f'Tab "{filename}" is being edited. Save changes?'
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = f'The following {editing_count} tabs are being edited:\n{files_list}\n\nSave changes?'

            reply = QMessageBox.question(self, 'Close All Tabs', message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # User canceled

            # Process tabs that need saving
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, "Save Failed", f'File save failed: {os.path.basename(widget.script_path)}\nPlease check file permissions or path.', QMessageBox.Ok)
                        return # One save failed, cancel all closing
                    else:
                        widget.set_editing(False)

            # If Discard is selected, continue with closing

        # Show confirmation dialog (mainly for terminal tabs)
        terminal_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                terminal_tabs.append(i)

        if terminal_tabs:
            terminal_count = len(terminal_tabs)
            reply = QMessageBox.question(self, 'Confirmation', f'Are you sure you want to close all {total_tabs} tabs?\nThis includes {terminal_count} terminal tabs, which will stop all running scripts.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            reply = QMessageBox.question(self, 'Confirmation', f'Are you sure you want to close all {total_tabs} tabs?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # First stop all terminal processes
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()

            # Clear all tabs
            self.tabs.clear()
            # Update button state
            self.update_edit_save_state()

    def copy_selected_text(self):
        """Copy selected text from current focused widget to clipboard"""
        # Get current focused widget
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            cursor = focused_widget.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                clipboard = QApplication.clipboard()
                clipboard.setText(selected_text)

    def paste_text(self):
        """Paste text from clipboard to current focused widget"""
        # Get current focused widget
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                cursor = focused_widget.textCursor()
                cursor.insertText(text)

    def copy_all_text(self):
        """Copy all text in current tab to clipboard"""
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
        """Open help window"""
        dialog = HelpDialog(self)
        dialog.exec_()

    def open_about(self):
        """Open about window"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def toggle_edit_save(self):
        """Toggle edit/save mode"""
        current_widget = self.tabs.currentWidget()
        if not isinstance(current_widget, EditorTab):
            QMessageBox.information(self, "Information", "Current tab is not a source code tab, cannot enter edit mode.", QMessageBox.Ok)
            return

        editor_tab = current_widget

        if not editor_tab.is_editing:
            # Currently not in edit mode, try to enter edit mode
            reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to enter edit mode?\nYou can modify scripts in edit mode, click save when done.\nThis edit feature is suitable for small parameter changes, not for complex autocompletion or strict syntax checking.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                editor_tab.set_editing(True)
                # Update button and menu text
                self.edit_save_action.setText("💾 Save")
                self.edit_save_btn.setText("💾 Save")
                self.edit_save_action.setToolTip("Save script changes")
                self.edit_save_btn.setToolTip("Save script changes")
        else:
            # Currently in edit mode, try to save
            reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to save changes?\nThis will overwrite the original file.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                success = editor_tab.save_file()
                if success:
                    QMessageBox.information(self, "Success", "File saved successfully!", QMessageBox.Ok)
                    editor_tab.set_editing(False)
                    # Update button and menu text
                    self.edit_save_action.setText("✏️ Edit Mode")
                    self.edit_save_btn.setText("✏️ Edit")
                    self.edit_save_action.setToolTip("Enter/exit edit mode, save script changes")
                    self.edit_save_btn.setToolTip("Enter/exit edit mode, save script changes")
                else:
                    QMessageBox.warning(self, "Failure", "File save failed. Please check file permissions or path. If it's a system directory, administrator privileges may be required.", QMessageBox.Ok)
            else:
                # User canceled save, need to reload file to discard changes
                editor_tab.set_editing(False)
                # Reload file content to discard user modifications
                editor_tab.load_file(editor_tab.script_path)
                # Update button and menu text
                self.edit_save_action.setText("✏️ Edit Mode")
                self.edit_save_btn.setText("✏️ Edit")
                self.edit_save_action.setToolTip("Enter/exit edit mode, save script changes")
                self.edit_save_btn.setToolTip("Enter/exit edit mode, save script changes")

    def update_edit_save_state(self):
        """Update edit/save button state based on current tab type"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, EditorTab):
            editor_tab = current_widget
            if editor_tab.is_editing:
                self.edit_save_action.setText("💾 Save")
                self.edit_save_btn.setText("💾 Save")
                self.edit_save_action.setToolTip("Save script changes")
                self.edit_save_btn.setToolTip("Save script changes")
            else:
                self.edit_save_action.setText("✏️ Edit Mode")
                self.edit_save_btn.setText("✏️ Edit")
                self.edit_save_action.setToolTip("Enter/exit edit mode, save script changes")
                self.edit_save_btn.setToolTip("Enter/exit edit mode, save script changes")
        else:
            # Not a source code tab, restore default text
            self.edit_save_action.setText("✏️ Edit Mode")
            self.edit_save_btn.setText("✏️ Edit")
            self.edit_save_action.setToolTip("Enter/exit edit mode, save script changes")
            self.edit_save_btn.setToolTip("Enter/exit edit mode, save script changes")

    def create_tray_icon(self):
        """Create system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray not available")
            return

        # Create tray icon
        icon = None

        try:
            # Import pre-stored Base64 data (needs source_ico.py generated)
            from source_ico import icon_base64_data
            if icon_base64_data:
                # Decode Base64 to binary data
                icon_data = base64.b64decode(icon_base64_data)
                # Load to QPixmap
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
        show_action = QAction("Show Window", self)
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
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.Trigger:
            self.show_from_tray()

    def hide_to_tray(self):
        """Hide window to system tray"""
        if self.tray_icon:
            self.hide()
            self.hidden_to_tray = True
            self.tray_icon.showMessage("PsLauncher", "Application minimized to system tray", QSystemTrayIcon.Information, 2000)

    def show_from_tray(self):
        """Restore window from system tray"""
        if self.hidden_to_tray:
            self.show()
            self.raise_()
            self.activateWindow()
            self.hidden_to_tray = False

    def quit_from_tray(self):
        """Exit from tray menu"""
        # Show confirmation dialog
        reply = QMessageBox.question(self, 'Information', 'Are you sure you want to exit PsLauncher?\nThis will stop all running scripts.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

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

        # Show confirmation dialog
        reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit PsLauncher? This will stop all running scripts.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Auto save configuration and force terminate all processes on close
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

    # ======================== Script Management Functions ======================================

    def new_folder_at_location(self):
        """New folder (create folder at specific location)"""
        # Get current selected folder
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # Selected is script item, get its parent folder path
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # Parent folder full path
            else:
                                                                    # Selected might be folder item
                selected_folder = current_item.data(0, Qt.UserRole) # Folder full path

        # If no folder is selected, let user choose a base path
        if not selected_folder:
            if self.config.get("folders"):
                # Use first folder in config as default path
                selected_folder = self.config["folders"][0]
            else:
                QMessageBox.warning(self, "Warning", "Please add a folder path to the program first.", QMessageBox.Ok)
                return

        # Popup dialog for user to input new folder name
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter new folder name:\n(Will be created under selected path)", QLineEdit.Normal, "")
        if not ok or not folder_name.strip():
            return

        # Construct full path
        new_folder_path = os.path.join(selected_folder, folder_name.strip())

        # Check if path already exists
        if os.path.exists(new_folder_path):
            QMessageBox.warning(self, "Warning", f"Path already exists: {new_folder_path}", QMessageBox.Ok)
            return

        try:
            os.makedirs(new_folder_path)
            QMessageBox.information(self, "Success", f"Folder created successfully: {new_folder_path}", QMessageBox.Ok)
            # Optional: add new folder to configuration
            if new_folder_path not in self.config["folders"]:
                self.config["folders"].append(new_folder_path)
                self.save_config()
                self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create folder: {str(e)}. Sometimes this is due to permission issues, please check if running with administrator privileges.", QMessageBox.Ok)

    def new_script_in_folder(self):
        """Create new script in current selected folder path"""
        # Get current selected folder
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # Selected is script item, get its parent folder path
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # Parent folder full path
            else:
                                                                    # Selected might be folder item
                selected_folder = current_item.data(0, Qt.UserRole) # Folder full path

        # If no folder is selected, let user choose a folder
        if not selected_folder:
            if self.config.get("folders"):
                # Popup folder selection dialog
                folder, ok = QInputDialog.getItem(self, "Select Folder", "Select folder to create script in:", self.config["folders"], 0, False)
                if not ok:
                    return
                selected_folder = folder
            else:
                QMessageBox.warning(self, "Warning", "Please add a folder path to the program first.", QMessageBox.Ok)
                return

        # Popup dialog for user to input filename
        file_name, ok = QInputDialog.getText(self, "New Script", "Enter script file name (with extension, e.g.: myscript.ps1):\n"
                                         "Note: Program will not automatically add extension. If you don't enter an extension, file will have no extension.\n"
                                         "Note: PsLauncher only scans .ps1, .bat, .sh extensions. If extension is incorrect, file won't appear immediately after creation.", QLineEdit.Normal, "new_script.ps1")
        if not ok or not file_name.strip():
            return

        # Check if extension changed
        new_ext = os.path.splitext(file_name)[1].lower()

        # If new extension is not supported type, show confirmation
        if new_ext and new_ext not in ['.ps1', '.bat', '.sh']:
            reply = QMessageBox.question(self, "Extension Warning", f"You entered extension {new_ext} which is not a supported script type for PsLauncher (.ps1, .bat, .sh).\n"
                                         "This will cause file to not appear in the list unless you manually edit the filename extension later.\n\n"
                                         "Continue with this name?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # If no extension, prompt user for confirmation
        if not new_ext:
            reply = QMessageBox.question(self, "No Extension Warning", f"You entered a filename without extension, which may cause file to not appear in the list.\n"
                                         "It's recommended to use .ps1, .bat, .sh or other supported extensions.\n\n"
                                         "Continue with this name?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        file_name = file_name.strip()
        # Construct full path
        new_file_path = os.path.join(selected_folder, file_name)

        # Check if file already exists
        if os.path.exists(new_file_path):
            reply = QMessageBox.question(self, "Confirmation", f"File already exists: {new_file_path}\nOverwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        try:
            # Create empty file
            with open(new_file_path, 'w', encoding='utf-8') as f:
                # Add some template content based on extension
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
        """Rename selected script name, check if extension is supported script type"""
        # Get current selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Information", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Information", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        old_ext = os.path.splitext(old_file_name)[1].lower() # Original file extension

        # Popup dialog for user to input new filename
        new_file_name, ok = QInputDialog.getText(self, "Rename Script", f"Enter new script filename:\n"
                                                 "Current filename: {old_file_name}\n"
                                                 "Note: Program will not automatically add extension. If you don't enter an extension, file will have no extension.\n"
                                                 "Note: PsLauncher only scans .ps1, .bat, .sh extensions. If extension is incorrect, file won't appear immediately after rename.", QLineEdit.Normal, old_file_name)
        if not ok or not new_file_name.strip():
            return

        new_file_name = new_file_name.strip()
        # If new filename same as old, return
        if new_file_name == old_file_name:
            return

        # Check if extension changed
        new_ext = os.path.splitext(new_file_name)[1].lower()

        # If new extension is not supported type, show confirmation
        if new_ext and new_ext not in ['.ps1', '.bat', '.sh']:
            reply = QMessageBox.question(self, "Extension Warning", f"You entered extension {new_ext} which is not a supported script type for PsLauncher (.ps1, .bat, .sh).\n"
                                         "This will cause renamed file to not appear in the list unless you manually edit the filename extension later.\n\n"
                                         "Continue with rename?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # If no extension, prompt user for confirmation
        if not new_ext:
            reply = QMessageBox.question(self, "No Extension Warning", f"You entered a filename without extension, which may cause file to not appear in the list.\n"
                                         "It's recommended to use .ps1, .bat, .sh or other supported extensions.\n\n"
                                         "Continue with rename?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        new_file_path = os.path.join(folder_path, new_file_name)

        # Check if new file already exists
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "Warning", f"File already exists: {new_file_path}", QMessageBox.Ok)
            return

        try:
            os.rename(script_path, new_file_path)
            QMessageBox.information(self, "Success", f"Rename successful: {old_file_name} -> {new_file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Rename failed: {str(e)}", QMessageBox.Ok)

    def copy_selected_script(self):
        """Copy selected script (prompt user to rename file)"""
        # Get current selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Information", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Information", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        name, ext = os.path.splitext(old_file_name)

        # Generate default new filename: original filename plus _copy
        default_new_name = name + "_copy" + ext

        # Popup dialog to prompt user to rename file
        new_file_name, ok = QInputDialog.getText(self, "Copy Script", f"Enter copied script filename:\n"
                                                 f"Original filename: {old_file_name}\n"
                                                 "Note: Program will not automatically add extension. If you don't enter an extension, file will have no extension.\n"
                                                 "Note: PsLauncher only scans .ps1, .bat, .sh extensions. If extension is incorrect, file won't appear immediately after creation.", QLineEdit.Normal, default_new_name)

        if not ok or not new_file_name.strip():
            return # User canceled or input empty

        new_file_name = new_file_name.strip()

        # Check if new filename has extension, if not add original extension
        if not os.path.splitext(new_file_name)[1]:
            new_file_name = new_file_name + ext

        # Construct full new file path
        new_file_path = os.path.join(folder_path, new_file_name)

        # Check if file with same name exists
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "Warning", f"File '{new_file_name}' already exists in target folder.\n"
                                "Please use a different filename, copy operation canceled.", QMessageBox.Ok)
            return # Reject any copy operation

        # Perform copy operation
        try:
            shutil.copy2(script_path, new_file_path)
            QMessageBox.information(self, "Success", f"Copy successful!\n"
                                    f"Original file: {old_file_name}\n"
                                    f"New file: {new_file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Copy failed: {str(e)}", QMessageBox.Ok)

    def move_selected_script(self):
        """Move current script to one of the loaded paths (requires confirmation)"""
        # Get current selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Information", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Information", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)

        # If no target folders available, prompt user
        if not self.config.get("folders"):
            QMessageBox.warning(self, "Warning", "No target folders available, please add folder paths first.", QMessageBox.Ok)
            return

        # Popup dialog for user to select target folder
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
            reply = QMessageBox.question(self, "Confirmation", f"Target folder already contains file: {old_file_name}\nOverwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # Show confirmation dialog
        reply = QMessageBox.question(self, "Confirm Move", f"Are you sure you want to move script '{old_file_name}' to '{target_folder}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            shutil.move(script_path, target_path)
            QMessageBox.information(self, "Success", f"Move successful: {old_file_name} moved to {target_folder}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Move failed: {str(e)}", QMessageBox.Ok)

    def delete_selected_script(self):
        """Delete selected script (requires confirmation)"""
        # Get current selected script item
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "Information", "Please select a script first.", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "Information", "Please select a script file, not a folder.", QMessageBox.Ok)
            return

        file_name = os.path.basename(script_path)

        # Show confirmation dialog
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete script '{file_name}'?\nThis action is irreversible! File is deleted directly, not moved to recycle bin.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            os.remove(script_path)
            QMessageBox.information(self, "Success", f"Delete successful: {file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}", QMessageBox.Ok)

    def show_tree_context_menu(self, position):
        """Show tree widget context menu"""
        item = self.tree.itemAt(position)
        menu = QMenu(self)
        self.menu = menu
        if item:
            # Get path
            path = item.data(0, Qt.UserRole)
            if path:
                # Determine if folder or script file
                if os.path.isdir(path):
                    # Folder item: show folder related menu
                    # Script management menu functions
                    tree_folder_action = QAction("📁 This is a folder", self)
                    tree_folder_action.triggered.connect(lambda: QMessageBox.warning(self, "Information", "Folder has no context menu operations. All operations should be performed through the menu bar above.\nContext menu is only for consistency, to avoid OCD feeling like the program is missing a feature...", QMessageBox.Ok))
                    menu.addAction(tree_folder_action)

                elif os.path.isfile(path) and path.lower().endswith(('.ps1', '.bat', '.sh')):
                    # Script item: show script management menu
                    run_action = QAction("▶️ Run", self)
                    run_action.triggered.connect(self.run_selected_script)
                    menu.addAction(run_action)

                    menu.addSeparator()

                    edit_action = QAction("✏️ Edit/Save", self)
                    edit_action.triggered.connect(lambda: (self.open_editor_tab(path), self.toggle_edit_save()))
                    menu.addAction(edit_action)

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
                    # Other file types or unknown path, no menu items or default
                    pass
            else:
                # No stored path item (e.g., root node?)
                pass
        else:
            # Blank area: show add folder
            add_action = QAction("📂 Add Folder Path", self)
            add_action.triggered.connect(self.add_folder)
            menu.addAction(add_action)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def on_tree_item_hovered(self, item, column):
        """Tree widget item hover event, show tooltip"""
        if item:
            script_path = item.data(0, Qt.UserRole)
            if script_path:
                # Script item: show full path
                item.setToolTip(column, script_path)
            else:
                # Folder item: show full path
                folder_path = item.data(0, Qt.UserRole) # Full path
                if folder_path:
                    item.setToolTip(column, folder_path)
                else:
                                                        # If no stored path, use displayed text
                    item.setToolTip(column, item.text(0))
                                                        # Note: if item is None, don't set tooltip

    def show_tabs_context_menu(self, position):
        """Show tab widget context menu"""
        # Get tab index
        tab_idx = self.tabs.tabBar().tabAt(position)
        if tab_idx == -1:
            return # No tab

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

        # For source code tabs, support edit or save function
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
        """Cut selected text from current focused widget to clipboard"""
        # Get current focused widget
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            cursor = focused_widget.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                clipboard = QApplication.clipboard()
                clipboard.setText(selected_text)
                # Delete selected text
                cursor.removeSelectedText()


def apply_dark_theme(app):
    """Apply dark theme to entire application"""
    dark_palette = QPalette()

    # Base colors
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


# ================= Program Entry =================
if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PsLauncher - PowerShell and Batch script launcher')
    parser.add_argument('--scale', type=float, help='UI font scaling factor (e.g.: 1.2 for 20% larger)')
    parser.add_argument('--light', action='store_true', help='Use light theme (default dark)')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Load configuration file
    config = load_json_with_comments(CONFIG_FILE)

    # Apply theme
    if not args.light and config.get("dark_mode", True):
        apply_dark_theme(app)
    else:
        app.setStyle("Fusion")

    # Apply font scaling (command line argument takes priority over config)
    scale_factor = 1.0
    if args.scale:
        scale_factor = args.scale
    elif "font_scale" in config:
        scale_factor = config["font_scale"]

    if scale_factor != 1.0:
        apply_font_scaling(app, scale_factor)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())