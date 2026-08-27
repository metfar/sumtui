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
import os;
import re;
import sys;
import time;

from ..events import Key, KeyEvent;


ANSI_KEYS = {
    b"\x1b[A": Key.UP,
    b"\x1b[B": Key.DOWN,
    b"\x1b[C": Key.RIGHT,
    b"\x1b[D": Key.LEFT,
    b"\x1b[H": Key.HOME,
    b"\x1b[F": Key.END,
    b"\x1bOH": Key.HOME,
    b"\x1bOF": Key.END,
    b"\x1b[2~": Key.INSERT,
    b"\x1b[3~": Key.DELETE,
    b"\x1b[5~": Key.PAGE_UP,
    b"\x1b[6~": Key.PAGE_DOWN,
    b"\x1bOP": Key.F1,
    b"\x1bOQ": Key.F2,
    b"\x1bOR": Key.F3,
    b"\x1bOS": Key.F4,
    b"\x1b[15~": Key.F5,
    b"\x1b[17~": Key.F6,
    b"\x1b[18~": Key.F7,
    b"\x1b[19~": Key.F8,
    b"\x1b[20~": Key.F9,
    b"\x1b[21~": Key.F10,
    b"\x1b[23~": Key.F11,
    b"\x1b[24~": Key.F12,
};


ANSI_MOD_KEYS = {
    b"\x1b[1;2A": (Key.UP, False, False, True),
    b"\x1b[1;2B": (Key.DOWN, False, False, True),
    b"\x1b[1;2C": (Key.RIGHT, False, False, True),
    b"\x1b[1;2D": (Key.LEFT, False, False, True),
    b"\x1b[5;2~": (Key.PAGE_UP, False, False, True),
    b"\x1b[6;2~": (Key.PAGE_DOWN, False, False, True),
    b"\x1b[5$": (Key.PAGE_UP, False, False, True),
    b"\x1b[6$": (Key.PAGE_DOWN, False, False, True),
    b"\x1b[1;5A": (Key.UP, True, False, False),
    b"\x1b[1;5B": (Key.DOWN, True, False, False),
    b"\x1b[1;5C": (Key.RIGHT, True, False, False),
    b"\x1b[1;5D": (Key.LEFT, True, False, False),
    b"\x1b[1;6A": (Key.UP, True, False, True),
    b"\x1b[1;6B": (Key.DOWN, True, False, True),
    b"\x1b[1;6C": (Key.RIGHT, True, False, True),
    b"\x1b[1;6D": (Key.LEFT, True, False, True),
    # rxvt/urxvt-style shifted cursor keys.  Some terminals advertise only
    # part of these in terminfo, so keep the historical sequences as explicit
    # fallbacks as well.
    b"\x1b[a": (Key.UP, False, False, True),
    b"\x1b[b": (Key.DOWN, False, False, True),
    b"\x1b[c": (Key.RIGHT, False, False, True),
    b"\x1b[d": (Key.LEFT, False, False, True),
    b"\x1b[7$": (Key.HOME, False, False, True),
    b"\x1b[8$": (Key.END, False, False, True),
};

ANSI_SHIFT_TAB = b"\x1b[Z";


_XTERM_MODIFIERS = {
    2: (False, False, True),
    3: (False, True, False),
    4: (False, True, True),
    5: (True, False, False),
    6: (True, False, True),
    7: (True, True, False),
    8: (True, True, True),
};

_XTERM_TILDE_KEYS = {
    1: Key.HOME, 2: Key.INSERT, 3: Key.DELETE, 4: Key.END, 5: Key.PAGE_UP, 6: Key.PAGE_DOWN, 7: Key.HOME, 8: Key.END,
    15: Key.F5, 17: Key.F6, 18: Key.F7, 19: Key.F8, 20: Key.F9,
    21: Key.F10, 23: Key.F11, 24: Key.F12,
};

_XTERM_SS3_FUNCTION_KEYS = {"P": Key.F1, "Q": Key.F2, "R": Key.F3, "S": Key.F4};
_XTERM_CSI_FINAL_KEYS = {"A": Key.UP, "B": Key.DOWN, "C": Key.RIGHT, "D": Key.LEFT, "H": Key.HOME, "F": Key.END};


