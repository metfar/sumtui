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
