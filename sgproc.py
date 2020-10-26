#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" main module """

import filecmp
import fnmatch
import math
import collections
import glob
import urllib.parse

from sggen import *
from sgmarkup import *
from sgexternal import *
from sgconf import *
from sgglobals import *
from sgutils import fwe, fad
import sgrss
import sgchunks

personalvars = {}
listaarc = []  # list of archives month


class Pagina:
	""" class to collect file properties"""
	def __init__(self):
		self.body = ""
		self.author = ""
		self.authormail = ""
		self.currentfile = ""
		self.date = ""
		self.filename = ""
		self.filelstm = ""
		self.filepath = ""
		self.filesize = ""
		self.keywords = ""
		self.pause = False
		self.permalink = ""
		self.raw = ""
		self.refer = ""
		self.tags = ""
		self.template = ""
		self.text = ""
		self.title = ""
		self.uid = ""
		self.update = False
		self.xdict = {}


def associatetexttoimage(nomedirs):
	""" it will create a text content file, associate with the name of image, if file doesn't
		exists: useful to create automatically content putting only images in a directory
	
	:param nomedirs:  directory that will be processed, recursively
	:return: none
	"""

	for mydir in nomedirs.split("|"):
		if not mydir.startswith(cfgget("dirstart")):
			sdir = os.path.join(cfgget("dirstart"), mydir)
		else:
			sdir = mydir
		imageexts = cfgget("imageextensions").split("|")

		for root, subf, files in os.walk(sdir):
			for fn in files:
				myfile = os.path.join(root, fn)
				if os.path.splitext(myfile)[1][1:] in imageexts:
					textfile = os.path.splitext(myfile)[0] + cfgget("processingext")
					if not os.path.exists(textfile):
						sgutils.file_write(textfile, "", "w")


def graphicresize(immagine, imagew, thumbw):
	"""resize and create the thumbnails

	:param immagine: name of the image
	:param imagew: image width
	:param thumbw:  thumbnail width
	:return:
	"""

	w = 0
	imgt = os.path.join(os.path.dirname(immagine), "thumbnails", os.path.basename(immagine))
	tpath = os.path.join(os.path.dirname(immagine), "thumbnails")

	if int(thumbw) == 0:
		thumbw = cfgget("imagesthumbwidth")

	if not os.path.exists(imgt):
		if not os.path.exists(tpath):
			sgutils.showmsg("Checking images in " + os.path.dirname(immagine), 0)
			os.makedirs(tpath)

		misure = extgraphicinfo(immagine, "arrdim")
		# now i've measures in misure [0] and [1], where 0 and 1, to be readable
		# are substituted with predefined variables w and h
		if not (int(imagew) == int(misure[w])):
			nw = int(imagew)
			# nh= round(int(misure[h]) / int(misure[w]) * int(imagew))

			extgraphicresize(immagine, nw, "")

		nw = int(thumbw)
		extgraphicresize(immagine, nw, imgt)


def createdocs(sdir):
	"""procedure to check and build documents directory indexes
	simply run a check on the subindex file, if it doesn't exist it creates file
	"""
	primofile = os.path.join(sdir, cfgget("indexfile") + cfgget("processingext"))
	if not os.path.exists(primofile):
		if not os.path.exists(os.path.dirname(primofile)):
			os.makedirs(os.path.dirname(primofile))
		sgutils.showmsg("  writing index for " + sdir, 0)
		sgutils.file_write(primofile, "${listdirindex}\n${listfiles}\n", "w")

	for root, subdirs, files in os.walk(sdir):
		for fl in subdirs:
			adir = os.path.join(root, fl)
			primofile = os.path.join(adir, cfgget("indexfile") + cfgget("processingext"))
			if adir[-10:] != "thumbnails":
				if not os.path.exists(primofile):
					sgutils.showmsg("  writing index for " + sdir, 0)
					sgutils.file_write(primofile, "${dirupindex}\n\n${listdirindex}\n${listfiles}\n", "w")
			createdocschkfiles(os.path.join(sdir, fl))


def createdocschkfiles(sdir):
	""" checks files in the directories scanned by createdocs
	:param sdir:
	:return:
	"""
	if sdir[-10:] == "thumbnails":
		return
	for fn in os.listdir(sdir):
		if os.path.splitext(fn)[1] == cfgget("processingext"):
			imgfile = os.path.join(sdir, os.path.splitext(fn)[0] + ".jpg")
			thumbfile = os.path.join(sdir, "thumbnails", os.path.splitext(fn)[0] + ".jpg")
			if os.path.exists(imgfile):
				if not os.path.exists(thumbfile):
					graphicresize(imgfile, cfgget("docsimagewidth"), cfgget("imagesthumbwidth"))


def creategalleries(imagedir):
	"""procedure to check and build documents directory indexes
		it simplies run creategalliereswork multiple times"""
	dirlist = []
	sdir = os.path.join(cfgget("dirstart"), imagedir)

	mainfile = os.path.join(sdir, cfgget("indexfile") + cfgget("processingext"))
	if not os.path.exists(mainfile):
		sgutils.file_write(mainfile, "${listdirindex}", "w")

	for root, subdirs, files in os.walk(sdir):
		for fl in subdirs:
			dirlist.append(os.path.join(root, fl))

	for sdir in dirlist:
		if not fnmatch.fnmatch(sdir, "*/thumbnails"):
			creategallerieswork(sdir, False)


def creategallerieswork(sdir, singledir):
	"""a work for one single gallery
	;param sdir: directory where gallery is created/updated
	;param singledir: boolean true if is called from main routine, false if from single command
	:return: none
	"""
	if not sdir.startswith(cfgget("dirstart")):
		sdir = os.path.join(cfgget("dirstart"), sdir)
	if not os.path.exists(sdir):
		sgutils.showmsg("directory " + sdir + " doesn't exist", 99)
		return

	filelist = []
	files = os.listdir(sdir)
	mainfile = os.path.join(sdir, cfgget("indexfile") + cfgget("processingext"))
	vargallery = "glr_" + getdirectoryname(sdir)

	# the index file, should be quit empty
	if not os.path.exists(mainfile):
		sgutils.file_write(mainfile, "${listthumbs}", "w")

	# creates the text files near the images
	associatetexttoimage(sdir)

	for fm in files:
		if os.path.splitext(fm)[1] == ".jpg":
			if not fnmatch.fnmatch(os.path.join(sdir, fm), os.path.join("*", "thumbnails", "*.jpg")):
				filelist.append(fm)

	filelist.sort()
	cfgset(vargallery, filelist)

	for fm in filelist:
		imagefile = os.path.join(sdir, fm)
		thumbfile = os.path.join(sdir, "thumbnails", fm)

		if os.path.exists(thumbfile):
			if int(os.path.getmtime(imagefile)) > int(os.path.getmtime(thumbfile)):
				os.remove(thumbfile)

		if not os.path.exists(thumbfile):
			graphicresize(imagefile, cfgget("galleriesimagewidth"), cfgget("imagesthumbwidth"))


def createmap():
	"""build a map of the site"""
	filelist = []
	passlist = []

	sdir = cfgget("dirstart")
	imgdir = os.path.join(cfgget("dirstart"), cfgget("dirimages")) + os.sep
	permadir = os.path.join(cfgget("dirstart"), cfgget("dirperma")) + os.sep
	sitedir = os.path.join(cfgget("dirstart"), "site") + os.sep
	mapfile = os.path.join(sdir, "site", "map", cfgget("indexfile") + cfgget("processingext"))

	for root, subFolders, files in os.walk(sdir):
		for fn in files:
			fileroot = os.path.join(root, fn)
			if fnmatch.fnmatch(os.path.join(root, fn), '*' + cfgget("processingext")):
				if os.path.dirname(fileroot) != os.path.dirname(cfgget("dirstart")):
					if not fileroot.startswith(permadir):
						if not fileroot.startswith(sitedir):
							if not fileroot.startswith(imgdir) > 0:
								if not isprivate(fileroot):
									if fn.find(" ") < 0:
										if not fnmatch.fnmatch(fileroot, os.path.join("*", cfgget("dirposts"), "list*.*")):
											if not fnmatch.fnmatch(fileroot, os.path.join("*", cfgget("dirposts"), "archive*.*")):
												if not os.path.basename(fn) == "robots.txt":
													if fn.find(os.path.join("site", "map", cfgget("indexfile"))) < 0:
														filelist.append(fileroot)

	if filelist:
		for fn in sorted(filelist):
			fileroot = os.path.join(sdir, fn)
			newlink = os.path.splitext(fileroot)[0] + ".html"
			newlink = newlink.replace(cfgget("dirstart"), "${rootdir}")
			newpath = os.path.dirname(fileroot).replace(cfgget("dirstart"), "")
			if newpath.startswith(cfgget("dirposts")):
				newpath = newpath[:-6]
			newshow = fad(os.path.basename(os.path.splitext(newlink)[0]))

			mydiz = {}
			mydiz["link"] = sgutils.lnkc(newlink)
			mydiz["linktitle"] = newshow
			mydiz["linkpos"] = newpath

			passlist.append(mydiz)

	f = open(mapfile, "w")
	f.write(":> date:00000000\n")
	f.write(sgchunks.process(cfgget("chunk_map_page"), "repeat", passlist))
	f.close()


