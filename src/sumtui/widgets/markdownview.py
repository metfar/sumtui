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
import re;

from rich import box;
from rich.console import Group;
from rich.markdown import Markdown;
from rich.panel import Panel as RichPanel;
from rich.segment import Segment;
from rich.style import Style;
from rich.table import Table;
from rich.text import Text;

from ..clipboard import clipboard as default_clipboard, trim_selected_text;
from ..events import Key, MouseEvent;
from ._viewport import horizontal_delta, line_cell_length, slice_segments, text_cell_length;
from .base import Widget;


def _split_table_row(source):
    text = str(source or "").strip();
    if text.startswith("|"):
        text = text[1:];
    if text.endswith("|") and not text.endswith(r"\|"):
        text = text[:-1];
    cells = [];
    current = [];
    escaped = False;
    code = False;
    for char in text:
        if escaped:
            current.append(char);
            escaped = False;
            continue;
        if char == "\\":
            escaped = True;
            continue;
        if char == "`":
            code = not code;
            current.append(char);
            continue;
        if char == "|" and not code:
            cells.append("".join(current).strip());
            current = [];
            continue;
        current.append(char);
    if escaped:
        current.append("\\");
    cells.append("".join(current).strip());
    return cells;


def _table_alignments(separator_cells):
    alignments = [];
    for cell in separator_cells:
        source = str(cell).strip();
        if not re.match(r"^:?-{3,}:?$", source):
            return None;
        left = source.startswith(":");
        right = source.endswith(":");
        if left and right:
            alignments.append("center");
        elif right:
            alignments.append("right");
        else:
            alignments.append("left");
    return alignments;


def _markdown_chunks(source):
    """Yield ('markdown', text) and ('table', (headers, rows, alignments)).""";
    lines = str(source or "").splitlines();
    index = 0;
    pending = [];
    fence_char = "";
    fence_size = 0;
    while index < len(lines):
        raw = lines[index];
        fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", raw);
        if fence:
            marker = fence.group(1);
            char = marker[0];
            if not fence_char:
                fence_char = char;
                fence_size = len(marker);
            elif char == fence_char and len(marker) >= fence_size:
                fence_char = "";
                fence_size = 0;
            pending.append(raw);
            index += 1;
            continue;
        if not fence_char and index + 1 < len(lines) and "|" in raw:
            headers = _split_table_row(raw);
            separators = _split_table_row(lines[index + 1]);
            alignments = _table_alignments(separators) if len(headers) == len(separators) and len(headers) >= 2 else None;
            if alignments is not None:
                if pending:
                    yield ("markdown", "\n".join(pending));
                    pending = [];
                rows = [];
                index += 2;
                while index < len(lines):
                    candidate = lines[index];
                    if not candidate.strip() or "|" not in candidate:
                        break;
                    cells = _split_table_row(candidate);
                    if len(cells) < len(headers):
                        cells += [""] * (len(headers) - len(cells));
                    rows.append(cells[:len(headers)]);
                    index += 1;
                yield ("table", (headers, rows, alignments));
                continue;
        pending.append(raw);
        index += 1;
    if pending:
        yield ("markdown", "\n".join(pending));


def fenced_code_blocks(source):
    """Return fenced Markdown code blocks as plain source strings.

    The helper intentionally ignores language tags and returns only the exact
    code payload.  Help browsers can therefore expose a safe Copy Example
    action without making rendered Markdown editable.
    """;
    lines = str(source or "").splitlines();
    blocks = [];
    current = [];
    fence_char = "";
    fence_size = 0;
    for raw in lines:
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", raw);
        if match:
            marker = match.group(1);
            char = marker[0];
            if not fence_char:
                fence_char = char;
                fence_size = len(marker);
                current = [];
                continue;
            if char == fence_char and len(marker) >= fence_size:
                blocks.append("\n".join(current));
                current = [];
                fence_char = "";
                fence_size = 0;
                continue;
        if fence_char:
            current.append(raw);
    return blocks;


