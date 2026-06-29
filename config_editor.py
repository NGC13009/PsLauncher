# coding = utf-8
# @File name:       config_editor.py
# @brief:           动态配置编辑对话框，根据配置字典自动生成 GUI 控件
# @Author:          NGC13009
# @History:         2026-06-30		Create

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from copy import deepcopy
from utils import _default_config, _COMMENT_MAP
from i18n import tr


class ConfigEditorDialog(QDialog):
    """动态配置编辑对话框，根据配置字典自动展开可编辑字段的 GUI"""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        # config 是 MainWindow 中 self.config 的引用，以便直接修改
        self.config = config
        self.setWindowTitle(tr("config_editor.title"))
        self.setMinimumWidth(650)
        self.setMinimumHeight(500)
        self.resize(700, 600)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 顶部说明文本
        desc_label = QLabel(tr("config_editor.desc"))
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # 可滚动的表单区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        self._form_layout = self._build_form(content, self.config)
        content.setLayout(self._form_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = QPushButton(tr("config_editor.save"))
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setMinimumWidth(80)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton(tr("config_editor.cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setMinimumWidth(80)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def _get_comment(self, key, full_path=""):
        """获取字段注释文本"""
        if full_path:
            comment = _COMMENT_MAP.get(full_path, "")
            if comment:
                return comment
        return _COMMENT_MAP.get(key, key)

    def _build_form(self, parent, config_dict, path=""):
        """递归构建表单布局"""
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.setSpacing(8)

        for key, value in config_dict.items():
            full_key = f"{path}.{key}" if path else key
            comment = self._get_comment(key, full_key)

            if isinstance(value, bool):
                widget = QCheckBox(comment)
                widget.setChecked(value)
                widget.setToolTip(comment)
                layout.addRow(QLabel(f"{key}:"), widget)

            elif isinstance(value, int):
                widget = QSpinBox()
                widget.setRange(0, 100000)
                widget.setValue(value)
                widget.setToolTip(comment)
                layout.addRow(QLabel(f"{key}:"), widget)

            elif isinstance(value, float):
                widget = QDoubleSpinBox()
                widget.setRange(0.0, 100.0)
                widget.setValue(value)
                widget.setSingleStep(0.1)
                widget.setDecimals(2)
                widget.setToolTip(comment)
                layout.addRow(QLabel(f"{key}:"), widget)

            elif isinstance(value, str):
                widget = QLineEdit(value)
                widget.setToolTip(comment)
                layout.addRow(QLabel(f"{key}:"), widget)

            elif isinstance(value, list):
                widget = self._create_list_editor(value, comment)
                layout.addRow(QLabel(f"{key}:"), widget)

            elif isinstance(value, dict):
                group = QGroupBox(f"{key}")
                group.setToolTip(comment)
                group.setFlat(False)
                group_layout = self._build_form(group, value, full_key)
                group.setLayout(group_layout)
                # 对于 dict 类型，直接作为整行添加
                layout.addRow(group)

        return layout

    def _create_list_editor(self, items, tooltip=""):
        """创建列表编辑器（QListWidget + 添加/删除按钮）"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        list_widget = QListWidget()
        list_widget.setToolTip(tooltip)
        list_widget.setAlternatingRowColors(True)
        list_widget.setMaximumHeight(120)
        for item in items:
            list_widget.addItem(str(item))

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(30)
        add_btn.setToolTip(tr("config_editor.add"))
        remove_btn = QPushButton("-")
        remove_btn.setFixedWidth(30)
        remove_btn.setToolTip(tr("config_editor.remove_selected"))
        edit_btn = QPushButton(tr("config_editor.edit"))
        edit_btn.setToolTip(tr("config_editor.edit_selected"))

        add_btn.clicked.connect(lambda: self._list_add_item(list_widget))
        remove_btn.clicked.connect(lambda: self._list_remove_item(list_widget))
        edit_btn.clicked.connect(lambda: self._list_edit_item(list_widget))

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addStretch()

        layout.addWidget(list_widget)
        layout.addLayout(btn_layout)

        # 存储引用以便 _on_save 读取
        container.list_widget = list_widget
        return container

    def _list_add_item(self, list_widget):
        """向列表中添加新项"""
        text, ok = QInputDialog.getText(self, tr("config_editor.add"), tr("config_editor.input_new_item"))
        if ok and text.strip():
            list_widget.addItem(text.strip())

    def _list_remove_item(self, list_widget):
        """从列表中删除选中项"""
        current = list_widget.currentRow()
        if current >= 0:
            list_widget.takeItem(current)

    def _list_edit_item(self, list_widget):
        """编辑列表中选中的项"""
        current = list_widget.currentItem()
        if current:
            text, ok = QInputDialog.getText(
                self, tr("config_editor.edit"), tr("config_editor.modify_value"),
                QLineEdit.Normal, current.text()
            )
            if ok and text.strip():
                current.setText(text.strip())

    def _collect_values(self, layout, config_dict, path=""):
        """递归从表单布局中收集修改后的值"""
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)

            if field_item is None:
                continue

            field_widget = field_item.widget()
            if field_widget is None:
                continue

            # 情况1：QGroupBox（跨列完整行，LabelRole 为空）
            if isinstance(field_widget, QGroupBox):
                key = field_widget.title().strip()
                if key and key in config_dict and isinstance(config_dict[key], dict):
                    inner_layout = field_widget.layout()
                    if isinstance(inner_layout, QFormLayout):
                        self._collect_values(
                            inner_layout, config_dict[key],
                            f"{path}.{key}" if path else key
                        )
                continue

            # 情况2：有 label 的普通行
            if label_item is None:
                continue
            label_widget = label_item.widget()
            if label_widget is None:
                continue

            label_text = label_widget.text() if isinstance(label_widget, QLabel) else ""
            key = label_text.replace(":", "").strip()

            if not key or key not in config_dict:
                continue

            # 根据控件类型读取值
            if isinstance(field_widget, QCheckBox):
                config_dict[key] = field_widget.isChecked()
            elif isinstance(field_widget, QSpinBox):
                config_dict[key] = field_widget.value()
            elif isinstance(field_widget, QDoubleSpinBox):
                config_dict[key] = field_widget.value()
            elif isinstance(field_widget, QLineEdit):
                config_dict[key] = field_widget.text()
            elif isinstance(field_widget, QWidget) and hasattr(field_widget, 'list_widget'):
                # 列表编辑器
                list_w = field_widget.list_widget
                items = []
                for j in range(list_w.count()):
                    items.append(list_w.item(j).text())
                config_dict[key] = items

    def _on_save(self):
        """保存修改到配置"""
        try:
            # 收集所有字段的新值，直接修改 self.config（MainWindow 的配置引用）
            self._collect_values(self._form_layout, self.config)
            self.accept()
        except Exception as e:
            QMessageBox.warning(
                self, tr("config_editor.error"),
                tr("config_editor.save_error").format(error=str(e))
            )