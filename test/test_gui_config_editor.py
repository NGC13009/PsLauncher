# coding = utf-8
#
# @File name:       test_gui_config_editor.py
# @brief:           GUI 层：ConfigEditorDialog 动态配置编辑器测试
# @Author:          NGC13009
# @History:         2026-06-30		Create

import pytest
from PyQt5.QtWidgets import *
from utils import _default_config, _COMMENT_MAP


@pytest.mark.gui
class TestConfigEditorConstruction:
    """ConfigEditorDialog 构造和基础属性测试"""

    def test_dialog_created(self, qtbot):
        """能用完整默认配置构造对话框"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        assert dialog is not None
        assert dialog.windowTitle() != ""

    def test_dialog_has_save_and_cancel_buttons(self, qtbot):
        """对话框应有保存和取消按钮"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        assert hasattr(dialog, 'save_btn')
        assert hasattr(dialog, 'cancel_btn')
        assert dialog.save_btn.text() != ""
        assert dialog.cancel_btn.text() != ""


@pytest.mark.gui
class TestBuildFormTypeMapping:
    """_build_form 根据字段类型自动生成正确控件"""

    def test_bool_field_creates_checkbox(self, qtbot):
        """bool 类型字段应生成 QCheckBox"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        # dark_mode 是 bool 类型
        layout = dialog._form_layout
        found = False
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and field_item:
                label = label_item.widget()
                if label and "dark_mode" in label.text():
                    assert isinstance(field_item.widget(), QCheckBox)
                    found = True
                    break
        assert found, "未找到 dark_mode 字段"

    def test_int_field_creates_spinbox(self, qtbot):
        """int 类型字段应生成 QSpinBox"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        layout = dialog._form_layout
        found = False
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and field_item:
                label = label_item.widget()
                if label and "height_value" in label.text():
                    assert isinstance(field_item.widget(), QSpinBox)
                    found = True
                    break
        assert found, "未找到 height_value 字段"

    def test_float_field_creates_doublespinbox(self, qtbot):
        """float 类型字段应生成 QDoubleSpinBox"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        layout = dialog._form_layout
        found = False
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and field_item:
                label = label_item.widget()
                if label and "font_scale" in label.text():
                    assert isinstance(field_item.widget(), QDoubleSpinBox)
                    found = True
                    break
        assert found, "未找到 font_scale 字段"

    def test_str_field_creates_lineedit(self, qtbot):
        """str 类型字段应生成 QLineEdit"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        layout = dialog._form_layout
        found = False
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and field_item:
                label = label_item.widget()
                if label and "font_family" in label.text():
                    assert isinstance(field_item.widget(), QLineEdit)
                    found = True
                    break
        assert found, "未找到 font_family 字段"

    def test_list_field_creates_list_editor(self, qtbot):
        """list 类型字段应生成含 QListWidget 的容器"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        layout = dialog._form_layout
        found = False
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and field_item:
                label = label_item.widget()
                if label and "folders" in label.text():
                    container = field_item.widget()
                    assert hasattr(container, 'list_widget')
                    assert isinstance(container.list_widget, QListWidget)
                    found = True
                    break
        assert found, "未找到 folders 字段"

    def test_dict_field_creates_groupbox(self, qtbot):
        """dict 类型字段应生成 QGroupBox 且递归包含子控件"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        layout = dialog._form_layout
        found_groupbox = False
        found_sub_field = False
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item is None and field_item:
                # dict 类型会直接添加 QGroupBox 作为整行（LabelRole 为空）
                groupbox = field_item.widget()
                if isinstance(groupbox, QGroupBox) and "api" in groupbox.title():
                    found_groupbox = True
                    # 检查内部是否有子字段（如 api.enabled）
                    inner_layout = groupbox.layout()
                    if isinstance(inner_layout, QFormLayout):
                        for j in range(inner_layout.rowCount()):
                            inner_label_item = inner_layout.itemAt(j, QFormLayout.LabelRole)
                            if inner_label_item and inner_label_item.widget():
                                found_sub_field = True
                                break
                    break
        assert found_groupbox, "未找到 api 字段对应的 QGroupBox"
        assert found_sub_field, "QGroupBox 内未找到子字段"