def createperma(linkname, fname):
	"""create a kind of permalink

	:param linkname: original link
	:param fname:
	:return:
	"""
	if cfgget("dirperma") == "":
		return

	linkpage = fname.replace(cfgget("dirstart"), "")
	linkpage = "../" + os.path.splitext(linkpage)[0] + ".html"

	permadir = os.path.join(cfgget("dirstart"), cfgget("dirperma"))
	templatefile = os.path.join(permadir, "template")
	nomefile = getfilenamefromstring(linkname)
	nomefile = os.path.join(permadir, nomefile) + cfgget("processingext")

	if not os.path.exists(permadir):
		os.makedirs(permadir)
	if not os.path.exists(templatefile):
		sgutils.file_write(templatefile, gen_getpermatemplate(), "w")

	sgutils.file_write(nomefile, gen_redirectcontent(linkpage), "w")


def createsitemap():
	""" build sitemap.xml of the site

	:return: none
	"""

	filelist = []
	imagedirs = []
	sdir = cfgget("dirstart")
	imgdir = cfgget("dirimages").split("|")
	for fn in imgdir:
		imagedirs.append(os.path.join(sdir, fn))

	mapfile = os.path.join(sdir, "sitemap.xml")
	sitendxfile = os.path.join(sdir, "siteindex.xml")

	for root, subFolders, files in os.walk(sdir):
		for fn in files:
			if fnmatch.fnmatch(os.path.join(root, fn), '*' + cfgget('processingext')):
				filelist.append(os.path.join(root, fn))

	filelist.sort()

	g = open(sitendxfile, "w")
	g.write(gen_getmapindex(True, True))
	g.write("\n  <sitemap>\n    <loc>http://" + cfgget("sitename") + "/" + os.path.basename(mapfile))

	f = open(mapfile, "w")
	f.write(gen_getmapindex(True, False))

	for fn in filelist:
		dontallow = False
		for l in imagedirs:
			if os.path.dirname(fn).startswith(l):
				dontallow = True
				break

		if not dontallow:
			if not isprivate(fn):
				if not fnmatch.fnmatch(fn, "*/" + cfgget("dirposts") + "/list*.*"):
					fdir = os.path.dirname(fn)
					if fnmatch.fnmatch(fdir, "*/[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]"):
						arr = fdir.rsplit(os.sep, -3)
						arr = arr[-3:]
						lastmod = "\n    <lastmod>" + "-".join(arr) + "</lastmod>"
					else:
						lastmod = "\n    <changefreq>monthly</changefreq>"
					fn = fwe(fn)
					fn = fn.replace(cfgget("dirstart"), "")
					fn = "\n  <url>\n    <loc>http://" + cfgget("sitename") + "/" + fn + ".html</loc>" + lastmod + "\n  </url>"
					f.write(fn)

	g.write("</loc>\n  </sitemap>")
	g.write(gen_getmapindex(False, True))
	f.write(gen_getmapindex(False, False))
	f.close()
	g.close()


def createposts(sdir):
	"""procedure to check and build posts files"""

	filelist = []
	global mypage

	# removing prebuilded index files
	for root, subFolders, files in os.walk(sdir):
		for fn in files:
			if fnmatch.fnmatch(os.path.join(root, fn), "*/list*.*"):
				os.remove(os.path.join(root, fn))
			if fnmatch.fnmatch(os.path.join(root, fn), "*/archive-*.*"):
				os.remove(os.path.join(root, fn))

	for root, subFolders, files in os.walk(sdir):
		for fn in files:
			if fnmatch.fnmatch(os.path.join(root, fn), '*/[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*' + cfgget("processingext")):
				filelist.append(os.path.join(root, fn))

	if not filelist:
		return
	filelist.sort(reverse=True)             # this set the list of files in blog part as sorted _
	filelist = listaset(filelist)           # from newest to oldest

	conto = len(filelist)                   # in filelist there are all posts now
	elepag = cfgget("maxpageitems")         # elements for page in lists
	pagine = cfgget("maxpages")             # calculated number of pages
	riquadri = int(elepag * pagine)         # total number of articles showed

	cfgset("lastpost", filelist[0])
	if not os.path.exists(os.path.join(sdir, cfgget("postsdir"), "template-index")):
		sgutils.file_write(os.path.join(sdir, cfgget("postsdir"), "template-index"), gen_gettemplateindex(), "w")

	if conto > 0:
		newlist = filelist[:riquadri]
		createpostsstream(newlist, "list")

	createpostsarchiveblock(filelist)


def createpostsarchiveblock(lista):
	"""  set the list of archives
	:param lista: posts to be showed
	:return: none
	"""

	directory = os.path.join(cfgget("dirstart"), cfgget("dirposts"))
	pos = len(os.path.join(cfgget("dirstart"), cfgget("dirposts") + os.sep))

	if cfgget("archivechunk") == "ok":
		filechunk = os.path.join(cfgget("dirstart"), "site", "vars", "z_archives_list")
		if os.path.exists(filechunk):
			os.remove(filechunk)

	cfgset("firstarchive", replacefirstarchivename(lista[0]))
	for n in lista:
		linkname = os.path.splitext(n[pos:])[0] + ".html"
		archivefile = os.path.join(directory, "archive-" + linkname[0:4] + "-" + linkname[5:7] + cfgget("processingext"))
		if not os.path.exists(archivefile):
			listaarc.append(archivefile)

		n = n.replace(cfgget("dirstart"), "")
		sgutils.file_write(archivefile, "<sqr:" + n + ">\n", "a")

	filechunkdyn = os.path.join(cfgget("dirstart"), "site", "vars", "z_archives_list")
	sgutils.file_write(filechunkdyn, "\n".join(listaarc).replace(cfgget("dirstart"), ""), "w")

	return


def createpostsstream(lista, cosa):
	sdir = os.path.join(cfgget("dirstart"), cfgget("dirposts"))

	conto = len(lista)  # in filelist there are all posts now
	elepag = cfgget("maxpageitems")  # elements for page in lists
	pagine = conto / elepag
	if conto % pagine > 0:
		pagine = math.floor(pagine + 1)
	riquadri = int(elepag * pagine)  # total number of articles showed
	progconto = 0
	indice = os.path.join(sdir, cosa)
	fileindice = indice + cfgget("processingext")
	res = ""

	for i in range(0, riquadri):
		# writing link to file
		if i == 0:
			filehome = os.path.join(sdir, cfgget("postsdir"), cfgget("indexfile") + cfgget("processingext"))
			sgutils.file_write(filehome, gen_redirectcontent(""), "w")

		if i % elepag == 0 and i > 0:
			res += createpostline(cosa, i, pagine)
			progconto += 1
			# todo
			f = open(fileindice, 'w')
			res = ":> title:" + cfgget("stringpostslisttitle") + "\n" + res
			f.write(res)
			fileindice = indice + "-" + str(progconto) + cfgget("processingext")
			res = ""

		if i < conto:
			nomefile = lista[i].replace(cfgget("dirstart"), "")
			res += "<sqr:" + nomefile + ">\n"

	res += createpostline(cosa, riquadri, pagine)
	res = ":> title:" + cfgget("stringpostslisttitle") + "\n" + res
	f = open(fileindice, 'w')
	f.write(res)


def createpostline(cosa, attuale, pagine):
	""" get the line of where are links to other index files

	"""
	passlist = []

	for i in range(0, int(pagine)):
		mydiz = {}
		if attuale == i:
			mydiz["working"] = " disabled"
		else:
			mydiz["working"] = ""

		mydiz["title"] = str(i)
		if i == 0:
			mydiz["link"] = "list.html"
		else:
			mydiz["link"] = "list-" + str(i) + ".html"

		passlist.append(mydiz)

	v = sgchunks.process("chunk_post_links", "repeat", passlist)
	return v


def createpostslink(nomefile, rootnode, cosa):
	if cosa == "link":
		v = os.path.splitext(nomefile)[0] + ".html"
		v = v[len(rootnode) + 1:]
	else:
		v = nomefile[len(rootnode):]
		v = v[1:11]

	v = seturlencode(v)

	return sgutils.lnkc(v)


