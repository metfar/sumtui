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
#
#import warnings;
#warnings.filterwarnings("ignore", category=UserWarning);
import io;
import os;
import subprocess;
import sys;
import tempfile;
import unittest;
from pathlib import Path;

from rich.console import Console;
from rich.style import Style;

from sumtui import Application, BrowseForm, Button, CheckBox, Choice, Column, CommandWindow, ContextMenu, Dialog, FileDialog, FormField, GroupBox, HBox, HexView, KeyBindingManager, ListView, MarkdownView, SyntaxView, Menu, MenuBar, MenuDesktop, MenuItem, Panel, ProgressBar, RecordForm, ScrollBar, Separator, Slider, Splitter, RadioGroup, TableView, TextEditor, TextInput, TextView, TreeNode, TreeView, VBox, format_key_spec;
from sumtui.backends import AnsiDecoder, PosixInput;
from sumtui.events import Key, KeyEvent, normalize_key_spec;
from sumtui.theme import make_theme;
from sumtui.progress_cli_support import parse_size;
from sumtui.tools.edit import EditApp;
from sumtui.syntax import EditorSyntaxHighlighter, ExtendedBasicLexer, detect_mode;


class ThemeTests(unittest.TestCase):
    def test_sumgui_theme_names(self):
        self.assertEqual(make_theme("ZX").name, "ZX");
        self.assertEqual(make_theme("DOS").name, "DOS");
        self.assertEqual(make_theme("C64").name, "C64");
        self.assertEqual(make_theme("MSX").name, "MSX");
        self.assertEqual(make_theme("Dark").name, "Dark");
        self.assertEqual(make_theme("Light").name, "Light");

    def test_rar_theme(self):
        self.assertEqual(make_theme("rar").name, "RAR");

    def test_ralesk_mc_theme_uses_geany_semantic_palette(self):
        theme = make_theme("ralesk");
        self.assertEqual(theme.name, "Ralesk's MC");
        self.assertEqual(theme.style("viewer"), "#c0c0c0 on #111144");
        self.assertEqual(theme.style("syntax_keyword"), "bold #f4d432");
        self.assertEqual(theme.style("syntax_string"), "#33aa33");
        self.assertEqual(theme.style("syntax_comment"), "italic #996600");
        self.assertEqual(theme.style("editor_gutter"), "#111144 on #339933");

    def test_editor_hidden_character_roles_are_distinct(self):
        theme = make_theme("DOS");
        self.assertNotEqual(theme.style("editor_space"), theme.style("editor_tab"));
        self.assertNotEqual(theme.style("editor_tab"), theme.style("editor_eol"));
        self.assertNotEqual(theme.style("editor_eol"), theme.style("editor_control"));


class EventTests(unittest.TestCase):
    def test_key_spec(self):
        self.assertEqual(normalize_key_spec("Shift-Ctrl-A"), "ctrl+shift+a");

    def test_ansi_keys(self):
        decoder = AnsiDecoder();
        self.assertEqual(decoder.feed(b"\x1b[A")[0].key, Key.UP);
        self.assertEqual(decoder.feed(b"\x1b[21~")[0].key, Key.F10);
        event = decoder.feed(b"\x1b[Z")[0];
        self.assertEqual(event.key, Key.TAB);
        self.assertTrue(event.shift);
        event = decoder.feed(b"\x1b[1;2C")[0];
        self.assertEqual(event.key, Key.RIGHT);
        self.assertTrue(event.shift);
        event = decoder.feed(b"\x1b[1;5D")[0];
        self.assertEqual(event.key, Key.LEFT);
        self.assertTrue(event.ctrl);
        event = decoder.feed(b"\x1b[5;2~")[0];
        self.assertEqual(event.key, Key.PAGE_UP);
        self.assertTrue(event.shift);
        event = decoder.feed(b"\x1b[6;2~")[0];
        self.assertEqual(event.key, Key.PAGE_DOWN);
        self.assertTrue(event.shift);
        event = decoder.feed(b"\x1b[1;5H")[0];
        self.assertEqual(event.key, Key.HOME);
        self.assertTrue(event.ctrl);
        event = decoder.feed(b"\x1b[1;5F")[0];
        self.assertEqual(event.key, Key.END);
        self.assertTrue(event.ctrl);
        event = decoder.feed(b"\x1b[1;2H")[0];
        self.assertEqual(event.key, Key.HOME);
        self.assertTrue(event.shift);
        event = decoder.feed(b"\x1b[20;5~")[0];
        self.assertEqual(event.key, Key.F9);
        self.assertTrue(event.ctrl);
        event = decoder.feed(b"\x1b[20;3~")[0];
        self.assertEqual(event.key, Key.F9);
        self.assertTrue(event.alt);

    def test_rxvt_shift_cursor_and_page_sequences(self):
        decoder = AnsiDecoder();
        for sequence, expected in ((b"\x1b[a", Key.UP), (b"\x1b[b", Key.DOWN), (b"\x1b[c", Key.RIGHT), (b"\x1b[d", Key.LEFT), (b"\x1b[5$", Key.PAGE_UP), (b"\x1b[6$", Key.PAGE_DOWN)):
            event = decoder.feed(sequence)[0];
            self.assertEqual(event.key, expected);
            self.assertTrue(event.shift);

    def test_runtime_extra_shift_sequence_can_be_added(self):
        decoder = AnsiDecoder();
        decoder.add_sequence(b"\x1b[99~", Key.DOWN, shift=True);
        event = decoder.feed(b"\x1b[99~")[0];
        self.assertEqual(event.key, Key.DOWN);
        self.assertTrue(event.shift);

    def test_split_ansi_sequence(self):
        decoder = AnsiDecoder();
        self.assertEqual(decoder.feed(b"\x1b["), []);
        event = decoder.feed(b"A")[0];
        self.assertEqual(event.key, Key.UP);

    def test_escape_timeout(self):
        decoder = AnsiDecoder(escape_timeout=0.01);
        self.assertEqual(decoder.feed(b"\x1b", now=1.0), []);
        event = decoder.feed(b"", now=1.02)[0];
        self.assertEqual(event.key, Key.ESCAPE);

    def test_unicode(self):
        decoder = AnsiDecoder();
        event = decoder.feed("ñ".encode("utf-8"))[0];
        self.assertEqual(event.text, "ñ");


class TextEditorTests(unittest.TestCase):
    def test_multiline_editing_and_cursor(self):
        editor = TextEditor("one\ntwo");
        editor.row = 0;
        editor.column = 3;
        self.assertTrue(editor.handle_event(KeyEvent(Key.ENTER)));
        self.assertEqual(editor.text, "one\n\ntwo");
        self.assertEqual((editor.cursor_line, editor.cursor_column), (2, 1));
        self.assertTrue(editor.handle_event(KeyEvent("x", text="x")));
        self.assertEqual(editor.lines[1], "x");
        self.assertTrue(editor.modified);

    def test_command_get_viewport_width_and_height_are_independent(self):
        command = CommandWindow();
        field = command.define_field("TXT", 1, 2, 3, "abcdefghi", fixed=False, height=2, max_length=12, multiline=True);
        self.assertEqual(field.width, 3);
        self.assertEqual(field.height, 2);
        self.assertEqual(field.value, "abcdefghi");
        command.begin_read();
        command.read_cursor = 8;
        console = Console(width=30, height=10, record=True, force_terminal=False);
        console.print(command);
        self.assertGreaterEqual(command.read_y_offset, 1);



class TableTests(unittest.TestCase):
    def test_navigation(self):
        table = TableView([Column("Name")]);
        table.add_row(["a"], value="a");
        table.add_row(["b"], value="b");
        self.assertTrue(table.handle_event(KeyEvent(Key.DOWN)));
        self.assertEqual(table.current_value, "b");
        table.handle_event(KeyEvent(Key.HOME));
        self.assertEqual(table.current_value, "a");

    def test_table_accepts_cells_value_pairs(self):
        table = TableView([Column("Name")]);
        table.set_rows([(["one"], 1), (["two"], 2)]);
        self.assertEqual(table.current_value, 1);
        table.move(1);
        self.assertEqual(table.current_value, 2);