class AnsiDecoder:
    def __init__(self, escape_timeout=0.035, extra_sequences=None):
        self.buffer = b"";
        self.escape_timeout = float(escape_timeout);
        self.escape_since = None;
        self.extra_sequences = {};
        for sequence, spec in dict(extra_sequences or {}).items():
            self.extra_sequences[bytes(sequence)] = spec;

    def add_sequence(self, sequence, key, ctrl=False, alt=False, shift=False):
        if sequence:
            self.extra_sequences[bytes(sequence)] = (key, bool(ctrl), bool(alt), bool(shift));
        return self;

    def feed(self, data, now=None):
        if data:
            self.buffer += bytes(data);
        return self._decode(time.monotonic() if now is None else float(now));

    def flush(self, now=None):
        return self._decode(time.monotonic() if now is None else float(now), flush=True);

    def _decode(self, now, flush=False):
        output = [];
        while self.buffer:
            if self.buffer.startswith(b"\x1b"):
                event = self._consume_escape(now, flush);
                if event is None:
                    break;
                if event is not False:
                    output.append(event);
                continue;
            event = self._consume_plain();
            if event is None:
                break;
            output.append(event);
        return output;

    def _consume_escape(self, now, flush):
        if self.buffer == ANSI_SHIFT_TAB:
            self.buffer = self.buffer[len(ANSI_SHIFT_TAB):];
            self.escape_since = None;
            return KeyEvent(Key.TAB, shift=True);
        modified_sequences = dict(ANSI_MOD_KEYS);
        modified_sequences.update(self.extra_sequences);
        for sequence, spec in sorted(modified_sequences.items(), key=lambda item: len(item[0]), reverse=True):
            if self.buffer.startswith(sequence):
                self.buffer = self.buffer[len(sequence):];
                self.escape_since = None;
                key, ctrl, alt, shift = spec;
                return KeyEvent(key, ctrl=ctrl, alt=alt, shift=shift);
        for sequence, key in sorted(ANSI_KEYS.items(), key=lambda item: len(item[0]), reverse=True):
            if self.buffer.startswith(sequence):
                self.buffer = self.buffer[len(sequence):];
                self.escape_since = None;
                return KeyEvent(key);
        modified = self._consume_xterm_modified_key();
        if modified is not None:
            self.escape_since = None;
            return modified;
        known_sequences = list(ANSI_MOD_KEYS) + list(self.extra_sequences) + list(ANSI_KEYS) + [ANSI_SHIFT_TAB];
        if any(sequence.startswith(self.buffer) for sequence in known_sequences):
            if self.escape_since is None:
                self.escape_since = now;
            if not flush and now - self.escape_since < self.escape_timeout:
                return None;
        if len(self.buffer) >= 2 and self.buffer[1:2] not in (b"[", b"O"):
            self.buffer = self.buffer[1:];
            self.escape_since = None;
            event = self._consume_plain();
            if event is None:
                return KeyEvent(Key.ESCAPE);
            return KeyEvent(event.key, event.text, event.ctrl, True, event.shift);
        if len(self.buffer) == 1:
            if self.escape_since is None:
                self.escape_since = now;
            if not flush and now - self.escape_since < self.escape_timeout:
                return None;
            self.buffer = b"";
            self.escape_since = None;
            return KeyEvent(Key.ESCAPE);
        end = self._escape_sequence_end(self.buffer);
        if end is not None:
            self.buffer = self.buffer[end:];
            self.escape_since = None;
            return False;
        if flush:
            self.buffer = self.buffer[1:];
            self.escape_since = None;
            return KeyEvent(Key.ESCAPE);
        return None;

    def _consume_xterm_modified_key(self):
        match = re.match(br"^\x1b\[(\d+);([2-8])~", self.buffer);
        if match:
            code = int(match.group(1));
            modifier = int(match.group(2));
            key = _XTERM_TILDE_KEYS.get(code);
            if key is not None:
                self.buffer = self.buffer[match.end():];
                ctrl, alt, shift = _XTERM_MODIFIERS[modifier];
                return KeyEvent(key, ctrl=ctrl, alt=alt, shift=shift);
        match = re.match(br"^\x1b\[1;([2-8])([ABCDHF])", self.buffer);
        if match:
            modifier = int(match.group(1));
            key = _XTERM_CSI_FINAL_KEYS.get(match.group(2).decode("ascii"));
            if key is not None:
                self.buffer = self.buffer[match.end():];
                ctrl, alt, shift = _XTERM_MODIFIERS[modifier];
                return KeyEvent(key, ctrl=ctrl, alt=alt, shift=shift);
        match = re.match(br"^\x1b\[1;([2-8])([PQRS])", self.buffer);
        if match:
            modifier = int(match.group(1));
            key = _XTERM_SS3_FUNCTION_KEYS.get(match.group(2).decode("ascii"));
            if key is not None:
                self.buffer = self.buffer[match.end():];
                ctrl, alt, shift = _XTERM_MODIFIERS[modifier];
                return KeyEvent(key, ctrl=ctrl, alt=alt, shift=shift);
        return None;

    @staticmethod
    def _escape_sequence_end(buffer):
        for index, value in enumerate(buffer[2:], start=2):
            if 0x40 <= value <= 0x7e:
                return index + 1;
        return None;

    def _consume_plain(self):
        first = self.buffer[0];
        if first in (10, 13):
            self.buffer = self.buffer[1:];
            return KeyEvent(Key.ENTER);
        if first == 9:
            self.buffer = self.buffer[1:];
            return KeyEvent(Key.TAB);
        if first in (8, 127):
            self.buffer = self.buffer[1:];
            return KeyEvent(Key.BACKSPACE);
        if first == 32:
            self.buffer = self.buffer[1:];
            return KeyEvent(Key.SPACE, text=" ");
        if 1 <= first <= 26:
            self.buffer = self.buffer[1:];
            key = chr(ord("a") + first - 1);
            return KeyEvent(key, ctrl=True);
        length = self._utf8_length(first);
        if len(self.buffer) < length:
            return None;
        raw = self.buffer[:length];
        try:
            text = raw.decode("utf-8");
        except UnicodeDecodeError:
            self.buffer = self.buffer[1:];
            return KeyEvent("unknown");
        self.buffer = self.buffer[length:];
        return KeyEvent(text.lower(), text=text);

    @staticmethod
    def _utf8_length(first):
        if first < 0x80:
            return 1;
        if 0xc0 <= first < 0xe0:
            return 2;
        if 0xe0 <= first < 0xf0:
            return 3;
        if 0xf0 <= first < 0xf8:
            return 4;
        return 1;