def finalcopy():
	"""finally copy the files in destination directory"""

	sgutils.showmsg("Copying new files from \n  " + cfgget("dirstart") + " to \n  " + cfgget("dirfinal"), 0)
	listnew = []

	# creating list of files to be copied
	named = cfgget("filestocopy").split("|")
	filelist = []
	for root, dirnames, filenames in os.walk(cfgget("dirstart")):
		for extensions in named:
			for filename in fnmatch.filter(filenames, extensions):
				filelist.append(os.path.join(root, filename))

	for oldfile in filelist:
		nw = oldfile.replace(cfgget("dirstart"), cfgget("dirfinal"))

		if not os.path.exists(os.path.dirname(nw)):
			os.makedirs(os.path.dirname(nw))

		# TODO test with Windows
		# the meaning of the next rows is to test if a file should be linked or copied directly. There are
		# some conditions, and the os.name is put there until I will find if it's possible to do this with
		# Windows (of course, giving permissions to application)
		if cfgget("duplicatefiles") == "no" and os.path.splitext(nw)[1] in cfgget("duplicatefilesextensions"):
			modo = 1
		else:
			modo = 0
		if os.name == "nt":
			modo = 0

		if modo == 0:
			if not os.path.exists(nw):
				sgutils.showmsg("    copying " + oldfile, 0)
				shutil.copy2(oldfile, nw)
				listnew.append(nw)
			else:
				if not filecmp.cmp(oldfile, nw):
					os.remove(nw)
					sgutils.showmsg("  upgrading " + nw, 0)
					shutil.copy(oldfile, nw)
					listnew.append(nw)
		else:
			if not os.path.exists(nw):
				sgutils.showmsg("    linking " + oldfile, 0)
				sgutils.filelink(oldfile, nw)
				listnew.append(nw)
			else:
				if not filecmp.cmp(oldfile, nw):
					os.remove(nw)
					sgutils.showmsg("  changing date to " + nw, 0)
					sgutils.filedatemod(oldfile)
					listnew.append(nw)

	if cfgget("updatefilelist") == "ok":
		finalcopylist(listnew)

	# deleting all completed file to deduplicate data
	for oldfile in filelist:
		if os.path.splitext(oldfile)[1] == ".html":
			if os.path.exists(oldfile):
				os.remove(oldfile)


def finalcopylist(lista):
	"""add a file in the list of updated

	:param lista: the list of files to be copied
	:return: anything
	"""

	updfile = os.path.join(cfgget("tempdirectory"), cfgget("ftpfilelist"))
	sgutils.showmsg("  updating " + updfile, 0)

	# i remove it also if there aren't new files
	if os.path.exists(updfile):
		os.remove(updfile)

	if lista:
		res = sgchunks.process("chunk_updated_files", "upfile", lista)
		sgutils.file_write(updfile, res, "w")


def getdirectoryname(sdir):
	""" get directory name, only last name, and replace '-' with spaces
		to have a name for identifying cur dirs, example in replacebuttons() """
	v = sdir
	if not os.path.isdir(v):
		v = os.path.dirname(v)
	v = v.replace(cfgget("dirstart"), "").replace(os.sep, "-")
	return v


def getdirectoryshortname(sdir):
	""" get directory name, only last name
	:param sdir:
	:return:
	"""
	v = sdir
	if not os.path.isdir(v):
		v = os.path.dirname(v)
	v = os.path.basename(v)
	return v


def getfileinvar():
	""" read all files in the site/vars directory and assign their content
	to a variable with the file name included in global personalvars:
	if you put a file called myvar containing the words 'hi all', you
	will have a variable $myvar containing these words """
	global personalvars

	for root, subFolders, files in os.walk(os.path.join(cfgget("dirstart"), "site", "vars")):
		for fn in files:
			chkfile = os.path.join(root, fn)
			varname = os.path.basename(chkfile)
			res = sgutils.file_read(chkfile)
			personalvars[varname] = res


def getfilescript():
	""" read all files in the site/scripts directory and assign their content
	to a variable with the file name

	:return: aanything
	"""

	for root, subFolders, files in os.walk(os.path.join(cfgget("dirstart"), "site", "scripts")):
		for fn in files:
			chkfile = os.path.join(root, fn)
			varname = os.path.basename(chkfile)
			res = sgutils.file_read(chkfile)
			personalvars[varname] = ":> file:" + res


def getlanglinks(listanomi, thelink):
	""" transform the passed string, that can be divided by a pipe if multilanguage,
		in links or tags

	:param listanomi: the value passed, like 'it Indice|en List'
	:param thelink: present if mode is 'a'
	:return: the html part chunked from a file
	"""

	res = ""
	passlist = []
	mydiz = {}

	arr = listanomi.split("|")

	for nome in arr:
		mydiz = {}
		mydiz["link"] = thelink
		if len(arr) > 1:
			mydiz["classes"] = nome[:2]
			mydiz["text"] = nome[3:]
			mydiz["displaymode"] = "style='display:none;'"
		else:
			mydiz["classes"] = ""
			mydiz["text"] = nome
			mydiz["displaymode"] = ""

		passlist.append(mydiz)

	res = sgchunks.process("chunk_languages_links", "repeat", passlist)
	return res


def getlanglinksrows(listanomi, modo):
	""" transform the passed string, that can be divided by a pipe if multilangue,
		in links or tags

	:param listanomi: the value passed, like 'it Indice|en List'
	:param modo: essentially is the html tag
	:return:
	"""

	res = ""
	passlist = []
	mydiz = {}

	if modo == "":
		modo = "span"

	# if the names are not beginning with 2 chars intern. code

	arr = listanomi.split("|")

	for nome in arr:
		mydiz = {}
		mydiz["mode"] = modo

		if len(arr) > 1:
			mydiz["classes"] = nome[:2]
			mydiz["text"] = nome[3:]
			mydiz["displaymode"] = "style='display:none;'"
		else:
			mydiz["classes"] = ""
			mydiz["text"] = nome
			mydiz["displaymode"] = ""

		passlist.append(mydiz)

	res = sgchunks.process("chunk_languages_rows", "repeat", passlist)
	return res


def isprivate(nf):
	""" investigates if file must be in map """
	if cfgget("hiddenpaths") == "":
		return False

	elenco = cfgget("hiddenpaths").split("|")
	v = False

	if len(elenco) > 0:
		for nome in elenco:
			if nf.find(nome) >= 0:
				v = True
				break

	return v


def privatedirectoryset():
	"""create apache access configuration files for a directory"""

	if cfgget("appopenssl") == "":
		return

	lista = cfgget("privatedirectories").split("|")

	for sdir in lista:
		filepw = os.path.join(cfgget("dirstart"), sdir, cfgget("passwdfile"))
		if os.path.exists(filepw):
			sgutils.showmsg("Setting configuration access for " + sdir, 0)
			lines = sgutils.file_read(filepw).splitlines()

			res = ""
			for line in lines:
				if line.find(":") > 0:
					arr = line.split(":")
					if len(arr[1]) > 8:
						sgutils.showmsg("Passwords must be 8 chars, truncating", 0)
						arr[1] = arr[1][:8]
					if res == "":
						res = arr[0] + ":" + extgetcmd(cfgget("appopenssl") + " passwd -crypt -salt " + sgutils.getuniqueid("", "salt") + " " + arr[1])
					else:
						res += "\n" + arr[0] + ":" + extgetcmd(cfgget("appopenssl") + " passwd -crypt -salt " + sgutils.getuniqueid("", "salt") + " " + arr[1])

			sgutils.file_write(os.path.join(cfgget("dirstart"), sdir, ".htaccess"), gen_gethtaccess(sdir), "w")
			sgutils.file_write(os.path.join(cfgget("dirstart"), sdir, ".htpasswd"), res, "w")


def pageauthor(autore, email):
	""" return the name of the author, if present
	:param autore:
	:param email:
	:return:
	"""

	if autore != "" or email != "":
		mydiz = {}
		mydiz["author"] = autore
		mydiz["authormail"] = email

		return sgchunks.process("chunk_author_description", "", mydiz)
	else:
		return ""


def pageroot(nomefile):
	""" replace the full path of the file with the relative path between the site, to be linked
	:param nomefile:
	:return:
	"""

	try:
		# lnkc is to have a correct link if using Windows file system: until I won't comprise the
		# reasons of trailing points, I've to block some conditions
		htmlpath = sgutils.lnkc(os.path.relpath(cfgget("dirstart"), nomefile))
		if htmlpath.endswith("/.."):
			htmlpath = htmlpath[:-2]
		if htmlpath.startswith(".."):
			if not htmlpath.startswith("../"):
				htmlpath = htmlpath[2:]		
	except Exception:
		htmlpath = ""

	return htmlpath


def pagescriptresult(linea):
	""" return the result of a batch script file that is launched with file as parameter
	:param linea: line to be process
	:return:
	"""

	workfile = cfgget("z_currentfile")
	res = linea[linea.find("(") + 1:]
	res = res[:res.find(")"):]
	scriptfile = os.path.join(cfgget("dirstart"), "site", "scripts", res)
	res = extgetcmd('"' + scriptfile + '" "' + workfile + '"')

	return res