class FormTests(unittest.TestCase):
    def test_text_input_editing(self):
        field = TextInput("ab");
        field.handle_event(KeyEvent("c", text="c"));
        self.assertEqual(field.value, "abc");
        field.handle_event(KeyEvent(Key.LEFT));
        field.handle_event(KeyEvent(Key.BACKSPACE));
        self.assertEqual(field.value, "ac");

    def test_checkbox(self):
        box = CheckBox("Solid");
        self.assertTrue(box.handle_event(KeyEvent(Key.SPACE)));
        self.assertTrue(box.checked);

    def test_radio_group(self):
        group = RadioGroup([("One", 1), ("Two", 2)], value=1);
        self.assertEqual(group.value, 1);
        group.buttons[1].select();
        self.assertEqual(group.value, 2);
        self.assertFalse(group.buttons[0].checked);
        self.assertTrue(group.buttons[1].checked);

    def test_radio_group_arrow_navigation_moves_selection_and_focus(self):
        group = RadioGroup([("One", 1), ("Two", 2), ("Three", 3)], value=1);
        root = VBox(group, Button("OK"));
        app = Application(root=root, theme="RAR");
        self.assertIs(app.focus.current, group.buttons[0]);
        self.assertTrue(app.dispatch(KeyEvent(Key.DOWN)));
        self.assertEqual(group.value, 2);
        self.assertIs(app.focus.current, group.buttons[1]);
        self.assertTrue(app.dispatch(KeyEvent(Key.RIGHT)));
        self.assertEqual(group.value, 3);
        self.assertIs(app.focus.current, group.buttons[2]);
        self.assertTrue(app.dispatch(KeyEvent(Key.DOWN)));
        self.assertEqual(group.value, 1);
        self.assertIs(app.focus.current, group.buttons[0]);

    def test_checkbox_arrow_navigation_keeps_values(self):
        first = CheckBox("One", checked=True);
        second = CheckBox("Two", checked=False);
        third = CheckBox("Three", checked=True);
        root = VBox(first, second, third, Button("OK"));
        app = Application(root=root, theme="RAR");
        self.assertIs(app.focus.current, first);
        self.assertTrue(app.dispatch(KeyEvent(Key.DOWN)));
        self.assertIs(app.focus.current, second);
        self.assertTrue(first.checked);
        self.assertFalse(second.checked);
        self.assertTrue(third.checked);
        self.assertTrue(app.dispatch(KeyEvent(Key.RIGHT)));
        self.assertIs(app.focus.current, third);
        self.assertTrue(app.dispatch(KeyEvent(Key.DOWN)));
        self.assertIs(app.focus.current, first);
        self.assertTrue(first.checked);
        self.assertFalse(second.checked);
        self.assertTrue(third.checked);

    def test_choice(self):
        choice = Choice([("A", "a"), ("B", "b")], value="a");
        choice.handle_event(KeyEvent(Key.RIGHT));
        self.assertEqual(choice.value, "b");

    def test_button(self):
        pressed = [];
        button = Button("OK", on_press=lambda: pressed.append(True));
        self.assertTrue(button.handle_event(KeyEvent(Key.ENTER)));
        self.assertEqual(pressed, [True]);

    def test_progress(self):
        progress = ProgressBar(50, maximum=100);
        self.assertEqual(progress.fraction, 0.5);
        progress.advance(25);
        self.assertEqual(progress.value, 75.0);

    def test_slider_keyboard(self):
        changes = [];
        slider = Slider(0, 100, 50, step=5, on_change=lambda widget, value: changes.append((widget, value)));
        self.assertTrue(slider.handle_event(KeyEvent(Key.RIGHT)));
        self.assertEqual(slider.value, 55.0);
        slider.handle_event(KeyEvent(Key.PAGE_UP));
        self.assertEqual(slider.value, 80.0);
        slider.handle_event(KeyEvent(Key.HOME));
        self.assertEqual(slider.value, 0.0);
        slider.handle_event(KeyEvent(Key.END));
        self.assertEqual(slider.value, 100.0);
        self.assertTrue(changes);
        self.assertIs(changes[-1][0], slider);

    def test_button_focus_marker(self):
        console = Console(width=20, height=3, record=True, force_terminal=False, file=io.StringIO());
        button = Button("OK", width=10);
        button.focused = True;
        console.print(button);
        self.assertIn("> OK <", console.export_text());

    def test_text_view(self):
        view = TextView("one\ntwo\nthree");
        view.page_size = 1;
        self.assertTrue(view.handle_event(KeyEvent(Key.DOWN)));
        self.assertEqual(view.offset, 1);

    def test_text_view_horizontal_scroll(self):
        console = Console(width=12, height=3, record=True, force_terminal=False, file=io.StringIO());
        view = TextView("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ");
        console.print(view);
        self.assertGreater(view.max_x_offset, 0);
        self.assertTrue(view.handle_event(KeyEvent(Key.RIGHT)));
        self.assertEqual(view.x_offset, 1);
        self.assertTrue(view.handle_event(KeyEvent(Key.RIGHT, ctrl=True)));
        self.assertEqual(view.x_offset, view.max_x_offset);
        self.assertTrue(view.handle_event(KeyEvent(Key.LEFT, ctrl=True)));
        self.assertEqual(view.x_offset, 0);



