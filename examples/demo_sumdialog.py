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
from pathlib import Path;
import sys;

ROOT = Path(__file__).resolve().parents[1];
sys.path.insert(0, str(ROOT / "src"));

from sumtui import ask_question, read_entry, show_message;


def main():
    theme = "Ralesk's MC";
    show_message("sumdialog services are available from Python too.", title="sumTUI", theme=theme);
    if not ask_question("Enter a small example value?", title="Question", theme=theme).accepted:
        return 0;
    result = read_entry("Value:", title="Input", theme=theme, width=30);
    if result.accepted:
        show_message("You entered: {}".format(result.value), title="Result", theme=theme);
    return int(result.status);


if __name__ == "__main__":
    raise SystemExit(main());
