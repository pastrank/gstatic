#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" module where global constants are specified """

import sgutils

# application and version
APPNAME = "g.static"
APPVERSION = "0.21"

# error showed when another script than sgrun.py is launched
ERROR_LAUNCHED_SCRIPT = "You should run sgrun.py instead"

# this constant is about a capitalized title
TITLE_CAP = 10

# about showmsg()
MESSAGE_NORMAL = 0
MESSAGE_ERROR = 1
MESSAGE_LOG = 9
MESSAGE_DEBUG = 99

if __name__ == "__main__":
	sgutils.showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)