class CommandWindowTests(unittest.TestCase):
    def test_submit_and_history(self):
        received = [];
        command = CommandWindow(on_submit=lambda value, widget: received.append(value));
        command.set_value("STORE 5 TO A");
        self.assertTrue(command.submit());
        self.assertEqual(received, ["STORE 5 TO A"]);
        self.assertEqual(command.command_history, ["STORE 5 TO A"]);
        self.assertTrue(command.handle_event(KeyEvent(Key.UP)));
        self.assertEqual(command.value, "STORE 5 TO A");

    def test_shift_pageup_pagedown_scroll_command_history(self):
        command = CommandWindow();
        command._last_content_height = 4;
        for index in range(20):
            command.write("line {}".format(index));
        self.assertEqual(command.history_scroll, 0);
        self.assertTrue(command.handle_event(KeyEvent(Key.PAGE_UP, shift=True)));
        self.assertGreater(command.history_scroll, 0);
        self.assertTrue(command.handle_event(KeyEvent(Key.PAGE_DOWN, shift=True)));
        self.assertEqual(command.history_scroll, 0);

    def test_pageup_pagedown_scroll_command_history(self):
        command = CommandWindow();
        command._last_content_height = 4;
        for index in range(20):
            command.write("line {}".format(index));
        self.assertEqual(command.history_scroll, 0);
        self.assertTrue(command.handle_event(KeyEvent(Key.PAGE_UP)));
        self.assertGreater(command.history_scroll, 0);
        self.assertTrue(command.handle_event(KeyEvent(Key.PAGE_DOWN)));
        self.assertEqual(command.history_scroll, 0);

    def test_command_render_has_black_background_role(self):
        console = Console(width=40, height=6, record=True, force_terminal=False, file=io.StringIO());
        command = CommandWindow();
        command.write("hello");
        console.print(command);
        self.assertIn("hello", console.export_text());

    def test_command_prompt_is_visible_on_last_interior_row(self):
        console = Console(width=40, height=8, force_terminal=False);
        command = CommandWindow();
        command.write("hello");
        panel = Panel(command, title="Command", content_style="command");
        panel.set_theme(make_theme("XBASE"));
        lines = console.render_lines(panel, console.options.update(height=8), pad=True);
        plain = ["".join(segment.text for segment in line) for line in lines];
        self.assertEqual(len(plain), 8);
        self.assertIn("hello", plain[1]);
        self.assertIn(".", plain[-2]);

    def test_command_panel_can_fill_complete_interior_black(self):
        console = Console(width=40, height=8, force_terminal=False);
        command = CommandWindow();
        command.write("hello");
        panel = Panel(command, title="Command", content_style="command");
        panel.set_theme(make_theme("XBASE"));
        lines = console.render_lines(panel, console.options.update(height=8), pad=True);
        blank_interior = lines[1];
        black = (0, 0, 0);
        for segment in blank_interior:
            if not segment.text:
                continue;
            self.assertIsNotNone(segment.style);
            self.assertIsNotNone(segment.style.bgcolor);
            self.assertEqual(tuple(segment.style.bgcolor.get_truecolor()), black);

    def test_command_write_at_uses_absolute_workspace_coordinates(self):
        console = Console(width=40, height=10, force_terminal=False);
        command = CommandWindow();
        command.write("history");
        command.write_at(4, 5, "HELLO");
        command.set_theme(make_theme("XBASE"));
        lines = console.render_lines(command, console.options.update(height=8), pad=True);
        plain = ["".join(segment.text for segment in line) for line in lines];
        self.assertEqual(plain[4][5:10], "HELLO");
        self.assertIn(".", plain[-1]);

    def test_command_clear_removes_coordinate_screen(self):
        command = CommandWindow();
        command.write_at(2, 3, "X");
        self.assertTrue(command.screen);
        command.clear();
        self.assertFalse(command.screen);

    def test_command_screen_fields_are_editable_during_read(self):
        command = CommandWindow();
        accepted = [];
        command.define_field("NOM", 2, 10, 10, " " * 10);
        command.define_field("APE", 4, 10, 10, " " * 10);
        self.assertTrue(command.begin_read(on_accept=lambda values, _widget: accepted.append(values)));
        for char in "Ana":
            self.assertTrue(command.handle_event(KeyEvent(char.lower(), text=char)));
        self.assertTrue(command.handle_event(KeyEvent(Key.ENTER)));
        for char in "Bas":
            self.assertTrue(command.handle_event(KeyEvent(char.lower(), text=char)));
        self.assertTrue(command.handle_event(KeyEvent(Key.ENTER)));
        self.assertFalse(command.read_active);
        self.assertEqual(accepted[0]["NOM"], "Ana".ljust(10));
        self.assertEqual(accepted[0]["APE"], "Bas".ljust(10));

    def test_multiline_last_get_tab_accepts_read(self):
        command = CommandWindow();
        accepted = [];
        command.define_field("NAME", 1, 1, 8, "Ana", fixed=False);
        command.define_field("NOTES", 3, 1, 12, "line one", fixed=False, height=3, multiline=True);
        command.begin_read(on_accept=lambda values, _widget: accepted.append(values));
        self.assertTrue(command.handle_event(KeyEvent(Key.TAB)));
        self.assertEqual(command.read_index, 1);
        self.assertTrue(command.handle_event(KeyEvent(Key.ENTER)));
        self.assertTrue(command.read_active);
        self.assertTrue(command.handle_event(KeyEvent(Key.TAB)));
        self.assertFalse(command.read_active);
        self.assertEqual(len(accepted), 1);
        self.assertIn("\n", accepted[0]["NOTES"]);

    def test_command_commit_screen_archives_gets_as_plain_history(self):
        command = CommandWindow();
        command.write("before");
        command.write_at(1, 1, "Notes:");
        command.define_field("NOTES", 2, 1, 10, "hello world", fixed=False, height=2, multiline=True);
        command.begin_read();
        archived = command.commit_screen_to_history();
        self.assertFalse(command.read_active);
        self.assertFalse(command.fields);
        self.assertFalse(command.screen);
        self.assertIn(" Notes:", archived);
        self.assertIn(" hello worl", archived);
        history = [line for line, _style in command.output];
        self.assertIn(" Notes:", history);
        self.assertIn(" hello worl", history);

    def test_command_read_render_shows_field_and_cursor(self):
        console = Console(width=50, height=10, force_terminal=False);
        command = CommandWindow();
        command.write_at(2, 1, "Nombre:");
        command.define_field("NOM", 2, 9, 12, " " * 12);
        command.begin_read();
        command.set_theme(make_theme("XBASE"));
        lines = console.render_lines(command, console.options.update(height=8), pad=True);
        plain = ["".join(segment.text for segment in line) for line in lines];
        self.assertIn("Nombre:", plain[2]);
        self.assertIn("READ", plain[-1]);

    def test_command_read_backspace_shifts_remaining_text_left(self):
        command = CommandWindow();
        command.define_field("TXT", 2, 10, 8, "abcdef  ");
        command.begin_read();
        command.read_cursor = 4;
        self.assertTrue(command.handle_event(KeyEvent(Key.BACKSPACE)));
        self.assertEqual(command.read_cursor, 3);
        self.assertEqual(command.fields[0].value, "abcef   ");

    def test_application_tab_is_consumed_by_command_read_before_focus_move(self):
        console = Console(width=80, height=24, force_terminal=False);
        command = CommandWindow();
        other = TextInput("outside");
        app = Application(root=VBox(command, other), theme="XBASE", console=console);
        command.define_field("NOM", 2, 10, 10, " " * 10);
        command.define_field("APE", 4, 10, 10, " " * 10);
        command.begin_read();
        self.assertIs(app.focus.current, command);
        self.assertEqual(command.read_index, 0);
        app.dispatch(KeyEvent(Key.TAB));
        self.assertIs(app.focus.current, command);
        self.assertEqual(command.read_index, 1);
        app.dispatch(KeyEvent(Key.TAB, shift=True));
        self.assertIs(app.focus.current, command);
        self.assertEqual(command.read_index, 0);

    def test_command_read_full_field_caret_moves_after_last_cell_and_backspace_deletes_last(self):
        command = CommandWindow();
        command.define_field("TXT", 2, 10, 5, " " * 5);
        command.begin_read();
        for char in "12345":
            self.assertTrue(command.handle_event(KeyEvent(char, text=char)));
        self.assertEqual(command.read_cursor, 5);
        self.assertEqual(command.fields[0].value, "12345");
        self.assertTrue(command.handle_event(KeyEvent(Key.BACKSPACE)));
        self.assertEqual(command.read_cursor, 4);
        self.assertEqual(command.fields[0].value, "1234 ");

    def test_command_read_end_and_right_allow_after_field_caret(self):
        command = CommandWindow();
        command.define_field("TXT", 2, 10, 5, "12345");
        command.begin_read();
        command.read_cursor = 4;
        self.assertTrue(command.handle_event(KeyEvent(Key.RIGHT)));
        self.assertEqual(command.read_cursor, 5);
        self.assertFalse(command.handle_event(KeyEvent(Key.RIGHT)));
        command.read_cursor = 0;
        self.assertTrue(command.handle_event(KeyEvent(Key.END)));
        self.assertEqual(command.read_cursor, 5);
        self.assertFalse(command.handle_event(KeyEvent(Key.DELETE)));

    def test_command_read_render_places_after_field_caret_outside_field(self):
        console = Console(width=30, height=8, force_terminal=False);
        command = CommandWindow();
        command.define_field("TXT", 2, 4, 5, "12345");
        command.begin_read();
        command.read_cursor = 5;
        command.set_theme(make_theme("XBASE"));
        lines = console.render_lines(command, console.options.update(height=7), pad=True);
        line = lines[2];
        # Field occupies columns 4..8; the caret style belongs at column 9.
        cursor_style = command.theme.style("cursor_cell");
        cells = [];
        for segment in line:
            for char in segment.text:
                cells.append((char, segment.style));
        self.assertGreater(len(cells), 9);
        self.assertEqual(cells[4][0], "1");
        self.assertEqual(cells[8][0], "5");
        self.assertEqual(cells[9][1], Style.parse(cursor_style));


