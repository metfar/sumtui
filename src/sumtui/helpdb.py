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
"""Compatibility exports for the backend-neutral Sum help model.

The semantic runtime model now lives in :mod:`sumui.help`.  Keeping this module
means existing ``from sumtui.helpdb import ...`` callers continue to work.
""";

from sumui.help import HelpCorpus, HelpTopic, load_helpdb;

__all__ = ["HelpCorpus", "HelpTopic", "load_helpdb"];