def _terminfo_shift_sequences(fd=None):
    """Return modified-key sequences advertised by the active terminfo entry.

    Shifted cursor/page keys are unfortunately not encoded identically by all
    terminal families.  Querying terminfo gives sumTUI the user's actual TERM
    conventions instead of assuming xterm, while the static decoder table still
    covers common xterm/rxvt fallbacks.
    """
    capabilities = {
        "kri": (Key.UP, False, False, True),
        "kind": (Key.DOWN, False, False, True),
        "kLFT": (Key.LEFT, False, False, True),
        "kRIT": (Key.RIGHT, False, False, True),
        "kPRV": (Key.PAGE_UP, False, False, True),
        "kNXT": (Key.PAGE_DOWN, False, False, True),
        "kHOM": (Key.HOME, False, False, True),
        "kEND": (Key.END, False, False, True),
    };
    found = {};
    try:
        import curses;
        kwargs = {};
        if fd is not None:
            kwargs["fd"] = int(fd);
        curses.setupterm(**kwargs);
        for capability, spec in capabilities.items():
            sequence = curses.tigetstr(capability);
            if sequence:
                found[bytes(sequence)] = spec;
    except Exception:
        return {};
    return found;


class PosixInput:
    def __init__(self, capture_control_keys=False):
        self.fd = None;
        self.saved = None;
        self.decoder = AnsiDecoder();
        self.capture_control_keys = bool(capture_control_keys);

    def __enter__(self):
        import termios;
        import tty;
        self.fd = sys.stdin.fileno();
        if not os.isatty(self.fd):
            raise RuntimeError("sumTUI requires an interactive terminal for input");
        self.saved = termios.tcgetattr(self.fd);
        for sequence, spec in _terminfo_shift_sequences(self.fd).items():
            key, ctrl, alt, shift = spec;
            self.decoder.add_sequence(sequence, key, ctrl=ctrl, alt=alt, shift=shift);
        tty.setcbreak(self.fd);
        if self.capture_control_keys:
            current = termios.tcgetattr(self.fd);
            current[0] &= ~getattr(termios, "IXON", 0);
            current[0] &= ~getattr(termios, "IXOFF", 0);
            current[3] &= ~getattr(termios, "ISIG", 0);
            termios.tcsetattr(self.fd, termios.TCSANOW, current);
        return self;

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fd is not None and self.saved is not None:
            import termios;
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved);
        return False;

    def read_events(self, timeout=0.05):
        import select;
        ready, _, _ = select.select([self.fd], [], [], max(0.0, float(timeout)));
        output = [];
        if ready:
            output.extend(self.decoder.feed(os.read(self.fd, 128)));
        output.extend(self.decoder.feed(b""));
        return output;


