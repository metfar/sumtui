#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018-2026 William Martinez Bas <metfar@gmail.com>
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
import io;

from rich.console import Console;

from sumtui.helpbrowser import HelpBrowser;
from sumtui.helpdb import HelpCorpus, HelpTopic;


def _corpus():
    return HelpCorpus("Test Help",(
        HelpTopic("CD","Navigation","Change directory.",( "cd DIR",),"cd work",see_also=("PWD",),aliases=("chdir",),language="bash"),
        HelpTopic("GREP","Commands","Search text.",( "grep PATTERN FILE",),"grep TODO *.py",aliases=("egrep","fgrep"),language="bash"),
        HelpTopic("PWD","Navigation","Print directory.",( "pwd -P",),"pwd -P",language="bash"),
    ),intro="Browser test.");


def _browser(topic=None,query=""):
    console=Console(file=io.StringIO(),force_terminal=True,width=100,height=30);
    return HelpBrowser(_corpus(),title="Test Help",topic=topic,query=query,theme="DOS",console=console);


def test_help_browser_filters_topics_and_renders_selection():
    browser=_browser();
    assert set(browser.visible)=={"CD","GREP","PWD"};
    browser.query.set("grep");
    assert browser.visible==["GREP"];
    assert browser.current_topic=="GREP";
    assert "Search text" in browser.view.markdown;


def test_help_browser_selects_alias_and_restores_full_topic_list():
    browser=_browser(query="grep");
    assert browser.visible==["GREP"];
    assert browser.select_topic("chdir") is True;
    assert set(browser.visible)=={"CD","GREP","PWD"};
    assert browser.current_topic=="CD";
    assert "Change directory" in browser.view.markdown;


def test_help_browser_contents_and_focus_shortcuts():
    browser=_browser(topic="PWD");
    assert browser.current_topic=="PWD";
    browser.show_contents();
    assert browser.current_topic is None;
    assert "Test Help" in browser.view.markdown;
    assert browser.focus_search() is True;
    assert browser.app.focus.current is browser.query;
    assert browser.focus_topic() is True;
    assert browser.app.focus.current is browser.view;


def test_help_browser_groups_topics_and_uses_short_leaf_labels():
    browser=_browser();
    roots=browser.topics.roots;
    assert [node.label for node in roots]==["Commands","Navigation"];
    commands=roots[0]; navigation=roots[1];
    assert [node.label for node in commands.children]==["GREP"];
    assert [node.label for node in navigation.children]==["CD","PWD"];
    assert browser.breadcrumb.text in ("Contents","Commands > GREP","Navigation > CD","Navigation > PWD");


def test_help_browser_mouse_focus_follows_the_pane_under_pointer():
    browser=_browser();
    browser.app.console.print(browser.app.root);
    from sumtui.events import MouseEvent;
    assert browser.app.focus.current is browser.topics;
    assert browser.app.dispatch(MouseEvent(50,5,button="left",action="press")) is True;
    assert browser.app.focus.current is browser.view;
    assert browser.app.dispatch(MouseEvent(10,7,button="left",action="press")) is True;
    assert browser.app.focus.current is browser.topics;


def test_help_browser_both_panes_support_horizontal_scroll():
    from sumtui.events import Key, KeyEvent, MouseEvent;
    corpus=HelpCorpus("Wide Help",(
        HelpTopic("THIS_IS_A_VERY_LONG_TOPIC_NAME","Category With A Long Name","Wide summary.",( "wide --option",),"wide --option",language="bash"),
    ),intro="A very wide contents line that should be horizontally scrollable rather than silently cropped.");
    console=Console(file=io.StringIO(),force_terminal=True,width=70,height=20);
    browser=HelpBrowser(corpus,title="Wide Help",theme="DOS",console=console);
    console.print(browser.app.root);
    assert browser.topics.max_x_offset > 0;
    assert browser.view.max_x_offset > 0;
    assert browser.topics.handle_event(KeyEvent(Key.RIGHT)) is True;
    assert browser.topics.x_offset==1;
    assert browser.topics.handle_event(MouseEvent(0,0,action="scroll_down",shift=True)) is True;
    assert browser.topics.x_offset>1;
    browser.app.focus.set(browser.view);
    assert browser.view.handle_event(KeyEvent(Key.RIGHT)) is True;
    assert browser.view.x_offset==1;
