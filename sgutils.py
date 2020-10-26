#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""this module should contain some procedures that are based
on working the files and directory, and generally to things
unrelated with doing a site"""

import os
import shutil
import datetime
import collections
import random
import string
import fnmatch
import textwrap
import csv

import sgconf
import sgexternal
from sgglobals import *

listarepl = collections.OrderedDict()  # list of replacing items in replace.conf


def clearfinal():
	""" if a directory doesn't exist on start, it must not be also in destination """
	dir1 = sgconf.cfgget("dirstart")
	dir2 = sgconf.cfgget("dirfinal")

	# first, I clear directories that don't exist anymore
	for root, subf, files in os.walk(dir2, topdown=False):
		for fn in subf:
			chkdir = os.path.join(root, fn)
			exdir = chkdir.replace(dir2, dir1)
			if not os.path.exists(exdir):
				try:
					showmsg("Clearing directory " + fn, 0)
					shutil.rmtree(chkdir)
				except:
					pass

	# then, I delete files: two ways. html & php are composed so others are only copied
	for root, subf, files in os.walk(dir2):
		for fn in files:
			chkfile = os.path.join(root, fn)
			chkext = os.path.splitext(chkfile)[1]

			if chkext == ".html" or chkext == ".php":
				oldfile = str(os.path.splitext(chkfile)[0].replace(dir2, dir1)) + sgconf.cfgget("processingext")
				if not os.path.exists(oldfile):
					os.remove(chkfile)
			else:
				oldfile = chkfile.replace(dir2, dir1)
				if not os.path.exists(oldfile):
					os.remove(chkfile)


def clearstart():
	""" clear some kinds of files if they don't have to exists anymore """

	listimagedirs = sgconf.cfgget("dirimages").split("|")

	for e in listimagedirs:
		for root, subf, files in os.walk(os.path.join(sgconf.cfgget("dirstart"), e)):
			for fn in files:
				basefile = os.path.splitext(fn)[0]          # base name
				extfile = os.path.splitext(fn)[1]           # extension
				chkfile = os.path.join(root, basefile)      # all path except extension
				if extfile == sgconf.cfgget("processingext"):
					if not os.path.exists(chkfile + sgconf.cfgget("processingext")):
						showmsg(" removing " + chkfile + sgconf.cfgget("processingext"), 0)
						try:
							os.remove(chkfile + sgconf.cfgget("processingext"))
						except:
							pass


def checkdep(application):
	"""check for dependencies and find installed applications
		for imagemagick and openssl
	"""
	chk = ""

	if os.name == "nt":
		checkingprog = "where"
	else:
		checkingprog = "which"

	# checking if there the magick executable or single apps
	chk = sgexternal.extgetcmd(checkingprog + " " + application)
	if chk == "":
		chk = sgexternal.extgetcmd(checkingprog + " magick")

	return chk


def checkpermission(fname, what):
	"""
	check file permissions
	:param fname: the name of the file
	:param what: request of the permission
	:return: True or False, if a situation is reached
	"""
	if what == "write":
		return os.access(fname, os.W_OK)
	if what == "read":
		return os.access(fname, os.R_OK)


def conformitynamecheck():
	"""
	:return: none
	"""

	spaths = []
	# two folders are checked, main and newposts, then i advise for empty values
	if sgconf.cfgget("dirstart") == "":
		showmsg("You've to set the start directory before check filenames", 99)
		return
	else:
		spaths.append(sgconf.cfgget("dirstart"))
	if sgconf.cfgget("dirnewposts") != "":
		spaths.append(sgconf.cfgget("dirnewposts"))

	for sdir in spaths:
		for root, subFolders, files in os.walk(sdir):
			for fn in files:
				newfile = fn.lower()
				newfile = newfile.replace("'", "_")
				newfile = newfile.replace(" ", "-")
				newfile = newfile.replace("..", ".")

				if fn != newfile:
					try:
						showmsg(" renaming " + os.path.join(root, fn), 0)
						os.rename(os.path.join(root, fn), os.path.join(root, newfile))
					except:
						showmsg(" error renaming " + os.path.join(root, fn), 0)


