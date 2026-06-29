# coding = utf-8
#
# @File name:       test_i18n.py
# @brief:           算法层：国际化模块纯函数测试
# @Author:          NGC13009
# @History:         2026-06-29		Create

import pytest

# ============================================================
# 算法层测试：i18n 国际化模块
# 无 Qt 依赖，纯函数
# ============================================================


@pytest.mark.algo
class TestAvailableLanguages:
    """available_languages 函数测试"""

    def test_returns_dict(self):
        """应返回字典"""
        from i18n import available_languages
        langs = available_languages()
        assert isinstance(langs, dict)

    def test_contains_en(self):
        """应包含英文"""
        from i18n import available_languages
        langs = available_languages()
        assert "en" in langs

    def test_contains_zh_CN(self):
        """应包含简体中文"""
        from i18n import available_languages
        langs = available_languages()
        assert "zh_CN" in langs

    def test_labels_are_strings(self):
        """语言标签应为字符串"""
        from i18n import available_languages
        langs = available_languages()
        for label in langs.values():
            assert isinstance(label, str)


@pytest.mark.algo
class TestSetLanguage:
    """set_language 函数测试"""

    def test_set_english(self):
        """设置为英文"""
        from i18n import set_language
        result = set_language("en")
        assert result == "en"

    def test_set_chinese(self):
        """设置为中文"""
        from i18n import set_language
        result = set_language("zh_CN")
        assert result == "zh_CN"

    def test_invalid_language_falls_back_to_default(self):
        """无效语言回退到默认"""
        from i18n import set_language, DEFAULT_LANGUAGE
        result = set_language("invalid_lang")
        assert result == DEFAULT_LANGUAGE

    def test_set_language_returns_string(self):
        """返回语言代码字符串"""
        from i18n import set_language
        result = set_language("en")
        assert isinstance(result, str)


@pytest.mark.algo
class TestTr:
    """tr 翻译函数测试"""

    def test_known_key_returns_translation(self):
        """已知键返回翻译文本"""
        from i18n import set_language, tr
        set_language("zh_CN")
        result = tr("app.title")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_key_returns_key_itself(self):
        """未知键返回键本身"""
        from i18n import set_language, tr
        set_language("en")
        result = tr("this_key_does_not_exist_12345")
        assert result == "this_key_does_not_exist_12345"

    def test_tr_with_format_args(self):
        """带 format 参数的翻译"""
        from i18n import set_language, tr
        set_language("en")
        # 找一个带占位符的 key
        result = tr("message.unsupported_runnable_ext", filename="test.ps1", ext=".ps1")
        assert isinstance(result, str)

    def test_tr_after_language_switch(self):
        """切换语言后翻译应改变"""
        from i18n import set_language, tr
        set_language("en")
        en_result = tr("menu.file")
        set_language("zh_CN")
        zh_result = tr("menu.file")
        # 中文和英文结果应不同（英文="File"，中文="文件"）
        assert en_result != zh_result


@pytest.mark.algo
class TestGetLanguage:
    """get_language 函数测试"""

    def test_get_after_set(self):
        """设置后应能正确获取"""
        from i18n import set_language, get_language
        set_language("en")
        assert get_language() == "en"
        set_language("zh_CN")
        assert get_language() == "zh_CN"

    def test_get_returns_string(self):
        """返回字符串"""
        from i18n import get_language
        result = get_language()
        assert isinstance(result, str)