#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" configuration module for gstatic: it includes the routines to modify work of application"""

import os
import sys
import tempfile
import datetime
from sgglobals import *
from configparser import ConfigParser


class CaseConfigParser(ConfigParser):
	"""subclassing necessary due configparser lower the
	case of the keys, an aestethic fix"""
	def optionxform(self, optionstr):
		return optionstr


cfg = {}  # prog variables
listaposts = []  # list of posts
listatmpl = {}  # list of template chunks


def getconf(myparser, ssect, skey):
	""" get a variable set into the conf file """

	res = myparser.get(ssect, skey)
	if res.isdigit():
		return int(res)
	else:
		return res


# noinspection PyArgumentEqualDefault
def readconf(sitedirectory):
	"""controlla il file site.conf"""
	
	iparse = CaseConfigParser(allow_no_value=True)
	conffile = os.path.join(sitedirectory, "site", "site.conf")

	if os.path.exists(conffile):
		with open(conffile, 'r', encoding='utf-8') as f:
			try:
				iparse.read_file(f)
			except:
				f.close()
				return
			f.close()
	else:
		return

	today = datetime.datetime.now()

	cfgset("archivechunk", getconf(iparse, "Posts", "ArchiveChunk"))
	cfgset("buildmappage", getconf(iparse, "Jobs", "BuildMapPage"))
	cfgset("buildsitemap", getconf(iparse, "Jobs", "BuildSiteMap"))
	cfgset("dirbackup", rcchk(getconf(iparse, "Paths", "BackupDirectory"), 2))
	cfgset("dirdocs", getconf(iparse, "Paths", "DocumentsDirectories"))
	cfgset("dirfinal", rcchk(getconf(iparse, "Paths", "FinalDirectory"), 1, "dirfinal"))
	cfgset("dirperma", getconf(iparse, "Paths", "PermalinksDirectory"))
	cfgset("dirposts", getconf(iparse, "Paths", "PostsDirectories"))
	cfgset("dirimages", getconf(iparse, "Paths", "ImagesDirectories"))
	cfgset("dirnewposts", rcchk(getconf(iparse, "Paths", "NewPostsDirectory"), 2))
	cfgset("duplicatefiles", getconf(iparse, "Jobs", "DuplicateFiles"))
	cfgset("duplicatefilesextensions", getconf(iparse, "Jobs", "DuplicateFilesExtensions"))
	cfgset("docsimagewidth", getconf(iparse, "Images", "DocumentsImageWidth"))
	cfgset("filepreprocessor", rcchk(getconf(iparse, "Paths", "FilePreProcessor"), 2))
	cfgset("filepostprocessor", rcchk(getconf(iparse, "Paths", "FilePostProcessor"), 2))
	cfgset("filestocopy", getconf(iparse, "Jobs", "FilesToCopy"))
	cfgset("finalcleaning", getconf(iparse, "Jobs", "FinalCleaning"))
	cfgset("ftpfilelist", getconf(iparse, "Paths", "FtpFileList"))
	cfgset("galleriesimagewidth", getconf(iparse, "Images", "GalleriesImageWidth"))				# gallery width
	cfgset("imagesresolution", getconf(iparse, "Images", "ImagesResolution"))							#
	cfgset("imagescompression", getconf(iparse, "Images", "ImagesCompression"))							# level of jpg compression after resize/cut
	cfgset("imagessmallgallerywidth", getconf(iparse, "Images", "SmallImageWidth"))
	cfgset("imagestriptags", rcchk(getconf(iparse, "Images", "StripTags"), 101))
	cfgset("imagesthumbwidth", getconf(iparse, "Images", "ImagesThumbWidth"))
	cfgset("indexfile", getconf(iparse, "Jobs", "IndexFile"))
	cfgset("initialcleaning", getconf(iparse, "Jobs", "InitialCleaning"))
	cfgset("languages", rcchk(getconf(iparse, "Site", "Languages"), 4))
	cfgset("languagedates", getconf(iparse, "Jobs", "LanguageDates"))
	cfgset("maxpages", getconf(iparse, "Posts", "MaxPages"))
	cfgset("maxpageitems", getconf(iparse, "Posts", "MaxPageItems"))
	cfgset("passwdfile", getconf(iparse, "Jobs", "PasswdFile"))
	cfgset("postsimagewidth", getconf(iparse, "Images", "PostImageWidth"))
	cfgset("postsummarylength", getconf(iparse, "Posts", "PostSummaryLength"))
	cfgset("poststhumbwidth", getconf(iparse, "Images", "PostThumbnailWidth"))
	cfgset("privatedirectories", getconf(iparse, "Paths", "PrivateDirectories"))
	cfgset("processingonagedays", getconf(iparse, "Jobs", "ProcessingAgeDays"))
	cfgset("replacefromfile", getconf(iparse, "Jobs", "UseReplaceConf"))
	cfgset("rsscreate", getconf(iparse, "RSS", "Create"))
	cfgset("rssauthor", getconf(iparse, "RSS", "RSSAuthor"))
	cfgset("rssdescription", getconf(iparse, "RSS", "RSSDescription"))
	cfgset("rsslistlength", getconf(iparse, "RSS", "RSSListLength"))						# max num of rss items
	cfgset("rssnoadd", getconf(iparse, "RSS", "RSSDontAddThese"))
	cfgset("rsssummarylength", getconf(iparse, "RSS", "RSSSummaryLength"))
	cfgset("hiddenpaths", rcchk(getconf(iparse, "Paths", "HiddenPaths"), 7))
	cfgset("processingext", rcchk(getconf(iparse, "Jobs", "ProcessingFileExtension"), 5))
	cfgset("hideprogressmessages", getconf(iparse, "Jobs", "ShowMessages"))
	cfgset("htmlredirect", rcchk(getconf(iparse, "Site", "HtmlRedirect"), "ok"))
	cfgset("sitename", getconf(iparse, "Site", "SiteName"))
	cfgset("sitepath", getconf(iparse, "Site", "SitePath"))
	cfgset("saltprefix", getconf(iparse, "Jobs", "SSLSaltPrefix"))
	cfgset("tempdirectory", rcchk(getconf(iparse, "Paths", "TemporaryDirectory"), 1, "tempdirectory"))
	cfgset("updatefilelist", getconf(iparse, "Jobs", "UpdateFileList"))
	#
	cfgset("stringgallerieslinehomename", getconf(iparse, "Images", "ImagesLineHomeName"))
	cfgset("stringpostslisttitle", getconf(iparse, "Posts", "ListTitle"))                #
	cfgset("stringpostslineindexname",  getconf(iparse, "Posts", "LineIndexName"))
	cfgset("stringpostsnext", getconf(iparse, "Posts", "LineNext"))
	cfgset("stringpostsprev", getconf(iparse, "Posts", "LinePrev"))
	cfgset("stringpostsindextop", getconf(iparse, "Posts", "IndexTopDef"))
	cfgset("stringpostsarchivetopname", getconf(iparse, "Posts", "ArchiveTopDef"))
	cfgset("stringupindexlinkname",  getconf(iparse, "Posts", "UpIndexLinkName"))
	cfgset("stringimageslinehomename", getconf(iparse, "Images", "ImagesHomeName"))

	# these aren't set by user, but are transitory values

	cfgset("z_archives_list", "")
	cfgset("z_currentfile", "")
	cfgset("z_currentdate", today.strftime('%Y') + today.strftime('%m') + today.strftime('%d'))
	cfgset("z_files", 0)						# counter for file processe
	cfgset("firstarchive", "")  				# the first archive file
	cfgset("lastpost", "")						# last inserted post