def cuttext(text, mode):
	""" cut the text passed to function
	:param text: text to be cutted
	:param mode: the way
	:return:
	"""

	if mode == "summary":
		maxdim = sgconf.cfgget("postsummarylength")
		return textwrap.shorten(sterilizetemplates(text), width=maxdim, placeholder="")

def dir_clean(nomedir):
	"""clean directory  tree recursively removing empty dirs
	:param nomedir: the name of directory
	:return: none
	"""

	if nomedir.find(sgconf.cfgget("dirstart")) < 0:
		return

	for dirpath, dirnames, filenames in os.walk(nomedir, topdown=False):
		try:
			os.rmdir(dirpath)
		except:
			pass


def file_search_replace(txt):
	""" replace some user defined variables

	:param txt:
	:return:
	"""
	global listarepl

	if not listarepl:
		replfile = os.path.join(sgconf.cfgget("dirstart"), "site", "replace.conf")
		if os.path.exists(replfile):
			showmsg(" replacing contents in " + replfile, 0)

			with open(replfile, newline='') as csvfile:
				sr = csv.reader(csvfile, delimiter='|')
				for row in sr:
					a = row[0]
					b = row[1]
					listarepl[a] = b
			csvfile.close()
		else:
			listarepl["zzz"] = "zzz"

	for key, value in listarepl.items():
		txt = txt.replace(key, value)

	return txt


def findreplace(sdir, sfind, sreplace, filepattern, subst):
	"""
	:param sdir: directory of the site
	:param sfind: string to find
	:param sreplace: replacing string, empty if for finding only
	:param filepattern: default is *.md
	:param subst: if it is False, is a dry run
	:return:
	"""
	if filepattern == "":
		filepattern = "*.md"

	for path, dirs, files in os.walk(os.path.abspath(sdir)):
		for filename in fnmatch.filter(files, filepattern):
			filepath = os.path.join(path, filename)
			with open(filepath) as f:
				s = f.read()

			if s.find(sfind) >= 0:
				if subst:
					s = s.replace(sfind, sreplace)
					with open(filepath, "w") as f:
						f.write(s)
				else:
					showmsg("Found: " + filepath[len(sdir):], 1)


def file_trash(filecont):
	""" remove all files containings this in name
	:param filecont: files that contains this will be deleted
	:return: none
	"""

	sdir = sgconf.cfgget("dirstart")
	for root, subdirs, files in os.walk(sdir):
		for fl in files:
			if fl.find(filecont) >= 0:
				showmsg("Removing " + os.path.join(root, fl), 0)
				try:
					os.remove(os.path.join(root, fl))
				except:
					pass


def file_write(nomefile, testo, modo):
	""" open a file and write on it

	:param nomefile: file name
	:param testo: text
	:param modo: can be w or a, write or append
	:return: none
	"""
	try:
		with open(nomefile, modo) as myfile:
			myfile.write(testo)
	except:
		showmsg("Error deleting " + nomefile, 9)


def file_write_csv(nomefile, arr, modo):
	""" write a csv file

	"""
	try:
		with open(nomefile, modo, newline='') as csvfile:
			w = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)
			w.writerow(arr)
	except:
		showmsg("Error writing CSV file " + nomefile, 9)


def file_read(nomefile):
	"""open a file and read it

	:param nomefile: text file name to be read
	:return: content of the file
	"""
	if os.path.exists(nomefile):
		# noinspection PyArgumentEqualDefault
		with open(nomefile, "r") as myfile:
			v = myfile.read()
		return v
	else:
		return ""


def file_read_csv(nomefile):
	arr = []
	with open(nomefile) as csvfile:
		sr = csv.reader(csvfile, delimiter='|')
		for row in sr:
		    arr.append(row)
	
	return arr
	

