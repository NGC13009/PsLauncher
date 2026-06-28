import json
import os


DEFAULT_LANGUAGE = "en"
LANGUAGE_LABELS = {
    "en": "English",
    "zh_CN": "简体中文",
}

_current_language = DEFAULT_LANGUAGE
_messages = {}


def _language_file(language):
    return os.path.join(os.path.dirname(__file__), f"{language}.json")


def available_languages():
    return dict(LANGUAGE_LABELS)


def get_language():
    return _current_language


def set_language(language):
    global _current_language, _messages
    if language not in LANGUAGE_LABELS:
        language = DEFAULT_LANGUAGE

    path = _language_file(language)
    fallback_path = _language_file(DEFAULT_LANGUAGE)

    messages = {}
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            messages.update(json.load(f))
    if path != fallback_path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            messages.update(json.load(f))

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
