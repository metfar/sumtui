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

from sumui.clipboard import ClipboardService, clipboard;


def trim_selected_text(text):
    """Remove visual right-side padding from copied selection lines.

    Selection in rendered terminal cells may include blank cells to the right of
    the last visible character.  Strip only spaces/tabs at the right edge of
    each copied line while preserving line breaks and all leading whitespace.
    """;
    return "\n".join(line.rstrip(" \t") for line in str(text).split("\n"));


__all__ = ["ClipboardService", "clipboard", "trim_selected_text"];
