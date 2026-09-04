import io;
from sumui import CursorState;
from sumtui import TerminalTextScreen;


def test_terminal_textscreen_dynamic_size_and_cursor_sequences():
    size=[80,25]; stream=io.StringIO(); screen=TerminalTextScreen(stream=stream,size_provider=lambda: tuple(size));
    assert screen.size()==(80,25);
    size[:]=[41,17]; assert screen.size()==(41,17);
    screen.cursor(CursorState.HIDDEN); screen.cursor(CursorState.NORMAL); screen.cursor(CursorState.BLOCK);
    rendered=stream.getvalue();
    assert "\x1b[?25l" in rendered;
    assert "\x1b[4 q" in rendered;
    assert "\x1b[2 q" in rendered;
