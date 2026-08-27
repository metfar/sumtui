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
from rich.text import Text;

from ..events import Key;
from .base import Widget;


class ScrollBar(Widget):
    def __init__(self, value=0, maximum=100, page=10, orientation="vertical", interactive=False,
                 on_change=None, theme=None):
        super().__init__(theme=theme);
        self.maximum = max(0, int(maximum));
        self.page = max(1, int(page));
        self.value = max(0, min(self.maximum, int(value)));
        self.orientation = str(orientation).lower();
        if self.orientation not in ("vertical", "horizontal"):
            raise ValueError("orientation must be 'vertical' or 'horizontal'");
        self.focusable = bool(interactive);
        self.on_change = on_change;

    def set(self, value, notify=True):
        old = self.value;
        self.value = max(0, min(self.maximum, int(value)));
        if notify and self.value != old and self.on_change is not None:
            self.on_change(self, self.value);
        return self.value != old;

    def handle_event(self, event):
        key = getattr(event, "key", "");
        if self.orientation == "vertical":
            if key == Key.UP:
                return self.set(self.value - 1);
            if key == Key.DOWN:
                return self.set(self.value + 1);
        else:
            if key == Key.LEFT:
                return self.set(self.value - 1);
            if key == Key.RIGHT:
                return self.set(self.value + 1);
        if key == Key.PAGE_UP:
            return self.set(self.value - self.page);
        if key == Key.PAGE_DOWN:
            return self.set(self.value + self.page);
        if key == Key.HOME:
            return self.set(0);
        if key == Key.END:
            return self.set(self.maximum);
        return False;

    def __rich_console__(self, console, options):
        if self.orientation == "horizontal":
            length = max(3, options.max_width);
        else:
            length = max(3, options.height or options.max_height or console.height);
        span = max(1, self.maximum + self.page);
        thumb = max(1, min(length, int(round(length * self.page / span))));
        room = max(0, length - thumb);
        pos = 0 if self.maximum <= 0 else int(round(room * self.value / self.maximum));
        normal = self.theme.style("scrollbar_track");
        selected = self.theme.style("scrollbar_thumb_focus" if self.focused else "scrollbar_thumb");
        if self.orientation == "horizontal":
            text = Text("─" * length, style=normal);
            text.stylize(selected, pos, min(length, pos + thumb));
            yield text;
            return;
        output = Text();
        for index in range(length):
            if index:
                output.append("\n");
            output.append("█" if pos <= index < pos + thumb else "│", style=selected if pos <= index < pos + thumb else normal);
        yield output;
