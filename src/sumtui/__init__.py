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
__version__ = "0.5.16";

from .app import Application, FocusManager;
from .events import Key, KeyEvent, MouseEvent, ResizeEvent, normalize_key_spec;
from .inputmask import InputMask, parse_input_mask;
from .keybindings import KeyBindingAction, KeyBindingManager, format_key_spec;
from .dialogs import DialogResult, FormFieldSpec, MenuItemSpec, ask_question, choose_checklist, choose_file, choose_list, choose_menu, choose_radio, read_entry, read_form, show_message, show_progress_demo, show_text;
from .dialogspec import DialogSpec, load_dialog_spec, parse_dialog_spec;
from .prompt import InputResult, InputSpec, read_input;
from .syntax import EditorSyntaxHighlighter, ExtendedBasicLexer, GenericLogLexer, SumXLexer, SYNTAX_MODES, detect_mode, mode_label, normalize_mode, semantic_role;
from .theme import BUILTIN_THEME_NAMES, C64_COLORS, DEFAULT_THEME, DOS_COLORS, MSX_COLORS, SPECTRUM_COLORS, THEME_EDIT_ROLES, THEMES, Theme, available_theme_names, load_theme_file, load_user_themes, make_theme, refresh_user_themes, save_user_theme, theme_from_dict, theme_to_dict, user_theme_dir;
from .widgets import BrowseForm, Button, CheckBox, Choice, Column, ComboBox, CommandWindow, ScreenField, ContextMenu, Dialog, DirectoryDialog, FileDialog, FormField, FunctionAction, FunctionBar, GroupBox, HBox, HexView, Label, LayoutItem, ListView, MarkdownView, SyntaxView, Menu, MenuBar, MenuDesktop, MenuItem, Panel, ProgressBar, RadioButton, RadioGroup, ReadOnlyField, RecordForm, ScrollBar, Separator, Slider, Splitter, StatusBar, TableRow, TableView, TextInput, TextArea, TextEditor, TextView, TreeNode, TreeView, VBox, Widget;

__all__ = [
    "__version__", "Application", "FocusManager",
    "Key", "KeyEvent", "MouseEvent", "ResizeEvent", "normalize_key_spec",
    "InputMask", "parse_input_mask", "InputSpec", "InputResult", "read_input",
    "DialogResult", "FormFieldSpec", "MenuItemSpec", "DialogSpec", "show_message", "ask_question", "read_entry", "read_form", "choose_file", "choose_list", "choose_menu", "choose_radio", "choose_checklist", "show_text", "show_progress_demo", "parse_dialog_spec", "load_dialog_spec",
    "KeyBindingAction", "KeyBindingManager", "format_key_spec",
    "EditorSyntaxHighlighter", "ExtendedBasicLexer", "GenericLogLexer", "SumXLexer", "SYNTAX_MODES",
    "detect_mode", "mode_label", "normalize_mode", "semantic_role",
    "Theme", "make_theme", "THEMES", "DEFAULT_THEME", "BUILTIN_THEME_NAMES", "THEME_EDIT_ROLES",
    "theme_to_dict", "theme_from_dict", "load_theme_file", "load_user_themes", "refresh_user_themes",
    "save_user_theme", "user_theme_dir", "available_theme_names",
    "SPECTRUM_COLORS", "DOS_COLORS", "C64_COLORS", "MSX_COLORS",
    "Widget", "Label", "Panel", "StatusBar", "CommandWindow", "ScreenField", "Dialog", "GroupBox",
    "FormField", "ReadOnlyField", "RecordForm", "BrowseForm",
    "Button", "TextInput", "TextArea", "TextEditor", "CheckBox", "RadioButton", "RadioGroup", "Choice", "ComboBox",
    "ProgressBar", "Slider", "ScrollBar", "TextView", "MarkdownView", "SyntaxView", "HexView",
    "FunctionAction", "FunctionBar", "MenuItem", "Separator", "Menu", "MenuBar", "MenuDesktop", "ContextMenu",
    "HBox", "VBox", "LayoutItem", "Splitter", "Column", "TableRow", "TableView", "ListView",
    "TreeNode", "TreeView", "FileDialog", "DirectoryDialog",
];
