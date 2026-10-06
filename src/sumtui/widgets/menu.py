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
from dataclasses import dataclass;
import time;

from sumui import DEFAULT_ALT_MENU_HOLD_MS, MenuInteractionConfig, parse_mnemonic;

from rich.columns import Columns;
from rich.console import Group;
from rich.panel import Panel as RichPanel;
from rich.text import Text;

from ..events import Key, KeyEvent, MouseEvent, normalize_key_spec;
from ..overlay import ModalOverlay;
from .base import Widget;
from .layout import VBox;


@dataclass
class MenuItem:
    label: str;
    action: object = None;
    shortcut: str = "";
    enabled: bool = True;
    checked: object = None;
    radio: object = None;
    submenu: object = None;

    @property
    def mnemonic_label(self):
        return parse_mnemonic(self.label, implicit=True);

    @property
    def display_label(self):
        return self.mnemonic_label.text;

    @property
    def mnemonic(self):
        return self.mnemonic_label.mnemonic;

    def invoke(self):
        if not self.enabled or self.submenu is not None:
            return False;
        if self.action is not None:
            self.action();
        return True;


class Separator(MenuItem):
    def __init__(self):
        super().__init__(label="", enabled=False);


class Menu:
    def __init__(self, title, items=None):
        self.title = str(title);
        self.items = list(items or []);

    @property
    def mnemonic_label(self):
        return parse_mnemonic(self.title, implicit=True);

    @property
    def display_title(self):
        return self.mnemonic_label.text;

    @property
    def mnemonic(self):
        return self.mnemonic_label.mnemonic;

    def selectable_indices(self):
        return [index for index, item in enumerate(self.items) if item.enabled and not isinstance(item, Separator)];