@pytest.mark.gui
class TestCollectValues:
    """_collect_values 收集表单值到配置字典"""

    def test_collect_bool_field(self, qtbot):
        """修改 CheckBox 后收集的值应正确"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        # 找到 dark_mode 字段并取反
        layout = dialog._form_layout
        for i in range(layout.rowCount()):
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if field_item and isinstance(field_item.widget(), QCheckBox):
                cb = field_item.widget()
                cb.setChecked(not cb.isChecked())
                break
        # 收集值到副本
        collected = dict(config)
        dialog._collect_values(layout, collected)
        assert collected['dark_mode'] != config['dark_mode']

    def test_collect_str_field(self, qtbot):
        """修改 LineEdit 后收集的值应正确"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        layout = dialog._form_layout
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and field_item:
                label = label_item.widget()
                if label and "font_family" in label.text():
                    line_edit = field_item.widget()
                    assert isinstance(line_edit, QLineEdit)
                    line_edit.setText("Arial")
                    break
        collected = dict(config)
        dialog._collect_values(layout, collected)
        assert collected['font_family'] == "Arial"

    def test_collect_nested_dict(self, qtbot):
        """修改嵌套 dict 字段后收集的值应正确"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        layout = dialog._form_layout
        # 找到 api 字段对应的 QGroupBox
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item is None and field_item:
                groupbox = field_item.widget()
                if isinstance(groupbox, QGroupBox) and "api" in groupbox.title():
                    inner_layout = groupbox.layout()
                    # 找到 bind_port 并修改
                    for j in range(inner_layout.rowCount()):
                        inner_label_item = inner_layout.itemAt(j, QFormLayout.LabelRole)
                        inner_field_item = inner_layout.itemAt(j, QFormLayout.FieldRole)
                        if inner_label_item and inner_field_item:
                            inner_label = inner_label_item.widget()
                            if inner_label and "bind_port" in inner_label.text():
                                spin = inner_field_item.widget()
                                if isinstance(spin, QSpinBox):
                                    spin.setValue(9999)
                                break
                    break
        collected = {"api": dict(config["api"])}
        # 仅收集 api 子布局
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item is None and field_item:
                groupbox = field_item.widget()
                if isinstance(groupbox, QGroupBox) and "api" in groupbox.title():
                    inner_layout = groupbox.layout()
                    if isinstance(inner_layout, QFormLayout):
                        dialog._collect_values(inner_layout, collected["api"])
                    break
        assert collected["api"]["bind_port"] == 9999

    def test_on_save_modifies_config_ref(self, qtbot):
        """_on_save 后传入的 config 引用内容应改变"""
        from config_editor import ConfigEditorDialog
        config = dict(_default_config)
        original_font = config.get('font_family', '')
        dialog = ConfigEditorDialog(config)
        qtbot.addWidget(dialog)
        # 修改一个字段
        layout = dialog._form_layout
        for i in range(layout.rowCount()):
            label_item = layout.itemAt(i, QFormLayout.LabelRole)
            field_item = layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and field_item:
                label = label_item.widget()
                if label and "font_family" in label.text():
                    line_edit = field_item.widget()
                    if isinstance(line_edit, QLineEdit):
                        line_edit.setText("ModifiedFont")
                    break
        # 调用保存
        dialog._on_save()
        assert config.get('font_family') == "ModifiedFont"
        assert config.get('font_family') != original_font

    def test_initial_values_match_config(self, qtbot):
        """对话框初始值应与传入 config 一致"""
        from config_editor import ConfigEditorDialog
        test_config = {
            "folders": ["/test/path"],
            "font_scale": 2.0,
            "dark_mode": False,
            "height_value": 600,
            "width_value": 800,
            "font_family": "Arial",
            "line_wrap_mode": False,
            "supported_extensions": [".ps1", ".bat"],
            "runnable_extensions": [".ps1", ".bat"],
            "syntax_highlight_mode": "none",
            "auto_run_scripts": [],
            "auto_minimize_to_tray": True,
            "language": "zh_CN",
            "api": {
                "enabled": False,
                "bind_ip": "0.0.0.0",
                "bind_port": 8080,
                "auth_token": "secret"
            }
        }
        dialog = ConfigEditorDialog(test_config)
        qtbot.addWidget(dialog)

        # 读取表单值并验证与 test_config 一致（收集到 test_config 自身，比较前后不变）
        collected = dict(test_config)
        # 深拷贝嵌套 dict
        collected["api"] = dict(test_config["api"])
        dialog._collect_values(dialog._form_layout, collected)
        for key in test_config:
            if isinstance(test_config[key], dict):
                for sub_key in test_config[key]:
                    assert collected[key][sub_key] == test_config[key][sub_key], \
                        f"字段 {key}.{sub_key} 初始值不匹配: {collected[key][sub_key]} != {test_config[key][sub_key]}"
            else:
                assert collected[key] == test_config[key], \
                    f"字段 {key} 初始值不匹配: {collected[key]} != {test_config[key]}"
