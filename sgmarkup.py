#!/usr/bin/python3
# -*- coding: utf-8 -*-
# module where there is the markup processing

import re
import os
import fnmatch
from string import Template

import sgconf
import sgproc
import sgchunks
import sgexternal
import sgmistune
from sgglobals import *
from sgutils import fwe


def getindexsquare(linea):
	""" function that returns the content of a block in the list files
	:param linea: content
	:return: the block
	"""
	dic = {}
	fname = os.path.join(sgconf.cfgget("dirstart"), linea)
	sdir = os.path.join(sgconf.cfgget("dirstart"), sgconf.cfgget("dirposts"))
	if not os.path.exists(fname):
		return linea

	nomefile = sgproc.fwe(fname)
	immagine = nomefile + ".jpg"
	thumbnail = os.path.join(os.path.dirname(immagine), "thumbnails", os.path.basename(immagine))

	dati = sgproc.Pagina()
	sgproc.textget(fname, dati)

	titles = dati.title.split("|")
	mylink = sgproc.createpostslink(fname, sdir, "link")
	if len(titles) == 1:
		dic["title"] = "<a href='" + mylink + "'>" + sgproc.replacetitle(dati.title, 0) + "</a>"

	else:
		tmp = ""
		for j in range(0, len(titles)):
			tmp = tmp + "<a href='" + mylink + "' class='" + titles[j][:2] + "' style='display:none;'>" + sgproc.replacetitle(titles[j], 0) + "</a>"
		dic["title"] = tmp

	dic["linktofullarticle"] = mylink
	dic["linkposts"] = sgproc.createpostslink(nomefile, sdir, "data")
	dic["tags"] = sgproc.replacetagfiles(nomefile.replace(sgconf.cfgget("dirstart"), ""), dati.tags, True, False, True)

	if os.path.exists(os.path.join(sdir, immagine)):
		if not os.path.exists(os.path.join(sdir, thumbnail)):
			sgproc.graphicresize(immagine, sgconf.cfgget("postsimagewidth"), sgconf.cfgget("poststhumbwidth"))


	if os.path.exists(os.path.join(sdir, thumbnail)):
		tmp = thumbnail.replace(os.path.join(sgconf.cfgget("dirstart"), sgconf.cfgget("dirposts")), "")[1:]
		desc = sgproc.replacetitle(sgproc.fwe(os.path.basename(tmp)), 0)
		tmp = seturlencode(tmp)

		dic["thumbdesc"] = desc
		dic["thumblink"] = sgutils.lnkc(tmp)
		dic["thumbsize"] = sgexternal.extgraphicinfo(thumbnail, "linksize")
	else:
		dic["thumbdesc"] = ""
		dic["thumblink"] = ""
		dic["thumbsize"] = ""

	#sort of summary
	if sgconf.cfgget("chunk_article_square").find("summary") > 0:
		nomefile = os.path.join(sgconf.cfgget("dirstart"), fname)
		dic["summary"] = getsummary(nomefile)
	else:
		dic["summary"] = ""

	return Template(sgconf.cfgget("chunk_article_square")).safe_substitute(dic)


def getsummary(fn):
	# return a summary of the article
	conto = 0                                       # to be sure that variable is set
	maxdim = sgconf.cfgget("postsummarylength")
	txt = sgutils.file_read(fn)

	pos = txt.find("\n:> lang:")
	if pos >= 0:
		multilang = True
	else:
		multilang = False

	lista = txt.split("\n")
	dictl = {}

	for i in range(0, len(lista)):
		if lista[i][:3] != ":> " or lista[1][:8] == ":> lang:":
			conto = i - 1
			break

	lista = lista[-(len(lista) - conto):]
	if multilang:
		condition = "all"
		dictl[condition] = ""
		for i in range(0, len(lista)):
			if lista[i][:8] == ":> lang:":
				try:
					condition = lista[i][-2:]
					if not condition in dictl:
						dictl[condition] = ""
				except:
					pass
			else:
				if len(dictl[condition]) < maxdim:
					if len(lista[i]) > 0:
						dictl[condition] = dictl[condition] + "\n" + lista[i]
				else:
					dictl[condition] = dictl[condition][:maxdim]

	txt = ""
	if not multilang:
		for n in lista:
			if len(txt) < maxdim and n[:3] != ":> ":
				txt = txt + "\n" + n
			if len(txt) >= maxdim:
				txt = sgutils.cuttext(txt, "summary")
				break

		txt = sgutils.removehtml(txt)
		txt = "<span class='sgsummary'>" + txt + "</span>"
	else:
		txt = ""
		for n in dictl:
			if n != "all":
				txt += "<span class='sgsummary sglang " + n + "' style='display:none;'>" + dictl[n] + "...\n</span>"

	if txt.find("{") > 0:
		txt = txt.replace("{", "&#123;")
		txt = txt.replace("}", "&#125;")

	return txt


