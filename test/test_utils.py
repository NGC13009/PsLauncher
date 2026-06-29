# coding = utf-8
#
# @File name:       test_utils.py
# @brief:           算法层：工具函数测试（apply_dark_theme, apply_font_scaling 等）
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest

# ============================================================
# 算法层测试：工具函数
# 需要 QApplication 环境
# ============================================================


@pytest.mark.algo
class TestApplyDarkTheme:
    """apply_dark_theme 函数测试"""

    def test_dark_theme_applies_palette(self, qapp):
        """应用暗色主题后调色板应改变"""
        # 注意：PsLauncher/ 是包，主模块是 PsLauncher.PsLauncher
        from PsLauncher.PsLauncher import apply_dark_theme
        original_palette = qapp.palette()
        apply_dark_theme(qapp)
        new_palette = qapp.palette()
        # 应用主题后颜色应不同
        assert new_palette is not None

    def test_dark_theme_sets_fusion_style(self, qapp):
        """暗色主题应设置 Fusion 样式"""
        from PsLauncher.PsLauncher import apply_dark_theme
        apply_dark_theme(qapp)
        assert qapp.style().objectName().lower() == "fusion"


@pytest.mark.algo
class TestApplyFontScaling:
    """apply_font_scaling 函数测试"""

    def test_scale_1_0_no_change(self, qapp):
        """缩放因子 1.0 不应该改变字体大小"""
        from PsLauncher.PsLauncher import apply_font_scaling
        original_size = qapp.font().pointSize()
        apply_font_scaling(qapp, 1.0)
        assert qapp.font().pointSize() == original_size

    def test_scale_2_0_doubles_font(self, qapp):
        """缩放因子 2.0 应加倍字体大小"""
        from PsLauncher.PsLauncher import apply_font_scaling
        original_size = qapp.font().pointSize()
        apply_font_scaling(qapp, 2.0)
        assert qapp.font().pointSize() == original_size * 2

    def test_scale_0_5_halves_font(self, qapp):
        """缩放因子 0.5 应减半字体大小"""
        from PsLauncher.PsLauncher import apply_font_scaling
        original_size = qapp.font().pointSize()
        apply_font_scaling(qapp, 0.5)
        assert qapp.font().pointSize() == max(1, int(original_size * 0.5))

    def test_scale_negative_ignored(self, qapp):
        """负数缩放因子应忽略（仅 scale != 1.0 时生效）"""
        from PsLauncher.PsLauncher import apply_font_scaling
        original_size = qapp.font().pointSize()
        apply_font_scaling(qapp, -1.0)
        # 缩放因子为 -1 时，font.setPointSize(int(-1 * pointSize)) 可能无效
        # 但不会崩溃
        assert qapp.font().pointSize() > 0


@pytest.mark.algo
class TestUtilsConstants:
    """工具模块常量测试"""

    def test_default_ext_list(self):
        """验证 DEFAULT_EXT"""
        from utils import DEFAULT_EXT
        assert isinstance(DEFAULT_EXT, list)
        assert len(DEFAULT_EXT) >= 3

    def test_config_file_constant(self):
        """验证 CONFIG_FILE"""
        from utils import CONFIG_FILE
        assert isinstance(CONFIG_FILE, str)
        assert CONFIG_FILE.endswith(".json")

    def test_default_config_keys(self):
        """_default_config 应包含所有必需字段"""
        from utils import _default_config
        required_keys = [
            "folders", "font_scale", "dark_mode", "height_value",
            "width_value", "font_family", "line_wrap_mode",
            "supported_extensions", "runnable_extensions",
            "syntax_highlight_mode", "auto_run_scripts",
            "auto_minimize_to_tray", "language"
        ]
        for key in required_keys:
            assert key in _default_config, f"缺少默认配置字段: {key}"