class ApplicationTests(unittest.TestCase):
    def test_focus_and_modal_stack(self):
        console = Console(width=80, height=24, force_terminal=False);
        first = TextInput("one");
        second = TextInput("two");
        root = VBox(first, second);
        app = Application(root=root, theme="RAR", console=console);
        self.assertIs(app.focus.current, first);
        app.dispatch(KeyEvent(Key.TAB));
        self.assertIs(app.focus.current, second);
        dialog_field = TextInput("modal");
        dialog = Dialog(dialog_field, on_cancel=app.pop_modal);
        app.push_modal(dialog);
        self.assertEqual(app.modal_depth, 1);
        self.assertIs(app.focus.current, dialog_field);
        app.dispatch(KeyEvent(Key.ESCAPE));
        self.assertEqual(app.modal_depth, 0);
        self.assertIs(app.root, root);

    def test_buttons_are_in_tab_order(self):
        console = Console(width=80, height=24, force_terminal=False);
        field = TextInput("archive.rar");
        ok = Button("OK");
        cancel = Button("Cancel");
        app = Application(root=VBox(field, HBox(ok, cancel)), theme="RAR", console=console);
        self.assertIs(app.focus.current, field);
        app.dispatch(KeyEvent(Key.TAB));
        self.assertIs(app.focus.current, ok);
        self.assertTrue(ok.focused);
        app.dispatch(KeyEvent(Key.TAB));
        self.assertIs(app.focus.current, cancel);
        self.assertTrue(cancel.focused);
        app.dispatch(KeyEvent(Key.TAB, shift=True));
        self.assertIs(app.focus.current, ok);
        self.assertTrue(ok.focused);

    def test_render_controls(self):
        console = Console(width=80, height=24, record=True, force_terminal=False, file=io.StringIO());
        root = VBox(
            TextInput("archive.rar"),
            CheckBox("Solid", checked=True),
            Choice(["RAR5", "RAR4"]),
            RadioGroup(["One", "Two"]),
            ProgressBar(40),
            Slider(0, 100, 40, step=5),
            HBox(Button("OK"), Button("Cancel")),
        );
        app = Application(root=root, theme="RAR", console=console);
        console.print(app.root);
        output = console.export_text();
        self.assertIn("archive.rar", output);
        self.assertIn("Solid", output);
        self.assertIn("RAR5", output);


