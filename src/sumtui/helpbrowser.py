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
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
"""Reusable classic two-pane help browser for SUM applications.

The document model intentionally stays outside this module.  Any corpus that
provides ``topics``, ``find_topic()`` and ``index_markdown()`` can be used; in
normal SUM builds the editable Markdown/helpdb model is owned by SumDoc while
sumTUI only renders the compiled runtime data.
""";

from .app import Application;
from .widgets import FunctionAction, FunctionBar, HBox, Label, MarkdownView, MarkdownViewPane, Panel, StatusBar, TextInput, TreeNode, TreeView, TreeViewPane, VBox;


class HelpBrowser:
    """Keyboard-first help browser inspired by classic DOS help systems.""";

    def __init__(self,corpus,title=None,topic=None,query="",theme="DOS",console=None):
        self.corpus=corpus;
        self.title=str(title or getattr(corpus,"title","SUM Help"));
        self.visible=[];
        self.current_topic=None;
        self.query=TextInput(str(query or ""),placeholder="Search topics...");
        self.topics=TreeView([],select_leaves_only=True);
        self.view=MarkdownView(self.corpus.index_markdown(),wrap=False);
        self.topic_pane=MarkdownViewPane(view=self.view);
        self.topic_list=TreeViewPane(self.topics);
        self.breadcrumb=Label("Contents",style="muted");
        self.status=StatusBar("Ready");
        self.functions=FunctionBar([
            FunctionAction("f1","Contents",self.show_contents),
            FunctionAction("f2","Topics",self.focus_topics),
            FunctionAction("f3","Search",self.focus_search),
            FunctionAction("f4","Read",self.focus_topic),
            FunctionAction("escape","Close",self.close),
        ]);
        left=VBox(self.query,self.topic_list,sizes=[1,None],use_preferred_sizes=False);
        right=VBox(self.breadcrumb,self.topic_pane,sizes=[1,None],use_preferred_sizes=False);
        center=HBox(Panel(left,title="Help topics"),Panel(right,title="Topic"),sizes=[32,None],use_preferred_sizes=False);
        root=VBox(center,self.status,self.functions,sizes=[None,1,1],use_preferred_sizes=False);
        self.app=Application(title=self.title,root=root,theme=theme,console=console,capture_control_keys=True,mouse=True);
        self.functions.install(self.app);
        self.app.bind("ctrl+f",self.focus_search);
        self.app.bind("alt+left",self.focus_topics);
        self.app.bind("ctrl+home",self.show_contents);
        self.topics.on_change=self._topic_changed;
        self.topics.on_activate=lambda _node:self.focus_topic();
        self.query.on_change=self.refill;
        self.refill(self.query.value);
        if topic:
            if not self.select_topic(topic):
                self.query.set(str(topic));
                self.refill(str(topic));
        else:
            self.show_contents(focus=False);
        self.app.focus.set(self.topics);

    def _ordered_topics(self):
        return sorted(self.corpus.topics,key=lambda item:(item.category.casefold(),item.name.casefold()));

    @staticmethod
    def _topic_roots(topics):
        roots=[];
        current_category=None;
        current_root=None;
        for topic in topics:
            category=str(topic.category or "Other");
            if current_root is None or category!=current_category:
                current_category=category;
                current_root=TreeNode(category,value=None,expanded=True);
                roots.append(current_root);
            current_root.add(TreeNode(str(topic.name),value=topic.name));
        return roots;

    def _topic_changed(self,node):
        if node is not None and node.value is not None:
            return self.render_topic(node.value);
        return False;

    def refill(self,text=""):
        needle=str(text or "").strip().casefold();
        matches=[];
        for topic in self._ordered_topics():
            haystack=" ".join((topic.name,topic.category,topic.summary," ".join(topic.aliases)," ".join(topic.see_also))).casefold();
            if needle and needle not in haystack:
                continue;
            matches.append(topic);
        self.visible=[topic.name for topic in matches];
        self.topics.set_roots(self._topic_roots(matches));
        if self.visible:
            if not self.topics.select_value(self.visible[0]):
                self.render_topic(self.visible[0]);
            else:
                self.render_topic(self.visible[0]);
            self.status.set("{} topic{}".format(len(self.visible),"" if len(self.visible)==1 else "s"));
        else:
            self.current_topic=None;
            self.view.set_text("# No help topics found\n\nSearch: `{}`".format(text));
            self.breadcrumb.set_text("Search > No matches");
            self.status.set("No topics match '{}'".format(text));
        self.app.invalidate();
        return True;

    def render_topic(self,name=None):
        topic=self.corpus.find_topic(name) if name else None;
        self.current_topic=topic.name if topic is not None else None;
        self.view.set_text(topic.markdown() if topic is not None else self.corpus.index_markdown());
        if topic is not None:
            crumb="{} > {}".format(topic.category,topic.name);
            self.breadcrumb.set_text(crumb);
            self.status.set(crumb);
        else:
            self.breadcrumb.set_text("Contents");
            self.status.set("Contents");
        self.app.invalidate();
        return True;

    def select_topic(self,name):
        topic=self.corpus.find_topic(name);
        if topic is None:
            return False;
        if topic.name not in self.visible:
            self.query.set("");
            self.refill("");
        if not self.topics.select_value(topic.name):
            return False;
        self.render_topic(topic.name);
        return True;

    def show_contents(self,*_args,focus=True):
        self.current_topic=None;
        self.view.set_text(self.corpus.index_markdown());
        self.breadcrumb.set_text("Contents");
        self.status.set("Contents");
        if focus:
            self.app.focus.set(self.topics);
        self.app.invalidate();
        return True;

    def focus_topics(self,*_args):
        self.app.focus.set(self.topics);
        self.status.set("Topics: arrows move, Enter reads, Left/Right scroll horizontally");
        self.app.invalidate();
        return True;

    def focus_search(self,*_args):
        self.app.focus.set(self.query);
        self.status.set("Search: type to filter, Tab returns to topics");
        self.app.invalidate();
        return True;

    def focus_topic(self,*_args):
        self.app.focus.set(self.view);
        self.status.set("Read: drag/Shift+arrows selects, Ctrl+C/Ctrl+Ins copies, right-click opens menu");
        self.app.invalidate();
        return True;

    def close(self,*_args):
        self.app.stop();
        return True;

    def run(self,backend="tui"):
        return self.app.run(backend=backend);


def run_help_browser(corpus,title=None,topic=None,query="",theme="DOS",console=None,backend="tui"):
    browser=HelpBrowser(corpus,title=title,topic=topic,query=query,theme=theme,console=console);
    return browser.run(backend=backend);
