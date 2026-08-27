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

from rich.layout import Layout;

from .base import Widget;


@dataclass
class LayoutItem:
    widget: Widget;
    size: int = None;
    ratio: int = 1;
    name: str = None;


class _Box(Widget):
    direction = "column";

    def __init__(self, *children, theme=None, sizes=None, ratios=None):
        super().__init__(theme=theme);
        sizes = list(sizes or []);
        ratios = list(ratios or []);
        self.items = [];
        for index, child in enumerate(children):
            size = sizes[index] if index < len(sizes) else None;
            ratio = ratios[index] if index < len(ratios) else 1;
            self.items.append(LayoutItem(child, size=size, ratio=ratio, name="item{}".format(index)));
        self.set_theme(self.theme);

    def children(self):
        return [item.widget for item in self.items];

    def add(self, widget, size=None, ratio=1, name=None):
        self.items.append(LayoutItem(widget, size=size, ratio=ratio, name=name or "item{}".format(len(self.items))));
        widget.set_theme(self.theme);
        return widget;

    def __rich_console__(self, console, options):
        root = Layout(name="root");
        layouts = [];
        for index, item in enumerate(self.items):
            size = item.size;
            if size is None and self.direction == "column" and hasattr(item.widget, "preferred_height"):
                preferred = item.widget.preferred_height(options.max_width);
                if preferred is not None:
                    size = max(1, int(preferred));
            layouts.append(Layout(item.widget, name=item.name or "item{}".format(index), size=size, ratio=max(1, int(item.ratio))));
        if self.direction == "row":
            root.split_row(*layouts);
        else:
            root.split_column(*layouts);
        yield from console.render(root, options);


class VBox(_Box):
    direction = "column";


class HBox(_Box):
    direction = "row";