def replacedirdate(nomefile, modo):
	"""get directory as date for posts, if modo = 0, else, can take day, month or year
	:param nomefile: file name
	:param modo: the work of the function
	:return: the value of date """

	v = ""

	if fnmatch.fnmatch(nomefile, '*/[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*.*'):
		tmp = os.path.dirname(nomefile)[-10:]
		if modo == 0:
			v = sgchunks.process("chunk_article_date", "", {"moment":tmp})
		elif modo == 1:  # day
			v = sgchunks.process("chunk_article_date", "", {"moment":tmp[-2:]})
		elif modo == 2:  # month
			v = sgchunks.process("chunk_article_date", "", {"moment":tmp[5:7]})
		elif modo == 3:  # year
			v = sgchunks.process("chunk_article_date", "", {"moment":tmp[0:4]})
		elif modo == 5:
			v = sgchunks.process("chunk_localized_date", "", {"vday":tmp[-2:], "vmonth":tmp[5:7], "vyear":tmp[0:4], "vhour":"0", "vminute":"0", "vsecond":"0"})
		elif modo == 9:  # languages
			v = cfgget("languagedates")
			if v == "" or v.find("|") < 1:
				v = tmp
			else:
				lista = cfgget("languagedates").split("|")
				v = ""
				for item in lista:
					if fnmatch.fnmatch(item, "[a-z][a-z] *"):
						diz = {}
						diz["moment"] = sgchunks.process(item[3:], "", {"day":tmp[-2:], "month":tmp[5:7], "year":tmp[0:4]})
						diz["language"] = item[:2]
						v += sgchunks.process("chunk_archive_date_local", "", diz)
	return v


def replacedirfiles(nf):
	"""
	get a block of links from name of the files in the current directory
	:param nf: file name where results are inserted
	:return: the list
	"""
	dirlist = []
	passlist = []

	sdir = os.path.dirname(nf)
	for root, subdirs, files in os.walk(sdir):
		for fn in files:
			dirlist.append(os.path.join(root, fn))

	dirlist.sort()
	for fl in dirlist:
		if os.path.splitext(fl)[1] == cfgget("processingext"):
			filec = os.path.basename(nf)
			filec = os.path.splitext(filec)[0]
			nome = os.path.splitext(fl)[0]
			nome = nome.replace(os.path.dirname(nf) + os.sep, "")
			if not fnmatch.fnmatch(filec, "*" + str(nome)):
				fnom = os.path.basename(nome)
				mydiz = {}
				mydiz["link"] = nome + ".html"
				mydiz["linkname"] = sgutils.fad(fnom)
				passlist.append(mydiz)

	v = sgchunks.process("chunk_index_dir", "link", passlist)
	return v


def replacedirindex(nf):
	"""get a block of links from underlaying directories
	:param nf: the file name
	"""
	dirlist = []
	passlist = []

	sdir = os.path.dirname(nf)
	for root, subdirs, files in os.walk(sdir):
		for fl in subdirs:
			dirlist.append(os.path.join(root, fl))

	dirlist.sort()
	for fl in dirlist:
		nome = fl + "/" + cfgget("indexfile")
		if os.path.exists(nome + cfgget("processingext")):
			diz = {}
			diz["link"] = os.path.join(fl.replace(sdir + "/", ""), cfgget("indexfile") + ".html")
			diz["linkname"] = sgutils.fad(fl)
			passlist.append(diz)

	v = sgchunks.process("chunk_index_dir_list", "link", passlist)
	return v


def replacedirtitle(cosa):
	"""return the directory, without complete path, of the file"""
	v = os.path.dirname(cosa)
	arr = v.split(os.sep)
	v = replacetitle(arr[len(arr) - 1], 0)
	return v


def replaceencodedurl(nf, plus):
	"""  return encoded url for the page
	:param nf: file name
	:param plus: the mode for encoding (false='http%3A//gina.sc/wewe%26ddd%20ee', true='http%3A%2F%2Fgina.sc%2Fwewe%26ddd+ee')
	:return: encoded url
	"""

	v = "http://" + cfgget("sitename") + "/"
	nf = nf.replace(cfgget("dirstart"), "")
	nf = os.path.splitext(nf)[0] + ".html"
	res = v + nf

	# false is to encode normally
	if not plus:
		res = urllib.parse.quote(res)
	else:
		res = urllib.parse.quote_plus(res)

	return res


def replaceexecuted(code, whatfile):
	if code.find("${filename}") >= 0:
		code = code.replace("${filename}", whatfile)

	res = extgetcmd(code)
	return res


def replacefilelist(cosa):
	"""list of links for files"""

	workingfile = cfgget("z_currentfile")
	res = cosa.split("(")[-1]
	res = res.rsplit(")")[0]
	arr = res.split("|")

	lista = []
	files = os.listdir(os.path.join(os.path.dirname(workingfile)))
	for x in arr:
		lista.extend(fnmatch.filter(files, x))

	dontlink = os.path.splitext(workingfile)[0]
	passlist = []

	for x in sorted(lista):
		if x == dontlink + ".html":
			pass
		elif x == dontlink + ".jpg":
			pass
		elif x == workingfile:
			pass
		else:
			mydiz = {}
			mydiz["link"] = seturlencode(x)
			mydiz["linkname"] = seturlcleaning(x)
			passlist.append(mydiz)

	v = sgchunks.process("chunk_index_generic_files", "repeat", passlist)
	return v


def replacefirstarchive():
	"""the html name and pos of the last post"""
	nf = cfgget("firstarchive")

	if len(nf) > 10:
		return nf
	else:
		return ""


def replacefirstarchivename(valore):
	res = os.path.dirname(valore)[-10:]
	res = res[:7]
	res = "archive-" + res.replace(os.sep, "-") + ".html"

	return res


def replacekeys(nf):
	"""try to set some keywords for file from names

	:param nf: file name
	:return: the modified string
	"""
	v = mypage.keywords
	# if there aren't defined keywords, i get page file title
	if v == "":
		v = nf.replace(cfgget("dirstart"), "")
		v = os.path.splitext(v)[0]
		v = v.replace(os.sep, " ")
		v = v.replace("-", " ")
		oldv = v
		arr = v.split(" ")  # i split the path within spaces, then, if
		v = ""  # there are words that are more than 3 chars
		for k in arr:  # i use them for keywords, if not i take all words
			if len(k) > 3:
				if v == "":
					v = k
				else:
					v = v + " " + k
		if v == "":
			v = oldv
		v = v.replace(" ", ",")
	return v


def replacelanguage(linea):
	""" return a piece of html from chunk, generally can be
		a div with lang class
	:date: 2017-08-28
	:param linea: line to be process
	:return:
	"""

	diz = {}
	res = linea[linea.find("(") + 1:]
	res = res[:res.find(")"):]

	diz["language"] = res
	res = sgchunks.process("chunk_replace_language", "", diz)
	return res


def replacegallerybox(nomefile):
	"""
	:param nomefile:
	:return: a part with script and link to image files, to create a small lightbox gallery
	"""

	mydiz = {}
	mydiz["firstimage"] = ""
	mydiz["lightboximages"] = ""

	txtfiles = []
	imgfiles = []
	sdir = os.path.dirname(nomefile)

	for fn in os.listdir(sdir):
		if fn.find("thumbnails") < 0:
			if os.path.splitext(fn)[1] == cfgget("processingext"):
				txtfiles.append(os.path.splitext(fn)[0])

	sorted(txtfiles)
	for xfn in txtfiles:

		if os.path.exists(os.path.join(sdir, xfn)):
			for fn in sorted(os.listdir(os.path.join(sdir, xfn))):
				if os.path.splitext(fn)[1] == ".jpg":
					imgfiles.append(xfn + "/" + fn)
					filen = os.path.join(sdir, xfn, fn)
					thumbn = os.path.join(sdir, xfn, "thumbnails", fn)
					if not os.path.exists(thumbn) and fn == imgfiles[0]:
						try:
							if not os.path.exists(os.path.join(sdir, xfn)):
								os.makedirs(os.path.join(sdir, xfn))
							shutil.copy2(filen, thumbn)
							extgraphicresize(thumbn, cfgget("postsimagewidth"), "")
						except:
							pass

					if int(extgraphicinfo(filen, "arrdim")[0]) != cfgget("imagessmallgallerywidth"):
						extgraphicresize(filen, cfgget("imagessmallgallerywidth"), "")
		else:
			if len(txtfiles) == 1:
				for fn in sorted(os.listdir(sdir)):
					if os.path.splitext(fn)[1] == ".jpg":
						if os.path.splitext(fn)[0] != xfn:
							imgfiles.append(fn)
							filen = os.path.join(sdir, fn)
							thumbn = os.path.join(sdir, "thumbnails", fn)
							if not os.path.exists(thumbn) and fn == imgfiles[0]:
								try:
									if not os.path.exists(os.path.join(sdir, "thumbnails")):
										os.makedirs(os.path.join(sdir, "thumbnails"))
									shutil.copy2(filen, thumbn)
									extgraphicresize(thumbn, cfgget("postsimagewidth"), "")
								except:
									pass

							if int(extgraphicinfo(filen, "arrdim")[0]) != cfgget("imagessmallgallerywidth"):
								extgraphicresize(filen, cfgget("imagessmallgallerywidth"), "")

	if len(imgfiles) == 0:
		return ""
	else:
		mydiz["firstimage"] = "thumbnails/" + imgfiles[0]
		mydiz["lightboximages"] = "['" + "','".join(imgfiles) + "']"
		# tmp = Template(getsmallgalleryscript()).safe_substitute(flist="','".join(imgfiles))
		return sgchunks.process("chunk_gallery_box", "", mydiz)


