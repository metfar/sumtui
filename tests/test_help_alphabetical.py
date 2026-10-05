#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sumtui.helpdb import HelpCorpus,HelpTopic;

def test_topic_names_are_global_alphabetical():
    corpus=HelpCorpus("x",[HelpTopic("ZETA","A","",(),"x"),HelpTopic("ALPHA","Z","",(),"x"),HelpTopic("BETA","A","",(),"x")]);
    assert corpus.topic_names()==["ALPHA","BETA","ZETA"];
