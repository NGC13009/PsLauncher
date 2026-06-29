# coding = utf-8
#
# @File name:       test_tray.py
# @brief:           GUI 层：托盘隐藏/恢复/退出
# @attention:       offscreen 下 QSystemTrayIcon 行为受限，用 skipif 跳过
# @Author:          NGC13009
# @History:         2026-06-29		Create

import os
import pytest

# ============================================================
# GUI 层测试：系统托盘
# offscreen 下托盘不可用，用 skipif 跳过
# 保留用例供本地有显示环境时运行
# ============================================================

_tray_skipif_reason = "offscreen 模式下系统托盘不可用，需人工在有显示环境验证"


@pytest.mark.gui
@pytest.mark.skipif(
    os.environ.get("QT_QPA_PLATFORM") == "offscreen",
    reason=_tray_skipif_reason
)
class TestSystemTray:
    """系统托盘测试（需真实显示环境）"""

    def test_tray_icon_created(self, main_window):
        """托盘图标应被创建"""
        # 需要 mock 使 isSystemTrayAvailable 返回 True
        import PyQt5.QtWidgets
        original = PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable
        PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable = staticmethod(lambda: True)
        try:
            # 重新创建托盘
            main_window.create_tray_icon()
            assert main_window.tray_icon is not None
        finally:
            PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable = original

    def test_hide_to_tray(self, main_window):
        """隐藏到托盘"""
        if main_window.tray_icon:
            main_window.hide_to_tray()
            assert main_window.hidden_to_tray is True
            assert main_window.isVisible() is False

    def test_show_from_tray(self, main_window):
        """从托盘恢复"""
        if main_window.tray_icon:
            main_window.hide_to_tray()
            main_window.show_from_tray()
            assert main_window.hidden_to_tray is False
            assert main_window.isVisible() is True

    def test_tray_menu_actions(self, main_window):
        """托盘菜单应有显示和退出项"""
        if main_window.tray_icon:
            assert hasattr(main_window, 'tray_show_action')
            assert hasattr(main_window, 'tray_exit_action')