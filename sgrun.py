#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


""" this module is intended to contain the starting controls"""

import time
import argparse
from string import Template

import sgproc
import sggen
from sgconf import *
from sgrss import rssgo
from configparser import ConfigParser


class CaseConfigParser(ConfigParser):
	"""subclassing necessary due configparser lower the
	case of the keys, an aestethic fix"""
	def optionxform(self, optionstr):
		return optionstr


def letsgo():
	# remove old files
	if cfgget("initialcleaning") == "ok":
		sgutils.clearstart()

	# images
	if cfgget("dirimages") != "":
		elenco = cfgget("dirimages").split("|")
		for e in elenco:
			d = os.path.join(cfgget("dirstart"), e)
			if os.path.exists(d):
				sgproc.creategalleries(d)

	# docs
	if cfgget("dirdocs") != "":
		elenco = cfgget("dirdocs").split("|")
		for e in elenco:
			d = os.path.join(cfgget("dirstart"), e)
			if os.path.exists(d):
				sgproc.createdocs(d)

	# posts
	if cfgget("dirposts") != "":
		elenco = cfgget("dirposts").split("|")
		for e in elenco:
			d = os.path.join(cfgget("dirstart"), e)
			if os.path.exists(d):
				sgproc.createposts(d)

	# putnewposts
	if cfgget("dirnewposts") != "":
		sgproc.putnewpost()

	# private and secured
	if cfgget("privatedirectories") != "":
		sgproc.privatedirectoryset()

	# if you build, this is a sure line
	sgproc.htmlbuild()

	# rss
	if cfgget("rsscreate") == "ok":
		rssgo()

	# create sitemap
	if cfgget("buildmappage") == "ok":
		sgproc.createmap()

	# create sitemap.xml
	if cfgget("buildsitemap") == "ok":
		sgproc.createsitemap()

	sgproc.finalcopy()

	# remove old files
	if cfgget("finalcleaning") == "ok":
		sgutils.clearfinal()


def startintro():
	"""simply show the copyright informations at the startup and set the timer to show running time"""

	cfgset("z_timer", time.time())
	startdiz = {}
	cfgset("appname", APPNAME)
	cfgset("appversion", APPVERSION)

	startdiz["appname"] = cfgget("appname")
	startdiz["appversion"] = cfgget("appversion")
	startdiz["ostype"] = os.name
	a = """
g.static
	---------------------------------
	$appname $appversion
	generic static site generator
	running on $ostype
	tags: python, bugs, horror_coding
	---------------------------------
	Gianni Piccini, gstatic@antani.li
	application is licensed under GPL v3
"""
	sgutils.showmsg((Template(a).safe_substitute(startdiz)), 0)


def finaltime():
	"""to show the execution time of the program"""
	res = int((time.time() - cfgget("z_timer")) * 1000) / 1000
	return "Processed: " + str(cfgget("z_files")) + " pages\nExec time: " + str(res) + " seconds"


def initialcleartagsfiles():
	"""initial cleaning of tags

	delete the files used for tags, due they're always recreated
	every time application runs
	"""
	spath = os.path.join(cfgget("dirstart"), "site", "tags")

	sgutils.showmsg("cleaning " + spath, 0)
	if not os.path.exists(spath):
		os.makedirs(spath)

	for root, subFolders, files in os.walk(spath):
		for fn in files:
			if not os.path.splitext(fn)[1] == "":
				os.remove(os.path.join(root, fn))


def initialworks():
	"""creates necessary directories"""

	spath = os.path.join(cfgget("dirstart"), "site")
	if not os.path.exists(spath):
		os.makedirs(spath)

	spath = os.path.join(cfgget("dirstart"), "site", "chunks")
	if not os.path.exists(spath):
		os.makedirs(spath)

	spath = os.path.join(cfgget("dirstart"), "site", "conf")
	if not os.path.exists(spath):
		os.makedirs(spath)
	sggen.createchunks()

	spath = os.path.join(cfgget("dirstart"), "site", "map")
	if not os.path.exists(spath):
		os.makedirs(spath)

	spath = os.path.join(cfgget("dirstart"), "site", "rss")
	if not os.path.exists(spath):
		os.makedirs(spath)

	# clean tags directory
	spath = os.path.join(cfgget("dirstart"), "site", "tags")
	if not os.path.exists(spath):
		os.makedirs(spath)
	initialcleartagsfiles()

	spath = os.path.join(cfgget("dirstart"), "site", "scripts")
	if not os.path.exists(spath):
		os.makedirs(spath)

	spath = os.path.join(cfgget("dirstart"), "site", "tmpl")
	if not os.path.exists(spath):
		os.makedirs(spath)
	conf_settemplatechunks()

	spath = os.path.join(cfgget("dirstart"), "site", "vars")
	if not os.path.exists(spath):
		os.makedirs(spath)

	# remove, if exists and is possible, updated file list
	spath = os.path.join(cfgget("tempdirectory"), cfgget("ftpfilelist"))
	if os.path.exists(spath):
		os.remove(spath)

	sggen.createdefaultreplaceconf()
	sggen.createdefaulttagconf()