def rcchk(cosa, modo, *args):
	""" check how some values are inserted in conf.file, called by readconf()
		cosa: the value
		modo: formatting
	"""

	if modo == 1:  # path must exists or app is stopped
		if cosa == "" or not os.path.exists(cosa):
			sgutils.showmsg(cosa + "\ndirectory doesn't exist", MESSAGE_ERROR)
			if args:
				sgutils.showmsg("About: " + args[0], MESSAGE_DEBUG)
			sys.exit()
		else:
			return cosa
	elif modo == 2:  # path must exists if set, or app is stopped
		if cosa != "":
			if not os.path.exists(cosa):
				cosa = os.path.exists(os.path.join(cfgget("dirstart"), cosa))
				if args:
					sgutils.showmsg("About: " + args[0], MESSAGE_DEBUG)

		if cosa != "":
			if not os.path.exists(cosa):
				sgutils.showmsg(cosa + "\ndirectory doesn't exist, but has been set", MESSAGE_DEBUG)
				sys.exit()

		return cosa
	elif modo == 4:
		elenco = cosa.split("|")
		if len(elenco) > 1:
			cfgset("defaultlang", elenco[0])
			return cosa.replace("|", ",")
		else:
			return ""
	elif modo == 5:  # add a . to a file ext)
		if cosa.startswith("*"):
			cosa = cosa[1:]
		if not cosa.startswith("."):
			cosa = "." + cosa
		return cosa
	elif modo == 7:  # trim
		return cosa.strip()
	elif modo == 101:  # convert from ok to -strip
		if cosa == "ok":
			return "-strip"
		else:
			return "no"


def cfgset(key, value):
	"""set a program variable to 'value

	:param key: the key of conf dictionary
	:param value: value of key
	:return: none
	"""
	global cfg
	if key == "dirstart":
		value = slashadd(value)
	elif key == "dirfinal":
		value = slashadd(value)
	cfg[key] = value


def cfgget(k):
	""" get a program variable

	:param k: the name of the value
	:return: the value
	"""
	return cfg.get(k, '')


def listaset(elenco):
	""" set a value for list elenco

	:param elenco: the list to be set in elenco
	:return: a more ordered list
	"""
	global listaposts
	listaposts = elenco
	cfgset("sgpostcount", len(listaposts))
	return listaposts


def listaget(nf):
	"""get a value from list

	:param nf: file name of start pos
	:return: the limits of the 'lista'
	"""
	try:
		num = listaposts.index(nf)
		nmx = len(listaposts) - 1
		if num == 0:
			return "", listaposts[1]
		elif num == nmx:
			return listaposts[nmx], ""
		elif num == -1:
			return "", ""
		else:
			return listaposts[num - 1], listaposts[num + 1]
	except:
		return "", ""


def listaall():
	"""return all the list listaposts"""
	return listaposts


def slashadd(tocosa):
	""" add a final slash to an element if present

	:param tocosa: the string to be set
	:return: string with final slash
	"""

	v = tocosa
	if tocosa[-1:] == os.sep:
		return v
	else:
		return v + os.sep


def slashremove(tocosa):
	""" remove the final slash if present

	:param tocosa: the string to be modified
	:return: modified string
	"""
	v = tocosa
	if tocosa[-1:] == os.sep:
		return v[:len(tocosa) - 1]
	else:
		return v


def conf_settemplatechunks():
	""" read pieces of templates """
	global listatmpl

	sdir = os.path.join(cfgget("dirstart"), "site", "tmpl")
	for fn in os.listdir(sdir):
		listatmpl[fn] = sgutils.file_read(os.path.join(sdir, fn))


if __name__ == "__main__":
	sgutils.showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)
