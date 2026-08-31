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
from dataclasses import dataclass;
from pathlib import Path;
import re;


@dataclass(frozen=True)
class CodeSymbol:
    kind: str;
    name: str;
    line: int;
    column: int = 1;

    @property
    def label(self):
        return "{:<10} {:<30} line {}".format(self.kind.upper(), self.name, self.line);


def detect_language(filename=None, language=None):
    requested = str(language or "").strip().lower();
    aliases = {
        "py": "python", "python3": "python", "rscript": "r",
        "sh": "bash", "shell": "bash", "zsh": "bash",
        "c++": "cpp", "cxx": "cpp", "cc": "cpp",
        "basic": "basic", "bas": "basic", "sumbasic": "basic",
        "xbase": "xbase", "sumx": "xbase", "prg": "xbase",
    };
    if requested and requested != "auto":
        return aliases.get(requested, requested);
    suffix = Path(str(filename or "")).suffix.lower();
    return {
        ".py": "python", ".pyw": "python", ".r": "r",
        ".sh": "bash", ".bash": "bash", ".zsh": "bash",
        ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp",
        ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp", ".hxx": "cpp",
        ".bas": "basic", ".basic": "basic", ".prg": "xbase",
    }.get(suffix, "text");


def _append(output, seen, kind, name, line, column=1):
    name = str(name or "").strip();
    if not name:
        return None;
    key = (str(kind).casefold(), name.casefold(), int(line));
    if key in seen:
        return None;
    seen.add(key);
    output.append(CodeSymbol(str(kind), name, int(line), int(column)));
    return output[-1];


def _python_symbols(lines, output, seen):
    for number, line in enumerate(lines, 1):
        match = re.match(r"^(\s*)(async\s+def|def|class)\s+([A-Za-z_]\w*)", line);
        if match:
            kind = "CLASS" if match.group(2).strip() == "class" else "FUNCTION";
            name = match.group(3);
            if match.group(1):
                name = "{}{}".format("  " * (len(match.group(1).expandtabs(4)) // 4), name);
                if kind == "FUNCTION":
                    kind = "METHOD";
            _append(output, seen, kind, name, number, len(match.group(1)) + 1);


def _r_symbols(lines, output, seen):
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s*([A-Za-z.][\w.]*)\s*(?:<-|=)\s*function\s*\(", line);
        if match:
            _append(output, seen, "FUNCTION", match.group(1), number);
        match = re.match(r"^\s*(?:setClass|R6Class)\s*\(\s*[\"']([^\"']+)", line);
        if match:
            _append(output, seen, "CLASS", match.group(1), number);


def _bash_symbols(lines, output, seen):
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s*(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(\s*\))?\s*\{", line);
        if match:
            _append(output, seen, "FUNCTION", match.group(1), number);


def _basic_symbols(lines, output, seen):
    for number, line in enumerate(lines, 1):
        source = re.sub(r"^\s*\d+\s+", "", line);
        match = re.match(r"^\s*(SUB|FUNCTION)\s+([A-Za-z_]\w*)", source, re.I);
        if match:
            _append(output, seen, match.group(1).upper(), match.group(2), number);
            continue;
        match = re.match(r"^\s*DEF\s+FN\s*([A-Za-z_]\w*)", source, re.I);
        if match:
            _append(output, seen, "FUNCTION", match.group(1), number);


def _xbase_symbols(lines, output, seen):
    class_name = "";
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s*DEFINE\s+CLASS\s+([A-Za-z_]\w*)", line, re.I);
        if match:
            class_name = match.group(1);
            _append(output, seen, "CLASS", class_name, number);
            continue;
        if re.match(r"^\s*ENDDEFINE\b", line, re.I):
            class_name = "";
            continue;
        match = re.match(r"^\s*(PROCEDURE|FUNCTION|METHOD)\s+([A-Za-z_]\w*)", line, re.I);
        if match:
            kind = match.group(1).upper();
            name = match.group(2);
            if class_name and kind in ("PROCEDURE", "METHOD"):
                name = "{}.{}".format(class_name, name);
                kind = "METHOD";
            _append(output, seen, kind, name, number);


def _c_symbols(lines, output, seen, cpp=False):
    controls = {"if", "for", "while", "switch", "catch", "return", "sizeof"};
    pending = "";
    pending_line = 0;
    for number, raw in enumerate(lines, 1):
        line = re.sub(r"//.*$", "", raw).strip();
        if cpp:
            match = re.match(r"^(?:template\s*<.*>\s*)?(class|struct)\s+([A-Za-z_]\w*)", line);
            if match:
                _append(output, seen, match.group(1).upper(), match.group(2), number);
        if not line or line.startswith("#"):
            continue;
        if pending:
            pending += " " + line;
        elif "(" in line and not line.endswith(";"):
            pending = line;
            pending_line = number;
        else:
            continue;
        if "{" not in pending:
            continue;
        candidate = pending;
        start_line = pending_line;
        pending = "";
        match = re.search(r"(?:^|[\s*&:>])([A-Za-z_~][\w:~]*)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[^\{]+)?\{", candidate);
        if not match:
            continue;
        name = match.group(1);
        base = name.split("::")[-1].casefold();
        if base in controls:
            continue;
        kind = "METHOD" if "::" in name else "FUNCTION";
        _append(output, seen, kind, name, start_line);


def build_symbol_map(text, language=None, filename=None):
    resolved = detect_language(filename=filename, language=language);
    lines = str(text or "").splitlines();
    output = [CodeSymbol("MAIN", "main", 1, 1)];
    seen = {("main", "main", 1)};
    if resolved == "python":
        _python_symbols(lines, output, seen);
    elif resolved == "r":
        _r_symbols(lines, output, seen);
    elif resolved == "bash":
        _bash_symbols(lines, output, seen);
    elif resolved == "basic":
        _basic_symbols(lines, output, seen);
    elif resolved == "xbase":
        _xbase_symbols(lines, output, seen);
    elif resolved in ("c", "cpp"):
        _c_symbols(lines, output, seen, cpp=resolved == "cpp");
    return output;
