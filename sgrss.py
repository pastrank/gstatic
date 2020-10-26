#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" module devoted to build rss files """

import os
import time
import hashlib
import fnmatch
import textwrap
from time import localtime, strftime

import sgconf
import sgproc
import sgexternal
import sggen

from sgglobals import *

global listarss
listarss = []


def rssaddtolist(nomefile, mydate):
	global listarss
	listarefuse = []
	maxnum = sgconf.cfgget("rsslistlength")

	if os.path.splitext(nomefile)[1] == sgconf.cfgget("processingext"):
		cln = nomefile[len(sgconf.cfgget("dirstart")):]
		# nome = mydate + " " + cln

		if listarss:
			if (mydate + " " + nomefile) in listarss:
				return
			if len(listarss) > maxnum * 2:
				listarss = sorted(listarss, reverse=True)[:maxnum]

		# no upper files
		if os.path.dirname(cln) == "":
			return
		# no files in site directory
		if fnmatch.fnmatch(cln, os.path.join("site", "*.*")):
			return
		# no image galleries
		if fnmatch.fnmatch(cln, os.path.join(sgconf.cfgget("dirimages"), "*")):
			return
		if os.path.dirname(cln) == sgconf.cfgget("dirposts"):
			return
		if os.path.dirname(cln) == sgconf.cfgget("dirperma"):
			return
		if fnmatch.fnmatch(cln, os.path.join(sgconf.cfgget("dirposts"), "*", sgconf.cfgget("indexfile") + ".*")):
			return

		# managing to no add some directories or files to rss.xml
		if sgconf.cfgget("hiddenpaths") != "":
			listarefuse = sgconf.cfgget("hiddenpaths").split("|")
		if sgconf.cfgget("rssnoadd") != "":
			listarefuse += sgconf.cfgget("rssnoadd").split("|")
		for lritem in listarefuse:
			if nomefile.find(lritem) > 0:
				return

		listarss.append(mydate + " " + nomefile)


def rssgo():
	""" main function """

	global listarss
	filerss = os.path.join(sgconf.cfgget("dirstart"), "site", "rss", "rss.xml")
	res = []
	mp = sgproc.Pagina()
	lista = sorted(listarss, reverse=True)[:sgconf.cfgget("rsslistlength")]

	if len(lista) == 0:
		return

	# will avoid creation of a new rss file if there are no file added
	if os.path.exists(filerss):
		fileh = open(filerss)
		lines = fileh.readlines()
		fileh.close()
		try:
			oldfirst = os.path.splitext(os.path.basename(lines[14].replace("</link>", "")))[0]
			newfirst = os.path.splitext(os.path.basename(sgconf.cfgget("lastpost")))[0]
			if oldfirst == newfirst:
				return
		except:
			pass

	dt = strftime("%a, %d %b %Y %H:%M:%S %z", localtime())

	res.append("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>")
	res.append("<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">")
	res.append("<channel>")
	# res.append("<atom:link href=\"http://" + cfgget("sitename") + "/" + cfgget("dirposts") + "/" + "rss.xml" + "\" rel=\"self\" type=\"application/rss+xml\">")
	res.append("<title>" + sgconf.cfgget("sitename") + "</title>")
	res.append("<link>http://" + sgconf.cfgget("sitename") + "/</link>")
	res.append("<description><![CDATA[" + sgconf.cfgget("rssdescription") + "]]></description>")
	res.append("<language>" + sgconf.cfgget("defaultlang") + "</language>")
	res.append("<pubDate>" + dt + "</pubDate>")
	res.append("<lastBuildDate>" + dt + "</lastBuildDate>")
	res.append("<docs>http://blogs.law.harvard.edu/tech/rss</docs>")
	res.append("<generator>" + sggen.getversion(True) + "</generator>")

	for ele in lista:
		myfile = ele[9:]
		fn = myfile.replace(sgconf.cfgget("dirstart"), "")
		fn = os.path.splitext(fn)[0] + ".html"
		dt = ele[:8]

		f = time.mktime((rssint(dt[0:4]), rssint(dt[4:6]), rssint(dt[6:8]), 0, 0, 1, 0, 0, 0))
		dt = time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime(f))

		sgproc.textget(myfile, mp)
		descr = rsspreview(mp.text, mp.title, mp.filepath)

		# xtext, xtitle, xtags, xfilesize, xfilelastm, xauthor,xfilename
		sitelink = os.path.join(sgconf.cfgget("sitename"), fn)
		res.append("  <item>")
		res.append("    <title><![CDATA[" + mp.title + "]]></title>")
		res.append("    <author><![CDATA[" + rsssetauthor(mp.author, mp.authormail) + "]]></author>")
		res.append("    <link>http://" + sitelink + "</link>")
		res.append("    <description><![CDATA[" + descr + "]]></description>")
		res.append("    <pubDate>" + dt + "</pubDate>")
		res.append("    <comments>http://" + sitelink + "</comments>")
		res.append("    <guid isPermaLink=\"false\">" + rsssetguid(ele) + "</guid>")
		res.append("  </item>")

	# res.append("</atom:link>")
	res.append("</channel>")
	res.append("</rss>")

	if os.path.exists(filerss):
		os.remove(filerss)
	filecontent = "\n".join(res)

	sgutils.file_write(filerss, filecontent, "w")


def rsssetauthor(proposedname, proposedmail):
	""" if author is not setted, than get defaults function should return an email address

	:param proposedname: default author mode
	:param proposedmail: default author mail
	:return: author name for rss feed
	"""

	if proposedname == "":
		res = sgconf.cfgget("rssauthor")
	else:
		if proposedmail.find("@") < 2 or proposedname == "":
			res = sgconf.cfgget("rssauthor")
		else:
			res = proposedmail + " (" + proposedname + ")"

	return res


def rsssetguid(fromthis):
	""" creates a guid hashing the name of a file, removing path before doing it
	this is necessary due it's needed to avoid duplicates

	:param fromthis: original
	:return: the guid
	"""

	if fromthis.find(os.sep) >= 0:
		stringa = os.path.basename(fromthis)
	else:
		stringa = fromthis
	return hashlib.md5(stringa.encode()).hexdigest()


def rssint(valore):
	""" make a value an integer
	:param valore: value to be processed
	:return: 'integerized' value
	"""
	try:
		i = int(valore)
	except:
		i = 0

	return i


def rsspreview(text, alternative, linkf):
	""" get a bit of the text to be used in rss summary. Different from the other summary in index files, it doesn't consider
		actually the fact that languages for article can be more of one.

	:param text: text of article
	:param alternative: if text is none, generally title is
	:param linkf:
	:return: smaller text
	"""
	misura = int(sgconf.cfgget("rsssummarylength"))
	thumbpath = os.path.join(os.path.dirname(linkf), "thumbnails", os.path.splitext(os.path.basename(linkf))[0] + ".jpg")

	if text != "":
		text = sgutils.removehtml(text)
		text = textwrap.shorten(text, width=misura, placeholder="")
		if text.rfind(".") > misura - 10:
			text = text[:text.rfind(".")]
		elif text.rfind(" ") > misura - 20:
			text = text[:text.rfind(" ")]
	else:
		text = alternative

	res = text + " [...]"

	res = sgutils.removehtml(res)
	res = res.replace("<", "")
	if os.path.exists(thumbpath):
		res = "<img src='http://" + sgconf.cfgget("sitename") + "/" + thumbpath.replace(sgconf.cfgget("dirstart"), "") + "' " + sgexternal.extgraphicinfo(thumbpath, "linksize") + "><p>\n" + res

	return res


if __name__ == "__main__":
	sgutils.showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)
