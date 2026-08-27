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
from rich.align import Align;
from rich.panel import Panel as RichPanel;
from rich.text import Text;

from .base import Widget;


class Label(Widget):
    def __init__(self, text="", style="text", align="left", theme=None):
        super().__init__(theme=theme);
        self.text = str(text);
        self.style = style;
        self.align = align;

    def set_text(self, text):
        self.text = str(text);
        return self;

    def __rich_console__(self, console, options):
        text = Text(self.text, style=self.theme.style(self.style));
        if self.align in ("center", "right"):
            yield Align(text, align=self.align, vertical="middle");
        else:
            yield text;


class Panel(Widget):
    def __init__(self, child=None, title="", subtitle="", padding=(0, 1), content_style=None, theme=None):
        super().__init__(theme=theme);
        self.child = child;
        self.title = str(title);
        self.subtitle = str(subtitle);
        self.padding = padding;
        self.content_style = None if content_style is None else str(content_style);
        if self.child is not None:
            self.child.set_theme(self.theme);

    def children(self):
        return [self.child] if self.child is not None else [];

    def set_child(self, child):
        self.child = child;
        if child is not None:
            child.set_theme(self.theme);
        return child;

    def __rich_console__(self, console, options):
        content = self.child if self.child is not None else Text("");
        height = options.height or options.max_height;
        yield RichPanel(
            content,
            title=self.title or None,
            subtitle=self.subtitle or None,
            title_align="center",
            border_style=self.theme.style("border"),
            style=self.theme.style(self.content_style or "panel"),
            padding=self.padding,
            expand=True,
            height=height,
        );


class StatusBar(Widget):
    def __init__(self, text="Ready", theme=None):
        super().__init__(theme=theme);
        self.text = str(text);

    def set(self, text):
        self.text = str(text);
        return self;

    def __rich_console__(self, console, options):
        width = max(1, options.max_width);
        text = self.text[:width].ljust(width);
        yield Text(text, style=self.theme.style("status"), overflow="crop", no_wrap=True);
