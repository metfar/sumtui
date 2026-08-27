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
import argparse;
from pathlib import Path;
import sys;

from .. import __version__;
from ..dialogs import ask_question, choose_checklist, choose_file, choose_list, choose_radio, read_entry, show_message, show_text;
from ..progress_cli import main as progress_main;
from ..prompt import TERMINAL_ERROR;
from .input import _parse_timeout;


def _parser():
    parser = argparse.ArgumentParser(
        prog="sumdialog",
        description="Console dialog helper built on sumTUI; stdout is reserved for returned values",
    );
    parser.add_argument("--version", action="version", version="sumdialog {}".format(__version__));
    mode = parser.add_mutually_exclusive_group(required=True);
    mode.add_argument("--info", action="store_true", help="show an informational dialog");
    mode.add_argument("--warning", action="store_true", help="show a warning dialog");
    mode.add_argument("--error", action="store_true", help="show an error dialog");
    mode.add_argument("--question", action="store_true", help="show a Yes/No dialog");
    mode.add_argument("--entry", action="store_true", help="read one value (suminput dialog mode)");
    mode.add_argument("--file-selection", action="store_true", help="select a file");
    mode.add_argument("--directory-selection", action="store_true", help="select a directory");
    mode.add_argument("--list", action="store_true", help="select one item from a list");
    mode.add_argument("--radiolist", action="store_true", help="select one radio item");
    mode.add_argument("--checklist", action="store_true", help="select zero or more checkbox items");
    mode.add_argument("--text-info", action="store_true", help="show scrollable plain text");
    mode.add_argument("--markdown", action="store_true", help="show scrollable Markdown");
    mode.add_argument("--progress", action="store_true", help="read progress from stdin; compatible with sumprogress");
    parser.add_argument("items", nargs="*", help="items used by --list/--radiolist/--checklist");
    parser.add_argument("--title", default=None, help="dialog title");
    parser.add_argument("--text", default="", help="message, prompt, or list description");
    parser.add_argument("--theme", default="DOS", help="sumTUI theme name");
    parser.add_argument("--width", type=int, default=None, help="dialog or entry width");
    parser.add_argument("--height", type=int, default=None, help="dialog height; --entry uses it as input height");
    parser.add_argument("--timeout", metavar="[DEFAULT,]SECONDS", help="timeout in seconds; entry also accepts DEFAULT,SECONDS");
    parser.add_argument("--default", default="", help="default entry/list/radio value");
    parser.add_argument("--ok-label", default=None, help="custom OK/Yes label for message/question dialogs");
    parser.add_argument("--cancel-label", default=None, help="custom Cancel/No label for question dialogs");
    parser.add_argument("--hidden", action="store_true", help="hide --entry input");
    parser.add_argument("--mask", nargs="?", const="*", help="visual echo mask for --entry; default: *");
    parser.add_argument("--keys", default="", help="accepted single-character set for --entry");
    parser.add_argument("--case-sensitive", action="store_true", help="case-sensitive --keys matching");
    parser.add_argument("--picture", default="", help="xBase-like PICTURE mask for --entry");
    parser.add_argument("--overflow", action="store_true", help="allow --entry input after PICTURE capacity");
    parser.add_argument("--path", default=".", help="initial path for file/directory selection");
    parser.add_argument("--filename", help="file shown by --text-info or --markdown");
    parser.add_argument("--selected", action="append", default=[], help="preselect checklist item; may be repeated");
    parser.add_argument("--separator", default="\n", help="checklist output separator; default newline");
    parser.add_argument("--percent-input", action="store_true", help="with --progress, read percentage values from stdin");
    parser.add_argument("--total", help="with --progress, byte passthrough total such as 10M or 4.7G");
    parser.add_argument("--label", default=None, help="progress label");
    return parser;


def _write_value(value):
    sys.stdout.write(str(value));
    sys.stdout.write("\n");
    sys.stdout.flush();


def _text_source(args):
    if args.filename:
        return Path(args.filename).expanduser().read_text(encoding="utf-8", errors="replace");
    if not sys.stdin.isatty():
        return sys.stdin.read();
    return str(args.text or "");