class WindowsInput:
    _SPECIAL = {
        "H": Key.UP, "P": Key.DOWN, "K": Key.LEFT, "M": Key.RIGHT,
        "G": Key.HOME, "O": Key.END, "I": Key.PAGE_UP, "Q": Key.PAGE_DOWN,
        "R": Key.INSERT, "S": Key.DELETE,
        ";": Key.F1, "<": Key.F2, "=": Key.F3, ">": Key.F4,
        "?": Key.F5, "@": Key.F6, "A": Key.F7, "B": Key.F8,
        "C": Key.F9, "D": Key.F10, "\x85": Key.F11, "\x86": Key.F12,
    };

    def __enter__(self):
        return self;

    def __exit__(self, exc_type, exc_value, traceback):
        return False;

    @staticmethod
    def _modifiers():
        try:
            import ctypes;
            state = ctypes.windll.user32.GetKeyState;
            return bool(state(0x11) & 0x8000), bool(state(0x12) & 0x8000), bool(state(0x10) & 0x8000);
        except Exception:
            return False, False, False;

    def read_events(self, timeout=0.05):
        import msvcrt;
        deadline = time.monotonic() + max(0.0, float(timeout));
        while not msvcrt.kbhit() and time.monotonic() < deadline:
            time.sleep(0.005);
        output = [];
        while msvcrt.kbhit():
            char = msvcrt.getwch();
            ctrl, alt, shift = self._modifiers();
            if char in ("\x00", "\xe0"):
                code = msvcrt.getwch();
                key = self._SPECIAL.get(code, "unknown");
                output.append(KeyEvent(key, ctrl=ctrl, alt=alt, shift=shift));
                continue;
            output.append(_windows_char_event(char, ctrl, alt, shift));
        return output;


def _windows_char_event(char, ctrl=False, alt=False, shift=False):
    if char in ("\r", "\n"):
        return KeyEvent(Key.ENTER, ctrl=ctrl, alt=alt, shift=shift);
    if char == "\t":
        return KeyEvent(Key.TAB, ctrl=ctrl, alt=alt, shift=shift);
    if char in ("\x08", "\x7f"):
        return KeyEvent(Key.BACKSPACE, ctrl=ctrl, alt=alt, shift=shift);
    if char == " ":
        return KeyEvent(Key.SPACE, text=" ", ctrl=ctrl, alt=alt, shift=shift);
    value = ord(char) if char else 0;
    if 1 <= value <= 26:
        return KeyEvent(chr(ord("a") + value - 1), ctrl=True, alt=alt, shift=shift);
    return KeyEvent(char.lower(), text=char, ctrl=ctrl, alt=alt, shift=shift);


def create_input_backend(capture_control_keys=False):
    if os.name == "nt":
        return WindowsInput();
    return PosixInput(capture_control_keys=capture_control_keys);