def replacegallerybuttons(nf):
	"""get the links/buttons used in galleries
	:param nf: the file name where buttons are going to be placed
	:return: the html piece for buttons
	"""
	arr = cfgget("glr_" + getdirectoryname(nf))
	checkname = os.path.basename(fwe(nf) + ".jpg")

	if checkname == cfgget("indexfile") + ".jpg":
		return ""
	try:
		pos = arr.index(checkname)
	except:
		return ""
	diz = {}

	diz["description"] = fad(nf)
	diz["linkindex"] = cfgget("indexfile") + ".html"
	diz["linkfrst"] = "#"
	diz["linkprev"] = "#"
	diz["linknext"] = "#"
	diz["linklast"] = "#"
	diz["linkfrstdisable"] = ""
	diz["linkprevdisable"] = ""
	diz["linknextdisable"] = ""
	diz["linklastdisable"] = ""

	if pos == 0:
		if len(arr) > 1:
			diz["linknext"] = fwe(arr[pos + 1]) + ".html"
			diz["linklast"] = fwe(arr[len(arr) - 1]) + ".html"
			diz["linkfrstdisable"] = "disabled"
			diz["linkprevdisable"] = "disabled"
	elif pos == len(arr) - 1:
		if len(arr) > 0:
			diz["linkfrst"] = fwe(arr[0]) + ".html"
			diz["linkprev"] = fwe(arr[pos - 1]) + ".html"
			diz["linknextdisable"] = "disabled"
			diz["linklastdisable"] = "disabled"
	else:
		diz["linkfrst"] = fwe(arr[0]) + ".html"
		diz["linkprev"] = fwe(arr[pos - 1]) + ".html"
		diz["linknext"] = fwe(arr[pos + 1]) + ".html"
		diz["linklast"] = fwe(arr[len(arr) - 1]) + ".html"

	return sgchunks.process("chunk_gallery_buttons", "", diz)


def replacelastpost(nomefile):
	"""the html name and pos of the last post"""
	nf = cfgget("lastpost")
	chkdir = os.path.dirname(nomefile) + os.sep

	nf = fwe(nf.replace(chkdir, "")) + ".html"
	if len(nf) > 10:
		return nf
	else:
		return ""


def replacepagename(nf):
	"""get the name of the page file without extension"""
	if nf != "":
		pagename = os.path.basename(os.path.splitext(nf)[0])
		return pagename
	else:
		return ""


def replacepagepath(nf):
	"""get the path of the page, on the site"""
	if nf != "":
		pagepath = (os.path.splitext(nf)[0]).replace(cfgget("dirstart"), "")
		pagepath = os.path.dirname(pagepath.replace(os.sep, "/"))
		return pagepath
	else:
		return ""


def replacepathid(nf):
	"""get an unique identifier of a file to be used with services like disqus"""
	if mypage.uid == "":
		v = os.path.splitext(nf)[0]
		v = v.replace(cfgget("dirstart"), "")
		v = v.replace(os.sep, "-")
	else:
		v = mypage.uid

	return v


def replacepermalink():
	"""get an unique identifier of a file to be used as permalink"""
	if mypage.permalink == "":
		return ""

	v = sgchunks.process("chunk_permalink", "",
		{"newlink":cfgget("dirperma") + "/" + getfilenamefromstring(mypage.permalink) + ".html",
		"perma":mypage.permalink, "site":cfgget("sitename")})

	return v


def replacepostshistory(orfile):
	""" substitute the template word with the content of the file
	:return: the content of the composed file where every item is a link
	"""
	if cfgget("z_archives_list") == "":
		mylist = []

		overpath = os.path.basename(os.path.dirname(orfile))
		nomefile = os.path.join(cfgget("dirstart"), "site", "vars", "z_archives_list")
		readlist = sgutils.file_read(nomefile).split("\n")
		for l in readlist:
			tmp = os.path.splitext(l)[0]
			if tmp.startswith(overpath):
				tmp = tmp.replace(overpath + os.sep, "")

			diz = {}
			diz["link"] = tmp + ".html"
			tmp = tmp[-7:]
			diz["linkmonth"] = tmp[5:]
			diz["linkyear"] = tmp[:4]
			mylist.append(diz)

		return sgchunks.process(cfgget("chunk_archives_list"), "repeat", mylist)


def replacetags(nomefile):
	res = ""
	dirlist = []
	spath = os.path.join(cfgget("dirstart"), "site", "tags")
	for root, subdirs, files in os.walk(spath):
		for fn in files:
			if os.path.splitext(fn)[1] == cfgget("processingext"):
				if os.path.splitext(fn)[0] != cfgget("indexfile"):
					if os.path.splitext(fn)[0] != os.path.splitext(os.path.basename(nomefile))[0]:
						dirlist.append(os.path.join(root, fn))

	if len(dirlist) > 0:
		sorted(dirlist)
		for fn in dirlist:
			res += sgchunks.process("chunk_tags_list", "", {"p1":replacecrosslink(fn, nomefile, ""), "p2":replacetitle(fn, TITLE_CAP)})

	return res


def replacetemplate(nomefile, modo):
	""" return the name of template used by page
		1, then is for header, with header
		2. then is for page, only corrected name
		3. is the text of template
	:param modo:
	:param nomefile:
	:return:
	"""
	if nomefile == "":
		return "none"

	else:
		nnt = nomefile.replace(cfgget("dirstart"), "+")

		if modo == 1:
			res = "<meta name=\"template\" content=\"" + nnt + "\">"
		elif modo == 2:
			res = nnt
		else:
			try:
				res = sgutils.file_read(nomefile)
			except:
				res = ""

		return res


def replacetagfiles(nomefile, tagstring, isnodiv, iswritetagsfile, issummary):
	"""get a string, and if has commas, it is divided to set tags
	:param nomefile:
	:param tagstring:
	:param iswritetagsfile:
	:param issummary:
	:param isnodiv: check if a div should be used or not
	"""
	if tagstring == "":
		return ""
	else:
		tmp = tagstring

	if not isnodiv:
		res = "<div class='sgpoststags'>\nTags: "
	else:
		res = ""

	arr = tmp.split(",")

	for line in arr:
		line = line.strip()
		if issummary:
			res = res + "<a href='../site/tags/" + line + ".html'>" + line + "</a> "
		else:
			res = res + "<a href='" + pageroot(nomefile) + "site/tags/" + line + ".html'>" + line + "</a> "
		tagfile = os.path.join(cfgget("dirstart"), "site/tags", line + cfgget("processingext"))
		if iswritetagsfile:
			htmlfile = os.path.splitext(nomefile)[0] + ".html"
			# thumbfile = os.path.join(os.path.splitext(nomefile)[0], "thumbnails",os.path.splitext(os.path.basename(nomefile))[0] + ".jpg")
			dirfile = os.path.join(cfgget("dirstart"), "site", "tags", cfgget("indexfile") + cfgget("processingext"))
			if not os.path.exists(dirfile):
				sgutils.file_write(dirfile, "${listfiles}", "w")

			a = pageroot(tagfile) + htmlfile.replace(cfgget("dirstart"), "")
			b = replacetitle(os.path.splitext(os.path.basename(nomefile))[0], 0)
			sgutils.file_write(tagfile, Template(cfgget("chunk_tags_page_items")).safe_substitute(p1=a, p2=b), "a")

	if not isnodiv:
		res += "\n</div>\n"
	return res


def replacethumbs(fname):
	"""get a thumb view of the directory"""
	res = ""
	dn = os.path.dirname(fname)
	arr = cfgget("glr_" + getdirectoryname(dn))
	for fn in arr:
		res += Template(cfgget("chunk_gallerysquare")).safe_substitute(file=os.path.splitext(fn)[0], image=fn)
	return res


def replaceupindex():
	"""link to the index of the upper directory"""
	fd = cfgget("stringupindexlinkname")
	fn = cfgget("indexfile") + ".html"

	res = sgchunks.process("chunk_up_index", "", {"link":fn, "linktitle":fd})
	return res


