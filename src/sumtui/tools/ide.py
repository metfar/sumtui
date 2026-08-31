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
"""Windowed Python/R/Bash/C/C++ source IDE built on the reusable sumTUI workspace.""";
import argparse;
import code;
import contextlib;
import io;
import os;
from pathlib import Path;
import queue;
import shlex;
import shutil;
import subprocess;
import sys;
import tempfile;
import threading;
import time;

from ..symbols import detect_language;
from ..widgets import Button, CommandWindow, CommandWindowPane, Dialog, FunctionAction, HBox, Label, Menu, MenuItem, Separator, TextInput, TextView, TextViewPane, VBox, Workspace, WorkspaceWindow;
from .edit import EditApp;


class _RSession:
    """Small persistent R process used by the direct command window.""";
    def __init__(self, executable=None):
        self.executable = executable or shutil.which("R");
        self.process = None;
        self.queue = queue.Queue();
        self.reader = None;
        self.counter = 0;
        self.lock = threading.Lock();

    @property
    def available(self):
        return bool(self.executable);

    @staticmethod
    def _quote(source):
        return str(source).replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n");

    def start(self):
        if self.process is not None and self.process.poll() is None:
            return self.process;
        if not self.executable:
            raise RuntimeError("R executable was not found in PATH");
        self.process = subprocess.Popen(
            [self.executable, "--vanilla", "--quiet", "--no-save", "--no-restore", "--slave"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        );
        def reader():
            for line in self.process.stdout:
                self.queue.put(line);
        self.reader = threading.Thread(target=reader, name="sumIDE-R-reader", daemon=True);
        self.reader.start();
        return self.process;

    def execute(self, source, timeout=30.0):
        with self.lock:
            process = self.start();
            self.counter += 1;
            marker = "__SUMIDE_R_DONE_{}__".format(self.counter);
            encoded = self._quote(source);
            command = (
                '.__sumide_expr <- try(parse(text="{}"), silent=TRUE); '
                'if (inherits(.__sumide_expr, "try-error")) {{ cat(as.character(.__sumide_expr), "\\n") }} '
                'else {{ for (.__sumide_e in .__sumide_expr) {{ .__sumide_v <- withVisible(eval(.__sumide_e, envir=.GlobalEnv)); if (.__sumide_v$visible) print(.__sumide_v$value) }} }}; '
                'cat("{}\\n"); flush.console()\n'
            ).format(encoded, marker);
            process.stdin.write(command);
            process.stdin.flush();
            lines = [];
            deadline = time.monotonic() + float(timeout);
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("R process exited with status {}".format(process.returncode));
                try:
                    line = self.queue.get(timeout=0.05);
                except queue.Empty:
                    continue;
                if line.rstrip("\r\n") == marker:
                    return "".join(lines);
                lines.append(line);
            raise TimeoutError("R direct command timed out");

    def close(self):
        process = self.process;
        self.process = None;
        if process is None:
            return False;
        try:
            if process.poll() is None:
                process.terminate();
                process.wait(timeout=1.0);
        except Exception:
            try: process.kill();
            except Exception: pass;
        return True;


class ScriptIDE(EditApp):
    """Common movable-window IDE for Python, R, Bash, C and C++ source files.""";
    def __init__(self, path=None, language="auto", theme=None, **kwargs):
        self._language_request = str(language or "auto").strip().lower();
        self.language = self._resolve_language(path, language);
        self._process = None;
        self._process_thread = None;
        self._process_queue = queue.Queue();
        self._process_done = False;
        self._process_returncode = None;
        self._temp_path = None;
        self._temp_output_path = None;
        self._direct_thread = None;
        self._direct_done = False;
        self._direct_output = "";
        self._direct_error = None;
        self._python_console = code.InteractiveConsole({"__name__": "__console__"});
        self._r_session = _RSession();
        super().__init__(path=path, theme=theme, **kwargs);
        self.ide_config = dict(self.config.get("ide", {})) if isinstance(self.config.get("ide", {}), dict) else {};
        self.output_view = TextView("Ready. F5 runs the current buffer.");
        self.command_view = CommandWindow(prompt=self._prompt(), on_submit=self._submit_direct);
        self.output_pane = TextViewPane(self.output_view);
        self.command_pane = CommandWindowPane(self.command_view);
        available_width = max(40, int(self.app.width));
        available_height = max(12, int(self.app.height) - 3);
        code_width = max(30, min(available_width - 2, int(available_width * 0.78)));
        code_height = max(9, min(available_height - 1, int(available_height * 0.72)));
        output_width = max(28, min(available_width - 4, int(available_width * 0.68)));
        output_height = max(7, min(available_height - 2, 10));
        command_width = max(28, min(available_width - 2, 44));
        command_height = max(7, min(available_height - 2, 11));
        self.code_window = WorkspaceWindow(self.panel.child, title=self._code_title(), name="code", left=1, top=0, width=code_width, height=code_height, content_style="viewer");
        self.output_window = WorkspaceWindow(self.output_pane, title="Output", name="output", left=3, top=max(1, available_height - output_height), width=output_width, height=output_height, content_style="viewer");
        self.command_window = WorkspaceWindow(self.command_pane, title="Command", name="command", left=max(0, available_width - command_width - 1), top=max(1, available_height - command_height - 1), width=command_width, height=command_height, content_style="command");
        self.workspace = Workspace(self.output_window, self.command_window, self.code_window);
        self.desktop.body = VBox(self.workspace, self.status, self.bar, sizes=[None, 1, 1]);
        self.app.set_root(self.desktop);
        self.workspace.activate(self.code_window);
        self.app.add_idle(self._poll_execution);
        self.menu.menus = self._menus();
        self._update_status("{} IDE".format(self.language.upper()));

    @staticmethod
    def _resolve_language(path, language):
        requested = str(language or "auto").strip().lower();
        aliases = {"py": "python", "python3": "python", "rscript": "r", "sh": "bash", "shell": "bash", "c++": "cpp", "cxx": "cpp", "cc": "cpp"};
        if requested not in ("", "auto"):
            resolved = aliases.get(requested, requested);
        else:
            resolved = detect_language(filename=str(path or ""));
            if resolved == "text":
                resolved = "python";
        if resolved not in ("python", "r", "bash", "c", "cpp"):
            raise ValueError("Unknown IDE language: {}".format(language));
        return resolved;

    def _prompt(self):
        return {"python": ">>> ", "r": "R> ", "bash": "$ ", "c": "sh> ", "cpp": "sh> "}.get(self.language, "> ");

    def _language_label(self):
        return {"python": "Python", "r": "R", "bash": "Bash", "c": "C", "cpp": "C++"}.get(self.language, self.language);

    def _code_title(self):
        name = self.document.path.name if self.document.path is not None else "Untitled";
        return "Code - {} [{}]".format(name, self._language_label());

    def _register_keybindings(self):
        super()._register_keybindings();
        self.keys.register("script.run", "Run / Stop", ["f5", "ctrl+r"], context="editor", callback=self.toggle_run);
        self.keys.register("menu.run", "Run menu", ["alt+r"], context="editor", callback=lambda: self.open_menu(6));
        self.keys.register("menu.help", "Help menu", ["alt+h"], context="editor", callback=lambda: self.open_menu(7));
        return self.keys;

    def _make_function_bar(self):
        bar = super()._make_function_bar();
        key = self.keys.primary("script.run");
        if key:
            bar.actions.insert(min(2, len(bar.actions)), FunctionAction(key, "Run/Stop", None));
        return bar;

    def _menus(self):
        menus = super()._menus();
        run_items = [
            MenuItem("Run / Stop current buffer", self.toggle_run, self._ks("script.run")),
            MenuItem("Clear output", self.clear_output),
        ];
        if self.language in ("c", "cpp"):
            run_items.insert(1, MenuItem("Build commands...", self.build_commands_dialog));
        run_menu = Menu("Run", run_items);
        options = next((menu for menu in menus if menu.title == "Options"), None);
        if options is not None and self.language in ("c", "cpp"):
            options.items.insert(0, MenuItem("C/C++ build commands...", self.build_commands_dialog));
            options.items.insert(1, Separator());
        help_index = next((index for index, menu in enumerate(menus) if menu.title == "Help"), len(menus));
        menus.insert(help_index, run_menu);
        return menus;

    def _menu_closed(self):
        if hasattr(self, "workspace") and self.workspace.active_window is not None:
            focus = self.workspace.active_window.primary_focus();
            if focus is not None:
                self.app.focus.set(focus);
                self.app.invalidate();
                return True;
        return super()._menu_closed();

    def _set_document(self, document):
        result = super()._set_document(document);
        if self._language_request in ("", "auto"):
            self.language = self._resolve_language(document.path, "auto");
            if hasattr(self, "command_view"):
                self.command_view.set_prompt(self._prompt());
        if hasattr(self, "code_window"):
            self.code_window.title = self._code_title();
        if hasattr(self, "menu"):
            self.menu.menus = self._menus();
        return result;

    def clear_output(self):
        self.output_view.set_text("");
        self.app.invalidate();
        return True;

    def _append_output(self, text):
        piece = str(text);
        if self.output_view.text == "Ready. F5 runs the current buffer.":
            self.output_view.set_text("");
        self.output_view.append_text(piece);
        return True;

    def _temporary_source(self):
        suffix = {"python": ".py", "r": ".R", "bash": ".sh", "c": ".c", "cpp": ".cpp"}[self.language];
        directory = self.document.path.parent if self.document.path is not None else Path.cwd();
        handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=suffix, prefix=".sumide-", dir=str(directory), delete=False);
        try:
            handle.write(self.editor.text);
            handle.flush();
            return Path(handle.name);
        finally:
            handle.close();

    def _runner_command(self, path):
        if self.language == "python":
            return [sys.executable, "-u", str(path)];
        if self.language == "r":
            executable = shutil.which("Rscript");
            if not executable:
                raise RuntimeError("Rscript was not found in PATH");
            return [executable, "--vanilla", str(path)];
        if self.language == "bash":
            executable = shutil.which("bash") or shutil.which("sh");
            if not executable:
                raise RuntimeError("bash/sh was not found in PATH");
            return [executable, str(path)];
        raise RuntimeError("{} uses the build command path".format(self._language_label()));

    def _build_defaults(self):
        return {
            "c_compile": 'cc -std=c17 -Wall -Wextra -O0 -g {source} -o {output}',
            "c_run": '{output}',
            "cpp_compile": 'c++ -std=c++17 -Wall -Wextra -O0 -g {source} -o {output}',
            "cpp_run": '{output}',
        };

    def _build_value(self, key):
        return str(self.ide_config.get(key, self._build_defaults()[key]));

    def _expanded_build(self, template, source, output):
        return str(template).format(source=shlex.quote(str(source)), output=shlex.quote(str(output)));

    def build_commands_dialog(self):
        defaults = self._build_defaults();
        entries = {key: TextInput(self._build_value(key)) for key in ("c_compile", "c_run", "cpp_compile", "cpp_run")};
        rows = [];
        labels = (("C compile", "c_compile"), ("C run", "c_run"), ("C++ compile", "cpp_compile"), ("C++ run", "cpp_run"));
        for label, key in labels:
            rows.append(HBox(Label(label), entries[key], sizes=[14, None]));
        def close(*_args):
            self.app.pop_modal();
            self.app.focus.set(self.editor);
            self.app.invalidate();
            return True;
        def save_values(*_args):
            for key, entry in entries.items():
                value = str(entry.value).strip();
                self.ide_config[key] = value or defaults[key];
            close();
            self._update_status("Build commands updated; Options -> Save configuration persists them.");
            return True;
        body = VBox(*rows, HBox(Button("OK", on_press=save_values, default=True, height=3), Button("Cancel", on_press=close, height=3), ratios=[1, 1]), sizes=[1, 1, 1, 1, None]);
        self.app.push_modal(Dialog(body, title="C/C++ build commands", width=90, height=13, on_cancel=close, shadow=True));
        self.app.focus.set(entries["c_compile"] if self.language == "c" else entries["cpp_compile"]);
        self.app.invalidate();
        return True;

    def save_config(self):
        self.config["ide"] = dict(self.ide_config);
        return super().save_config();

    def _start_process(self):
        path = self._temporary_source();
        cwd = str(self.document.path.parent if self.document.path is not None else Path.cwd());
        self._temp_path = path;
        self._temp_output_path = None;
        if self.language in ("c", "cpp"):
            output_path = Path(str(path) + ".out");
            self._temp_output_path = output_path;
            prefix = "c" if self.language == "c" else "cpp";
            compile_command = self._expanded_build(self._build_value(prefix + "_compile"), path, output_path);
            run_command = self._expanded_build(self._build_value(prefix + "_run"), path, output_path);
            shell = shutil.which("sh") or "/bin/sh";
            command = [shell, "-c", compile_command + " && " + run_command];
        else:
            command = self._runner_command(path);
        self._process_done = False;
        self._process_returncode = None;
        self._process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        );
        def reader():
            try:
                for line in self._process.stdout:
                    self._process_queue.put(line);
            finally:
                self._process_returncode = self._process.wait();
                self._process_done = True;
        self._process_thread = threading.Thread(target=reader, name="sumIDE-run", daemon=True);
        self._process_thread.start();
        return True;

    def run_program(self):
        if self._process is not None and self._process.poll() is None:
            self._update_status("Program already running. F5 stops it.");
            return True;
        self.output_view.set_text("--- Run {} ({}) ---\n".format(self.document.path.name if self.document.path is not None else "Untitled", self.language));
        self.workspace.show(self.output_window);
        try:
            self._start_process();
            self._update_status("Running {}. F5 stops; F6 switches windows.".format(self.language));
        except Exception as exc:
            self._append_output("Error: {}\n".format(exc));
            self._cleanup_process();
            self._update_status("Run failed");
        self.app.invalidate();
        return True;

    def stop_program(self):
        process = self._process;
        if process is None or process.poll() is not None:
            self._update_status("No program is running.");
            return True;
        try:
            process.terminate();
        except Exception:
            pass;
        self._update_status("Stopping program...");
        return True;

    def toggle_run(self):
        process = self._process;
        return self.stop_program() if process is not None and process.poll() is None else self.run_program();

    def _cleanup_process(self):
        path = self._temp_path;
        self._temp_path = None;
        self._process = None;
        self._process_thread = None;
        self._process_done = False;
        if path is not None:
            try: path.unlink();
            except OSError: pass;
        output_path = self._temp_output_path;
        self._temp_output_path = None;
        if output_path is not None:
            try: output_path.unlink();
            except OSError: pass;
        return True;

    def _python_direct(self, source):
        stream = io.StringIO();
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            more = self._python_console.push(source);
        return stream.getvalue(), more;

    def _run_shell_direct(self, command):
        completed = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", check=False);
        output = str(completed.stdout or "");
        if completed.returncode != 0:
            output += "[shell exit {}]\n".format(completed.returncode);
        return output;

    def _direct_worker(self, source):
        try:
            if source.lstrip().startswith("!"):
                output = self._run_shell_direct(source.lstrip()[1:]);
                more = False;
            elif self.language == "python":
                output, more = self._python_direct(source);
            elif self.language == "r":
                output = self._r_session.execute(source);
                more = False;
            else:
                output = self._run_shell_direct(source);
                more = False;
            self._direct_output = output;
            if self.language == "python":
                self.command_view.set_prompt("... " if more else ">>> ");
        except Exception as exc:
            self._direct_error = exc;
        finally:
            self._direct_done = True;
        return None;

    def _submit_direct(self, line, window):
        source = str(line or "");
        if self._process is not None and self._process.poll() is None:
            window.write_error("A program is running; stop it before using direct mode.");
            return None;
        if self._direct_thread is not None and self._direct_thread.is_alive():
            window.write_error("A direct command is already running.");
            return None;
        self._direct_output = "";
        self._direct_error = None;
        self._direct_done = False;
        if not self.app.running:
            self._direct_worker(source);
            self._finish_direct();
            return None;
        self._direct_thread = threading.Thread(target=self._direct_worker, args=(source,), name="sumIDE-direct", daemon=True);
        self._direct_thread.start();
        self._update_status("Direct {} command running...".format(self.language));
        return None;

    def _finish_direct(self):
        if self._direct_output:
            for line in self._direct_output.rstrip("\n").splitlines():
                self.command_view.write(line, style="command");
        if self._direct_error is not None:
            self.command_view.write_error("Error: {}".format(self._direct_error));
            self._update_status("Direct command error");
        else:
            self._update_status("Direct command complete");
        self._direct_thread = None;
        self._direct_done = False;
        self.app.invalidate();
        return True;

    def _poll_execution(self):
        dirty = False;
        while True:
            try:
                piece = self._process_queue.get_nowait();
            except queue.Empty:
                break;
            self._append_output(piece);
            dirty = True;
        if self._process_done:
            code_value = self._process_returncode;
            self._append_output("--- exit {} ---\n".format(code_value));
            self._update_status("Run complete" if code_value == 0 else "Run failed (exit {})".format(code_value));
            self._cleanup_process();
            dirty = True;
        if self._direct_done:
            self._finish_direct();
            dirty = True;
        return dirty;

    def _quit_now(self):
        self.stop_program();
        self._r_session.close();
        return super()._quit_now();


