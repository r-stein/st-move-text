import operator
import re

import sublime
import sublime_plugin


def contains(a, b):
    """Check whether a contains b."""
    return bool(re.search(b, a))


def match(a, b):
    """Check whether a matches b."""
    return bool(re.match(b, a))


op_map = {
    sublime.OP_EQUAL: operator.eq,
    sublime.OP_NOT_EQUAL: operator.ne,
    sublime.OP_REGEX_CONTAINS: contains,
    sublime.OP_REGEX_MATCH: match,
    sublime.OP_NOT_REGEX_CONTAINS: lambda a, b: not contains(a, b),
    sublime.OP_NOT_REGEX_MATCH: lambda a, b: not match(a, b),
}


class MoveContextEvents(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if not key.startswith("move_text."):
            return
        setting_list = key.split(".")[1:]

        if len(setting_list) >= 2 and setting_list[0] == "setting":
            rem_setting_list = setting_list[1:]
            settings = sublime.load_settings("MoveText.sublime-settings")
            try:
                res = settings
                for s in rem_setting_list:
                    res = res.get(s)
                    if res is None:
                        KeyError
            except (AttributeError, KeyError):
                setting_name = ".".join(rem_setting_list)
                result = settings.get(setting_name)
            else:
                result = res
        else:
            print("Invalid context key '{0}'.".format(key))
            return

        return op_map[operator](operand, result)