def replacetitle(titolo, modo):
	"""
	:param titolo: stringo to be checked
	:param modo: mode of checking
	:return: changed title, 0=clear name,  1=div+h1 name, 2=script array format, 10=capitalized,
	"""

	v = ""

	if os.path.exists(titolo):
		titolo = os.path.splitext(os.path.basename(titolo))[0]

	if modo == TITLE_CAP:
		titolo = fad(titolo)
		return v

	# capitalize or leave as is?
	if titolo == titolo.lower():
		titolo = titolo.title()

	# if there aren't pipes dividing items
	if not titolo.find("|") > 0:
		if modo == 0:
			v = os.path.splitext(titolo)[0]
			v = fad(v)
		elif modo == 1:
			v = sgchunks.process("chunk_title_simple", "", {"title":titolo})
	else:
		titolo = titolo.replace(r"\,", "&#44;")

		if modo == 0:
			v = ""
			arr = titolo.split("|")
			for line in arr:
				brr = line.split(" ", 1)
				if not v == "":
					v += ", "
				v = v + brr[0] + " " + brr[1]
		elif modo == 1:
			v = ""
			arr = titolo.split("|")
			for line in arr:
				brr = line.split(" ", 1)
				v += sgchunks.process("chunk_title_mode1", "", {"languageclass":brr[0], "title": brr[1]})
		elif modo == 2:
			v = ""
			arr = titolo.split("|")
			for line in arr:
				brr = line.split(" ", 1)
				if not v == "":
					v += ","
				v = v + "'" + brr[0] + " " + brr[1] + "'"
		# simple translating of messages in span classes
		elif modo == 3:
			v = ""
			arr = titolo.split("|")
			for line in arr:
				brr = line.split(" ", 1)
				v += sgchunks.process("chunk_title_mode3", "", {"languageclass": brr[0], "title": brr[1]})

	return v


def replacetitleprep(nome):
	""" set the file name to be used later with replacetitle

	:param nome: file name
	:return: cleaned file name
	"""

	# presetting by title
	clnome = fwe(nome)

	if fnmatch.fnmatch(clnome, os.path.join(cfgget("dirstart"), cfgget("dirposts"), 'list*')):
		if not cfgget("postsindexestitle") == "":
			nome = cfgget("postsindexestitle")
		v = nome
	if fnmatch.fnmatch(clnome, os.path.join(cfgget("dirstart"), cfgget("dirposts"), 'archive*')):
		if not cfgget("postsarchivetopname") == "":
			nome = cfgget("postsarchivetopname")
		v = nome

	elif os.path.exists(nome):
		if os.path.isdir(nome):
			# lista=[]
			lista = nome.split(os.sep)
			v = lista[len(lista) - 1]
		else:
			v = os.path.basename(nome)
			v = fwe(v)

			if v == cfgget("indexfile"):
				v = getdirectoryshortname(nome)

		v = v.replace("-", " ")
		v = v.replace("_", "&#39;")
		v = v.title()
	else:
		v = nome

	return v


def replacecaption(titolo):
	""" used in $autotitle

	:param titolo; tipically the content of mypage.title
	:return: the title to be showed on caption
	"""
	if os.path.exists(titolo):
		titolo = os.path.splitext(os.path.basename(titolo))[0]

	if titolo.find("|") <= 0:
		v = titolo.replace("-", " ")
		v = v.replace("_", "'").title()
	else:
		v = ""
		arr = titolo.split("|")
		for line in arr:
			brr = line.split(" ", 1)
			if not v == "":
				v += ", "
			v = v + " " + brr[1]

	return v


def replacecrosslink(orlink, applyfile, supername):
	f1 = os.path.dirname(orlink)
	f1 = f1.replace(cfgget("dirstart"), "")

	f2 = pageroot(applyfile)
	if supername == "":
		orlink = os.path.splitext(orlink)[0] + ".html"
		return os.path.join(f2, f1, os.path.basename(orlink))
	else:
		return f2 + supername


def replacelistlinks(nf):
	""" put the links to previous and next post on the page
	:param nf: file name
	:return: the links next+prev on every page to go from last post to first in time
	"""

	mydiz = {}
	arr = listaget(nf)

	a = getlanglinksrows(cfgget("stringpostsnext"), "")
	b = getlanglinksrows(cfgget("stringpostsprev"), "")

	# todo todo
	mydiz["home"] = getlanglinks(cfgget("stringpostslineindexname"), "../../../list.html")
	mydiz["homedesc"] = replacetitle(cfgget("stringpostslineindexname"), 3)

	if arr[0] == "":
		mydiz["prevexpl"] = ""
		mydiz["prevlink"] = ""
	else:
		varbn = os.path.basename(arr[0])  # basename
		vardn = slashadd(os.path.dirname(arr[0]).replace(cfgget("dirstart"), ""))  # path without general and posts
		varnm = os.path.splitext(varbn)[0]  # only the name
		a = a + "<a href='" + pageroot(arr[0]) + vardn + varnm + ".html'>" + replacetitle(replacetitleprep(arr[0]), 0) + "</a>"
		mydiz["prevexpl"] = replacetitle(cfgget("stringpostsprev"), 3)
		mydiz["prevlink"] = a

	if arr[1] == "":
		mydiz["nextlink"] = ""
		mydiz["nextexpl"] = ""
	else:
		varbn = os.path.basename(arr[1])  # basename
		vardn = slashadd(os.path.dirname(arr[1]).replace(cfgget("dirstart"), ""))  # path without general and posts
		varnm = os.path.splitext(varbn)[0]  # only the name
		b += "<a href='" + pageroot(arr[1]) + vardn + varnm + ".html'>" + replacetitle(replacetitleprep(arr[1]), 0) + "</a>"
		mydiz["nextexpl"] = replacetitle(cfgget("stringpostsnext"), 3)
		mydiz["nextlink"] = b

	strt = cfgget("chunk_post_page_links")
	return sgchunks.process(strt, "", mydiz)


def replacenavbar(fname):
	""" insert the links bar to upper directories

	:param fname: file name to be processed
	:return: the html and javascript code
	"""
	sdir = os.path.dirname(fname).replace(cfgget("dirstart"), "")
	arr = sdir.split(os.sep)
	basedir = pageroot(fname)
	res = "<div class='sgnavbar'>\n"

	linkfile = os.path.join(cfgget("dirstart"), cfgget("indexfile") + cfgget("processingext"))
	if os.path.exists(linkfile):
		linkfile = os.path.join(pageroot(fname), cfgget("indexfile") + ".html")
		res += sgchunks.process(cfgget("chunk_navbar_items"), "", {"link":linkfile, "home":"Home"})

	sdir = cfgget("dirstart")
	for n in arr:
		sdir = os.path.join(sdir, n)
		basedir += n + "/"
		linkfile = os.path.join(sdir, cfgget("indexfile") + cfgget("processingext"))
		if os.path.exists(linkfile):
			linkfile = basedir + cfgget("indexfile") + ".html"
			res += sgchunks.process(cfgget("chunk_navbar_items"), "", {"link":linkfile, "home":n})
		else:
			res += sgchunks.process(cfgget("chunk_navbar_items"), "", {"link":"#' onClick='return false;", "home":n})

	res += "\n</div>\n"
	return res


def replacestat(nomefile, cosa, accessori):
	v = ""
	if cosa == "STATIMAGELASTMOD":
		nomefile = os.path.splitext(nomefile)[0] + ".jpg"
		if os.path.exists(nomefile):
			tmp = os.path.getmtime(nomefile)
			tmp2 = datetime.datetime.fromtimestamp(tmp)
			v = str(tmp2)[:16]
	elif cosa == "STATIMAGESIZE":
		nomefile = os.path.splitext(nomefile)[0] + ".jpg"
		if os.path.exists(nomefile):
			v = os.path.getsize(nomefile)
			if accessori == "b":
				v = str(v) + " bytes"
	elif cosa == "STATSIZE":
		if os.path.exists(nomefile):
			v = os.path.getsize(nomefile)
			if accessori == "b":
				v = str(v) + " bytes"
	elif cosa == "STATLASTMOD":
		v = sgutils.lastmod(nomefile, 0)
	return v


def replacepageimage(nf):
	""" when an image with same name of the page file is found, is added in a css in a
	    mode depending if is a normal page or a gallery
	:param nf: file name
	:return: the appropriate image link
	"""

	imagefile = os.path.splitext(nf)[0] + ".jpg"
	if os.path.exists(imagefile):
		res = imagefile
	else:
		imagefile = os.path.splitext(nf)[0] + ".png"
		if os.path.exists(imagefile):
			res = imagefile
		else:
			res = ""

	if not res == "":
		res = os.path.basename(res)
		commento = replacetitle(imagefile, TITLE_CAP)
		dimensioni = extgraphicinfo(imagefile, "linksize")

		basedir = nf.split(os.sep)[-3]
		if not basedir == cfgget("dirimages"):
			strt = cfgget("chunk_page_image")
		else:
			strt = cfgget("chunk_page_image_gallery")
		return sgchunks.process(strt, "", {"imagefile":res, "bounds":dimensioni, "description":commento})
	else:
		return ""


def replacepageurl(nf):
	v = cfgget("sitename") + "/"
	nf = nf.replace(cfgget("dirstart"), "")
	nf = os.path.splitext(nf)[0] + ".html"

	return v + nf