def getlinkreplace(linea):
	"""replace a fast link with the correct link"""
	flink = linea
	fdir = os.path.dirname(sgconf.cfgget("z_currentfile"))
	fname = os.path.splitext(flink)[0]
	fext = os.path.splitext(flink)[1]
	appl = ""
	#res = ""

	listimages = [".bmp", ".jpg", ".png"]
	listaudio = ["dsd", "dsf", ".flac", ".mp3", ".ogg", ".wav", "wv"]
	listvideo = [".flv", ".mkv", ".mp4", ".ogm", ".webm"]

	# image files -------------------------------------------------------------------------------
	if fext in listimages:
		res = "<img src='" + flink + "' " + sgexternal.extgraphicinfo(os.path.join(fdir, linea), "linksize") + " alt='" + fname + "' class='sgfastimage'>"
	# audio files -------------------------------------------------------------------------------
	elif fext in listaudio:
		res = "<audio controls class='sgfastaudio'>\n"
		if fext == ".ogg":
			appl = "audio/ogg"
		elif fext == ".mp3":
			appl = "audio/mpeg"
		elif fext == ".wav":
			appl = "audio/wave"
		res += "  <source src='" + flink + "' type='" + appl + "'>\n"
		res += "  <a href='" + flink + "'>" + fname + "</a>\<br>n"
		res += "  Your browser does not support the audio element.\n</audio>\n"
	# video files --------------------------------------------------------------------------------
	elif fext in listvideo:
		res = Template(sgconf.cfgget("chunk_video_link")).safe_substitute(filelink=fname)
	elif fext == ".youtube":
		res = Template(sgconf.cfgget("chunk_youtube_link")).safe_substitute(p1=fname)
	# all others, including html and php ----------------------------------------------------------
	else:
		res = "<a href='" + seturlencode(flink) + "'>" + fname + "</a>"

	return res


def markup(elenco):
	"""try to convert some rows as utility and some as an implementation of a markup"""
	testo = '\n'.join(elenco)

	# nobracket = r'[^\]\[]*'
	# brk = (r'\[(' + (nobracket + r'(\[' + nobracket) * 6 + (nobracket + r'\])*' + nobracket) * 6 + nobracket + r')\]')

	local_re = r'<:([^>]*)>'                				# <:link>
	#mark_re = r'<m:([^>]*)>'    							# <m: * >
	notes_re = r'<n:([^>]*)>'    							# <n: * >
	# quote_re = r'<q:([^>]*)>'    							# <q: * >
	#
	filelist_re = r'\$\{?listgeneric\(.*\)\}?'              # listgeneric(kindoffiles)
	# history_re = r'\$\{?history\([0-9][0-9]\)\}?'           # listgeneric(kindoffiles)
	scripts_re = r'\$\{?script\(.*\)\}?'                    # script(scriptname)
	lang_re = r'\$\{?lang\([a-z][a-z]\)\}?'                 # listgeneric(kindoffiles)
	# for internal use
	square_re = r'<sqr:([^>]*)>'    						# <sqr: * >

	for line in re.findall(lang_re, testo):
		testo = testo.replace(line, sgproc.replacelanguage(line))
	for line in re.findall(local_re, testo):
		testo = testo.replace("<:" + line + ">", getlinkreplace(line))
	for line in re.findall(filelist_re, testo):
		testo = testo.replace(line, sgproc.replacefilelist(line))
	for line in re.findall(scripts_re, testo):
		testo = testo.replace(line, sgproc.pagescriptresult(line))
	# for line in re.findall(mark_re, testo):
	# 	testo = testo.replace("<m:" + line + ">", "<mark class='sgmark'>" + line + "</mark>")
	for line in re.findall(square_re, testo):
		testo = testo.replace("<sqr:" + line + ">", getindexsquare(line))
	# for line in re.findall(quote_re, testo):
	#	testo = testo.replace("<q:" + line + ">", sgchunks.process(sgconf.cfgget("chunk_note"), "", {"quote": line}))
	
	myconds = sgconf.cfgget("replacetagfile")
	if myconds:
		for r in myconds:
			if testo.find(r[0]) < testo.rfind(r[0]):
				m_re = r[0] + '(.*?)' + r[0]
				for line in re.findall(m_re, testo):
					testo = testo.replace(r[0] + line + r[0], r[1] + line + r[2])

	testo = sgmistune.markdown(testo, False)
	# these lines about correcting the results from sgmistune
	if testo[:3] == "<p>":
		if testo.rstrip()[-4:] == "</p>":
			testo = testo.rstrip()[3:-4]

	testo = testo.replace("${}", "</div>")
	return testo


def clearname(nome):
	"""clear the name of the link - the showed name, due it mustn't be formatted"""
	v = nome.replace("_", " ")
	return v


def seturlcleaning(linkname):
	""" htmlize some chars in the links

	:param linkname: the link where substition will be done
	:return: sanitized link
	"""

	v = linkname.replace("-", "&#45;")
	v = v.replace("_", "&#95;")

	return v


def seturlencode(linkname):
	""" encode some chars in the links

	:param linkname: the link where substition will be done
	:return: sanitized link
	"""

	v = linkname.replace("_", "%5F")
	v = v.replace(" ", "%20")
	return v


if __name__ == "__main__":
	sgutils.showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)