class EditorToolTests(unittest.TestCase):
    def test_sumedit_uses_f9_menu_and_f10_exit(self):
        editor = EditApp();
        self.assertIn("f9", editor.app.bindings);
        self.assertIn("f10", editor.app.bindings);
        self.assertEqual([menu.title for menu in editor.menu.menus], ["File", "Edit", "Search", "View", "Options", "Help"]);
        self.assertTrue(editor.app.capture_control_keys);
        self.assertTrue(editor.open_menu(0));
        self.assertTrue(editor.menu.active);
        self.assertIs(editor.app.focus.current, editor.menu);


    def test_sumedit_help_is_modal_and_options_are_nested(self):
        with tempfile.TemporaryDirectory() as tempdir:
            editor = EditApp(config_path=Path(tempdir) / "edit.json");
            options = editor.menu.menus[4];
            self.assertEqual(options.items[0].label, "Tab");
            self.assertIsNotNone(options.items[0].submenu);
            self.assertEqual([item.label for item in options.items[0].submenu.items], ["2", "4", "8"]);
            self.assertEqual(options.items[1].label, "Theme");
            self.assertIsNotNone(options.items[1].submenu);
            self.assertIn("Dark", [item.label for item in options.items[1].submenu.items]);
            self.assertIn("Light", [item.label for item in options.items[1].submenu.items]);
            self.assertTrue(editor.help());
            self.assertEqual(editor.app.modal_depth, 1);
            self.assertIsInstance(editor.app.root, Dialog);

    def test_sumedit_about_from_help_menu_opens_and_renders_modal(self):
        editor = EditApp();
        self.assertTrue(editor.open_menu(5));
        self.assertTrue(editor.menu._move_item(1));
        self.assertEqual(editor.menu.current_menu.items[editor.menu.current_index].label, "About...");
        self.assertTrue(editor.menu.activate());
        self.assertFalse(editor.menu.active);
        self.assertEqual(editor.app.modal_depth, 1);
        self.assertIsInstance(editor.app.root, Dialog);
        console = Console(width=100, height=30, record=True, force_terminal=False, file=io.StringIO());
        console.print(editor.app._renderable(), height=30);
        output = console.export_text();
        self.assertIn("About sumTUI edit", output);
        self.assertIn("GNU GPL v2 or later", output);

    def test_sumedit_search_find_previous_replace_and_replace_all(self):
        editor = EditApp();
        editor.editor.set_text("Alpha beta alpha\nbeta", modified=False);
        editor._set_search_options("alpha", False, False, False, True);
        self.assertTrue(editor.find_next());
        self.assertEqual(editor.editor.selected_text, "Alpha");
        self.assertTrue(editor.find_next());
        self.assertEqual(editor.editor.selected_text, "alpha");
        self.assertTrue(editor.find_previous());
        self.assertEqual(editor.editor.selected_text, "Alpha");
        editor._set_search_options("beta", False, False, False, True);
        editor.replace_text = "BETA";
        self.assertTrue(editor.find_next());
        self.assertTrue(editor.replace_current());
        self.assertIn("Alpha BETA alpha", editor.editor.text);
        editor.replace_text = "X";
        self.assertTrue(editor.replace_all());
        self.assertEqual(editor.editor.text.count("X"), 2);
        self.assertTrue(editor.editor.undo());
        self.assertIn("BETA", editor.editor.text);

    def test_sumedit_search_and_replace_dialogs_are_modal(self):
        editor = EditApp();
        self.assertTrue(editor.find_dialog());
        self.assertEqual(editor.app.modal_depth, 1);
        editor._close_modal_to_editor();
        self.assertTrue(editor.replace_dialog());
        self.assertEqual(editor.app.modal_depth, 1);
        editor._close_modal_to_editor();
        self.assertTrue(editor.goto_line_dialog());
        self.assertEqual(editor.app.modal_depth, 1);

    @unittest.skipIf(os.name == "nt", "termios is POSIX-only")
    def test_posix_capture_control_keys_disables_signals_and_flow_control_then_restores(self):
        import termios;
        master, slave = os.openpty();
        original = termios.tcgetattr(slave);
        class _FakeStdin:
            def fileno(self):
                return slave;
        saved_stdin = sys.stdin;
        try:
            sys.stdin = _FakeStdin();
            backend = PosixInput(capture_control_keys=True);
            with backend:
                current = termios.tcgetattr(slave);
                self.assertFalse(current[3] & termios.ISIG);
                self.assertFalse(current[0] & termios.IXON);
            restored = termios.tcgetattr(slave);
            self.assertEqual(restored, original);
        finally:
            sys.stdin = saved_stdin;
            os.close(master);
            os.close(slave);

    def test_sumedit_config_round_trip_and_hidden_markers(self):
        with tempfile.TemporaryDirectory() as tempdir:
            config = Path(tempdir) / "edit.json";
            editor = EditApp(config_path=config);
            editor.set_tab_width(8);
            editor.set_theme("Light");
            editor.toggle_spaces();
            editor.toggle_tabs();
            editor.toggle_eols();
            editor.toggle_controls();
            self.assertTrue(editor.save_config());
            loaded = EditApp(config_path=config);
            self.assertEqual(loaded.editor.tab_size, 8);
            self.assertEqual(loaded.app.theme.name, "Light");
            self.assertTrue(loaded.editor.show_spaces);
            self.assertTrue(loaded.editor.show_tabs);
            self.assertTrue(loaded.editor.show_line_endings);
            self.assertTrue(loaded.editor.show_control_chars);
            self.assertEqual(loaded.editor._display_char("\t"), "⇥");
            self.assertEqual(loaded.editor._display_char("\x00"), "␀");
            self.assertEqual(loaded.editor.line_end_marker, "↵");

    def test_sumedit_markdown_highlighting_is_auto_detected_and_configurable(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "README.md";
            path.write_text("# Title\n\n**bold**\n", encoding="utf-8");
            editor = EditApp(path, config_path=Path(tempdir) / "edit.json");
            self.assertTrue(editor.editor.syntax_highlighting);
            self.assertEqual(editor.editor.syntax_language, "markdown");
            self.assertEqual(editor.editor.syntax_name, "Markdown");
            self.assertTrue(editor.set_syntax_mode("python"));
            self.assertEqual(editor.editor.syntax_language, "python");
            self.assertTrue(editor.toggle_syntax());
            self.assertFalse(editor.editor.syntax_highlighting);

    def test_sumedit_saves_syntax_preferences(self):
        with tempfile.TemporaryDirectory() as tempdir:
            config = Path(tempdir) / "edit.json";
            editor = EditApp(config_path=config);
            editor.set_syntax_mode("markdown");
            editor.editor.syntax_highlighting = False;
            self.assertTrue(editor.save_config());
            loaded = EditApp(config_path=config);
            self.assertFalse(loaded.editor.syntax_highlighting);
            self.assertEqual(loaded.editor.syntax.mode, "markdown");


class SyntaxHighlightingTests(unittest.TestCase):
    def test_markdown_roles_include_heading_strong_embedded_python_and_inline_html(self):
        source = "# Heading\n\n**strong**\n\n```python\nif value == 5:\n    print(\"ok\")\n```\n\n<p align=center><b>- oOo -</b></p>\n";
        highlighter = EditorSyntaxHighlighter(mode="markdown", filename="README.md");
        roles = highlighter.highlight(source);
        self.assertEqual(highlighter.resolved_mode, "markdown");
        self.assertIn("syntax_heading", roles[0]);
        self.assertIn("syntax_strong", roles[2]);
        self.assertIn("syntax_keyword", roles[5]);
        self.assertIn("syntax_builtin", roles[6]);
        self.assertIn("syntax_markup", roles[9]);

    def test_markdown_detection_handles_readme_without_extension(self):
        self.assertEqual(detect_mode("README", "# Test\n"), "markdown");
        self.assertEqual(detect_mode("notes.markdown", "# Test\n"), "markdown");

    def test_extended_basic_adds_spectrum_and_qbasic_vocabulary_case_insensitively(self):
        highlighter = EditorSyntaxHighlighter(mode="basic", filename="demo.bas");
        roles = highlighter.highlight("10 rectangle 1,2,3,4\n20 PRINT left$(name$, 2)\n30 SUB Demo\n");
        self.assertIn("syntax_keyword", roles[0]);
        self.assertIn("syntax_builtin", roles[1]);
        self.assertIn("syntax_keyword", roles[2]);

    def test_texteditor_semantic_highlighting_does_not_change_buffer(self):
        editor = TextEditor("# Heading\ntext", syntax_highlighting=True, syntax_language="markdown", syntax_filename="a.md");
        before = editor.text;
        console = Console(width=50, height=6, record=True, force_terminal=False, file=io.StringIO());
        console.print(editor, height=6);
        self.assertEqual(editor.text, before);
        self.assertEqual(editor.syntax_name, "Markdown");



class KeyBindingTests(unittest.TestCase):
    def test_keybinding_manager_defaults_overrides_conflicts_and_display(self):
        manager = KeyBindingManager();
        manager.register("editor.copy", "Copy", ["Ctrl+C", "Ctrl+Insert"], context="editor");
        manager.register("editor.cut", "Cut", ["Ctrl+X"], context="editor");
        self.assertEqual(manager.bindings_for("editor.copy"), ("ctrl+c", "ctrl+insert"));
        self.assertEqual(manager.display("editor.copy", all_keys=True), "Ctrl+C, Ctrl+Insert");
        self.assertEqual(format_key_spec("shift-ctrl-left"), "Ctrl+Shift+Left");
        manager.set_bindings("editor.copy", ["Alt+C"]);
        self.assertEqual(manager.primary("editor.copy"), "alt+c");
        self.assertEqual(manager.overrides(), {"editor.copy": ["alt+c"]});
        manager.add_binding("editor.cut", "Alt+C");
        conflicts = manager.conflicts("Alt+C", action_name="editor.copy");
        self.assertEqual([item.name for item in conflicts], ["editor.cut"]);
        manager.reset_all();
        self.assertEqual(manager.primary("editor.copy"), "ctrl+c");

    def test_sumedit_custom_shortcut_is_loaded_saved_and_used(self):
        with tempfile.TemporaryDirectory() as tempdir:
            config = Path(tempdir) / "edit.json";
            editor = EditApp(config_path=config);
            editor.keys.set_bindings("editor.copy", ["alt+c"]);
            editor._refresh_key_surfaces();
            editor.editor.set_text("copy me", modified=False);
            editor.editor.select_offsets(0, 7);
            self.assertFalse(editor.app.dispatch(KeyEvent("c", text="c", ctrl=True)));
            self.assertTrue(editor.app.dispatch(KeyEvent("c", text="c", alt=True)));
            self.assertEqual(editor.editor.clipboard.paste_text(), "copy me");
            edit_menu = editor.menu.menus[1];
            copy_item = next(item for item in edit_menu.items if item.label == "Copy");
            self.assertEqual(copy_item.shortcut, "Alt+C");
            self.assertTrue(editor.save_config());
            loaded = EditApp(config_path=config);
            self.assertEqual(loaded.keys.bindings_for("editor.copy"), ("alt+c",));
            self.assertEqual(loaded.config.get("keybindings", {}).get("editor.copy"), ["alt+c"]);

    def test_sumedit_shortcut_dialog_is_modal(self):
        editor = EditApp();
        self.assertTrue(editor.shortcuts_dialog());
        self.assertEqual(editor.app.modal_depth, 1);
        self.assertIsInstance(editor.app.root, Dialog);
        self.assertIn("Keyboard shortcuts", editor.app.root.title);

    def test_menubar_custom_activation_and_disabled_mnemonics(self):
        called = [];
        bar = MenuBar([Menu("File", [MenuItem("Open", lambda: called.append("open"))])], activation_key="f8", mnemonics=False);
        self.assertFalse(bar.handle_event(KeyEvent("f", text="f", alt=True)));
        self.assertFalse(bar.active);
        self.assertTrue(bar.handle_event(KeyEvent(Key.F8)));
        self.assertTrue(bar.active);
        self.assertFalse(bar.handle_event(KeyEvent(Key.F9)));
        self.assertTrue(bar.active);
        self.assertTrue(bar.handle_event(KeyEvent(Key.F8)));
        self.assertFalse(bar.active);


class CommanderWidgetTests(unittest.TestCase):
    def test_menu_space_toggles_checked_item_without_closing(self):
        state = {"value": False};
        def toggle():
            state["value"] = not state["value"];
        bar = MenuBar([Menu("View", [MenuItem("Show tabs", toggle, checked=lambda: state["value"])])]);
        self.assertTrue(bar.open());
        self.assertTrue(bar.handle_event(KeyEvent(Key.SPACE, text=" ")));
        self.assertTrue(state["value"]);
        self.assertTrue(bar.active);
        self.assertTrue(bar.handle_event(KeyEvent(Key.SPACE, text=" ")));
        self.assertFalse(state["value"]);
        self.assertTrue(bar.active);

    def test_menu_navigation_and_submenu(self):
        called = [];
        submenu = Menu("View", [MenuItem("Text", lambda: called.append("text")), MenuItem("Hex", lambda: called.append("hex"))]);
        bar = MenuBar([Menu("File", [MenuItem("View", submenu=submenu), Separator(), MenuItem("Quit", lambda: called.append("quit"))])]);
        self.assertTrue(bar.open());
        self.assertTrue(bar.handle_event(KeyEvent(Key.RIGHT)));
        self.assertEqual(len(bar.path), 2);
        self.assertTrue(bar.handle_event(KeyEvent(Key.DOWN)));
        self.assertTrue(bar.handle_event(KeyEvent(Key.ENTER)));
        self.assertEqual(called, ["hex"]);
        self.assertFalse(bar.active);

    def test_hexview_navigation(self):
        view = HexView(data=bytes(range(128)), bytes_per_row=16);
        self.assertTrue(view.handle_event(KeyEvent(Key.DOWN)));
        self.assertEqual(view.offset, 16);
        self.assertTrue(view.handle_event(KeyEvent(Key.END)));
        self.assertGreaterEqual(view.offset, 16);
        self.assertTrue(view.handle_event(KeyEvent(Key.HOME)));
        self.assertEqual(view.offset, 0);

    def test_hexview_horizontal_scroll(self):
        console = Console(width=30, height=6, record=True, force_terminal=False, file=io.StringIO());
        view = HexView(data=bytes(range(64)), bytes_per_row=16);
        console.print(view);
        self.assertGreater(view.max_x_offset, 0);
        self.assertTrue(view.handle_event(KeyEvent(Key.RIGHT, shift=True)));
        self.assertGreater(view.x_offset, 1);

    def test_scrollbar_and_splitter(self):
        scroll = ScrollBar(10, maximum=100, page=20, orientation="vertical", interactive=True);
        self.assertTrue(scroll.handle_event(KeyEvent(Key.DOWN)));
        self.assertEqual(scroll.value, 11);
        splitter = Splitter(TextView("left"), TextView("right"), ratio=0.5);
        splitter.handle_event(KeyEvent(Key.RIGHT));
        self.assertGreater(splitter.ratio, 0.5);

    def test_treeview(self):
        root = TreeNode("root", expanded=True);
        root.add(TreeNode("child"));
        tree = TreeView([root]);
        self.assertTrue(tree.handle_event(KeyEvent(Key.DOWN)));
        self.assertEqual(tree.current.label, "child");
        self.assertTrue(tree.handle_event(KeyEvent(Key.LEFT)));
        self.assertEqual(tree.current.label, "root");

    def test_listview(self):
        view = ListView([("One", 1), ("Two", 2)]);
        self.assertEqual(view.current_value, 1);
        view.move(1);
        self.assertEqual(view.current_value, 2);

    def test_groupbox_render(self):
        console = Console(width=40, height=8, record=True, force_terminal=False, file=io.StringIO());
        console.print(GroupBox(TextView("inside"), title="Options"));
        output = console.export_text();
        self.assertIn("Options", output);
        self.assertIn("inside", output);

    def test_markdown_render(self):
        console = Console(width=50, height=10, record=True, force_terminal=False, file=io.StringIO());
        console.print(MarkdownView("# Header\n\n**bold**"));
        output = console.export_text();
        self.assertIn("Header", output);

    def test_filedialog_activation_callback_signature(self):
        accepted = [];
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt";
            path.write_text("hello");
            dialog = FileDialog(path=directory, on_accept=lambda value: accepted.append(Path(value)));
            index = next(index for index, row in enumerate(dialog.table.rows) if row.value == path);
            dialog.table.select(index);
            self.assertTrue(dialog.table.activate());
            self.assertEqual(accepted, [path]);


    def test_menu_desktop_dropdown_overlays_client(self):
        console = Console(width=60, height=12, record=True, force_terminal=False, file=io.StringIO());
        bar = MenuBar([Menu("File", [MenuItem("Open"), MenuItem("Save"), MenuItem("Exit")]), Menu("Edit", [MenuItem("Undo")])]);
        bar.open(0);
        desktop = MenuDesktop(bar, TextView("line 1\nline 2\nline 3\nline 4\nline 5\nCLIENT CONTENT"));
        console.print(desktop);
        output = console.export_text();
        self.assertIn("File", output);
        self.assertIn("Open", output);
        self.assertIn("Save", output);
        self.assertIn("CLIENT CONTENT", output);
        self.assertTrue(output.splitlines()[0].lstrip().startswith("File"));

    def test_menu_shortcut_fits_same_line(self):
        console = Console(width=60, height=12, record=True, force_terminal=False, file=io.StringIO());
        bar = MenuBar([Menu("File", [MenuItem("View", shortcut="F3"), MenuItem("Quit", shortcut="F10")])]);
        bar.open();
        console.print(bar);
        output = console.export_text();
        self.assertIn("Quit", output);
        self.assertIn("F10", output);
        self.assertTrue(any("Quit" in line and "F10" in line for line in output.splitlines()));

    def test_syntaxview_detects_filename(self):
        view = SyntaxView("def hello():\n    return 1\n", filename="hello.py", syntax_theme="vim");
        self.assertEqual(view.lexer, "python");
        console = Console(width=60, height=8, record=True, force_terminal=False, file=io.StringIO());
        console.print(view);
        self.assertIn("def hello", console.export_text());

    def test_syntaxview_horizontal_scroll(self):
        code = "value = '" + ("x" * 120) + "'\n";
        view = SyntaxView(code, filename="long.py", syntax_theme="vim", line_numbers=True);
        console = Console(width=32, height=5, record=True, force_terminal=False, file=io.StringIO());
        console.print(view);
        self.assertGreater(view.max_x_offset, 0);
        self.assertTrue(view.handle_event(KeyEvent(Key.RIGHT)));
        self.assertEqual(view.x_offset, 1);

    def test_progress_size_parser(self):
        self.assertEqual(parse_size("1K"), 1024);
        self.assertEqual(parse_size("1.5M"), int(1.5 * 1024 * 1024));

    def test_modal_overlay_keeps_base(self):
        console = Console(width=60, height=16, record=True, force_terminal=False, file=io.StringIO());
        app = Application(root=TextView("BASE CONTENT"), theme="RAR", console=console);
        app.push_modal(Dialog(TextView("MODAL CONTENT"), title="Dialog", width=30, height=7));
        console.print(app._renderable());
        output = console.export_text();
        self.assertIn("BASE CONTENT", output);
        self.assertIn("MODAL CONTENT", output);

    def test_dialog_content_style_uses_viewer_background(self):
        dialog = Dialog(TextView("content"), title="Viewer", width=30, height=7, content_style="viewer");
        panel = dialog.as_panel(width=30, height=7);
        self.assertEqual(str(panel.style), dialog.theme.style("viewer"));

    def test_dialog_f11_maximize_restore(self):
        console = Console(width=60, height=16, record=True, force_terminal=False, file=io.StringIO());
        app = Application(root=TextView("BASE"), theme="RAR", console=console);
        field = TextInput("focused");
        dialog = Dialog(field, title="Viewer", width=30, height=7, maximizable=True);
        app.push_modal(dialog);
        self.assertFalse(dialog.maximized);
        self.assertTrue(app.dispatch(KeyEvent(Key.F11)));
        self.assertTrue(dialog.maximized);
        console.print(app._renderable());
        self.assertTrue(app.dispatch(KeyEvent(Key.F11)));
        self.assertFalse(dialog.maximized);


if __name__ == "__main__":
    unittest.main();


class DataFormTests(unittest.TestCase):
    def test_textinput_mask_is_visible_when_empty_and_focused(self):
        console = Console(width=20, height=3, record=True, force_terminal=False, file=io.StringIO());
        field = TextInput("", width=10, mask="XXXXXX");
        field.focused = True;
        console.print(field);
        output = console.export_text();
        self.assertIn("XXXXXX", output);

    def test_record_form_collects_values_and_keeps_readonly_out(self):
        form = RecordForm([
            FormField("id", value="<auto>", width=8, readonly=True),
            FormField("name", value="Ana", width=12, max_length=12, mask="XXXXXXXXXXXX"),
            FormField("active", value=True, kind="logical", width=1),
        ]);
        self.assertEqual(form.control("name").value, "Ana");
        values = form.values();
        self.assertNotIn("id", values);
        self.assertEqual(values["name"], "Ana");
        self.assertTrue(values["active"]);

    def test_record_form_fields_are_editable_and_enter_advances(self):
        form = RecordForm([
            FormField("id", value="<auto>", readonly=True),
            FormField("name", value="Ana", width=12),
            FormField("city", value="Montevideo", width=16),
        ]);
        app = Application(root=form);
        self.assertIs(app.focus.current, form.control("name"));
        name = form.control("name");
        name.cursor = len(name.value);
        self.assertTrue(app.dispatch(KeyEvent("x", text="X")));
        self.assertEqual(name.value, "AnaX");
        self.assertTrue(app.dispatch(KeyEvent(Key.ENTER)));
        self.assertIs(app.focus.current, form.control("city"));

    def test_record_form_ctrl_end_is_left_for_dialog_binding(self):
        form = RecordForm([FormField("name", value="Ana")]);
        app = Application(root=form);
        called = [];
        app.bind("ctrl+end", lambda: called.append(True));
        self.assertTrue(app.dispatch(KeyEvent(Key.END, ctrl=True)));
        self.assertEqual(called, [True]);

    def test_browse_form_uses_column_headers_and_tracks_record(self):
        form = BrowseForm(["id", "name"], [[1, "Ana"], [2, "Luis"]]);
        self.assertEqual([column.title for column in form.table.columns], ["id", "name"]);
        self.assertEqual(form.status.text, "Rec 1/2");
        form.select(1);
        self.assertEqual(form.status.text, "Rec 2/2");

    def test_browse_form_navigation_and_search(self):
        form = BrowseForm(["id", "name"], [[1, "Ana"], [2, "Luis"], [3, "Bea"]]);
        form.last();
        self.assertEqual(form.selected, 2);
        form.first();
        self.assertEqual(form.selected, 0);
        form.next();
        self.assertEqual(form.selected, 1);
        form.previous();
        self.assertEqual(form.selected, 0);
        self.assertTrue(form.find("Bea"));
        self.assertEqual(form.selected, 2);

    def test_record_form_set_values(self):
        form = RecordForm([
            FormField("id", value="<auto>", readonly=True),
            FormField("name", value="Ana"),
            FormField("active", value=False, kind="logical"),
        ]);
        form.set_values({"id": 7, "name": "Bea", "active": True});
        self.assertEqual(form.control("id").value, "7");
        self.assertEqual(form.control("name").value, "Bea");
        self.assertTrue(form.control("active").checked);

class AdvancedTextEditorTests(unittest.TestCase):
    class _Clipboard:
        def __init__(self):
            self.value = "";
        def copy_text(self, text):
            self.value = str(text);
        def paste_text(self):
            return self.value;

    def test_shift_selection_copy_cut_paste_undo_redo(self):
        clip = self._Clipboard();
        editor = TextEditor("hello world", clipboard=clip);
        editor.handle_event(KeyEvent(Key.RIGHT, ctrl=True, shift=True));
        self.assertEqual(editor.selected_text, "hello");
        self.assertTrue(editor.handle_event(KeyEvent("c", ctrl=True)));
        self.assertEqual(clip.value, "hello");
        self.assertTrue(editor.handle_event(KeyEvent("x", ctrl=True)));
        self.assertEqual(editor.text, " world");
        self.assertTrue(editor.handle_event(KeyEvent("z", ctrl=True)));
        self.assertEqual(editor.text, "hello world");
        self.assertTrue(editor.handle_event(KeyEvent("y", ctrl=True)));
        self.assertEqual(editor.text, " world");
        editor.handle_event(KeyEvent(Key.END, ctrl=True));
        self.assertTrue(editor.handle_event(KeyEvent("v", ctrl=True)));
        self.assertEqual(editor.text, " worldhello");

    def test_ctrl_word_navigation(self):
        editor = TextEditor("one two three");
        self.assertTrue(editor.handle_event(KeyEvent(Key.RIGHT, ctrl=True)));
        self.assertEqual(editor.column, 3);
        self.assertTrue(editor.handle_event(KeyEvent(Key.RIGHT, ctrl=True)));
        self.assertEqual(editor.column, 7);
        self.assertTrue(editor.handle_event(KeyEvent(Key.LEFT, ctrl=True)));
        self.assertEqual(editor.column, 4);
        self.assertTrue(editor.handle_event(KeyEvent(Key.LEFT, ctrl=True, shift=True)));
        self.assertEqual(editor.selected_text, "one ");

    def test_ctrl_home_end_and_shift_vertical_page_selection(self):
        editor = TextEditor("zero\none\ntwo\nthree\nfour\nfive");
        editor.page_height = 3;
        editor.handle_event(KeyEvent(Key.END, ctrl=True));
        self.assertEqual((editor.row, editor.column), (5, 4));
        editor.handle_event(KeyEvent(Key.HOME, ctrl=True));
        self.assertEqual((editor.row, editor.column), (0, 0));
        self.assertTrue(editor.handle_event(KeyEvent(Key.DOWN, shift=True)));
        self.assertEqual(editor.selected_text, "zero\n");
        self.assertTrue(editor.handle_event(KeyEvent(Key.PAGE_DOWN, shift=True)));
        self.assertEqual(editor.row, 3);
        self.assertTrue(editor.selected_text.startswith("zero\none\ntwo\n"));
        self.assertTrue(editor.handle_event(KeyEvent(Key.PAGE_UP, shift=True)));
        self.assertEqual(editor.row, 1);
        self.assertTrue(editor.has_selection);

    def test_document_detects_and_preserves_mixed_eol(self):
        from sumtui.document import TextDocument, detect_eol_bytes;
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "mixed.txt";
            path.write_bytes(b"one\r\ntwo\nthree\rfour");
            doc = TextDocument.load(path);
            self.assertEqual(doc.eol, "MIXED");
            self.assertEqual(doc.text, "one\ntwo\nthree\nfour");
            doc.save(text=doc.text);
            kind, counts = detect_eol_bytes(path.read_bytes());
            self.assertEqual(kind, "MIXED");
            self.assertEqual((counts["CRLF"], counts["LF"], counts["CR"]), (1, 1, 1));

class SumInputTests(unittest.TestCase):
    def test_input_mask_formats_and_maps_cursor(self):
        from sumtui import InputMask;
        mask = InputMask.parse("@! (999) NNN-XXX");
        self.assertEqual(mask.input_char(0, "5"), "5");
        self.assertIsNone(mask.input_char(3, "-"));
        self.assertEqual(mask.input_char(3, "a"), "A");
        self.assertTrue(mask.format("555abcxyz").startswith("(555) ABC-XYZ"));
        self.assertEqual(mask.cursor_display_position("", 0), 1);

    def test_textinput_custom_echo_mask_and_hidden(self):
        field = TextInput("abc", echo_mask="***");
        display, cursor = field._display();
        self.assertEqual(display, "*********");
        self.assertEqual(cursor, 9);
        field = TextInput("secret", hidden=True);
        self.assertEqual(field._display(), ("", 0));

    def test_textarea_tab_can_move_focus(self):
        from sumtui import TextArea;
        area = TextArea("abc", tab_moves_focus=True);
        self.assertFalse(area.handle_event(KeyEvent(Key.TAB)));
        self.assertEqual(area.text, "abc");

    def test_suminput_colon_compatibility_and_timeout_parser(self):
        from sumtui.tools.input import _expand_colon_options, _parse_timeout;
        self.assertEqual(_expand_colon_options(["-c:YN", "-v:answer", "Prompt"]), ["--keys", "YN", "--variable", "answer", "Prompt"]);
        seconds, default = _parse_timeout("N,10");
        self.assertEqual(seconds, 10.0);
        self.assertEqual(default, "N");


class WindowPrimitiveTests(unittest.TestCase):
    def test_dialog_accepts_position_shadow_and_color_scheme(self):
        dialog = Dialog(TextInput("x"), title="Window", width=30, height=8, top=3, left=7, shadow=True, panel=True, color_scheme=5);
        self.assertEqual((dialog.top, dialog.left), (3, 7));
        self.assertTrue(dialog.shadow);
        self.assertTrue(dialog.panel);
        self.assertEqual(dialog.color_scheme, 5);

    def test_command_window_can_render_without_command_prompt(self):
        console = Console(width=20, height=4, record=True, force_terminal=False, file=io.StringIO());
        command = CommandWindow(prompt="", show_prompt=False);
        command.write_at(1, 1, "HELLO");
        console.print(command, height=4);
        text = console.export_text();
        self.assertIn("HELLO", text);
        self.assertNotIn("READ 0/", text);

class EditorWrappingTests(unittest.TestCase):
    def test_texteditor_soft_wrap_builds_visual_rows_without_changing_text(self):
        source = "0123456789ABCDEFGHIJ";
        editor = TextEditor(source, line_numbers=False, line_wrapping=-1);
        editor.page_width = 10;
        editor.page_height = 5;
        self.assertEqual(editor.visual_line_count(10), 2);
        self.assertEqual(editor.text, source);
        self.assertFalse(editor.modified);
        console = Console(width=10, height=4, record=True, force_terminal=False, file=io.StringIO());
        console.print(editor, height=4);
        self.assertEqual(editor.text, source);

    def test_sumedit_wrapping_defaults_auto_and_has_legacy_78_preset(self):
        editor = EditApp();
        self.assertEqual(editor.app.theme.name, "Ralesk's MC");
        self.assertEqual(editor.editor.line_wrapping, -1);
        self.assertEqual(editor.editor.line_breaking, 0);
        options = editor.menu.menus[4];
        wrapping = next(item.submenu for item in options.items if getattr(item, "label", "") == "Line wrapping");
        labels = [item.label for item in wrapping.items if hasattr(item, "label")];
        self.assertIn("Auto (-1)", labels);
        self.assertIn("Off (0)", labels);
        self.assertIn("78 (legacy 80-col)", labels);

    def test_sumedit_wrapping_and_breaking_persist(self):
        with tempfile.TemporaryDirectory() as tempdir:
            config = Path(tempdir) / "edit.json";
            editor = EditApp(config_path=config);
            editor.set_line_wrapping(78);
            editor.set_line_breaking(80);
            self.assertTrue(editor.save_config());
            loaded = EditApp(config_path=config);
            self.assertEqual(loaded.editor.line_wrapping, 78);
            self.assertEqual(loaded.editor.line_breaking, 80);

    def test_hard_line_breaking_is_opt_in_and_undo_is_single_step(self):
        editor = TextEditor("123456789", line_numbers=False, line_breaking=10);
        editor.row = 0;
        editor.column = 9;
        editor.preferred_column = 9;
        self.assertTrue(editor.handle_event(KeyEvent("A", text="A")));
        self.assertEqual(editor.text, "123456789A");
        self.assertTrue(editor.handle_event(KeyEvent("B", text="B")));
        self.assertEqual(editor.text, "123456789A\nB");
        self.assertTrue(editor.undo());
        self.assertEqual(editor.text, "123456789");

class ThemeEditorTests(unittest.TestCase):
    def test_user_theme_roundtrip_and_registration(self):
        from sumtui import THEMES, load_theme_file, make_theme, save_user_theme;
        with tempfile.TemporaryDirectory() as tempdir:
            custom = make_theme("Ralesk's MC").copy(name="Teaching MC", style_overrides=(("syntax_keyword", "bold #abcdef"),));
            path = save_user_theme(custom, path=tempdir);
            loaded = load_theme_file(path);
            self.assertEqual(loaded.name, "Teaching MC");
            self.assertEqual(loaded.style("syntax_keyword"), "bold #abcdef");
            THEMES.pop("Teaching MC", None);

    def test_theme_preview_tool_lists_roles(self):
        from sumtui.tools.themeedit import ThemeEditorApp;
        app = ThemeEditorApp(theme="Ralesk's MC");
        self.assertEqual(app.current_name, "Ralesk's MC");
        self.assertIn("syntax_keyword", [row.value for row in app.role_list.rows]);
        self.assertIn("editor_gutter", [row.value for row in app.role_list.rows]);


class SumDialogTests(unittest.TestCase):
    def test_dialog_result_properties(self):
        from sumtui.dialogs import DialogResult;
        accepted = DialogResult("yes", 0);
        self.assertTrue(accepted.accepted);
        self.assertFalse(accepted.cancelled);
        cancelled = DialogResult("", 1);
        self.assertTrue(cancelled.cancelled);

    def test_sumdialog_entry_uses_shared_input_engine(self):
        from contextlib import redirect_stdout;
        from unittest.mock import patch;
        from sumtui.dialogs import DialogResult;
        from sumtui.tools import dialog as dialog_tool;
        output = io.StringIO();
        with patch.object(dialog_tool, "read_entry", return_value=DialogResult("Ada", 0)) as mocked:
            with redirect_stdout(output):
                status = dialog_tool.main(["--entry", "--text", "Name:", "--theme", "DOS", "--width", "20"]);
        self.assertEqual(status, 0);
        self.assertEqual(output.getvalue(), "Ada\n");
        kwargs = mocked.call_args.kwargs;
        self.assertEqual(kwargs["text"], "Name:");
        self.assertEqual(kwargs["theme"], "DOS");
        self.assertEqual(kwargs["width"], 20);

    def test_sumdialog_question_exit_status(self):
        from unittest.mock import patch;
        from sumtui.dialogs import DialogResult;
        from sumtui.tools import dialog as dialog_tool;
        with patch.object(dialog_tool, "ask_question", return_value=DialogResult("", 1)):
            status = dialog_tool.main(["--question", "--text", "Continue?"]);
        self.assertEqual(status, 1);

    def test_sumdialog_checklist_writes_separator_output(self):
        from contextlib import redirect_stdout;
        from unittest.mock import patch;
        from sumtui.dialogs import DialogResult;
        from sumtui.tools import dialog as dialog_tool;
        output = io.StringIO();
        with patch.object(dialog_tool, "choose_checklist", return_value=DialogResult("Python|SQL", 0)) as mocked:
            with redirect_stdout(output):
                status = dialog_tool.main(["--checklist", "--separator", "|", "Python", "SQL", "Bash"]);
        self.assertEqual(status, 0);
        self.assertEqual(output.getvalue(), "Python|SQL\n");
        self.assertEqual(mocked.call_args.kwargs["separator"], "|");

    def test_sumdialog_progress_delegates_to_sumprogress_engine(self):
        from unittest.mock import patch;
        from sumtui.tools import dialog as dialog_tool;
        with patch.object(dialog_tool, "progress_main", return_value=0) as mocked:
            status = dialog_tool.main(["--progress", "--label", "Job"]);
        self.assertEqual(status, 0);
        self.assertIn("--percent-input", mocked.call_args.args[0]);
        self.assertIn("Job", mocked.call_args.args[0]);

    def test_sumdialog_bash_examples_are_syntax_valid(self):
        root = Path(__file__).resolve().parents[1];
        scripts = sorted((root / "examples" / "bash" / "sumdialog").glob("*.sh"));
        scripts.append(root / "examples" / "bash" / "sumdialog_examples.sh");
        self.assertGreaterEqual(len(scripts), 21);
        for script in scripts:
            completed = subprocess.run(["bash", "-n", str(script)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False);
            self.assertEqual(completed.returncode, 0, msg="{}: {}".format(script.name, completed.stderr));