class MarkdownView(Widget):
    focusable = True;

    def __init__(self, markdown="", code_theme="vim", wrap=True, theme=None, clipboard=None):
        super().__init__(theme=theme);
        self.clipboard = clipboard or default_clipboard;
        self.markdown = str(markdown);
        self.code_theme = str(code_theme or "vim");
        self.wrap = bool(wrap);
        self.offset = 0;
        self.x_offset = 0;
        self.page_size = 1;
        self.page_width = 1;
        self.content_width = 1;
        self.content_height = 1;
        self.cursor = (0, 0);
        self.selection_anchor = None;
        self.selection_cursor = None;
        self.mouse_selecting = False;
        self._rendered_lines = [[]];
        self._render_width = None;
        self.context_menu_open = False;
        self.context_menu_index = 0;
        self.context_menu_x = 0;
        self.context_menu_y = 0;
        self._context_menu_bounds = None;

    @property
    def max_x_offset(self):
        return max(0, self.content_width - self.page_width);

    def set_text(self, markdown):
        self.markdown = str(markdown);
        self.offset = 0;
        self.x_offset = 0;
        self.cursor = (0, 0);
        self.clear_selection();
        self.mouse_selecting = False;
        self.close_context_menu();
        self._rendered_lines = [[]];
        self._render_width = None;
        return self;

    @property
    def code_blocks(self):
        return fenced_code_blocks(self.markdown);

    def copy_text(self):
        return self.clipboard.copy_text(self.markdown);

    def copy_code_block(self, index=-1):
        blocks = self.code_blocks;
        if not blocks:
            return "";
        try:
            text = blocks[int(index)];
        except (IndexError, TypeError, ValueError):
            return "";
        return self.clipboard.copy_text(text);

    def _renderable(self, chunk):
        return Markdown(
            str(chunk),
            code_theme=self.code_theme,
            inline_code_theme=self.code_theme,
        );

    def _table_renderable(self, headers, rows, alignments):
        table = Table(
            box=box.SQUARE,
            show_header=True,
            show_edge=True,
            expand=False,
            padding=(0, 1),
            header_style="bold",
        );
        for header, alignment in zip(headers, alignments):
            table.add_column(str(header), justify=alignment, overflow="fold", no_wrap=False);
        for row in rows:
            table.add_row(*[self._renderable(str(cell)) for cell in row]);
        return table;

    def _preferred_width(self, viewport_width):
        if self.wrap:
            return max(20, int(viewport_width));
        source_width = max([text_cell_length(line.expandtabs(4)) for line in self.markdown.splitlines()] or [20]);
        return max(20, int(viewport_width), source_width + 4);

    def _lines(self, console, width):
        output = [];
        for kind, payload in _markdown_chunks(self.markdown):
            if kind == "table":
                renderable = self._table_renderable(*payload);
            else:
                if not str(payload).strip():
                    continue;
                renderable = self._renderable(payload);
            segments = console.render(renderable, console.options.update(width=max(20, int(width))));
            lines = list(Segment.split_lines(segments));
            if output and lines:
                output.append([]);
            output.extend(lines);
        return output or [[]];

    def scroll(self, delta, line_count=None):
        old = self.offset;
        count = self.content_height if line_count is None else int(line_count);
        self.offset = max(0, min(max(0, count - self.page_size), self.offset + int(delta)));
        return self.offset != old;

    def scroll_horizontal(self, delta):
        old = self.x_offset;
        if delta == "start":
            self.x_offset = 0;
        elif delta == "end":
            self.x_offset = self.max_x_offset;
        else:
            self.x_offset = max(0, min(self.max_x_offset, self.x_offset + int(delta)));
        return self.x_offset != old;

    def _line_width(self, line):
        lines = self._rendered_lines or [[]];
        line = max(0, min(len(lines) - 1, int(line)));
        return line_cell_length(lines[line]);

    def _clamp_position(self, line, column):
        lines = self._rendered_lines or [[]];
        line = max(0, min(len(lines) - 1, int(line)));
        column = max(0, min(self._line_width(line), int(column)));
        return (line, column);

    def _event_position(self, event):
        return self._clamp_position(self.offset + int(event.y), self.x_offset + int(event.x));

    @property
    def has_selection(self):
        return self.selection_anchor is not None and self.selection_cursor is not None and self.selection_anchor != self.selection_cursor;

    def clear_selection(self):
        self.selection_anchor = None;
        self.selection_cursor = None;
        return True;

    def select_all(self):
        lines = self._rendered_lines or [[]];
        last_line = max(0, len(lines) - 1);
        self.selection_anchor = (0, 0);
        self.selection_cursor = (last_line, self._line_width(last_line));
        self.cursor = self.selection_cursor;
        return True;

    def _selection_bounds(self):
        if not self.has_selection:
            return None;
        start, end = sorted((self.selection_anchor, self.selection_cursor));
        return start, end;

    @staticmethod
    def _segments_text(segments):
        return "".join(segment.text for segment in segments if not segment.control);

    def _line_text(self, line_index, start=0, end=None):
        lines = self._rendered_lines or [[]];
        line_index = max(0, min(len(lines) - 1, int(line_index)));
        line = lines[line_index];
        width = line_cell_length(line);
        start = max(0, min(width, int(start)));
        end = width if end is None else max(start, min(width, int(end)));
        return self._segments_text(slice_segments(line, start, end - start));

    @property
    def selected_text(self):
        bounds = self._selection_bounds();
        if bounds is None:
            return "";
        (line1, col1), (line2, col2) = bounds;
        if line1 == line2:
            return self._line_text(line1, col1, col2);
        parts = [self._line_text(line1, col1, None)];
        parts.extend(self._line_text(index, 0, None) for index in range(line1 + 1, line2));
        parts.append(self._line_text(line2, 0, col2));
        return "\n".join(parts);

    def copy_selection(self):
        if not self.has_selection:
            return False;
        self.clipboard.copy_text(trim_selected_text(self.selected_text));
        return True;

    def _context_menu_items(self):
        return [
            ("Copy", "Ctrl+C / Ctrl+Ins", self.has_selection, self.copy_selection),
            ("Select all", "Ctrl+A", True, self.select_all),
        ];

    def _first_context_menu_index(self):
        for index, (_label, _shortcut, enabled, _action) in enumerate(self._context_menu_items()):
            if enabled:
                return index;
        return 0;

    def open_context_menu(self, x=0, y=0):
        self.context_menu_open = True;
        self.context_menu_x = max(0, int(x));
        self.context_menu_y = max(0, int(y));
        self.context_menu_index = self._first_context_menu_index();
        self._context_menu_bounds = None;
        return True;

    def close_context_menu(self):
        changed = self.context_menu_open;
        self.context_menu_open = False;
        self._context_menu_bounds = None;
        return changed;

    def _move_context_menu(self, delta):
        items = self._context_menu_items();
        choices = [index for index, (_label, _shortcut, enabled, _action) in enumerate(items) if enabled];
        if not choices:
            return False;
        try:
            position = choices.index(self.context_menu_index);
        except ValueError:
            position = 0;
        self.context_menu_index = choices[(position + int(delta)) % len(choices)];
        return True;

    def _activate_context_menu(self, index=None):
        items = self._context_menu_items();
        target = self.context_menu_index if index is None else int(index);
        if target < 0 or target >= len(items):
            return False;
        _label, _shortcut, enabled, action = items[target];
        if not enabled:
            return False;
        result = bool(action());
        self.close_context_menu();
        return result;

    def _context_menu_hit(self, event):
        if self._context_menu_bounds is None:
            return None;
        left, top, width, height = self._context_menu_bounds;
        x = int(event.x);
        y = int(event.y);
        if not (left <= x < left + width and top <= y < top + height):
            return None;
        row = y - top - 1;
        items = self._context_menu_items();
        if 0 <= row < len(items):
            return row;
        return -1;

    def _context_menu_renderable(self):
        rows = [];
        items = self._context_menu_items();
        content_width = max([len(label) + len(shortcut) + 3 for label, shortcut, _enabled, _action in items] or [12]);
        for index, (label, shortcut, enabled, _action) in enumerate(items):
            gap = max(1, content_width - len(label) - len(shortcut));
            row = Text(label + (" " * gap) + shortcut);
            if not enabled:
                row.stylize(self.theme.style("disabled"));
            elif index == self.context_menu_index:
                row.stylize(self.theme.style("menu_selection"));
            else:
                row.stylize(self.theme.style("menu"));
            rows.append(row);
        return RichPanel(
            Group(*rows),
            padding=(0, 0),
            border_style=self.theme.style("menu_border"),
            style=self.theme.style("menu"),
            width=content_width + 2,
        );

    @staticmethod
    def _overlay_line(base_line, overlay_line, left, width):
        left = max(0, int(left));
        width = max(1, int(width));
        overlay_width = min(width - left, line_cell_length(overlay_line));
        if overlay_width <= 0:
            return base_line;
        prefix = slice_segments(base_line, 0, left);
        middle = slice_segments(overlay_line, 0, overlay_width);
        suffix_start = left + overlay_width;
        suffix = slice_segments(base_line, suffix_start, max(0, width - suffix_start));
        return prefix + middle + suffix;

    def _move_cursor(self, line_delta=0, column_delta=0, select=False):
        lines = self._rendered_lines or [[]];
        line, column = self._clamp_position(*self.cursor);
        if line_delta:
            line = max(0, min(len(lines) - 1, line + int(line_delta)));
            column = min(column, self._line_width(line));
        if column_delta:
            column += int(column_delta);
            while column < 0 and line > 0:
                line -= 1;
                column = self._line_width(line);
            while line < len(lines) - 1 and column > self._line_width(line):
                column -= self._line_width(line) + 1;
                line += 1;
            column = max(0, min(self._line_width(line), column));
        new = (line, column);
        if select:
            if self.selection_anchor is None:
                self.selection_anchor = self.cursor;
            self.selection_cursor = new;
        else:
            self.clear_selection();
        self.cursor = new;
        return True;

    def handle_event(self, event):
        if isinstance(event, MouseEvent):
            if event.action == "press" and event.button == "right":
                if self._focus_manager is not None:
                    self._focus_manager.set(self);
                self.mouse_selecting = False;
                return self.open_context_menu(event.x, event.y);
            if self.context_menu_open:
                if event.action in ("scroll_up", "scroll_down"):
                    return self._move_context_menu(-1 if event.action == "scroll_up" else 1);
                if event.action == "press" and event.button == "left":
                    hit = self._context_menu_hit(event);
                    if hit is None:
                        self.close_context_menu();
                        return True;
                    if hit >= 0:
                        self.context_menu_index = hit;
                        return self._activate_context_menu(hit);
                    return True;
                if event.action in ("move", "drag"):
                    hit = self._context_menu_hit(event);
                    if hit is not None and hit >= 0:
                        items = self._context_menu_items();
                        if items[hit][2]:
                            self.context_menu_index = hit;
                    return True;
                return True;
            if event.action in ("scroll_up", "scroll_down"):
                amount = -3 if event.action == "scroll_up" else 3;
                if event.shift and not self.wrap:
                    return self.scroll_horizontal(amount);
                return self.scroll(amount);
            if event.action == "press" and event.button == "left":
                self.close_context_menu();
                if self._focus_manager is not None:
                    self._focus_manager.set(self);
                position = self._event_position(event);
                self.cursor = position;
                self.selection_anchor = position;
                self.selection_cursor = position;
                self.mouse_selecting = True;
                return True;
            if self.mouse_selecting and event.action in ("move", "drag"):
                self.cursor = self._event_position(event);
                self.selection_cursor = self.cursor;
                return True;
            if event.action == "release" and event.button == "left" and self.mouse_selecting:
                self.cursor = self._event_position(event);
                self.selection_cursor = self.cursor;
                self.mouse_selecting = False;
                return True;
            return False;
        key = getattr(event, "key", "");
        ctrl = bool(getattr(event, "ctrl", False));
        shift = bool(getattr(event, "shift", False));
        if ctrl and key in ("c", Key.INSERT):
            self.close_context_menu();
            return self.copy_selection();
        if ctrl and key == "a":
            self.close_context_menu();
            return self.select_all();
        if self.context_menu_open:
            if key == Key.ESCAPE:
                return self.close_context_menu();
            if key == Key.UP:
                return self._move_context_menu(-1);
            if key == Key.DOWN:
                return self._move_context_menu(1);
            if key == Key.ENTER:
                return self._activate_context_menu();
            return True;
        if shift and key == Key.LEFT:
            return self._move_cursor(column_delta=-1, select=True);
        if shift and key == Key.RIGHT:
            return self._move_cursor(column_delta=1, select=True);
        if shift and key == Key.UP:
            return self._move_cursor(line_delta=-1, select=True);
        if shift and key == Key.DOWN:
            return self._move_cursor(line_delta=1, select=True);
        horizontal = horizontal_delta(event, self.page_width);
        if horizontal is not None and not self.wrap:
            return self.scroll_horizontal(horizontal);
        self._pending_key = key;
        return self._pending_key in (Key.UP, Key.DOWN, Key.PAGE_UP, Key.PAGE_DOWN, Key.HOME, Key.END);

    def __rich_console__(self, console, options):
        viewport_width = max(1, options.max_width);
        height = options.height or options.max_height or console.height;
        self.page_width = viewport_width;
        self.page_size = max(1, int(height));
        render_width = self._preferred_width(viewport_width);
        if self._render_width is not None and render_width != self._render_width:
            self.clear_selection();
            self.mouse_selecting = False;
            self.close_context_menu();
        self._render_width = render_width;
        lines = self._lines(console, render_width);
        self._rendered_lines = lines;
        self.cursor = self._clamp_position(*self.cursor);
        if self.selection_anchor is not None:
            self.selection_anchor = self._clamp_position(*self.selection_anchor);
        if self.selection_cursor is not None:
            self.selection_cursor = self._clamp_position(*self.selection_cursor);
        self.content_height = max(1, len(lines));
        self.content_width = max([line_cell_length(line) for line in lines] or [viewport_width]);
        key = getattr(self, "_pending_key", "");
        if key == Key.UP:
            self.scroll(-1, len(lines));
        elif key == Key.DOWN:
            self.scroll(1, len(lines));
        elif key == Key.PAGE_UP:
            self.scroll(-self.page_size, len(lines));
        elif key == Key.PAGE_DOWN:
            self.scroll(self.page_size, len(lines));
        elif key == Key.HOME:
            self.offset = 0;
        elif key == Key.END:
            self.offset = max(0, len(lines) - self.page_size);
        self._pending_key = "";
        self.offset = max(0, min(self.offset, max(0, len(lines) - self.page_size)));
        self.x_offset = max(0, min(self.x_offset, self.max_x_offset));
        visible = lines[self.offset:self.offset + self.page_size];
        background = Style(bgcolor=self.theme.color("viewer_bg"));
        selection_style = Style.parse(self.theme.style("selection"));
        bounds = self._selection_bounds();
        output_lines = [];
        for line_index in range(self.page_size):
            absolute_line = self.offset + line_index;
            line = visible[line_index] if line_index < len(visible) else [];
            styled = [];
            line_width = line_cell_length(line);
            selected_start = selected_end = None;
            if bounds is not None:
                (line1, col1), (line2, col2) = bounds;
                if line1 <= absolute_line <= line2:
                    selected_start = col1 if absolute_line == line1 else 0;
                    selected_end = col2 if absolute_line == line2 else line_width;
                    selected_start = max(0, min(line_width, selected_start));
                    selected_end = max(selected_start, min(line_width, selected_end));
            chunks = [];
            if selected_start is None:
                chunks.append((line, False));
            else:
                if selected_start:
                    chunks.append((slice_segments(line, 0, selected_start), False));
                if selected_end > selected_start:
                    chunks.append((slice_segments(line, selected_start, selected_end - selected_start), True));
                if selected_end < line_width:
                    chunks.append((slice_segments(line, selected_end, line_width - selected_end), False));
            for chunk, selected in chunks:
                for segment in chunk:
                    style = (segment.style or Style()) + background;
                    if selected:
                        style = style + selection_style;
                    styled.append(Segment(segment.text, style, segment.control));
            pieces = slice_segments(styled, self.x_offset, viewport_width);
            used = 0;
            output_line = [];
            for segment in pieces:
                used += segment.cell_length;
                output_line.append(segment);
            if used < viewport_width:
                output_line.append(Segment(" " * (viewport_width - used), background));
            output_lines.append(output_line);
        if self.context_menu_open and output_lines:
            menu = self._context_menu_renderable();
            requested_width = max(1, int(getattr(menu, "width", 1) or 1));
            menu_width = min(viewport_width, requested_width);
            menu_lines = console.render_lines(menu, options.update(width=menu_width), pad=True, new_lines=False);
            menu_height = min(len(output_lines), len(menu_lines));
            left = max(0, min(self.context_menu_x, max(0, viewport_width - menu_width)));
            top = max(0, min(self.context_menu_y, max(0, len(output_lines) - menu_height)));
            self._context_menu_bounds = (left, top, menu_width, menu_height);
            for row in range(menu_height):
                output_lines[top + row] = self._overlay_line(output_lines[top + row], menu_lines[row], left, viewport_width);
        else:
            self._context_menu_bounds = None;
        for line_index, output_line in enumerate(output_lines):
            for segment in output_line:
                yield segment;
            if line_index + 1 < len(output_lines):
                yield Segment.line();
