# coding = utf-8
# Arch   = manyArch
#
# @File name:       PsLauncher.py
# @brief:           主程序, 从这里开始运行
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


# 主窗口
class MainWindow(QMainWindow):

    def __init__(self, font_family, h, w, dark_mode):
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
        self.dark_mode = dark_mode

        self.setup_ui()
        self.refresh_tree()
        self.set_window_icon()

        # 初始化系统托盘
        self.tray_icon = None
        self.tray_menu = None
        self.create_tray_icon()

        # 跟踪窗口是否隐藏到托盘
        self.hidden_to_tray = False

    def set_window_icon(self):
        """设置窗口图标"""
        try:
            try:
                # 导入base64数据
                if icon_base64_data:
                    # 解码base64数据
                    icon_data = base64.b64decode(icon_base64_data)
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(icon_data))
                    icon = QIcon(pixmap)
                    self.setWindowIcon(icon)
                    icon_set = True
            except Exception as e:
                print(f"从base64加载图标失败: {e}")

            if not icon_set:
                print("无法加载程序图标，使用默认图标")
        except Exception as e:
            print(f"设置窗口图标时出错: {e}")

    def setup_ui(self):
        menubar = self.menuBar()

        # ======================== 菜单 ======================================
        # 系统菜单

        sys_menu = menubar.addMenu("系统")

        save_action = QAction("保存当前配置", self)
        save_action.triggered.connect(self.save_config)
        sys_menu.addAction(save_action)

        sys_menu.addSeparator()
        hide_action = QAction("隐藏窗口到系统托盘", self)
        hide_action.setShortcut("F10")
        hide_action.triggered.connect(self.hide_to_tray)
        sys_menu.addAction(hide_action)

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        addpath_action = QAction("添加文件夹路径", self)
        addpath_action.setShortcut("F2")
        addpath_action.triggered.connect(self.add_folder)
        file_menu.addAction(addpath_action)
        removepath_action = QAction("移除文件夹路径", self)
        removepath_action.setShortcut("F3")
        removepath_action.triggered.connect(self.remove_folder)
        file_menu.addAction(removepath_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")

        copy_action = QAction("复制选定内容", self)
        copy_action.triggered.connect(self.copy_selected_text)
        copy_action.setShortcut("F11")
        edit_menu.addAction(copy_action)

        paste_action = QAction("粘贴", self)
        paste_action.triggered.connect(self.paste_text)
        paste_action.setShortcut("F12")
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()
        copy_all_action = QAction("复制标签页全部到剪贴板", self)
        copy_all_action.triggered.connect(self.copy_all_text)
        edit_menu.addAction(copy_all_action)

        edit_menu.addSeparator()
        # 编辑/保存菜单项
        self.edit_save_action = QAction("编辑脚本源代码", self)
        self.edit_save_action.setShortcut("F4")
        self.edit_save_action.setToolTip("进入/退出编辑模式，保存脚本更改")
        self.edit_save_action.triggered.connect(self.toggle_edit_save)
        edit_menu.addAction(self.edit_save_action)

        # 运行菜单
        tools_menu = menubar.addMenu("运行")

        run_action = QAction("启动脚本", self)
        run_action.triggered.connect(self.run_selected_script)
        run_action.setShortcut("F5")
        tools_menu.addAction(run_action)

        stop_action = QAction("终止脚本", self)
        stop_action.triggered.connect(self.stop_current_script)
        stop_action.setShortcut("F6")
        tools_menu.addAction(stop_action)

        # 脚本管理菜单
        script_menu = menubar.addMenu("脚本管理")

        new_folder_action = QAction("新建路径", self)
        new_folder_action.triggered.connect(self.new_folder_at_location)
        script_menu.addAction(new_folder_action)

        new_script_action = QAction("新建脚本", self)
        new_script_action.triggered.connect(self.new_script_in_folder)
        script_menu.addAction(new_script_action)

        rename_script_action = QAction("重命名脚本", self)
        rename_script_action.triggered.connect(self.rename_selected_script)
        script_menu.addAction(rename_script_action)

        copy_script_action = QAction("复制脚本", self)
        copy_script_action.triggered.connect(self.copy_selected_script)
        script_menu.addAction(copy_script_action)

        move_script_action = QAction("移动脚本", self)
        move_script_action.triggered.connect(self.move_selected_script)
        script_menu.addAction(move_script_action)

        delete_script_action = QAction("删除脚本", self)
        delete_script_action.triggered.connect(self.delete_selected_script)
        script_menu.addAction(delete_script_action)

        # 标签页管理功能
        tab_menu = menubar.addMenu("标签")
        close_editor_tabs_action = QAction("关闭所有源码标签页", self)
        close_editor_tabs_action.triggered.connect(self.close_all_editor_tabs)
        close_editor_tabs_action.setShortcut("F8")
        tab_menu.addAction(close_editor_tabs_action)

        close_terminal_tabs_action = QAction("关闭所有运行标签页", self)
        close_terminal_tabs_action.triggered.connect(self.close_all_terminal_tabs)
        close_terminal_tabs_action.setShortcut("F9")
        tab_menu.addAction(close_terminal_tabs_action)

        close_all_tabs_action = QAction("关闭所有标签页", self)
        close_all_tabs_action.triggered.connect(self.close_all_tabs)
        tab_menu.addAction(close_all_tabs_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        help_action = QAction("帮助", self)
        help_action.triggered.connect(self.open_help)
        help_menu.addAction(help_action)
        help_action.setShortcut("F1")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.open_about)
        help_menu.addAction(about_action)

        # ======================== 工具栏 ======================================

        toolbar = QToolBar("Main Toolbar")
        # 设置工具栏可移动且允许换行
        toolbar.setMovable(True)
        toolbar.setFloatable(False)
        # 设置工具栏按钮样式，使用图标和文本
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # 启用工具栏的溢出菜单功能
        toolbar.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.addToolBar(toolbar)

        # 系统托盘按钮
        self.tray_btn = QAction(self)
        self.tray_btn.setText("📌隐藏")
        self.tray_btn.setToolTip("隐藏窗口到系统托盘, 通过单击托盘图标即可恢复窗口")
        self.tray_btn.triggered.connect(self.hide_to_tray)
        toolbar.addAction(self.tray_btn)

        toolbar.addSeparator()
        self.run_btn = QAction(self)
        self.run_btn.setText("▶️运行")
        self.run_btn.setToolTip("运行当前焦点标签页的脚本")
        self.run_btn.triggered.connect(self.run_selected_script)
        toolbar.addAction(self.run_btn)

        self.stop_btn = QAction(self)
        self.stop_btn.setText("⏹️中止")
        self.stop_btn.setToolTip("中止当前焦点标签页的脚本")
        self.stop_btn.triggered.connect(self.stop_current_script)
        toolbar.addAction(self.stop_btn)
        toolbar.addSeparator()

        # 复制/粘贴功能按钮
        self.copy_btn = QAction(self)
        self.copy_btn.setText("📋复制")
        self.copy_btn.setToolTip("复制当前选中的文本到剪贴板")

        self.copy_btn.triggered.connect(self.copy_selected_text)
        toolbar.addAction(self.copy_btn)

        self.paste_btn = QAction(self)
        self.paste_btn.setText("📤粘贴")
        self.paste_btn.setToolTip("粘贴当前剪贴板内容到光标位置")
        self.paste_btn.triggered.connect(self.paste_text)
        toolbar.addAction(self.paste_btn)

        toolbar.addSeparator()
        self.close_editor_tabs_btn = QAction(self)
        self.close_editor_tabs_btn.setText("🗑️关闭所有源码")
        self.close_editor_tabs_btn.setToolTip("关闭所有只读源代码查看标签页")
        self.close_editor_tabs_btn.triggered.connect(self.close_all_editor_tabs)
        toolbar.addAction(self.close_editor_tabs_btn)

        # 编辑/保存按钮
        self.edit_save_btn = QAction(self)
        self.edit_save_btn.setText("✏️快速编辑")
        self.edit_save_btn.setToolTip("进入/退出编辑模式，保存脚本更改")
        self.edit_save_btn.triggered.connect(self.toggle_edit_save)
        toolbar.addAction(self.edit_save_btn)

        toolbar.addSeparator()

        # 快捷关闭按钮

        self.close_terminal_tabs_btn = QAction(self)
        self.close_terminal_tabs_btn.setText("🚫中止所有终端")
        self.close_terminal_tabs_btn.setToolTip("关闭所有终端标签页, 包括运行中的以及已经结束的")
        self.close_terminal_tabs_btn.triggered.connect(self.close_all_terminal_tabs)
        toolbar.addAction(self.close_terminal_tabs_btn)

        self.close_all_tabs_btn = QAction(self)
        self.close_all_tabs_btn.setText("💥关闭所有标签")
        self.close_all_tabs_btn.setToolTip("关闭所有标签, 这会关闭所有源代码标签页, 同时关闭所有终端标签页, 如果终端内正在执行, 那么将强制中止. 可能导致执行中的程序或脚本不能正常退出.")
        self.close_all_tabs_btn.triggered.connect(self.close_all_tabs)
        toolbar.addAction(self.close_all_tabs_btn)

        # ======================== 资源管理器 ======================================

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("资源管理器")
        font = QFont(self.font_family, 14) # 字体族，字号
                                           # font.setBold(True) # 加粗
        self.tree.setFont(font)            # 应用到整个树形控件
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
                                           # 设置右键菜单
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
                                           # 设置悬浮提示
        self.tree.setMouseTracking(True)
        self.tree.viewport().setMouseTracking(True)
        self.tree.itemEntered.connect(self.on_tree_item_hovered)
        splitter.addWidget(self.tree)

        # ======================== 文件树样式 ======================================
        backgroundcolor = '#1E1E1E' if self.dark_mode else '#efefef'
        backgroundcolor2 = '#3c3c3c' if self.dark_mode else '#d1d1d1'
        backgroundcolor3 = '#d4d4d4' if self.dark_mode else '#3c3c3c'
        color = '#efefef' if self.dark_mode else '#1e1e1e'

        # 样式
        dark_stylesheet = f"""
        /* 主窗口背景 */
        QMainWindow {{
            background-color: {backgroundcolor};
        }}
        
        /* 分割器背景 */
        QSplitter {{
            background-color: {backgroundcolor};
        }}
        QSplitter::handle {{
            background-color: {backgroundcolor2};
            width: 2px;
            height: 2px;
        }}
        
        /* 树形控件样式 */
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
            background-color: #264f78;  /* 选中项深蓝色 */
            color: #ffffff;
        }}
        QTreeWidget::item:hover {{
            background-color: {backgroundcolor2};  /* 悬停稍亮 */
        }}
        QTreeWidget::branch {{
            background-color: {backgroundcolor};  /* 分支箭头区域背景 */
        }}
        
        /* 表头样式 */
        QHeaderView::section {{
            background-color: {backgroundcolor2};
            color: {backgroundcolor3};
            padding: 5px;
            border: none;
            border-right: 1px solid {backgroundcolor};
        }}
        """
        self.setStyleSheet(dark_stylesheet)

        # ======================== 标签们 ======================================
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        # 连接标签页切换信号
        self.tabs.currentChanged.connect(self.update_edit_save_state)
        # 设置右键菜单
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tabs_context_menu)
        splitter.addWidget(self.tabs)
        splitter.setSizes([300, 750])

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择要扫描的文件夹")
        if folder and folder not in self.config["folders"]:
            self.config["folders"].append(folder)
            self.refresh_tree()
            self.save_config()

    def remove_folder(self):
        """移除选中的文件夹或让用户选择要移除的文件夹"""
        if not self.config.get("folders"):
            QMessageBox.information(self, "提示", "当前没有可移除的文件夹。")
            return

        # 获取当前选中的文件夹项
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            # 检查选中的是文件夹项还是脚本项
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # 选中的是脚本项，获取其父文件夹
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # 父文件夹的完整路径
            else:
                                                                    # 选中的可能是文件夹项
                selected_folder = current_item.data(0, Qt.UserRole) # 文件夹的完整路径

        # 如果选中了文件夹，提供确认对话框
        if selected_folder and selected_folder in self.config["folders"]:
            folder_name = os.path.basename(selected_folder.rstrip(os.sep))
            reply = QMessageBox.question(self, '确认', f'确定要移除文件夹 "{folder_name}" 吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.config["folders"].remove(selected_folder)
                self.refresh_tree()
                self.save_config()
                return

        # 如果没有选中的文件夹或选中的不是文件夹，显示文件夹选择对话框
        folder, ok = QInputDialog.getItem(self, "移除文件夹", "选择要移除的文件夹:", self.config["folders"], 0, False)
        if ok and folder:
            folder_name = os.path.basename(folder.rstrip(os.sep))
            reply = QMessageBox.question(self, '确认', f'确定要移除文件夹 "{folder_name}" 吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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

            # 创建父节点 不管物理层级如何，在UI里平等展示
            folder_item = QTreeWidgetItem(self.tree)
            # 显示文件夹名称（路径的最后一部分）
            folder_name = os.path.basename(folder.rstrip(os.sep))
            folder_item.setText(0, folder_name)
            # 存储完整路径到 UserRole
            folder_item.setData(0, Qt.UserRole, folder)
            folder_item.setExpanded(True)

            # 扫描当前目录下的 bat 和 ps1 不递归
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
            # 检查是否为文件且扩展名是支持的脚本类型
            if os.path.isfile(script_path) and script_path.lower().endswith(('.ps1', '.bat', '.sh')):
                # 单击文件时，在右侧打开源码阅读
                self.open_editor_tab(script_path)
            # 如果路径是文件夹或非脚本文件，则不执行任何操作（文件夹点击已由树形控件处理）

    def open_editor_tab(self, script_path):
        filename = os.path.basename(script_path)
        tab_name = f"📝 {filename}"

        # 避免重复打开相同的源码标签
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                self.tabs.setCurrentIndex(i)
                return

        editor = EditorTab(script_path, self.font_family, self.dark_mode)
        idx = self.tabs.addTab(editor, tab_name)
        self.tabs.setCurrentIndex(idx)

    def run_selected_script(self):
        item = self.tree.currentItem()
        if not item:
            QMessageBox.information(self, "失败", "没有焦点的标签, 你必须先选中一个程序才能点击运行按钮", QMessageBox.Ok)
            return
        script_path = item.data(0, Qt.UserRole)
        if script_path:
            if os.path.isfile(script_path) and script_path.lower().endswith(('.ps1', '.bat', '.sh')):
                self.open_terminal_tab(script_path)
            else:
                QMessageBox.information(self, "失败", "选择的路径不是一个支持的脚本文件（.ps1, .bat, .sh）。", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "失败", "没有焦点的标签, 你必须先选中一个程序才能点击运行按钮", QMessageBox.Ok)

    def open_terminal_tab(self, script_path):
        filename = os.path.basename(script_path)
        # 为运行的程序创建一个独立标签页，使用不同emoji以视觉区分
        tab_name = f"🖥️ {filename}"
        terminal = TerminalTab(script_path, self.font_family, self.dark_mode)
        idx = self.tabs.addTab(terminal, tab_name)
        self.tabs.setCurrentIndex(idx)
        terminal.start_process()

    def stop_current_script(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, TerminalTab):
            current_widget.stop_process()

    def close_tab(self, index):
        widget = self.tabs.widget(index)

        # 首先检查是否是源码标签页且处于编辑模式
        if isinstance(widget, EditorTab) and widget.is_editing:
            filename = os.path.basename(widget.script_path)
            reply = QMessageBox.question(self, '关闭标签页', f'标签页 "{filename}" 正在编辑中，是否保存更改？', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Save:
                success = widget.save_file()
                if not success:
                    QMessageBox.warning(self, "保存失败", "文件保存失败，请检查文件权限或路径。", QMessageBox.Ok)
                    return
                else:
                    widget.set_editing(False)
                    self.update_edit_save_state()

        # 如果是终端标签页，停止进程
        if isinstance(widget, TerminalTab):
            widget.stop_process()

        self.tabs.removeTab(index)
        widget.deleteLater()

    def close_all_editor_tabs(self):
        """关闭所有源码标签页（检查编辑状态）"""
        # 先检查是否有编辑中的标签页
        editing_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab) and widget.is_editing:
                editing_tabs.append((i, widget))

        if editing_tabs:
            # 如果有编辑中的标签页，提示用户
            editing_count = len(editing_tabs)
            if editing_count == 1:
                filename = os.path.basename(editing_tabs[0][1].script_path)
                message = f'标签页 "{filename}" 正在编辑中，是否保存更改？'
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = f'有以下 {editing_count} 个标签页正在编辑中：\n{files_list}\n\n是否保存更改？'

            reply = QMessageBox.question(self, '关闭所有源码标签页', message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # 用户取消关闭

            # 处理需要保存的标签页
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, "保存失败", f'文件保存失败：{os.path.basename(widget.script_path)}\n请检查文件权限或路径。', QMessageBox.Ok)
                        return # 有一个保存失败，取消全部关闭操作
                    else:
                        widget.set_editing(False)

            # 如果选择Discard，直接继续关闭

        # 关闭所有源码标签页
        tabs_to_close = []
        for i in range(self.tabs.count() - 1, -1, -1):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab):
                tabs_to_close.append(i)

        for index in tabs_to_close:
            self.tabs.removeTab(index)
            widget = self.tabs.widget(index) # 注意：移除后索引会变化，但因为我们是从后往前处理，所以没问题

        # 更新按钮状态
        self.update_edit_save_state()

    def close_all_terminal_tabs(self):
        """关闭所有运行标签页（有确认框）"""
        terminal_count = 0
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                terminal_count += 1

        if terminal_count == 0:
            return

        # 显示确认对话框
        reply = QMessageBox.question(self, '确认', f'确定要关闭所有 {terminal_count} 个运行标签页吗？这会停止所有正在运行的脚本。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

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
        """关闭所有标签页，包括源码和运行标签页（检查编辑状态）"""
        total_tabs = self.tabs.count()
        if total_tabs == 0:
            return

        # 先检查是否有编辑中的标签页
        editing_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, EditorTab) and widget.is_editing:
                editing_tabs.append((i, widget))

        if editing_tabs:
            # 如果有编辑中的标签页，提示用户
            editing_count = len(editing_tabs)
            if editing_count == 1:
                filename = os.path.basename(editing_tabs[0][1].script_path)
                message = f'标签页 "{filename}" 正在编辑中，是否保存更改？'
            else:
                filenames = [os.path.basename(widget.script_path) for _, widget in editing_tabs]
                files_list = "\n".join(f'  • {name}' for name in filenames)
                message = f'有以下 {editing_count} 个标签页正在编辑中：\n{files_list}\n\n是否保存更改？'

            reply = QMessageBox.question(self, '关闭所有标签页', message, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

            if reply == QMessageBox.Cancel:
                return # 用户取消关闭

            # 处理需要保存的标签页
            if reply == QMessageBox.Save:
                for index, widget in editing_tabs:
                    success = widget.save_file()
                    if not success:
                        QMessageBox.warning(self, "保存失败", f'文件保存失败：{os.path.basename(widget.script_path)}\n请检查文件权限或路径。', QMessageBox.Ok)
                        return # 有一个保存失败，取消全部关闭操作
                    else:
                        widget.set_editing(False)

            # 如果选择Discard，继续下面的关闭操作

        # 显示确认对话框（主要针对终端标签页）
        terminal_tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                terminal_tabs.append(i)

        if terminal_tabs:
            terminal_count = len(terminal_tabs)
            reply = QMessageBox.question(self, '确认', f'确定要关闭所有 {total_tabs} 个标签页吗？\n这包括 {terminal_count} 个终端标签页，会停止所有正在运行的脚本。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            reply = QMessageBox.question(self, '确认', f'确定要关闭所有 {total_tabs} 个标签页吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 先停止所有终端进程
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()

            # 清空所有标签页
            self.tabs.clear()
            # 更新按钮状态
            self.update_edit_save_state()

    def copy_selected_text(self):
        """复制当前焦点控件的选中文本到剪贴板"""
        # 获取当前焦点控件
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            cursor = focused_widget.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                clipboard = QApplication.clipboard()
                clipboard.setText(selected_text)

    def paste_text(self):
        """从剪贴板粘贴文本到当前焦点控件"""
        # 获取当前焦点控件
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                cursor = focused_widget.textCursor()
                cursor.insertText(text)

    def copy_all_text(self):
        """复制当前标签页内的所有文本到剪贴板"""
        current_widget = self.tabs.currentWidget()
        if current_widget:
            text = ""
            if isinstance(current_widget, EditorTab):
                text = current_widget.editor.toPlainText()
            elif isinstance(current_widget, TerminalTab):
                text = current_widget.terminal.toPlainText()
            else:
                # 其他类型的标签页
                return

            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)

    def open_help(self):
        """打开帮助窗口"""
        dialog = HelpDialog(self)
        dialog.exec_()

    def open_about(self):
        """打开关于窗口"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def toggle_edit_save(self):
        """切换编辑/保存模式"""
        current_widget = self.tabs.currentWidget()
        if not isinstance(current_widget, EditorTab):
            QMessageBox.information(self, "提示", "当前标签页不是源码标签页，无法进入编辑模式。", QMessageBox.Ok)
            return

        editor_tab = current_widget

        if not editor_tab.is_editing:
            # 当前不在编辑模式，尝试进入编辑模式
            reply = QMessageBox.question(self, '确认', '确定要进入编辑模式吗？\n进入后可以对脚本进行修改，完成后请点击保存。\n这个编辑功能适合修改少量参数等操作, 不支持复杂的自动补全或严格的语法检查等功能.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                editor_tab.set_editing(True)
                # 更新按钮和菜单文本
                self.edit_save_action.setText("💾保存")
                self.edit_save_btn.setText("💾保存")
                self.edit_save_action.setToolTip("保存脚本更改")
                self.edit_save_btn.setToolTip("保存脚本更改")
        else:
            # 当前在编辑模式，尝试保存
            reply = QMessageBox.question(self, '确认', '确定要保存更改吗？\n这将覆盖原始文件。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                success = editor_tab.save_file()
                if success:
                    QMessageBox.information(self, "成功", "文件保存成功！", QMessageBox.Ok)
                    editor_tab.set_editing(False)
                    # 更新按钮和菜单文本
                    self.edit_save_action.setText("✏️编辑模式")
                    self.edit_save_btn.setText("✏️编辑")
                    self.edit_save_action.setToolTip("进入/退出编辑模式，保存脚本更改")
                    self.edit_save_btn.setToolTip("进入/退出编辑模式，保存脚本更改")
                else:
                    QMessageBox.warning(self, "失败", "文件保存失败，请检查文件权限或路径。如果是系统目录等, 可能需要运行管理员权限.", QMessageBox.Ok)
            else:
                # 用户取消保存，需要重新从文件读取内容来恢复原始状态
                editor_tab.set_editing(False)
                # 重新加载文件内容以丢弃用户的修改
                editor_tab.load_file(editor_tab.script_path)
                # 更新按钮和菜单文本
                self.edit_save_action.setText("✏️编辑模式")
                self.edit_save_btn.setText("✏️编辑")
                self.edit_save_action.setToolTip("进入/退出编辑模式，保存脚本更改")
                self.edit_save_btn.setToolTip("进入/退出编辑模式，保存脚本更改")

    def update_edit_save_state(self):
        """更新编辑/保存按钮状态，根据当前标签页类型"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, EditorTab):
            editor_tab = current_widget
            if editor_tab.is_editing:
                self.edit_save_action.setText("💾保存")
                self.edit_save_btn.setText("💾保存")
                self.edit_save_action.setToolTip("保存脚本更改")
                self.edit_save_btn.setToolTip("保存脚本更改")
            else:
                self.edit_save_action.setText("✏️编辑模式")
                self.edit_save_btn.setText("✏️编辑")
                self.edit_save_action.setToolTip("进入/退出编辑模式，保存脚本更改")
                self.edit_save_btn.setToolTip("进入/退出编辑模式，保存脚本更改")
        else:
            # 不是源码标签页，恢复默认文本
            self.edit_save_action.setText("✏️编辑模式")
            self.edit_save_btn.setText("✏️编辑")
            self.edit_save_action.setToolTip("进入/退出编辑模式，保存脚本更改")
            self.edit_save_btn.setToolTip("进入/退出编辑模式，保存脚本更改")

    def create_tray_icon(self):
        """创建系统托盘图标和菜单"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统托盘不可用")
            return

        # 创建托盘图标
        icon = None

        try:
            # 导入预存的Base64数据（需提前生成source_ico.py）
            from source_ico import icon_base64_data
            if icon_base64_data:
                # 解码Base64为二进制数据
                icon_data = base64.b64decode(icon_base64_data)
                # 加载到QPixmap
                pixmap = QPixmap()
                if pixmap.loadFromData(QByteArray(icon_data)):
                    icon = QIcon(pixmap)
        except ImportError:
            print("未找到source_ico.py，跳过Base64加载")
        except Exception as e:
            print(f"从Base64加载图标失败: {e}")

        if icon is None:
            # 使用默认的Qt图标
            icon = self.style().standardIcon(self.style().SP_ComputerIcon)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("PsLauncher - 脚本管理器")

        # 创建托盘菜单
        self.tray_menu = QMenu(self)

        # 打开窗口菜单项
        show_action = QAction("打开窗口", self)
        show_action.triggered.connect(self.show_from_tray)
        self.tray_menu.addAction(show_action)

        # 分隔符
        self.tray_menu.addSeparator()

        # 退出菜单项
        exit_action = QAction("退出程序", self)
        exit_action.triggered.connect(self.quit_from_tray)
        self.tray_menu.addAction(exit_action)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)

        # 连接托盘图标点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        """托盘图标被激活时的处理"""
        if reason == QSystemTrayIcon.Trigger:
            self.show_from_tray()

    def hide_to_tray(self):
        """隐藏窗口到系统托盘"""
        if self.tray_icon:
            self.hide()
            self.hidden_to_tray = True
            self.tray_icon.showMessage("PsLauncher", "程序已最小化到系统托盘", QSystemTrayIcon.Information, 2000)

    def show_from_tray(self):
        """从系统托盘恢复显示窗口"""
        if self.hidden_to_tray:
            self.show()
            self.raise_()
            self.activateWindow()
            self.hidden_to_tray = False

    def quit_from_tray(self):
        """从托盘菜单退出程序"""
        # 显示确认对话框
        reply = QMessageBox.question(self, '提示', '确定要退出 PsLauncher 吗？\n这将会停止所有正在运行的脚本。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 保存配置并停止所有进程
            self.save_config()
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()

            # 隐藏托盘图标
            if self.tray_icon:
                self.tray_icon.hide()

            # 退出应用程序
            QApplication.quit()

    def closeEvent(self, event):
        """重写关闭事件，支持隐藏到托盘"""
        # 检查是否正在隐藏到托盘
        if self.hidden_to_tray:
            event.ignore() # 忽略关闭事件，只是隐藏到托盘
            return

        if self.tabs.count() != 0:
            # 显示确认对话框
            reply = QMessageBox.Yes # 轮了一遍全是源代码tab那还确认个dier
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    reply = QMessageBox.question(self, '确认退出', '确定要退出 PsLauncher 吗？这将停止所有正在运行的脚本。', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    break
        else:
            reply = QMessageBox.Yes

        if reply == QMessageBox.Yes:
            # 关闭时自动保存配置并强制终止所有进程
            self.save_config()
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, TerminalTab):
                    widget.stop_process()

            # 隐藏托盘图标
            if self.tray_icon:
                self.tray_icon.hide()

            event.accept()
        else:
            event.ignore()

    # ======================== 脚本管理功能 ======================================

    def new_folder_at_location(self):
        """新建路径（在特定位置创建文件夹）"""
        # 获取当前选中的文件夹
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # 选中的是脚本项，获取其父文件夹路径
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # 父文件夹的完整路径
            else:
                                                                    # 选中的可能是文件夹项
                selected_folder = current_item.data(0, Qt.UserRole) # 文件夹的完整路径

        # 如果没有选中任何文件夹，让用户选择一个基础路径
        if not selected_folder:
            if self.config.get("folders"):
                # 使用配置中的第一个文件夹作为默认路径
                selected_folder = self.config["folders"][0]
            else:
                QMessageBox.warning(self, "警告", "请先添加一个文件夹路径到程序。", QMessageBox.Ok)
                return

        # 弹出对话框让用户输入新文件夹名
        folder_name, ok = QInputDialog.getText(self, "新建路径", "请输入新文件夹名称:\n（将在所选路径下创建）", QLineEdit.Normal, "")
        if not ok or not folder_name.strip():
            return

        # 构造完整路径
        new_folder_path = os.path.join(selected_folder, folder_name.strip())

        # 检查路径是否已存在
        if os.path.exists(new_folder_path):
            QMessageBox.warning(self, "警告", f"路径已存在：{new_folder_path}", QMessageBox.Ok)
            return

        try:
            os.makedirs(new_folder_path)
            QMessageBox.information(self, "成功", f"文件夹创建成功：{new_folder_path}", QMessageBox.Ok)
            # 可选：将新文件夹添加到配置中
            if new_folder_path not in self.config["folders"]:
                self.config["folders"].append(new_folder_path)
                self.save_config()
                self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建文件夹失败：{str(e)}. 有时候这是因为权限问题, 请检查是否是管理员权限执行的程序.", QMessageBox.Ok)

    def new_script_in_folder(self):
        """在当前选定的文件夹路径内新建脚本"""
        # 获取当前选中的文件夹
        current_item = self.tree.currentItem()
        selected_folder = None

        if current_item:
            script_path = current_item.data(0, Qt.UserRole)
            if script_path:
                # 选中的是脚本项，获取其父文件夹路径
                parent = current_item.parent()
                if parent:
                    selected_folder = parent.data(0, Qt.UserRole)   # 父文件夹的完整路径
            else:
                                                                    # 选中的可能是文件夹项
                selected_folder = current_item.data(0, Qt.UserRole) # 文件夹的完整路径

        # 如果没有选中任何文件夹，让用户选择一个文件夹
        if not selected_folder:
            if self.config.get("folders"):
                # 弹出文件夹选择对话框
                folder, ok = QInputDialog.getItem(self, "选择文件夹", "请选择要创建脚本的文件夹:", self.config["folders"], 0, False)
                if not ok:
                    return
                selected_folder = folder
            else:
                QMessageBox.warning(self, "警告", "请先添加一个文件夹路径到程序。", QMessageBox.Ok)
                return

        # 弹出对话框让用户输入文件名
        file_name, ok = QInputDialog.getText(self, "新建脚本", "请输入脚本文件名（包含后缀，例如：myscript.ps1）:\n"
                                             "注意：程序不会自动添加后缀，如果您不输入后缀，文件将没有扩展名。\n"
                                             "注意：PsLauncher仅扫描 .ps1, .bat, .sh 这三种后缀, 如果后缀不正确, 创建后将无法在此处立即看见.", QLineEdit.Normal, "new_script.ps1")
        if not ok or not file_name.strip():
            return

        # 检查是否改变了后缀
        new_ext = os.path.splitext(file_name)[1].lower()

        # 如果新后缀不是支持的类型，进行提示确认
        if new_ext and new_ext not in ['.ps1', '.bat', '.sh']:
            reply = QMessageBox.question(self, "后缀警告", f"您输入的后缀 {new_ext} 不是 PsLauncher 支持的脚本类型（.ps1, .bat, .sh）。\n"
                                         "这将导致文件在列表中不显示，除非再次手动编辑文件名后缀。\n\n"
                                         "是否确认继续命名？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # 如果没有后缀，提示用户确认
        if not new_ext:
            reply = QMessageBox.question(self, "无后缀警告", f"您输入的文件名没有后缀，这可能导致文件在列表中不显示。\n"
                                         "建议使用 .ps1, .bat, .sh 等支持的后缀。\n\n"
                                         "是否确认继续命名？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        file_name = file_name.strip()
        # 构造完整路径
        new_file_path = os.path.join(selected_folder, file_name)

        # 检查文件是否已存在
        if os.path.exists(new_file_path):
            reply = QMessageBox.question(self, "确认", f"文件已存在：{new_file_path}\n是否覆盖？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        try:
            # 创建空文件
            with open(new_file_path, 'w', encoding='utf-8') as f:
                # 可以根据后缀添加一些模板内容
                ext = os.path.splitext(file_name)[1].lower()
                if ext == '.ps1':
                    f.write("# PowerShell 脚本\nWrite-Host \"This is .ps1 demo created by PsLauncher.\"\n")
                elif ext == '.bat':
                    f.write("@echo off\necho This is .bat demo created by PsLauncher.\n")
                elif ext == '.sh':
                    f.write("#!/bin/bash\necho \"This is .sh demo created by PsLauncher.\"\n")
                else:
                    f.write("")

            QMessageBox.information(self, "成功", f"脚本创建成功：{new_file_path}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建脚本失败：{str(e)}", QMessageBox.Ok)

    def rename_selected_script(self):
        """重命名选定的脚本名称，检查后缀是否为支持的脚本类型"""
        # 获取当前选中的脚本项
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择一个脚本。", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "提示", "请选择一个脚本文件，而不是文件夹。", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        old_ext = os.path.splitext(old_file_name)[1].lower() # 原文件扩展名

        # 弹出对话框让用户输入新文件名
        new_file_name, ok = QInputDialog.getText(self, "重命名脚本", f"请输入新的脚本文件名：\n"
                                                 "当前文件名：{old_file_name}\n"
                                                 "注意：程序不会自动添加后缀，如果您不输入后缀，文件将没有扩展名。\n"
                                                 "注意: PsLauncher仅扫描 .ps1, .bat, .sh 这三种后缀, 如果后缀不正确, 创建后将无法在此处立即看见.", QLineEdit.Normal, old_file_name)
        if not ok or not new_file_name.strip():
            return

        new_file_name = new_file_name.strip()
        # 如果新文件名和旧文件名相同，直接返回
        if new_file_name == old_file_name:
            return

        # 检查是否改变了后缀
        new_ext = os.path.splitext(new_file_name)[1].lower()

        # 如果新后缀不是支持的类型，进行提示确认
        if new_ext and new_ext not in ['.ps1', '.bat', '.sh']:
            reply = QMessageBox.question(self, "后缀警告", f"您输入的后缀 {new_ext} 不是 PsLauncher 支持的脚本类型（.ps1, .bat, .sh）。\n"
                                         "这将导致重命名后文件在列表中不显示，除非再次手动编辑文件名后缀。\n\n"
                                         "是否确认继续重命名？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # 如果没有后缀，提示用户确认
        if not new_ext:
            reply = QMessageBox.question(self, "无后缀警告", f"您输入的文件名没有后缀，这可能导致文件在列表中不显示。\n"
                                         "建议使用 .ps1, .bat, .sh 等支持的后缀。\n\n"
                                         "是否确认继续重命名？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        new_file_path = os.path.join(folder_path, new_file_name)

        # 检查新文件是否已存在
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "警告", f"文件已存在：{new_file_path}", QMessageBox.Ok)
            return

        try:
            os.rename(script_path, new_file_path)
            QMessageBox.information(self, "成功", f"重命名成功：{old_file_name} -> {new_file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名失败：{str(e)}", QMessageBox.Ok)

    def copy_selected_script(self):
        """复制选定的脚本（提示用户重命名文件名称）"""
        # 获取当前选中的脚本项
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择一个脚本。", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "提示", "请选择一个脚本文件，而不是文件夹。", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)
        folder_path = os.path.dirname(script_path)
        name, ext = os.path.splitext(old_file_name)

        # 生成默认的新文件名：原文件名加_copy
        default_new_name = name + "_copy" + ext

        # 弹出对话框提示用户重命名文件名称
        new_file_name, ok = QInputDialog.getText(self, "复制脚本", f"请输入复制后的脚本文件名：\n"
                                                 f"原始文件名：{old_file_name}\n"
                                                 "注意：程序不会自动添加后缀，如果您不输入后缀，文件将没有扩展名。\n"
                                                 "注意: PsLauncher仅扫描 .ps1, .bat, .sh 这三种后缀, 如果后缀不正确, 创建后将无法在此处立即看见.", QLineEdit.Normal, default_new_name)

        if not ok or not new_file_name.strip():
            return # 用户取消或输入为空

        new_file_name = new_file_name.strip()

        # 检查新文件名是否有扩展名，如果没有则添加原扩展名
        if not os.path.splitext(new_file_name)[1]:
            new_file_name = new_file_name + ext

        # 构造完整的新文件路径
        new_file_path = os.path.join(folder_path, new_file_name)

        # 检查是否存在同名文件
        if os.path.exists(new_file_path):
            QMessageBox.warning(self, "警告", f"文件 '{new_file_name}' 已存在于目标文件夹中。\n"
                                "请使用不同的文件名，复制操作已取消。", QMessageBox.Ok)
            return # 拒绝进行任何复制操作

        # 执行复制操作
        try:
            shutil.copy2(script_path, new_file_path)
            QMessageBox.information(self, "成功", f"复制成功！\n"
                                    f"原始文件：{old_file_name}\n"
                                    f"新文件：{new_file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败：{str(e)}", QMessageBox.Ok)

    def move_selected_script(self):
        """移动当前脚本到当前载入的某个路径（需要有确认框）"""
        # 获取当前选中的脚本项
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择一个脚本。", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "提示", "请选择一个脚本文件，而不是文件夹。", QMessageBox.Ok)
            return

        old_file_name = os.path.basename(script_path)

        # 如果没有可用的目标文件夹，提示用户
        if not self.config.get("folders"):
            QMessageBox.warning(self, "警告", "没有可用的目标文件夹，请先添加文件夹路径。", QMessageBox.Ok)
            return

        # 弹出对话框让用户选择目标文件夹
        target_folder, ok = QInputDialog.getItem(self, "移动脚本", f"选择要将脚本 '{old_file_name}' 移动到的文件夹：", self.config["folders"], 0, False)
        if not ok:
            return

        # 检查目标文件夹是否存在
        if not os.path.exists(target_folder):
            QMessageBox.warning(self, "警告", f"目标文件夹不存在：{target_folder}", QMessageBox.Ok)
            return

        # 构造目标路径
        target_path = os.path.join(target_folder, old_file_name)

        # 检查目标文件是否已存在
        if os.path.exists(target_path):
            reply = QMessageBox.question(self, "确认", f"目标文件夹已存在同名文件：{old_file_name}\n是否覆盖？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        # 显示确认对话框
        reply = QMessageBox.question(self, "确认移动", f"确定要将脚本 '{old_file_name}' 移动到 '{target_folder}' 吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            shutil.move(script_path, target_path)
            QMessageBox.information(self, "成功", f"移动成功：{old_file_name} 已移动到 {target_folder}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"移动失败：{str(e)}", QMessageBox.Ok)

    def delete_selected_script(self):
        """删除选定的脚本（需要有确认框）"""
        # 获取当前选中的脚本项
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择一个脚本。", QMessageBox.Ok)
            return

        script_path = current_item.data(0, Qt.UserRole)
        if not script_path:
            QMessageBox.information(self, "提示", "请选择一个脚本文件，而不是文件夹。", QMessageBox.Ok)
            return

        file_name = os.path.basename(script_path)

        # 显示确认对话框
        reply = QMessageBox.question(self, "确认删除", f"确定要删除脚本 '{file_name}' 吗？\n此操作不可恢复！文件是被直接删除的, 并非移动到回收站等.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            os.remove(script_path)
            QMessageBox.information(self, "成功", f"删除成功：{file_name}", QMessageBox.Ok)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败：{str(e)}", QMessageBox.Ok)

    def show_tree_context_menu(self, position):
        """显示树形控件的右键菜单"""
        item = self.tree.itemAt(position)
        menu = QMenu(self)
        self.menu = menu
        if item:
            # 获取路径
            path = item.data(0, Qt.UserRole)
            if path:
                # 判断是文件夹还是脚本文件
                if os.path.isdir(path):
                    # 文件夹项：显示文件夹相关菜单
                    # 脚本管理菜单中的功能
                    tree_folder_action = QAction("📁 这是一个文件夹", self)
                    tree_folder_action.triggered.connect(lambda: QMessageBox.warning(self, "提示", "文件夹没有右键菜单操作. 所有操作请通过上方菜单栏进行.\n设置右键菜单只是为了统一, 以避免强迫症总是感觉程序缺少了一个功能一样...", QMessageBox.Ok))
                    menu.addAction(tree_folder_action)

                elif os.path.isfile(path) and path.lower().endswith(('.ps1', '.bat', '.sh')):
                    # 脚本项：显示脚本管理菜单
                    run_action = QAction("▶️ 运行", self)
                    run_action.triggered.connect(self.run_selected_script)
                    menu.addAction(run_action)

                    menu.addSeparator()

                    edit_action = QAction("✏️ 编辑/保存", self)
                    edit_action.triggered.connect(lambda: (self.open_editor_tab(path), self.toggle_edit_save()))
                    menu.addAction(edit_action)

                    menu.addSeparator()

                    rename_action = QAction("📝 重命名", self)
                    rename_action.triggered.connect(self.rename_selected_script)
                    menu.addAction(rename_action)

                    copy_action = QAction("📋 复制", self)
                    copy_action.triggered.connect(self.copy_selected_script)
                    menu.addAction(copy_action)

                    move_action = QAction("🚚 移动", self)
                    move_action.triggered.connect(self.move_selected_script)
                    menu.addAction(move_action)

                    delete_action = QAction("🗑️ 删除", self)
                    delete_action.triggered.connect(self.delete_selected_script)
                    menu.addAction(delete_action)
                else:
                    # 其他类型的文件或未知路径，不显示菜单项或显示默认项
                    pass
            else:
                # 没有存储路径的项（例如根节点？）
                pass
        else:
            # 空白区域：显示添加文件夹
            add_action = QAction("📂 添加文件夹路径", self)
            add_action.triggered.connect(self.add_folder)
            menu.addAction(add_action)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def on_tree_item_hovered(self, item, column):
        """树形控件项悬浮事件，显示工具提示"""
        if item:
            script_path = item.data(0, Qt.UserRole)
            if script_path:
                # 脚本项：显示完整路径
                item.setToolTip(column, script_path)
            else:
                # 文件夹项：显示完整路径
                folder_path = item.data(0, Qt.UserRole) # 完整路径
                if folder_path:
                    item.setToolTip(column, folder_path)
                else:
                                                        # 如果没有存储路径，则使用显示的文本
                    item.setToolTip(column, item.text(0))
                                                        # 注意：如果 item 为 None，不设置工具提示

    def show_tabs_context_menu(self, position):
        """显示标签页控件的右键菜单"""
        # 获取标签页索引
        tab_idx = self.tabs.tabBar().tabAt(position)
        if tab_idx == -1:
            return # 没有标签页

        menu = QMenu(self)

        # 剪贴、复制、粘贴功能
        cut_action = QAction("✂️ 剪切", self)
        cut_action.triggered.connect(self.cut_selected_text)
        menu.addAction(cut_action)

        copy_action = QAction("📋 复制", self)
        copy_action.triggered.connect(self.copy_selected_text)
        menu.addAction(copy_action)

        paste_action = QAction("📤 粘贴", self)
        paste_action.triggered.connect(self.paste_text)
        menu.addAction(paste_action)

        menu.addSeparator()

        # 对源代码标签，支持编辑或保存功能
        current_widget = self.tabs.widget(tab_idx)
        if isinstance(current_widget, EditorTab):
            if current_widget.is_editing:
                save_action = QAction("💾 保存", self)
                save_action.triggered.connect(self.toggle_edit_save)
                menu.addAction(save_action)
            else:
                edit_action = QAction("✏️ 编辑", self)
                edit_action.triggered.connect(self.toggle_edit_save)
                menu.addAction(edit_action)

        menu.addSeparator()

        # 关闭标签页
        close_action = QAction("🗑️ 关闭标签页", self)
        close_action.triggered.connect(lambda: self.close_tab(tab_idx))
        menu.addAction(close_action)

        # 显示菜单
        menu.exec_(self.tabs.mapToGlobal(position))

    def cut_selected_text(self):
        """剪切当前焦点控件的选中文本到剪贴板"""
        # 获取当前焦点控件
        focused_widget = QApplication.focusWidget()
        if focused_widget and hasattr(focused_widget, 'textCursor'):
            cursor = focused_widget.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                clipboard = QApplication.clipboard()
                clipboard.setText(selected_text)
                # 删除选中文本
                cursor.removeSelectedText()


def apply_dark_theme(app):
    """应用暗色主题到整个应用程序"""
    dark_palette = QPalette()

    # 基础颜色
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

    # 禁用状态颜色
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    app.setPalette(dark_palette)
    app.setStyle("Fusion")


def apply_font_scaling(app, scale_factor):
    """应用全局字体缩放"""
    font = app.font()
    if scale_factor != 1.0:
        font.setPointSize(int(font.pointSize() * scale_factor))
        app.setFont(font)


# ================= 程序入口 =================
if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='PsLauncher - A general script launcher')
    parser.add_argument('--scale', type=float, help='window DPI scale')
    parser.add_argument('--light', action='store_true', help='use light theme')
    parser.add_argument('--dark', action='store_true', help='use dark theme')
    parser.add_argument('--font', type=str, help='set font family')
    parser.add_argument('--height', type=int, help='window height')
    parser.add_argument('--width', type=int, help='window width')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # 加载配置文件
    config = load_json_with_comments(CONFIG_FILE)

    # 应用主题
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

    # 应用字体缩放（命令行参数优先于配置文件）
    scale_factor = 1.0
    if args.scale:
        scale_factor = args.scale
    elif "font_scale" in config:
        scale_factor = config["font_scale"]

    if scale_factor != 1.0:
        apply_font_scaling(app, scale_factor)

    # 应用字体
    font_family = config["font_family"]
    if args.font:
        font_family = args.font

    # 窗口尺寸
    height = config["height_value"]
    if args.height:
        height = args.height

    width = config["width_value"]
    if args.width:
        width = args.width

    window = MainWindow(font_family, height, width, dark_mode)
    window.show()
    sys.exit(app.exec_())
