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

from rich.console import Console;

from sumtui import ChartSpec, ChartView;


console = Console();

console.print(ChartView(ChartSpec.bar(["A", "B", "C"], [25, 50, 35], title="Bar chart"), height=8));
console.print();
console.print(ChartView(ChartSpec.pie(["Python", "R", "C"], [45, 35, 20], title="Pie chart"), height=12));
console.print();
console.print(ChartView(ChartSpec.line([(0, 1), (1, 4), (2, 3), (3, 8), (4, 6)], title="Braille line", x_label="time"), height=10));