def _main(argv=None, forced_language=None, prog="sumide"):
    parser = argparse.ArgumentParser(prog=prog, description="Movable-window Python/R/Bash/C/C++ IDE built with sumTUI");
    parser.add_argument("file", nargs="?", help="source file");
    parser.add_argument("--language", choices=("auto", "python", "r", "bash", "c", "cpp"), default=forced_language or "auto", help="language profile (default: auto by extension)");
    parser.add_argument("--theme", default=None, help="sumTUI theme");
    args = parser.parse_args(argv);
    language = forced_language or args.language;
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("{} requires an interactive terminal".format(prog), file=sys.stderr);
        return 2;
    try:
        return ScriptIDE(args.file, language=language, theme=args.theme).run();
    except Exception as exc:
        print("{}: {}".format(prog, exc), file=sys.stderr);
        return 1;


def main(argv=None):
    return _main(argv=argv, forced_language=None, prog="sumide");


def main_python(argv=None):
    return _main(argv=argv, forced_language="python", prog="sumpyide");


def main_r(argv=None):
    return _main(argv=argv, forced_language="r", prog="sumride");


def main_bash(argv=None):
    return _main(argv=argv, forced_language="bash", prog="sumbashide");


def main_c(argv=None):
    return _main(argv=argv, forced_language="c", prog="sumcide");


def main_cpp(argv=None):
    return _main(argv=argv, forced_language="cpp", prog="sumcppide");


if __name__ == "__main__":
    raise SystemExit(main());
