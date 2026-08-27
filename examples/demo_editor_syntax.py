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
from sumtui import Application, Panel, TextEditor;


MARKDOWN = '''# sumTUI Markdown highlighting

The editor keeps **Markdown source** editable and highlights fenced code with the same semantic roles used by the source language.

```python
if value == 5:
    print("Python")
```

```bash
if [ -f README.md ]; then
    echo "Bash"
fi
```

<p align=center><b>- oOo -</b></p>
''';


def main():
    editor = TextEditor(MARKDOWN, line_numbers=True, syntax_highlighting=True, syntax_language="markdown", syntax_filename="README.md");
    app = Application(root=Panel(editor, title="Markdown source", content_style="viewer"), title="sumTUI syntax demo", theme="DOS", capture_control_keys=True);
    app.focus.set(editor);
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