def _mode_title(args, fallback):
    return str(args.title or fallback);


def main(argv=None):
    parser = _parser();
    args = parser.parse_args(sys.argv[1:] if argv is None else list(argv));
    try:
        timeout, timeout_default = _parse_timeout(args.timeout, args.default);
        if timeout_default != "":
            args.default = timeout_default;
        if args.progress:
            progress_args = [];
            if args.total:
                progress_args.extend(["--total", str(args.total)]);
            else:
                progress_args.append("--percent-input");
            if args.label:
                progress_args.extend(["--label", str(args.label)]);
            if args.width is not None:
                progress_args.extend(["--width", str(args.width)]);
            return int(progress_main(progress_args));
        if args.info or args.warning or args.error:
            kind = "warning" if args.warning else ("error" if args.error else "info");
            fallback = "Warning" if args.warning else ("Error" if args.error else "Information");
            result = show_message(
                args.text,
                title=_mode_title(args, fallback),
                kind=kind,
                theme=args.theme,
                width=args.width,
                height=args.height,
                timeout=timeout,
                ok_label=args.ok_label or "OK",
            );
            return int(result.status);
        if args.question:
            result = ask_question(
                args.text,
                title=_mode_title(args, "Question"),
                theme=args.theme,
                width=args.width,
                height=args.height,
                timeout=timeout,
                yes_label=args.ok_label or "Yes",
                no_label=args.cancel_label or "No",
            );
            return int(result.status);
        if args.entry:
            result = read_entry(
                text=args.text,
                title=_mode_title(args, "Input"),
                theme=args.theme,
                width=args.width,
                height=(1 if args.height is None else args.height),
                picture=args.picture,
                overflow=args.overflow,
                hidden=args.hidden,
                mask=args.mask,
                keys=args.keys,
                case_sensitive=args.case_sensitive,
                default=args.default,
                timeout=timeout,
            );
            if result.status in (0, 3):
                _write_value(result.value);
            return int(result.status);
        if args.file_selection or args.directory_selection:
            result = choose_file(
                path=args.path,
                title=_mode_title(args, "Select directory" if args.directory_selection else "Open file"),
                theme=args.theme,
                width=(76 if args.width is None else args.width),
                height=(24 if args.height is None else args.height),
                directory=args.directory_selection,
            );
            if result.accepted:
                _write_value(result.value);
            return int(result.status);
        if args.list:
            result = choose_list(
                args.items,
                title=_mode_title(args, "Select"),
                text=args.text,
                theme=args.theme,
                width=(60 if args.width is None else args.width),
                height=(18 if args.height is None else args.height),
                default=args.default,
                timeout=timeout,
            );
            if result.accepted:
                _write_value(result.value);
            return int(result.status);
        if args.radiolist:
            result = choose_radio(
                args.items,
                title=_mode_title(args, "Select"),
                text=args.text,
                theme=args.theme,
                width=(60 if args.width is None else args.width),
                height=args.height,
                default=args.default,
                timeout=timeout,
            );
            if result.accepted:
                _write_value(result.value);
            return int(result.status);
        if args.checklist:
            result = choose_checklist(
                args.items,
                title=_mode_title(args, "Select"),
                text=args.text,
                theme=args.theme,
                width=(60 if args.width is None else args.width),
                height=args.height,
                selected=args.selected,
                separator=args.separator,
                timeout=timeout,
            );
            if result.accepted:
                _write_value(result.value);
            return int(result.status);
        if args.text_info or args.markdown:
            content = _text_source(args);
            result = show_text(
                content,
                title=_mode_title(args, "Markdown" if args.markdown else "Text"),
                theme=args.theme,
                width=(80 if args.width is None else args.width),
                height=(24 if args.height is None else args.height),
                markdown=args.markdown,
            );
            return int(result.status);
        return 2;
    except (OSError, RuntimeError) as exc:
        print("sumdialog: {}".format(exc), file=sys.stderr);
        return TERMINAL_ERROR;
    except ValueError as exc:
        parser.error(str(exc));
    return 2;


if __name__ == "__main__":
    raise SystemExit(main());