class MenuBar(Widget):
    focusable = True;

    def __init__(self, menus=None, on_close=None, activation_key="f9", mnemonics=True, theme=None,
                 alt_menu_hold_ms=DEFAULT_ALT_MENU_HOLD_MS, shortcut_available=None, clock=None):
        super().__init__(theme=theme);
        self.menus = list(menus or []);
        self.active = False;
        self.menu_index = 0;
        self.path = [];
        self.on_close = on_close;
        self.activation_key = normalize_key_spec(activation_key);
        self.mnemonics = bool(mnemonics);
        self.interaction = MenuInteractionConfig(alt_menu_hold_ms=alt_menu_hold_ms);
        self.shortcut_available = shortcut_available;
        self._clock = clock or time.monotonic;
        self._alt_down_since = None;
        self._alt_chorded = False;

    def set_alt_menu_hold_ms(self, value):
        self.interaction = MenuInteractionConfig(alt_menu_hold_ms=value);
        return self.interaction.normalized_hold_ms();

    @property
    def current_menu(self):
        menu = self.menus[self.menu_index] if self.menus else None;
        for index in self.path[:-1]:
            if menu is None or index >= len(menu.items):
                return None;
            menu = menu.items[index].submenu;
        return menu;

    @property
    def current_index(self):
        return self.path[-1] if self.path else -1;

    def _first(self, menu):
        indices = menu.selectable_indices() if menu is not None else [];
        return indices[0] if indices else -1;

    def open(self, index=None):
        if not self.menus:
            return False;
        if index is not None:
            self.menu_index = int(index) % len(self.menus);
        self.active = True;
        if self._focus_manager is not None:
            self._focus_manager.set(self);
        first = self._first(self.menus[self.menu_index]);
        self.path = [first] if first >= 0 else [];
        return True;

    def close(self):
        changed = self.active;
        self.active = False;
        self.path = [];
        if changed and self.on_close is not None:
            self.on_close();
        return changed;

    def _move_item(self, delta):
        menu = self.current_menu;
        choices = menu.selectable_indices() if menu is not None else [];
        if not choices:
            return False;
        current = self.current_index;
        try:
            pos = choices.index(current);
        except ValueError:
            pos = 0;
        target = choices[(pos + int(delta)) % len(choices)];
        if self.path:
            self.path[-1] = target;
        else:
            self.path = [target];
        return True;

    def _move_menu(self, delta):
        if not self.menus:
            return False;
        self.menu_index = (self.menu_index + int(delta)) % len(self.menus);
        first = self._first(self.menus[self.menu_index]);
        self.path = [first] if first >= 0 else [];
        return True;

    def _open_submenu(self):
        menu = self.current_menu;
        index = self.current_index;
        if menu is None or index < 0:
            return False;
        item = menu.items[index];
        if item.submenu is None:
            return False;
        first = self._first(item.submenu);
        if first < 0:
            return False;
        self.path.append(first);
        return True;

    def _close_submenu(self):
        if len(self.path) <= 1:
            return False;
        self.path.pop();
        return True;

    def activate(self):
        menu = self.current_menu;
        index = self.current_index;
        if menu is None or index < 0:
            return False;
        item = menu.items[index];
        if item.submenu is not None:
            return self._open_submenu();
        done = item.invoke();
        if done:
            self.close();
        return done;

    def _menu_for_mnemonic(self, needle):
        key = str(needle or "").casefold();
        for index, menu in enumerate(self.menus):
            if menu.mnemonic and menu.mnemonic == key:
                return index;
        return None;

    def _item_for_mnemonic(self, menu, needle):
        key = str(needle or "").casefold();
        if menu is None:
            return None;
        for index, item in enumerate(menu.items):
            if item.enabled and not isinstance(item, Separator) and item.mnemonic and item.mnemonic == key:
                return index;
        return None;

    def _alt_shortcut_available(self, mnemonic):
        if not mnemonic:
            return False;
        if self.shortcut_available is None:
            return True;
        return bool(self.shortcut_available("alt+{}".format(mnemonic)));

    def handle_event(self, event):
        if isinstance(event, MouseEvent):
            if event.action in ("scroll_up", "scroll_down") and self.active:
                return self._move_item(-1 if event.action == "scroll_up" else 1);
            if event.action != "press" or event.button != "left":
                return False;
            if event.y == 0:
                cursor = 0;
                for index, menu in enumerate(self.menus):
                    span = len(" {} ".format(menu.display_title));
                    if cursor <= event.x < cursor + span:
                        if self._focus_manager is not None:
                            self._focus_manager.set(self);
                        return self.open(index);
                    cursor += span;
                if self.active:
                    return self.close();
                return False;
            if self.active and self.path:
                left = self.popup_left;
                menu = self.menus[self.menu_index];
                for depth, selected in enumerate(list(self.path)):
                    width = self._menu_content_width(menu) + 2;
                    height = len(menu.items) + 2;
                    if left <= event.x < left + width and 1 <= event.y < 1 + height:
                        row = event.y - 2;
                        if 0 <= row < len(menu.items):
                            item = menu.items[row];
                            if item.enabled and not isinstance(item, Separator):
                                self.path = self.path[:depth] + [row];
                                if item.submenu is not None:
                                    first = self._first(item.submenu);
                                    if first >= 0:
                                        self.path.append(first);
                                    return True;
                                done = item.invoke();
                                if done:
                                    self.close();
                                return True;
                        return True;
                    item = menu.items[selected] if 0 <= selected < len(menu.items) else None;
                    if item is None or item.submenu is None:
                        break;
                    left += width;
                    menu = item.submenu;
                return self.close();
            return False;
        key = getattr(event, "key", "");
        action = getattr(event, "action", "press");
        if key in ("alt", "left_alt", "right_alt"):
            if action == "press":
                self._alt_down_since = self._clock();
                self._alt_chorded = False;
                return True;
            if action == "release":
                started = self._alt_down_since;
                self._alt_down_since = None;
                if started is None or self._alt_chorded:
                    return True;
                hold_ms = self.interaction.normalized_hold_ms();
                if hold_ms is not None and ((self._clock() - started) * 1000.0) >= hold_ms:
                    return self.close() if self.active else self.open();
                return True;
        if action == "release":
            return False;
        if self.activation_key and getattr(event, "name", "") == self.activation_key:
            return self.close() if self.active else self.open();
        if not self.active:
            if self.mnemonics and getattr(event, "alt", False) and getattr(event, "text", ""):
                self._alt_chorded = True;
                needle = event.text.casefold();
                index = self._menu_for_mnemonic(needle);
                if index is not None and self._alt_shortcut_available(needle):
                    return self.open(index);
            return False;
        if key == Key.ESCAPE:
            return self._close_submenu() or self.close();
        if key == Key.UP:
            return self._move_item(-1);
        if key == Key.DOWN:
            return self._move_item(1);
        if key == Key.RIGHT:
            return self._open_submenu() or self._move_menu(1);
        if key == Key.LEFT:
            return self._close_submenu() or self._move_menu(-1);
        if key == Key.HOME:
            menu = self.current_menu;
            first = self._first(menu);
            if first >= 0 and self.path:
                self.path[-1] = first;
                return True;
        if key == Key.END:
            menu = self.current_menu;
            choices = menu.selectable_indices() if menu is not None else [];
            if choices and self.path:
                self.path[-1] = choices[-1];
                return True;
        if key == Key.ENTER:
            return self.activate();
        if key == Key.SPACE or (getattr(event, "text", "") == " " and not getattr(event, "ctrl", False) and not getattr(event, "alt", False)):
            menu = self.current_menu;
            index = self.current_index;
            if menu is not None and index >= 0:
                item = menu.items[index];
                if item.enabled and item.submenu is None and (item.checked is not None or item.radio is not None):
                    item.invoke();
                    return True;
        text = getattr(event, "text", "");
        if text and self.mnemonics:
            needle = text.casefold();
            if len(self.path) <= 1:
                menu_index = self._menu_for_mnemonic(needle);
                if menu_index is not None:
                    return self.open(menu_index);
            menu = self.current_menu;
            index = self._item_for_mnemonic(menu, needle);
            if index is not None:
                if self.path:
                    self.path[-1] = index;
                else:
                    self.path = [index];
                item = menu.items[index];
                if item.submenu is not None:
                    return self._open_submenu();
                return self.activate();
        return False;

    def _menu_content_width(self, menu):
        widths = [12];
        for item in menu.items:
            if isinstance(item, Separator):
                continue;
            marker_width = 4;
            shortcut_width = (2 + len(item.shortcut)) if item.shortcut else 0;
            arrow_width = 2 if item.submenu is not None else 0;
            widths.append(marker_width + len(item.display_label) + shortcut_width + arrow_width + 1);
        return max(widths);

    @property
    def popup_left(self):
        if not self.menus:
            return 0;
        return sum(len(" {} ".format(menu.display_title)) for menu in self.menus[:self.menu_index]);

    def _visible_menu_path(self):
        output = [];
        if not self.active or not self.path or not self.menus:
            return output;
        menu = self.menus[self.menu_index];
        for selected in self.path:
            output.append((menu, selected));
            item = menu.items[selected] if 0 <= selected < len(menu.items) else None;
            if item is None or item.submenu is None:
                break;
            menu = item.submenu;
        return output;

    @property
    def popup_width(self):
        visible = self._visible_menu_path();
        if not visible:
            return 1;
        return max(1, sum(self._menu_content_width(menu) + 2 for menu, _selected in visible));

    @property
    def popup_height(self):
        visible = self._visible_menu_path();
        if not visible:
            return 1;
        return max(1, max(len(menu.items) + 2 for menu, _selected in visible));

    def popup_renderable(self):
        visible = self._visible_menu_path();
        if not visible:
            return None;
        return Columns([self._render_menu(menu, selected, depth) for depth, (menu, selected) in enumerate(visible)], padding=(0, 0), expand=False);

    def preferred_height(self, width=None):
        if not self.active or not self.path:
            return 1;
        menu = self.menus[self.menu_index];
        height = len(menu.items) + 3;
        for selected in self.path[:-1]:
            item = menu.items[selected] if 0 <= selected < len(menu.items) else None;
            if item is None or item.submenu is None:
                break;
            menu = item.submenu;
            height = max(height, len(menu.items) + 3);
        return max(1, height);

    def _render_menu(self, menu, selected, depth=0):
        rows = [];
        content_width = self._menu_content_width(menu);
        panel_width = content_width + 2;
        for index, item in enumerate(menu.items):
            if isinstance(item, Separator):
                rows.append(Text("─" * max(3, content_width), style=self.theme.style("menu_border")));
                continue;
            marker = "";
            if item.checked is not None:
                checked = item.checked() if callable(item.checked) else bool(item.checked);
                marker = "[x] " if checked else "[ ] ";
            elif item.radio is not None:
                selected_radio = item.radio() if callable(item.radio) else bool(item.radio);
                marker = "(●) " if selected_radio else "( ) ";
            else:
                marker = "    ";
            arrow = " ▶" if item.submenu is not None else "";
            shortcut = ("  " + item.shortcut) if item.shortcut else "";
            body = (marker + item.display_label);
            space = max(1, content_width - len(body) - len(shortcut) - len(arrow));
            text = Text(body + (" " * space) + shortcut + arrow);
            if not item.enabled:
                text.stylize(self.theme.style("disabled"));
            elif index == selected:
                text.stylize(self.theme.style("menu_selection"));
            else:
                text.stylize(self.theme.style("menu"));
            mnemonic = item.mnemonic_label;
            if mnemonic.index >= 0 and item.enabled:
                offset = len(marker) + mnemonic.index;
                text.stylize("underline", offset, offset + 1);
            rows.append(text);
        return RichPanel(Group(*rows), padding=(0, 0), border_style=self.theme.style("menu_border"), style=self.theme.style("menu"), width=panel_width);

    def __rich_console__(self, console, options):
        labels = [];
        for index, menu in enumerate(self.menus):
            style = self.theme.style("menu_title_active" if self.active and index == self.menu_index else "menu_title");
            label = Text(" {} ".format(menu.display_title), style=style);
            mnemonic = menu.mnemonic_label;
            if mnemonic.index >= 0:
                label.stylize("underline", 1 + mnemonic.index, 2 + mnemonic.index);
            labels.append(label);
        bar = Text();
        for label in labels:
            bar.append_text(label);
        remaining = max(0, options.max_width - len(bar.plain));
        if remaining:
            bar.append(" " * remaining, style=self.theme.style("menu_bar"));
        if not self.active or not self.path:
            yield bar;
            return;
        panels = [];
        menu = self.menus[self.menu_index];
        for depth, selected in enumerate(self.path):
            panels.append(self._render_menu(menu, selected, depth));
            item = menu.items[selected] if 0 <= selected < len(menu.items) else None;
            if item is None or item.submenu is None:
                break;
            menu = item.submenu;
        yield Group(bar, Columns(panels, padding=(0, 0), expand=False));


