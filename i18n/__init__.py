# coding = utf-8
# Arch   = manyArch
#
# @File name:       __init__.py
# @brief:           i18n支持框架
# @attention:       None
# @Author:          NGC13009
# @History:         2026-06-29		Create

from i18n.en import messages as _en_messages
from i18n.zh_CN import messages as _zh_CN_messages

DEFAULT_LANGUAGE = "en"
LANGUAGE_LABELS = {
    "en": "English",
    "zh_CN": "简体中文",
}

_LANGUAGE_MESSAGES = {
    "en": _en_messages,
    "zh_CN": _zh_CN_messages,
}

_current_language = DEFAULT_LANGUAGE
_messages = {}


def available_languages():
    return dict(LANGUAGE_LABELS)


def get_language():
    return _current_language


def set_language(language):
    global _current_language, _messages
    if language not in LANGUAGE_LABELS:
        language = DEFAULT_LANGUAGE

    messages = {}
    default_msgs = _LANGUAGE_MESSAGES.get(DEFAULT_LANGUAGE, {})
    messages.update(default_msgs)

    if language != DEFAULT_LANGUAGE:
        lang_msgs = _LANGUAGE_MESSAGES.get(language, {})
        messages.update(lang_msgs)

    _current_language = language
    _messages = messages
    return _current_language


def tr(key, **kwargs):
    text = _messages.get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


set_language(DEFAULT_LANGUAGE)
