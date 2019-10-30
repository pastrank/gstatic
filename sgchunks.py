#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" module for work with templates """

from string import Template
import sgconf
# import sgmarkup
import re
from sgglobals import *


def process(cosa, nomi, elenco):
	""" new proc for templating chunks

	:param cosa: what is going to be templated, tipically a variable set from chunks. See [1]
	:param nomi: list of variable names in the substitution, can be empty an empty list if elenco is a dict
	:param elenco: a list if nomi is set, or a dictionary
	:return:
	"""

	mydiz = {}

	if cosa.startswith("chunk"):
		text = sgconf.cfgget(cosa)
	else:
		text = cosa

	# simpliest substitution: one or more parameters, without
	# any kind of repeating
	if isinstance(nomi, str) and isinstance(elenco, dict):
		if nomi == "":
			mydiz = elenco
			text = Template(text).safe_substitute(mydiz)

		return text

	# repeat a single value for more than 1 block: it can be repeated as a list
	# (name repeated is named as "nomi", while if it is a dict in the blocks are
	# templated key and value
	if isinstance(nomi, str) and isinstance(elenco, list):
		res = ""
		kindoflist = ""
		regstart = "<for " + nomi + ">"
		regend = "<next " + nomi + ">"
		regex = regstart + ".*?" + regend
		re.compile(regex)

		if all(isinstance(i, str) for i in elenco):
			kindoflist = "lst"
		if all(isinstance(i, dict) for i in elenco):
			kindoflist = "dct"

		matches = re.findall(regex, text, re.DOTALL)
		if matches:
			for m in matches:
				newdata = m[len(regstart):]
				newdata = newdata[:-len(regend)]

				if kindoflist == "lst":
					for e in elenco:
						mydiz[nomi] = e
						res += Template(newdata).safe_substitute(mydiz)
				if kindoflist == "dct":
					for mydiz in elenco:
						res += Template(newdata).safe_substitute(mydiz)

				text = text.replace(m, res)

		return text


if __name__ == "__main__":
	sgutils.showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)