def putnewpost():
	""" move an eventual post to correct dir

	:return: anything
	"""
	sdir = cfgget("dirnewposts")
	if os.path.exists(sdir):
		filelist = []
		exte = []
		for root, subFolders, files in os.walk(sdir):
			for fn in files:
				filelist.append(os.path.join(root, fn))

		filelist.sort()
		for fn in filelist:
			exte.append(os.path.splitext(fn)[1])
		# this part look in the default directory, change the name of the image if needed
		# then move files in the correct post directory
		if not cfgget("processingext") in exte:
			return
		elif len(exte) == 0 or len(exte) > 2:
			return

		for fn in filelist:
			if not sgutils.checkpermission(fn, "write") or not sgutils.checkpermission(fn, "read"):
				sgutils.showmsg("Files in new posts directory haven't the right permissions, can't proceed.", 99)
				return

		if len(exte) == 2:
			if cfgget("processingext") in exte and ".jpg" in exte:
				if filelist[0].endswith(cfgget("processingext")):
					if not filelist[1] == os.path.splitext(filelist[0])[0] + ".jpg":
						os.rename(filelist[1], os.path.splitext(filelist[0])[0] + ".jpg")
				elif filelist[1].endswith(cfgget("processingext")):
					if not filelist[0] == os.path.splitext(filelist[1])[0] + ".jpg":
						os.rename(filelist[0], os.path.splitext(filelist[1])[0] + ".jpg")

		today = datetime.date.today()
		# dirposts can be multiple, first is used
		mynewpath = os.path.join(cfgget("dirstart"), cfgget("dirposts").split("|")[0], today.strftime('%Y'), today.strftime('%m'), today.strftime('%d'))
		if not os.path.exists(mynewpath):
			os.makedirs(mynewpath)
		# final move
		filelist = []
		for root, subFolders, files in os.walk(sdir):
			for fn in files:
				filelist.append(os.path.join(root, fn))

		for fn in filelist:
			shutil.move(fn, mynewpath)


def getencodedaddress(url):
	"""return an encoded url"""
	v = url.replace(" ", "%20")
	v = v.replace("/", "%2F")

	return v


def getfilenamefromstring(stringa):
	"""get a string and replace spaces and other chars to be used as file name without pain"""
	res = stringa.replace(" ", "-").lower()
	res = res.replace("'", "_")
	return res


def htmlbuild():
	""" main function to process all contents of all text files

	:return: anything
	"""
	filelist = []
	lastlist = []

	for root, subFolders, files in os.walk(cfgget("dirstart")):
		for fn in files:
			filelist.append(os.path.join(root, fn))

	cfgset("z_files", len(filelist))
	for fn in filelist:
		extension = os.path.splitext(fn)[1]
		if extension == cfgget("processingext"):
			htmlbuildprocess(fn)

	# lost directories: tags
	# some files are read only when processed, so a single pass
	# can't do all work
	for root, subFolders, files in os.walk(os.path.join(cfgget("dirstart"), "site", "tags")):
		for fn in files:
			extension = os.path.splitext(fn)[1]
			if extension == cfgget("processingext"):
				lastlist.append(os.path.join(root, fn))

	for fn in lastlist:
		htmlbuildprocess(fn)


def htmlbuildprocess(nf):
	"""build the static html file as we need"""

	global mypage
	mydict = {}
	mypage = Pagina()
	mypage.__init__()

	# if os.path.basename(nf) == "robots.txt":
	# return

	sgutils.showmsg(" processing " + nf, 0)
	mypage.currentfile = nf

	outfile = nf[:nf.rfind(".")] + ".html"
	fileimg = nf[:nf.rfind(".")] + ".jpg"

	if nf.find("access")>0:
		pass

	textget(nf, mypage)
	if not htmlbuildagecontrol(mypage.date):
		return

	templatefile = htmlbuildgettemplate(nf, mypage.template)
	strf = mypage.text

	# put image in file if present
	if os.path.exists(fileimg):
		strf = replacepageimage(nf) + "\n" + strf

	# template can contains some chunks to be changed in text of the template itself
	# noinspection PyArgumentEqualDefault

	strt = open(templatefile, 'r').read()
	strt = Template(strt).safe_substitute(listatmpl)
	strt = Template(strt).safe_substitute(personalvars)

	# BODY must be the first replace, due it can contains some other things
	strt = Template(strt).safe_substitute(body=strf)

	if len(personalvars) > 0:
		for x in sorted(personalvars.keys()):
			if strt.find(x) > 0:
				if personalvars[x].startswith(":> file:"):
					res = replaceexecuted(personalvars[x][8:], nf)
					mydict[x] = res
				elif personalvars[x].startswith(":> ref:"):
					res = replacecrosslink(personalvars[x][7:], nf, mypage.filename)
					mydict[x] = res
				else:
					mydict[x] = personalvars[x]

	# now i'm getting all variables, and the text to parse will be complete
	strt = Template(strt).safe_substitute(mydict)

	mydict["appname"] = "g.static site generator"
	if strt.find("title") > 0:
		mydict["autotitle"] = replacecaption(mypage.title)
		mydict["dirtitle"] = replacedirtitle(nf)
		mydict["title"] = replacetitle(mypage.title, 1)
	if strt.find("author") > 0:
		mydict["author"] = pageauthor(mypage.author, mypage.authormail)
	if strt.find("$date") > 0 or strt.find("${date") > 0:
		if strt.find("datedir") > 0:
			mydict["datedir"] = replacedirdate(nf, 0)
		if strt.find("dateday") > 0:
			mydict["dateday"] = replacedirdate(nf, 1)
		if strt.find("datemonth") > 0:
			mydict["datemonth"] = replacedirdate(nf, 2)
		if strt.find("dateyear") > 0:
			mydict["dateyear"] = replacedirdate(nf, 3)
		if strt.find("dateautolang") > 0:
			mydict["dateautolang"] = replacedirdate(nf, 5)
		if strt.find("datelang") > 0:
			mydict["datelang"] = replacedirdate(nf, 9)
	if strt.find("$dir") > 0 or strt.find("${dir") > 0:
		if strt.find("dirdocs") > 0:
			mydict["dirdocs"] = cfgget("dirdocs")
		if strt.find("dirimages") > 0:
			mydict["dirimages"] = cfgget("dirimages")
		if strt.find("dirposts") > 0:
			mydict["dirposts"] = cfgget("dirposts")
		if strt.find("dirupindex") > 0:
			mydict["dirupindex"] = replaceupindex()
	if strt.find("filename") > 0:
		mydict["filename"] = nf
	if strt.find("firstarchive") > 0:
		mydict["firstarchive"] = replacefirstarchive()
	if strt.find("gallerybox") > 0:
		mydict["gallerybox"] = replacegallerybox(nf)
	if strt.find("gallerybuttons") > 0:
		mydict["gallerybuttons"] = replacegallerybuttons(nf)
	if strt.find("keywords") > 0:
		mydict["keywords"] = replacekeys(nf)
	if strt.find("$list") > 0 or strt.find("${list") > 0:
		if strt.find("listdirindex") > 0:
			mydict["listdirindex"] = replacedirindex(nf)
		if strt.find("listgallerieslink") > 0:
			mydict["listgallerieslink"] = getlanglinks(cfgget("stringimageslinehomename"), "../" + cfgget("indexfile") + ".html")
		if strt.find("listfiles") > 0:
			mydict["listfiles"] = replacedirfiles(nf)
		if strt.find("listtags") > 0:
			if not nf == os.path.join(cfgget("dirstart"), "site", "tags", cfgget("indexfile") + cfgget("processingext")):
				mydict["listtags"] = replacetags(nf)
			else:
				mydict["listtags"] = ""
		if strt.find("listthumbs") > 0:
			mydict["listthumbs"] = replacethumbs(nf)
	if strt.find("lastpost") > 0:
		mydict["lastpost"] = replacelastpost(nf)
	if strt.find("navbar") > 0:
		mydict["navbar"] = replacenavbar(nf)
	if strt.find("pageencodedurl") > 0:
		mydict["pageencodedurl"] = replaceencodedurl(nf, False)
	if strt.find("pageencodedurlplus") > 0:
		mydict["pageencodedurlplus"] = replaceencodedurl(nf, True)
	if strt.find("pageimage") > 0:
		mydict["pageimage"] = replacepageimage(nf)
	if strt.find("pagename") > 0:
		mydict["pagename"] = replacepagename(nf)
	if strt.find("pagepath") > 0:
		mydict["pagepath"] = replacepagepath(nf)
	if strt.find("pageurl") > 0:
		mydict["pageurl"] = replacepageurl(nf)
	if strt.find("pathid") > 0:
		mydict["pathid"] = replacepathid(nf)
	if strt.find("permalink") > 0:
		mydict["permalink"] = replacepermalink()
	if strt.find("postlinks") > 0:
		mydict["postlinks"] = replacelistlinks(nf)
	if strt.find("postsarchives") > 0:
		mydict["postsarchives"] = replacepostshistory(nf)
	if strt.find("rootdir") > 0:
		mydict["rootdir"] = pageroot(nf)
	if strt.find("scriptlang") > 0:
		mydict["scriptlang"] = getlangscript(cfgget("languages"), replacetitle(mypage.title, 2))
	if strt.find("sitename") > 0:
		mydict["sitename"] = cfgget("sitename")
	if strt.find("$stat") > 0 or strt.find("${stat") > 0:
		if strt.find("statimagelastmod") > 0:
			mydict["statimagelastmod"] = replacestat(nf, "STATIMAGELASTMOD", "b")
		if strt.find("statimagesize") > 0:
			mydict["statimagesize"] = replacestat(nf, "STATIMAGESIZE", "b")
		if strt.find("statsize") > 0:
			mydict["statsize"] = replacestat(nf, "STATSIZE", "b")
		if strt.find("statlastmod") > 0:
			mydict["statlastmod"] = replacestat(nf, "STATLASTMOD", "")
	if strt.find("tags") > 0:
		mydict["tags"] = replacetagfiles(nf, mypage.tags, False, True, False)
	if strt.find("templatefile") > 0:
		mydict["templatefile1"] = replacetemplate(templatefile, 1)
		mydict["templatefile2"] = replacetemplate(templatefile, 2)
		mydict["templatefile3"] = replacetemplate(templatefile, 3)
	if strt.find("word") > 0:
			mydict["wordnext"] = getlanglinksrows(cfgget("setpostsnext"), "")
			mydict["wordprev"] = getlanglinksrows(cfgget("setpostsprev"), "")

	strt = Template(strt).safe_substitute(mydict)

	# print(mypage.filename)
	if not mypage.filename == "":
		outfile = os.path.join(os.path.dirname(outfile), mypage.filename)

	# a redirect file for php or other files. This proc places an html file that
	# contains the redirect js to file.
	if os.path.splitext(outfile)[1] != ".html":
		if cfgget("htmlredirect") == "ok":
			if not os.path.basename(outfile).startswith("."):
				f = open(os.path.splitext(outfile)[0] + ".html", "w")
				f.write(gen_getredirectfilecontent(os.path.basename(outfile)))
				f.close()

	# normal writing of file	
	sgutils.file_write(outfile, strt, "w")
	
	if cfgget("filepostprocessor") != "":
		cmdline = Template(cfgget("filepostprocessor")).safe_substitute(file=outfile)
		extruncmd(cmdline, False)


