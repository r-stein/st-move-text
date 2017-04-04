import sublime
import sublime_plugin


def _make_move(move_point):
    def move(self, edit, forward):
        view = self.view
        new_sels = []

        for sel in view.sel():
            try:
                point = move_point(self, sel, forward)  # TODO
            except Exception as e:
                print("Error while moving:", e)
                new_sels.append(sel)
                continue
            text = view.substr(sel)
            if forward:
                new_sel = sublime.Region(point - len(text), point)
            else:
                new_sel = sublime.Region(point, point + len(text))
            view.replace(edit, sel, "")
            view.insert(edit, new_sel.begin(), text)
            new_sels.append(new_sel)
        if new_sels:
            view.sel().clear()
            view.sel().add_all(new_sels)
    return move


def _create_move_by_flags(flags):
    def move_point(self, sel, forward):
        start_point = sel.end() if forward else sel.begin()
        point = self.view.find_by_class(start_point, forward, flags)
        return point
    return _make_move(move_point)


class MoveTextCommand(sublime_plugin.TextCommand):

    # def _move_chars(self, edit, forward):
    #     view = self.view
    #     for sel in view.sel():
    #         if forward:
    #             end = sel.end()
    #             region_after = sublime.Region(end, end+1)
    #             char_after = view.substr(region_after)
    #             view.replace(edit, region_after, "")
    #             view.insert(edit, sel.begin(), char_after)
    #         else:
    #             begin = sel.begin()
    #             region_before = sublime.Region(begin-1, begin)
    #             char_before = view.substr(region_before)
    #             view.insert(edit, sel.end(), char_before)
    #             view.replace(edit, region_before, "")

    def _move_char_point(self, sel, forward):
        point = sel.end() + 1 if forward else sel.begin() - 1
        return point

    def _move_line_point(self, sel, forward):
        view = self.view
        if len(view.lines(sel)) > 1:
            raise Exception("Only single line allowed")
        line, col = view.rowcol(sel.begin())
        line += 1 if forward else -1

        point = view.text_point(line, col)
        return point

    # def _make_find_by_class(self, flags):
    #     def _move_point(self, sel, forward):
    #         start_point = sel.end() if forward else sel.begin()
    #         point = self.view.find_by_class(start_point, forward, flags)
    #         return point
    #     return self._make_move(_move_point)

    def _move_word_point(self, sel, forward):
        flags = sublime.CLASS_WORD_START | sublime.CLASS_WORD_END
        start_point = sel.end() if forward else sel.begin()
        point = self.view.find_by_class(start_point, forward, flags)
        return point

    _move_chars = _make_move(_move_char_point)
    _move_lines = _make_move(_move_line_point)
    _move_words = _create_move_by_flags(
        sublime.CLASS_WORD_START | sublime.CLASS_WORD_END)
    _move_word_ends = _create_move_by_flags(sublime.CLASS_WORD_END)
    _move_subword_ends = _create_move_by_flags(
        sublime.CLASS_WORD_END | sublime.CLASS_SUB_WORD_END)
    _move_subwords = _create_move_by_flags(
        sublime.CLASS_WORD_START | sublime.CLASS_WORD_END |
        sublime.CLASS_SUB_WORD_START | sublime.CLASS_SUB_WORD_END)

    def run(self, edit, forward=True, lines=False, by="chars"):
        if lines:
            by = "lines"
        try:
            move = getattr(self, "_move_{0}".format(by))
        except AttributeError:
            sublime.error_message("Move by '{0}' is not supported.".format(by))
        move(edit, forward)


class MoveTextToCommand(sublime_plugin.TextCommand):
    def run(self, edit, to):
        view = self.view
        print("to:", to)
        # eol, bol, eof, bof, brackets
        forward = to[0] == "e"
        w = to[2]
        new_sel = []
        if to == "brackets":
            # TODO not supported yet
            pass
        elif w == "l":
            for sel in view.sel():
                line = view.line(sel)
                content = view.substr(sel)
                if forward:
                    point = line.end()
                else:
                    point = line.begin()
                if point < sel.begin():
                    view.replace(edit, sel, "")
                    view.insert(edit, point, content)
                    new_sel.append(sublime.Region(point, point + len(content)))
                else:
                    view.insert(edit, point, content)
                    view.replace(edit, sel, "")
                    new_sel.append(sublime.Region(point - len(content), point))
        elif w == "f":
            for sel in view.sel():
                content = view.substr(sel)
                if forward:
                    point = view.size()
                else:
                    point = 0
                if point < sel.begin():
                    view.replace(edit, sel, "")
                    view.insert(edit, point, content)
                    new_sel.append(sublime.Region(point, point + len(content)))
                else:
                    view.insert(edit, point, content)
                    view.replace(edit, sel, "")
                    new_sel.append(sublime.Region(point - len(content), point))

        if new_sel:
            view.sel().clear()
            view.sel().add_all(new_sel)
            view.show(new_sel[0])
