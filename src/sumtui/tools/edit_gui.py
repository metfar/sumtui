#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

from pathlib import Path;

from ..document import TextDocument;


class GuiEditorUnavailable(RuntimeError):
    """Raised when the optional graphical editor backend is unavailable.""";


def _load_gui():
    try:
        import pygame;
        from sumgui import Button, DEFAULT_THEME, Panel, StatusBar, TextArea, enable_key_repeat, fit_window_size, get_events, make_theme;
        from sumgui.dialogs import input_box, message_box, question_box;
        from sumgui.eventbridge import is_focus_loss, touch_to_mouse_event;
    except (ImportError, ModuleNotFoundError) as exc:
        raise GuiEditorUnavailable("sumedit --gui requires sumGUI/Pygame; install with: pip install 'sumtui[gui]'") from exc;
    return pygame, Button, DEFAULT_THEME, Panel, StatusBar, TextArea, enable_key_repeat, fit_window_size, get_events, make_theme, input_box, message_box, question_box, is_focus_loss, touch_to_mouse_event;


class GuiEditApp:
    """Graphical frontend for the same ``TextDocument`` used by sumedit.""";
    def __init__(self, path=None, force_binary=False, theme=None):
        modules = _load_gui();
        (self.pygame, self.Button, default_theme, self.Panel, self.StatusBar, self.TextArea,
         enable_key_repeat, fit_window_size, self.get_events, make_theme, self.input_box, self.message_box,
         self.question_box, self.is_focus_loss, self.touch_to_mouse_event) = modules;
        self.force_binary = bool(force_binary);
        self.theme = make_theme(theme) if isinstance(theme, str) else (theme or default_theme);
        self.document = self._load_document(path);
        self.saved_text = self.document.text;
        self.undo_stack = [];
        self.redo_stack = [];
        self.max_undo = 1000;
        self.running = True;
        self.pygame.init();
        enable_key_repeat(250, 31);
        size = fit_window_size(1100, 760);
        self.screen = self.pygame.display.set_mode(size, self.pygame.RESIZABLE);
        self.pygame.display.set_caption("sumedit --gui");
        self.clock = self.pygame.time.Clock();
        self.font = self.pygame.font.SysFont("monospace", 18);
        self.small_font = self.pygame.font.SysFont("monospace", 15);
        self.panel = self.Panel(self.pygame.Rect(0, 0, *self.screen.get_size()), self.theme);
        self.editor = self.TextArea(self.pygame.Rect(0, 0, 1, 1), self.font, self.document.text, True, True, True, -1, -1, self.theme, show_v_scrollbar=True, show_h_scrollbar=True, accepts_tab=True, tab_size=4, syntax=self._syntax());
        self.status = self.StatusBar(self.pygame.Rect(0, 0, 1, 1), self.small_font, theme=self.theme, zones=[{"text":"", "width":-1}, {"text":"", "width":240}, {"text":"", "width":170}]);
        self.panel.add(self.editor);
        self.buttons = [];
        self._make_toolbar();
        self.panel.add(self.status);
        self.panel.set_focus_widget(self.editor);
        self._layout(*self.screen.get_size());
        self._update_status();

    def _load_document(self, path):
        if path is None:
            return TextDocument.empty();
        target = Path(path).expanduser();
        if not target.exists():
            return TextDocument.empty(target);
        return TextDocument.load(target, force_binary=self.force_binary);

    def _syntax(self):
        path = self.document.path;
        return "python" if path is not None and str(path).lower().endswith(".py") else None;

    def _make_toolbar(self):
        actions = [
            ("OPEN", self.open_file),
            ("SAVE", self.save_file),
            ("SAVE AS", self.save_as),
            ("RELOAD", self.reload_file),
            ("QUIT", self.request_quit),
        ];
        for index, (label, callback) in enumerate(actions):
            button = self.Button(self.pygame.Rect(0, 0, 1, 1), label, self.small_font, lambda widget, fn=callback: fn(), self.theme, tab_index=index + 1);
            self.buttons.append(button);
            self.panel.add(button);
        return None;

    def _layout(self, width, height):
        width = max(320, int(width)); height = max(240, int(height));
        self.panel.rect = self.pygame.Rect(0, 0, width, height);
        margin = 10; toolbar_h = 42; status_h = 30; gap = 8;
        button_w = max(72, min(120, (width - margin * 2 - gap * 4) // 5));
        x = margin;
        for button in self.buttons:
            button.rect = self.pygame.Rect(x, margin, button_w, toolbar_h);
            x += button_w + gap;
        editor_y = margin + toolbar_h + gap;
        self.editor.rect = self.pygame.Rect(margin, editor_y, max(1, width - margin * 2), max(1, height - editor_y - status_h - margin * 2));
        self.status.rect = self.pygame.Rect(0, height - status_h, width, status_h);
        self.editor.ensure_visible();
        return None;

    def _snapshot(self):
        return (
            self.editor.text(), self.editor.cursor_row, self.editor.cursor_col,
            self.editor.selection_anchor, self.editor.scroll_row, self.editor.scroll_col,
        );

    def _restore(self, snapshot):
        text, row, col, anchor, scroll_row, scroll_col = snapshot;
        self.editor.set_text(text);
        self.editor.cursor_row = max(0, min(int(row), len(self.editor.lines) - 1));
        self.editor.cursor_col = max(0, min(int(col), len(self.editor.lines[self.editor.cursor_row])));
        self.editor.selection_anchor = anchor;
        self.editor.scroll_row = max(0, int(scroll_row));
        self.editor.scroll_col = max(0, int(scroll_col));
        self.editor.ensure_visible();
        return True;

    def _record_edit(self, before):
        after = self._snapshot();
        if before[0] == after[0]:
            return False;
        self.undo_stack.append(before);
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack = self.undo_stack[-self.max_undo:];
        self.redo_stack = [];
        return True;

    def undo(self):
        if not self.undo_stack:
            return False;
        current = self._snapshot();
        snapshot = self.undo_stack.pop();
        self.redo_stack.append(current);
        self._restore(snapshot);
        return True;

    def redo(self):
        if not self.redo_stack:
            return False;
        current = self._snapshot();
        snapshot = self.redo_stack.pop();
        self.undo_stack.append(current);
        self._restore(snapshot);
        return True;

    def _modified(self):
        return self.editor.text() != self.saved_text;

    def _path_label(self):
        return str(self.document.path) if self.document.path is not None else "[Untitled]";

    def _update_status(self):
        marker = " *" if self._modified() else "";
        self.status.set_zone(0, self._path_label() + marker);
        self.status.set_zone(1, "{} / {}".format(self.document.encoding_label, self.document.eol));
        self.status.set_zone(2, "Ln {}, Col {}".format(self.editor.cursor_row + 1, self.editor.cursor_col + 1));
        self.pygame.display.set_caption("sumedit --gui - {}{}".format(self._path_label(), marker));
        return None;

    def _confirm_discard(self):
        if not self._modified():
            return True;
        return bool(self.question_box(self.screen, self.clock, "Unsaved changes", "Discard unsaved changes?", self.theme, yes_label="DISCARD", no_label="CANCEL"));

    def _focus_editor(self):
        self.panel.set_focus_widget(self.editor);
        return True;

    def open_file(self):
        if not self._confirm_discard():
            return False;
        default = "" if self.document.path is None else str(self.document.path);
        value = self.input_box(self.screen, self.clock, "Open file", "Path", default, self.theme);
        if not value:
            return False;
        try:
            self.document = self._load_document(value);
        except Exception as exc:
            self.message_box(self.screen, self.clock, "sumedit", str(exc), self.theme);
            return False;
        self.editor.set_text(self.document.text);
        self.editor.syntax = self._syntax();
        self.saved_text = self.document.text;
        self.undo_stack = [];
        self.redo_stack = [];
        self._focus_editor();
        return True;

    def save_file(self):
        if self.document.path is None:
            return self.save_as();
        try:
            self.document.save(text=self.editor.text());
        except Exception as exc:
            self.message_box(self.screen, self.clock, "Save error", str(exc), self.theme);
            return False;
        self.saved_text = self.editor.text();
        self._focus_editor();
        return True;

    def save_as(self):
        default = "" if self.document.path is None else str(self.document.path);
        value = self.input_box(self.screen, self.clock, "Save as", "Path", default, self.theme);
        if not value:
            return False;
        try:
            self.document.save(path=value, text=self.editor.text());
        except Exception as exc:
            self.message_box(self.screen, self.clock, "Save error", str(exc), self.theme);
            return False;
        self.saved_text = self.editor.text();
        self.editor.syntax = self._syntax();
        self._focus_editor();
        return True;

    def reload_file(self):
        if self.document.path is None:
            return False;
        if not self._confirm_discard():
            return False;
        try:
            self.document = TextDocument.load(self.document.path, force_binary=self.force_binary);
        except Exception as exc:
            self.message_box(self.screen, self.clock, "Reload error", str(exc), self.theme);
            return False;
        self.editor.set_text(self.document.text);
        self.saved_text = self.document.text;
        self.undo_stack = [];
        self.redo_stack = [];
        self._focus_editor();
        return True;

    def request_quit(self):
        if self._confirm_discard():
            self.running = False;
            return True;
        self._focus_editor();
        return False;

    def show_help(self):
        self.message_box(self.screen, self.clock, "sumedit --gui", "Ctrl+S Save   Ctrl+Shift+S Save As   Ctrl+O Open\nCtrl+Z Undo   Ctrl+Y Redo   F10/Ctrl+Q Quit\nSelection, clipboard, tabs and scrollbars use the SumGUI TextArea.", self.theme);
        self._focus_editor();
        return True;

    def _global_key(self, event):
        if event.type != self.pygame.KEYDOWN:
            return False;
        mods = getattr(event, "mod", self.pygame.key.get_mods());
        ctrl = bool(mods & self.pygame.KMOD_CTRL); shift = bool(mods & self.pygame.KMOD_SHIFT);
        if event.key == self.pygame.K_F1:
            return self.show_help();
        if event.key == self.pygame.K_F10 or (ctrl and event.key == self.pygame.K_q):
            return self.request_quit();
        if ctrl and event.key == self.pygame.K_s:
            return self.save_as() if shift else self.save_file();
        if ctrl and event.key == self.pygame.K_o:
            return self.open_file();
        if ctrl and event.key == self.pygame.K_z and not shift:
            return self.undo();
        if ctrl and (event.key == self.pygame.K_y or (event.key == self.pygame.K_z and shift)):
            return self.redo();
        return False;

    def _normalize_event(self, event):
        if self.is_focus_loss(event):
            self.panel.cancel_pointer_capture();
            return None;
        finger_types = (getattr(self.pygame, "FINGERDOWN", -101), getattr(self.pygame, "FINGERMOTION", -102), getattr(self.pygame, "FINGERUP", -103));
        if event.type in finger_types:
            return self.touch_to_mouse_event(event, self.screen.get_size());
        if event.type in (self.pygame.MOUSEBUTTONDOWN, self.pygame.MOUSEBUTTONUP, self.pygame.MOUSEMOTION) and getattr(event, "touch", False):
            return None;
        return event;

    def run(self):
        try:
            while self.running:
                dt = self.clock.tick(60);
                for raw_event in self.get_events():
                    event = self._normalize_event(raw_event);
                    if event is None:
                        continue;
                    if event.type == self.pygame.QUIT:
                        self.request_quit();
                        continue;
                    if event.type == getattr(self.pygame, "VIDEORESIZE", -1):
                        width = max(320, int(getattr(event, "w", self.screen.get_width())));
                        height = max(240, int(getattr(event, "h", self.screen.get_height())));
                        self.screen = self.pygame.display.set_mode((width, height), self.pygame.RESIZABLE);
                        self._layout(width, height);
                        continue;
                    if self._global_key(event):
                        continue;
                    before = self._snapshot();
                    self.panel.handle_event(event);
                    self._record_edit(before);
                self.panel.update(dt);
                self._update_status();
                self.screen.fill(self.theme.bg);
                self.panel.draw(self.screen);
                self.pygame.display.flip();
        finally:
            self.pygame.quit();
        return 0;


def run_gui_editor(path=None, force_binary=False, theme=None):
    return GuiEditApp(path=path, force_binary=force_binary, theme=theme).run();