def htmlbuildagecontrol(fdate):
	"""
	:param fdate: last saved file changes
	:return: a false or true to the request of process file due the age
	"""
	eta = sgconf.cfgget("processingonagedays")
	cur = sgconf.cfgget("z_currentdate")
	fda = int(fdate)

	try:
		if eta == 0:
			return True
		else:
			if (cur - fda) <= eta:
				return True
			else:
				return False
	except:
		return True


def htmlbuildgettemplate(nf, personalized):
	"""get template file for a specified file: it gets first the file in slug, then template-name, then"
	upper dirs template-name-all, then template: it can be a bit confusing, but consistency is using"
	a template file in root dir, in second looking for a template without -, then slugging templates,
	then again using template-index-all the inside name. With a file called abc.md, for example
	"""

	if personalized != "":
		tp = os.path.join(cfgget("dirstart"), "site", "tmpl", personalized)

		if os.path.exists(tp):
			return tp

	# template-all
	v = ""
	tp = nf
	basenf = os.path.basename(nf)
	upfile = os.path.dirname(nf)

	# first case the mask
	os.chdir(upfile)
	for file in glob.glob("template-(*)"):
		maskstring = "*" + file.partition("(")[2].partition(")")[0] + "*"
		if fnmatch.fnmatch(nf, maskstring):
			return file

	upfile = os.path.join(os.path.dirname(upfile), "template-" + os.path.splitext(basenf)[0] + "-all")
	samelevelfile = os.path.join(os.path.dirname(nf), "template-" + os.path.splitext(basenf)[0])

	sameclassfile = os.path.splitext(basenf)[0]
	if sameclassfile.find("-") > 0:
		sameclassfile = sameclassfile[:sameclassfile.find("-")]
		sameclassfile = os.path.join(os.path.dirname(nf), "template-" + sameclassfile)
	else:
		sameclassfile = ""

	# template-nomefile
	if os.path.exists(samelevelfile):
		return samelevelfile
	elif os.path.exists(sameclassfile):
		return sameclassfile
	elif os.path.exists(upfile):
		return upfile
	else:
		# template until find
		while 1 > 0:
			tp = tp[:tp.rfind(os.sep)]
			if os.path.exists(os.path.join(tp, "template")) or tp == "":
				v = os.path.join(tp, "template")
				break

		# last chance: if not exists any of them,
		# get the first

		return v


def textget(nomefile, mypage):
	""" procedure to get future html text

	:param nomefile: file name to be parsed
	:param mypage: the mypage object class
	:return: all properties
	"""

	mypage.title = ""
	mypage.filepath = nomefile
	mypage.date = 0
	mypage.pause = False
	cfgset("z_currentfile", nomefile)

	testo = sgutils.file_read(nomefile)

	if not testo.startswith(":> date:") or testo.find("\n>: update:") > 0:
		if cfgget("replacefromfile") == "ok":
			testo = sgutils.file_search_replace(testo)
		if cfgget("filepreprocessor") != "":
			cmdline = Template(cfgget("filepreprocessor")).safe_substitute(file=nomefile)
			extruncmd(cmdline, False)

		if testo.find(":> uid:") < 0:
			testo = ":> date:" + datetime.date.today().strftime('%Y%m%d') + "\n:> uid:" + sgutils.getuniqueid(nomefile, "fileid") + "\n" + testo
		else:
			testo = ":> date:" + datetime.date.today().strftime('%Y%m%d') + "\n" + testo
		sgutils.file_write(nomefile, testo, "w")
		testo = sgutils.file_read(nomefile)

	# testo=markupreplacesubst(testo)
	testo = testo.replace("\\$", "&#36;")
	testo = testo.replace("\\%", "&#37;")
	testo = testo.replace("\\_", "&#95;")
	testo = testo.replace("\\/", "&#47;")
	testo = testo.replace("\\*", "&#42;")
	testo = testo.replace("\\#", "&#35;")
	testo = testo.replace("\\[", "&#91;")
	testo = testo.replace("\\]", "&#93;")
	testo = testo.replace("\\{", "&#123;")
	testo = testo.replace("\\}", "&#125;")
	testo = testo.replace("\\<", "&#60;")
	testo = testo.replace("\\>", "&#62;")

	lines = testo.split("\n")
	primariga = -1

	for line in lines:
		primariga += 1

		if line.startswith(":> tags:"):
			mypage.tags = line[8:].lower()
		elif line.startswith(":> title:"):
			mypage.title = line[9:]
		elif line.startswith(":> ref:"):
			varname = line[7:]
			personalvars[varname] = ":> ref:" + nomefile
		elif line.startswith(":> amail:"):
			mypage.authormail = line[9:]
		elif line.startswith(":> author:"):
			mypage.author = line[10:]
		elif line.startswith(":> file:"):
			tmp = line[8:]
			if tmp.find(os.sep) < 0:
				tmp = os.path.join(os.path.dirname(nomefile), tmp)
			if os.path.exists(tmp):
				pos = lines.index(line)             # line position
				testo2 = sgutils.file_read(tmp)     # get content of the second file
				arr = testo2.split("\n")            # i read file and split in lines
				lines.pop(pos)
				if arr[-1] == "":
					del arr[-1]
				for l in arr:
					lines.insert(pos, l)
					pos += 1
		elif line.startswith(":> filename:"):
			mypage.filename = line[12:].strip()
		elif line.startswith(":> keys:"):
			mypage.keywords = line[8:].strip()
		elif line.startswith(":> tmpl:"):
			mypage.template = line[8:].strip()
		elif line.startswith(":> date:"):
			mypage.date = line[8:]
			if cfgget("rsscreate") == "ok":
				sgrss.rssaddtolist(nomefile, mypage.date)
		elif line.startswith(":> perm:"):
			mypage.permalink = line[8:]
			createperma(mypage.permalink, nomefile)
		elif line.startswith(":> raw:"):
			mypage.raw = line[7:].strip()
		elif line.startswith(":> uid:"):
			mypage.uid = line[7:].strip()
		elif line.startswith(":> pause"):
			mypage.pause = True
		elif line.startswith(":> update"):
			mypage.update = True
		elif line.startswith(":> @"):
			tmp = line[4:]
			if fnmatch.fnmatch(tmp, "*:*"):
				mypage.xdict[tmp.split(":")[0]] = tmp.split(":", 1)[1]
		else:
			break

	if mypage.raw.lower() == "yes":
		mypage.text = '\n'.join(lines[primariga:])
	else:
		mypage.text = markup(lines[primariga:])

	if len(mypage.xdict) > 0:
		mypage.text = Template(mypage.text).safe_substitute(mypage.xdict)

	stats = os.stat(nomefile)
	mypage.filesize = str(stats.st_size)
	mypage.filelstm = str(stats.st_mtime)

	# fallback
	if mypage.title == "":
		mypage.title = replacetitleprep(nomefile)


if __name__ == "__main__":
	sgutils.showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)