def fad(nomefile):
	""" Filename As Description
		return the base file name cleared """
	res = os.path.basename(os.path.splitext(nomefile)[0])
	res = res.replace("-", " ")
	res = res.replace("_", "'")

	return res


def fwe(nomefile):
	""" Filename Without Extension
		return the file name without extension: used to short routines """
	return os.path.splitext(nomefile)[0]


def getuniqueid(nf, modo):
	""" get an unique random string. For file id, it's simply an unique id. For 'salt', if you think to secure relatively the process
		you can set in action file the string, or put in it the value 'random' or simply nothing, to make prefix always changing. A consideration
		is that you need to upload always the hashed password files. This is not generally a problem, due they are often small files, but
		think to transfer mode due security, to passwords length, to simple words, etc etc
	:param nf: file name if useful,
	:param modo: the kind of id
	:return:
	"""
	if modo == "fileid":
		res = ''.join(random.choice(string.ascii_lowercase) for i in range(12))
		res += "-" + os.path.basename(os.path.splitext(nf)[0])
	elif modo == "salt":
		if sgconf.cfgget("saltprefix") == "":
			res = ''.join(random.choice(string.ascii_lowercase) for i in range(2))
		else:
			res = sgconf.cfgget("saltprefix")
	else:
		res = ""

	return res


def lastmod(nomefile, modo):
	"""
	:param nomefile: file name to be checked
	:param modo: 0=yyyy-mm-dd hh:mm  1=yyyymmdd
	:return: the last modification time
	"""
	v = ""
	try:
		if os.path.exists(nomefile):
			tmp = os.path.getmtime(nomefile)
			tmp2 = datetime.datetime.fromtimestamp(tmp)
			if modo == 0:
				v = str(tmp2)[:16]
			if modo == 1:
				v = str(tmp2)[:10].replace("-", "")
	except:
		pass

	return v


def lnkc(linkname):
	""" replace slash in windows systems: in Linux and Mac, I get paths and resolve them
		in Windows I have a backslash, different from the needs of the page. Due a lot
		of links are coming from file names, using Windows make path a pain for a prog
		based on directories

	:param linkname: the contents of link
	:return: link corrected
	"""

	return linkname.replace(os.sep, "/")


def removehtml(s):
	"""as function name says :-) """

	tag = False
	quote = False
	out = ""

	for c in s:
		if c == '<' and not quote:
			tag = True
		elif c == '>' and not quote:
			tag = False
		elif (c == '"' or c == "'") and tag:
			quote = not quote
		elif not tag:
			out = out + c

	return out


def sterilizetemplates(s):
	""" cleaning some chars from templates """
	testo = s.replace("{", "[").replace("}", "]")
	return testo


def filedatemod(nf):
	""" update the modification time of a file: these are standalone functions, due
		probably I will have to adjust for use on Windows

	:param nf: name of the file to be updated
	:return: none
	"""
	# TODO check if Windows implementation is working
	try:
		os.utime(nf, None)  # Set access/modified times to now
	except OSError:
		showmsg("Can't touch " + nf, 1)


def filelink(oldfile, newlink):
	""" link a file to a position by sym link (equivalent to ln -s)

	:param oldfile: file to be linked
	:param newlink: new position
	:return: none
	"""

	# TODO check if Windows implementation is working
	try:
		os.symlink(oldfile, newlink)
	except:
		showmsg("Error linking " + oldfile, 1)


def showmsg(message, modo):
	"""
	:param message: message to be showed
	:param modo: the way message is showed 0=show, 9=log
	:return: link corrected
	"""

	if sgconf.cfgget("hideprogressmessages") == "no" and modo != 1:
		return

	if message == "":
		return

	if modo == 0:           # normal
		print(message)
	elif modo == 1:         # error
		print(message)
	elif modo == 9:         # log file
		file_write(sgconf.cfgget("logfile"), message + "\n", "a")
	elif modo == 99:        # debug
		print("..................\n.. " + message + "\n..................")


if __name__ == "__main__":
	showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)