class _MenuPanelSurface:
    def __init__(self, menu_bar, menu, selected, left, top=1):
        self.menu_bar = menu_bar;
        self.menu = menu;
        self.selected = selected;
        self.top = int(top);
        self.left = int(left);
        self.shadow = False;

    @property
    def width(self):
        return self.menu_bar._menu_content_width(self.menu) + 2;

    @property
    def height(self):
        return len(self.menu.items) + 2;

    def __rich_console__(self, console, options):
        yield self.menu_bar._render_menu(self.menu, self.selected);


class MenuDesktop(Widget):
    """One-line MenuBar with dropdowns composited over the client area.

    Each visible popup panel is overlaid independently.  This matters when a
    submenu is taller than its parent: the cells below the shorter panel stay
    transparent and the underlying editor/viewer remains visible instead of
    being replaced by terminal-default black padding.
    """;
    def __init__(self, menu, body, theme=None):
        super().__init__(theme=theme);
        self.menu = menu;
        self.body = body;
        self.set_theme(self.theme);

    def children(self):
        return [self.menu, self.body];

    @property
    def items(self):
        """Compatibility view of body layout items for simple hosts/tests.""";
        return getattr(self.body, "items", []);

    def capture_event(self, event):
        if not isinstance(event, KeyEvent):
            return False;
        key = getattr(event, "key", "");
        if key in ("alt", "left_alt", "right_alt"):
            return bool(self.menu.handle_event(event));
        if self.menu.mnemonics and getattr(event, "alt", False) and getattr(event, "text", ""):
            return bool(self.menu.handle_event(event));
        return False;

    def handle_event(self, event):
        if isinstance(event, MouseEvent):
            if event.y == 0 or self.menu.active:
                handled = self.menu.handle_event(event);
                if handled:
                    return True;
            if event.y > 0:
                return bool(self.body.handle_event(event.translated(0, 1)));
            return False;
        return bool(self.body.handle_event(event));

    def __rich_console__(self, console, options):
        base = VBox(self.menu, self.body, sizes=[1, None]);
        base.set_theme(self.theme);
        renderable = base;
        if self.menu.active and self.menu.path:
            left = self.menu.popup_left;
            menu = self.menu.menus[self.menu.menu_index];
            for depth, selected in enumerate(self.menu.path):
                panel = _MenuPanelSurface(self.menu, menu, selected, left=left, top=1);
                renderable = ModalOverlay(renderable, panel);
                item = menu.items[selected] if 0 <= selected < len(menu.items) else None;
                if item is None or item.submenu is None:
                    break;
                left += panel.width;
                menu = item.submenu;
        yield renderable;


class ContextMenu(MenuBar):
    def __init__(self, items=None, title="Menu", on_close=None, theme=None):
        super().__init__([Menu(title, items or [])], on_close=on_close, theme=theme);
        self.open(0);

    def __rich_console__(self, console, options):
        if not self.path:
            return;
        panels = [];
        menu = self.menus[0];
        for depth, selected in enumerate(self.path):
            panels.append(self._render_menu(menu, selected, depth));
            item = menu.items[selected] if 0 <= selected < len(menu.items) else None;
            if item is None or item.submenu is None:
                break;
            menu = item.submenu;
        yield Columns(panels, padding=(0, 0), expand=False);