def extractvalue(valore):
	""" get a value from the action file

	:param valore: complete line to be cut
	:return: part of line after the space
	"""
	v = valore
	if valore.find(" ") > 0:
		lista = valore.split(" ", 1)
		v = lista[1].strip()
	return v


###############################################################
# start -----------------------------------------------------
arg = ""
if __name__ == "__main__":

	startintro()
	parser = argparse.ArgumentParser(epilog="Check http://www.antani.li/gstatic to get more help")

	parser.add_argument("--build", nargs=1, metavar='SITE_DIRECTORY', help="execute the actions in the file")
	parser.add_argument("--newsite", nargs=1, metavar='SITE_DIRECTORY', help="create a new site in an existing directory")
	parser.add_argument("--checkcss", nargs=1, metavar='SITE_DIRECTORY', help="create the default css in an existing site")
	parser.add_argument("--checkchunks", metavar='SITE_DIRECTORY', nargs=1, help="check chunks in an existing site")
	parser.add_argument("--createconf", metavar='SITE_DIRECTORY', nargs=1, help="set configuration file for a site")
	parser.add_argument("--createscripts", metavar='SITE_DIRECTORY', nargs=1, help="create the default script file for site")
	parser.add_argument("--find", nargs=2, metavar=("SITE_DIRECTORY", "STRING"), help="perform search on a site directory")
	parser.add_argument("--findreplace", nargs=3, metavar=("SITE_DIRECTORY", "FIND", "REPLACE"), help="perform search and replace on a site directory")
	parser.add_argument("--hidemessages", help="hide output")

	args = parser.parse_args()
	argsdict = vars(args)

	# single options
	if args.hidemessages:
		cfgset("hideprogressmessages", "no")

	# exclusive options
	if args.build:
		tmp = getattr(args, 'build')[0]
		if os.path.exists(tmp):
			cfgset("dirstart", slashadd(tmp))

			readconf(tmp)
			# checkdeps()
			initialworks()
			sgproc.getfileinvar()
			sgproc.getfilescript()
			letsgo()
		else:
			sgutils.showmsg("You need to specify an action file", 99)
		print(finaltime())

	elif args.newsite:
		tmp = getattr(args, 'newsite')[0]
		if os.path.exists(tmp):
			sggen.createnewsite(tmp)
		else:
			sgutils.showmsg("You need to specify a directory where you want to build the site", 99)

	elif args.checkcss:
		tmp = getattr(args, 'checkcss')[0]
		if os.path.exists(tmp):
			cfgset("dirstart", slashadd(tmp))
			sggen.createdefaultcss()
		else:
			sgutils.showmsg("You need to specify the site directory where css will be updated", 99)

	elif args.checkchunks:
		tmp = getattr(args, 'checkchunks')[0]
		if os.path.exists(tmp):
			cfgset("dirstart", slashadd(tmp))
			sggen.createchunks()
		else:
			sgutils.showmsg("You need to specify the site directory where chunks will be updated", 99)

	elif args.createconf:
		tmp = getattr(args, 'createconf')[0]
		if os.path.exists(tmp):
			sggen.createconfigfile(tmp)
		else:
			sgutils.showmsg("You need to specify a site directory where you want to check configuration", 99)	

	elif args.createscripts:
		tmp = getattr(args, 'createscripts')[0]
		if os.path.exists(tmp):
			cfgset("dirstart", slashadd(tmp))
			sggen.createdefaultjsfile()
		else:
			sgutils.showmsg("You need to specify the main site directory where script file will be created", 99)

	elif args.find:
		tmp = getattr(args, 'find')
		if list:
			sgutils.findreplace(tmp[0], tmp[1], "", "", False)
		else:
			sgutils.showmsg("You need to specify a string to find\nrun sgrun.py --help", 99)

	elif args.findreplace:
		tmp = getattr(args, 'findreplace')
		if list:
			sgutils.findreplace(tmp[0], tmp[1], tmp[2], "", False)
		else:
			sgutils.showmsg("You need to specify strings to find and replace\nrun sgrun.py --help", 99)

	else:
		# startintro()
		print("  please digit   sgrun.py --help   to show commands list")
