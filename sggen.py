#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import datetime
import tempfile
import sgchunks

from sgexternal import *
from sgglobals import *
from configparser import ConfigParser


class CaseConfigParser(ConfigParser):
	"""subclassing necessary due configparser lower the
	case of the keys, an aestethic fix"""
	def optionxform(self, optionstr):
		return optionstr


# noinspection PyArgumentEqualDefault
def createconfigfile(creatingdirectory):
	""" create a configuration file for the site
	moved to sgconf to don't use imports """

	iparse = CaseConfigParser(allow_no_value=True)
	conffile = os.path.join(creatingdirectory, "site", "site.conf")

	if os.path.exists(conffile):
		with open(conffile, 'r', encoding='utf-8') as f:
			try:
				iparse.read_file(f)
			except:
				f.close()
				return
			f.close()

	# site -----------------------------------------------------------------------------------
	if not iparse.has_section("Site"):
		iparse.add_section("Site")
	if not iparse.has_option("Site", "Created"):
		iparse.set("Site", "Created", datetime.date.today().strftime("%Y-%m-%d"))
	if not iparse.has_option("Site", "SiteName"):
		iparse.set("Site", "SiteName", "My site name")
	if not iparse.has_option("Site", "SitePath"):
		iparse.set("Site", "SitePath", "/www")
	if not iparse.has_option("Site", "Languages"):
		iparse.set("Site", "Languages", "en")
	if not iparse.has_option("Site", "HtmlRedirect"):
		iparse.set("Site", "HtmlRedirect", "ok")

	# paths -----------------------------------------------------------------------------------
	if not iparse.has_section("Paths"):
		iparse.add_section("Paths")
	if not iparse.has_option("Paths", "BackupDirectory"):
		iparse.set("Paths", "BackupDirectory", "")
	if not iparse.has_option("Paths", "DocumentsDirectories"):
		iparse.set("Paths", "DocumentsDirectories", "documents")
	if not iparse.has_option("Paths", "FilePreProcessor"):
		iparse.set("Paths", "FilePreProcessor", "")
	if not iparse.has_option("Paths", "FilePostProcessor"):
		iparse.set("Paths", "FilePostProcessor", "")
	if not iparse.has_option("Paths", "FinalDirectory"):
		iparse.set("Paths", "FinalDirectory", "")
	if not iparse.has_option("Paths", "FtpFileList"):
		iparse.set("Paths", "FtpFileList", "gstatic_updated_files.tmp")
	if not iparse.has_option("Paths", "NewPostsDirectory"):
		iparse.set("Paths", "NewPostsDirectory", "")
	if not iparse.has_option("Paths", "ImagesDirectories"):
		iparse.set("Paths", "ImagesDirectories", "images")
	if not iparse.has_option("Paths", "PrivateDirectories"):
		iparse.set("Paths", "PrivateDirectories", "")
	if not iparse.has_option("Paths", "PermalinksDirectory"):
		iparse.set("Paths", "PermalinksDirectory", "l")	
	if not iparse.has_option("Paths", "PostsDirectories"):
		iparse.set("Paths", "PostsDirectories", "l")
	if not iparse.has_option("Paths", "HiddenPaths"):
		iparse.set("Paths", "HiddenPaths", "")
	if not iparse.has_option("Paths", "TemporaryDirectory"):
		iparse.set("Paths", "TemporaryDirectory", tempfile.gettempdir())
	# posts -----------------------------------------------------------------------------------
	if not iparse.has_section("Posts"):
		iparse.add_section("Posts")
	if not iparse.has_option("Posts", "ArchiveChunk"):
		iparse.set("Posts", "ArchiveChunk", "ok")
	if not iparse.has_option("Posts", "ArchiveTopDef"):
		iparse.set("Posts", "ArchiveTopDef", "Index")
	if not iparse.has_option("Posts", "IndexTopDef"):
		iparse.set("Posts", "IndexTopDef", "Index")
	if not iparse.has_option("Posts", "LineNext"):
		iparse.set("Posts", "LineNext", "Next")
	if not iparse.has_option("Posts", "LinePrev"):
		iparse.set("Posts", "LinePrev", "Prev")
	if not iparse.has_option("Posts", "MaxPages"):
		iparse.set("Posts", "MaxPages", "10")
	if not iparse.has_option("Posts", "LineIndexName"):
		iparse.set("Posts", "LineIndexName", "List")
	if not iparse.has_option("Posts", "ListTitle"):
		iparse.set("Posts", "ListTitle", "List")
	if not iparse.has_option("Posts", "MaxPageItems"):
		iparse.set("Posts", "MaxPageItems", "12")
	if not iparse.has_option("Posts", "PostSummaryLength"):
		iparse.set("Posts", "PostSummaryLength", "300")
	if not iparse.has_option("Posts", "UpIndexLinkName"):
		iparse.set("Posts", "UpIndexLinkName", "[*]")
	# images -----------------------------------------------------------------------------------
	if not iparse.has_section("Images"):
		iparse.add_section("Images")
	if not iparse.has_option("Images", "ImagesCompression"):
		iparse.set("Images", "ImagesCompression", "95")
	if not iparse.has_option("Images", "ImagesResolution"):
		iparse.set("Images", "ImagesResolution", "200")
	if not iparse.has_option("Images", "ImagesThumbWidth"):
		iparse.set("Images", "ImagesThumbWidth", "150")
	if not iparse.has_option("Images", "GalleriesImageWidth"):
		iparse.set("Images", "GalleriesImageWidth", "800")
	if not iparse.has_option("Images", "DocumentsImageWidth"):
		iparse.set("Images", "DocumentsImageWidth", "400")
	if not iparse.has_option("Images", "PostImageWidth"):
		iparse.set("Images", "PostImageWidth", "400")
	if not iparse.has_option("Images", "PostThumbnailWidth"):
		iparse.set("Images", "PostThumbnailWidth", "100")
	if not iparse.has_option("Images", "SmallImageWidth"):
		iparse.set("Images", "SmallImageWidth", "800")
	if not iparse.has_option("Images", "ImagesHomeName"):
		iparse.set("Images", "ImagesHomeName", "Galleries")
	if not iparse.has_option("Images", "ImagesLineHomeName"):
		iparse.set("Images", "ImagesLineHomeName", "Other galleries")
	if not iparse.has_option("Images", "StripTags"):
		iparse.set("Images", "StripTags", "")
	# jobs  -----------------------------------------------------------------------------------
	if not iparse.has_section("Jobs"):
		iparse.add_section("Jobs")
	if not iparse.has_option("Jobs", "BuildMapPage"):
		iparse.set("Jobs", "BuildMapPage", "no")
	if not iparse.has_option("Jobs", "BuildSiteMap"):
		iparse.set("Jobs", "BuildSiteMap", "no")
	if not iparse.has_option("Jobs", "DuplicateFiles"):
		iparse.set("Jobs", "DuplicateFiles", "ok")
	if not iparse.has_option("Jobs", "DuplicateFilesExtensions"):
		iparse.set("Jobs", "DuplicateFilesExtensions", "*.jpg|*.png")
	if not iparse.has_option("Jobs", "FilesToCopy"):
		iparse.set("Jobs", "FilesToCopy", "*.css|*.jpg|*.html|*.php|*.png")
	if not iparse.has_option("Jobs", "FinalCleaning"):
		iparse.set("Jobs", "FinalCleaning", "ok")
	if not iparse.has_option("Jobs", "IndexFile"):
		iparse.set("Jobs", "IndexFile", "index")
	if not iparse.has_option("Jobs", "InitialCleaning"):
		iparse.set("Jobs", "InitialCleaning", "ok")
	if not iparse.has_option("Jobs", "LanguageDates"):
		iparse.set("Jobs", "LanguageDates", "en $month/$day/$year|it $day/$month/$year")
	if not iparse.has_option("Jobs", "PasswdFile"):
		iparse.set("Jobs", "PasswdFile", "pw.pw")
	if not iparse.has_option("Jobs", "ProcessingAgeDays"):
		iparse.set("Jobs", "ProcessingAgeDays", "0")
	if not iparse.has_option("Jobs", "ProcessingFileExtension"):
		iparse.set("Jobs", "ProcessingFileExtension", ".md")
	if not iparse.has_option("Jobs", "ShowMessages"):
		iparse.set("Jobs", "ShowMessages", "no")
	if not iparse.has_option("Jobs", "SSLSaltPrefix"):
		iparse.set("Jobs", "SSLSaltPrefix", "zz")
	if not iparse.has_option("Jobs", "UpdateFileList"):
		iparse.set("Jobs", "UpdateFileList", "no")
	if not iparse.has_option("Jobs", "UseReplaceConf"):
		iparse.set("Jobs", "UseReplaceConf", "no")
	# rss  -----------------------------------------------------------------------------------
	if not iparse.has_section("RSS"):
		iparse.add_section("RSS")
	if not iparse.has_option("RSS", "Create"):
		iparse.set("RSS", "Create", "no")
	if not iparse.has_option("RSS", "RSSAuthor"):
		iparse.set("RSS", "RSSAuthor", "rss master <rss.master@my.site>")
	if not iparse.has_option("RSS", "RSSDescription"):
		iparse.set("RSS", "RSSDescription", "My site RSS description")
	if not iparse.has_option("RSS", "RSSListLength"):
		iparse.set("RSS", "RSSListLength", "10")
	if not iparse.has_option("RSS", "RSSDontAddThese"):
		iparse.set("RSS", "RSSDontAddThese", "")
	if not iparse.has_option("RSS", "RSSSummaryLength"):
		iparse.set("RSS", "RSSSummaryLength", "300")
	# external progs  -------------------------------------------------------------------------
	if not iparse.has_section("Applications"):
		iparse.add_section("Applications")

	if not iparse.has_option("Applications", "Convert"):
			iparse.set("Applications", "Convert", sgutils.checkdep("convert"))
	if not iparse.has_option("Applications", "Identify"):
			iparse.set("Applications", "Identify", sgutils.checkdep("identify"))
	if not iparse.has_option("Applications", "Mogrify"):
			iparse.set("Applications", "Mogrify", sgutils.checkdep("mogrify"))
	if not iparse.has_option("Applications", "OpenSSL"):
			iparse.set("Applications", "OpenSSL", sgutils.checkdep("openssl"))

	# final writing
	with open(os.path.join(creatingdirectory, "site", "site.conf"), "w", encoding="utf-8") as f:
		iparse.write(f)
		f.close()


def createchunks():
	"""check if necessary chunks are present in their directory
		:date: 2017-09-02
		:return: none
	"""

	cdir = os.path.join(sgconf.cfgget("dirstart"), "site", "chunks")

	fn = os.path.join(cdir, "archive_date")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!-- composing date\nmoment=block composing the date -->\n<span>${moment}</span>", "w")
	sgconf.cfgset("chunk_archive_date", createchunksreading(fn))

	fn = os.path.join(cdir, "archive_date_local")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!-- composing date\nmoment=block composing the date\nlanguage=two chars language -->\n<span class='${language}' style='display:none;'>${moment}</span>", "w")
	sgconf.cfgset("chunk_archive_date_local", createchunksreading(fn))

	fn = os.path.join(cdir, "article_square")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkarticlesquare(), "w")
	sgconf.cfgset("chunk_article_square", createchunksreading(fn))

	fn = os.path.join(cdir, "archives_list")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkarchiveslist(), "w")
	sgconf.cfgset("chunk_archives_list", createchunksreading(fn))

	fn = os.path.join(cdir, "author_description")
	if not os.path.exists(fn):
		sgutils.file_write(fn,  "<!--author as showed\nauthor=author name\nauthormail=email -->\n<a href='mailto:${authormail}'>${author}</a><br>\n", "w")
	sgconf.cfgset("chunk_author_description", createchunksreading(fn))

	fn = os.path.join(cdir, "gallery_buttons")
	if not os.path.exists(fn):
		tmp = "<!--\nlinkindex=index\n"
		tmp += "description=file name cleared and capitalized\n"
		tmp += "linkfrst=go to first image\n"
		tmp += "linkfrstdisable=set to 'disabled' if not to be used\n"
		tmp += "linkprev=go to first image\n"
		tmp += "linkprevdisable=set to 'disabled' if not to be used\n"
		tmp += "linknext=go to first image\n"
		tmp += "linknextdisable=set to 'disabled' if not to be used\n"
		tmp += "linklast=go to first image\n"
		tmp += "linklastdisable=set to 'disabled' if not to be used\n"
		tmp += "-->\n"
		tmp += "<div>\n"
		tmp += "<a href='$linkindex' class='sggallerybuttons'>[O]</a>\n"
		tmp += "<a href='$linkfrst' class='sggallerybuttons$linkfrstdisable'>&lt;&lt;</a>\n"
		tmp += "<a href='$linkprev' class='sggallerybuttons$linkprevdisable'>&lt;</a>\n"
		tmp += "<a href='$linknext' class='sggallerybuttons$linknextdisable'>&gt;</a>\n"
		tmp += "<a href='$linklast' class='sggallerybuttons$linklastdisable'>&gt;&gt;</a>\n"
		tmp += "</div>\n"
		sgutils.file_write(fn, tmp, "w")
	sgconf.cfgset("chunk_gallery_buttons", createchunksreading(fn))

	fn = os.path.join(cdir, "gallery_square")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<div class='sgimagethumbs'>\n<a href='${file}.html'><img src='thumbnails/${image}' title='${image}' alt='${image}' class='sgthumb'></a>\n</div>\n", "w")
	sgconf.cfgset("chunk_gallerysquare", createchunksreading(fn))

	fn = os.path.join(cdir, "gallery_box")
	try:
		os.remove(fn)
	except:
		pass
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkgallerybox(), "w")
	sgconf.cfgset("chunk_gallery_box", createchunksreading(fn))

	fn = os.path.join(cdir, "index_dir")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkindexdir(), "w")
	sgconf.cfgset("chunk_index_dir", createchunksreading(fn))

	fn = os.path.join(cdir, "index_dir_list")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkindexdirlist(), "w")
	sgconf.cfgset("chunk_index_dir_list", createchunksreading(fn))

	fn = os.path.join(cdir, "index_files")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<div>\n<ul>\n<for repeat><li><a href='${link}'>${linkname}</a></li>\n<next repeat></ul>\n</div>\n ", "w")
	sgconf.cfgset("chunk_index_files", createchunksreading(fn))

	fn = os.path.join(cdir, "index_generic_files")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<div>\n<ul>\n<for repeat><li><a href='${link}'>${linkname}</a></li>\n<next repeat></ul>\n</div>\n ", "w")
	sgconf.cfgset("chunk_index_generic_files", createchunksreading(fn))

	# fixme
	fn = os.path.join(cdir, "languages_links")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunklanguageslinks(), "w")
	sgconf.cfgset("chunk_languages_links", createchunksreading(fn))

	# fixme
	fn = os.path.join(cdir, "languages_rows")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunklanguagesrows(), "w")
	sgconf.cfgset("chunk_languages_rows", createchunksreading(fn))

	fn = os.path.join(cdir, "line_links")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunklinelinks(), "w")
	sgconf.cfgset("chunk_line_links", createchunksreading(fn))

	fn = os.path.join(cdir, "localized_date")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunklocalizeddate(), "w")
	sgconf.cfgset("chunk_localized_date", createchunksreading(fn))

	fn = os.path.join(cdir, "map_page")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkmap(), "w")
	sgconf.cfgset("chunk_map_page", createchunksreading(fn))

	fn = os.path.join(cdir, "navbar_items")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!-- navigation bar\n$link=link to file\n$home=site home\n-->\n<a href='$link'>$home</a>", "w")
	sgconf.cfgset("chunk_navbar_items", createchunksreading(fn))

	fn = os.path.join(cdir, "note")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!-- the note linked\nnote=note name\ntext=text note\n-->\n<div class='sgnote' id='n${note}'><a href='#s${note}'>${note}</a> ${text}</div>", "w")
	sgconf.cfgset("chunk_note", createchunksreading(fn))

	fn = os.path.join(cdir, "note_link")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!-- link with a note\nnote=note name\ntext=text note\n-->\n<span id='s${note}' class='s${note}'><a href='#n${note}'>${text}</a></span>", "w")
	sgconf.cfgset("chunk_note_link", createchunksreading(fn))

	fn = os.path.join(cdir, "page_image")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!-- main image on all pages -->\n<img src='${imagefile}' ${bounds} id='sgimage' class='sgimage' alt='${description}' title='${description}'>", "w")
	sgconf.cfgset("chunk_page_image", createchunksreading(fn))

	fn = os.path.join(cdir, "page_image_gallery")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkpageimagegallery(), "w")
	sgconf.cfgset("chunk_page_image_gallery", createchunksreading(fn))

	fn = os.path.join(cdir, "permalink")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!--\nnewlink=link\nperma=link to old file\nsite=site name\n-->\n<span>http://${site}/${newlink}</span>\n ", "w")
	sgconf.cfgset("chunk_permalink", createchunksreading(fn))

	# fixme
	fn = os.path.join(cdir, "post_links")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkpostlinks(), "w")
	sgconf.cfgset("chunk_post_links", createchunksreading(fn))

	fn = os.path.join(cdir, "post_page_links")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkpostpagelinks(), "w")
	sgconf.cfgset("chunk_post_page_links", createchunksreading(fn))

	fn = os.path.join(cdir, "quote")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkquote(), "w")
	sgconf.cfgset("chunk_quote", createchunksreading(fn))

	fn = os.path.join(cdir, "replace_language")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!--\nlanguage=the language\n-->\n<div class='${language}' style='display:none;'>\n ", 						   "w")
	sgconf.cfgset("chunk_replace_language", createchunksreading(fn))

	fn = os.path.join(cdir, "tags_list")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<span class='sgtagslist'><a href='$p1'>$p2</a></span>\n ", "w")
	sgconf.cfgset("chunk_tags_list", createchunksreading(fn))

	fn = os.path.join(cdir, "tags_page_items")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "0. <a href='$p1'>$p2</a> \n", "w")
	sgconf.cfgset("chunk_tags_page_items", createchunksreading(fn))

	fn = os.path.join(cdir, "title_simple")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunktitlesimple(), "w")
	sgconf.cfgset("chunk_title_simple", createchunksreading(fn))

	fn = os.path.join(cdir, "title_mode1")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunktitlemode1(), "w")
	sgconf.cfgset("chunk_title_mode1", createchunksreading(fn))

	fn = os.path.join(cdir, "title_mode3")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunktitlemode3(), "w")
	sgconf.cfgset("chunk_title_mode3", createchunksreading(fn))

	fn = os.path.join(cdir, "up_index")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<a href='../${link}' class='sgupindex'>${linktitle}</a>", "w")
	sgconf.cfgset("chunk_up_index", createchunksreading(fn))

	fn = os.path.join(cdir, "updated_files")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkupdatedfiles(), "w")
	sgconf.cfgset("chunk_updated_files", createchunksreading(fn))
	
	fn = os.path.join(cdir, "video_link")
	if not os.path.exists(fn):
		sgutils.file_write(fn, getchunkvideolink(), "w")
	sgconf.cfgset("chunk_video_link", createchunksreading(fn))	

	fn = os.path.join(cdir, "youtube_link")
	if not os.path.exists(fn):
		sgutils.file_write(fn, "<!-- youtube object -->\n<div class='sgfastyoutube'>\n<iframe width='640' height='480' src='http://www.youtube.com/embed/$p1' frameborder='0' allowfullscreen></iframe>\n</div>", "w")
	sgconf.cfgset("chunk_youtube_link", createchunksreading(fn))


def createchunksreading(chunk):
	""" create a chunk
	"""

	content = sgutils.file_read(chunk)
	myre = r'<!-(.*?)-->'

	mo = re.search(myre, content, re.DOTALL)
	if mo:
		content = content.replace(mo.group(), "")

	return content


def createdefaultcss():
	""" try to check default css
	"""
	filename = os.path.join(sgconf.cfgget("dirstart"), "site", "styles.md")

	if not os.path.exists(filename):
		res = ":> filename:styles.css\n"
		res += ":> tmpl:none\n"
		res += ":> raw:yes\n"
		res += "/* g.static base css file */"
		sgutils.file_write(filename, res, "w")
	cssdef = open(filename).read()
	tmplen = len(cssdef)

	if cssdef.find(".sgarticle") < 0:
		cssdef += "\n.sgarticle {\n float:  none;\n  display: block;\n  margin: 0px;\n  margin-bottom: 10px;\n  padding: 0px 5px;\n  min-height: 105px;\n  font-size: 90%; }"
	if cssdef.find(".sgarticleimage") < 0:
		cssdef += "\n.sgarticleimage { }"
	if cssdef.find(".sgarticlefulllink") < 0:
		cssdef += "\n.sgarticlefulllink { }"
	if cssdef.find(".sgcode") < 0:
		cssdef += "\n.sgcode {\n  border: 1px;\n  background-color: white; }"
	if cssdef.find(".sgdiv1") < 0:
		cssdef += "\n.sgdiv1 {\n  border: 1px;}"
	if cssdef.find(".sgdiv2") < 0:
		cssdef += "\n.sgdiv2 {\n  border: 1px;}"
	if cssdef.find(".sgfastimage") < 0:
		cssdef += "\n.sgfastimage {\n  float: left;\n  margin: 5px;\n  border: 0px; }"
	if cssdef.find(".sgfastyoutube") < 0:
		cssdef += "\n/*.sgfastyoutube { }*/"
	if cssdef.find(".sggallerybuttons") < 0:
		cssdef += "\n.sggallerybuttons {\n  width: 40px;\n  height: 10px;\n  padding: 10px;\n  border: 1px; }"
	if cssdef.find(".sggallerybuttonsdisabled") < 0:
		cssdef += "\n.sggallerybuttonsdisabled {\n  width: 40px;\n  height: 10px;\n  padding: 10px;\n  border: 1px;\n pointer-events: none;\n cursor: default;\n color: #c0c0c0;\n background-color: #ffffff}"
	if cssdef.find(".sgimage") < 0:
		cssdef += "\n.sgimage {\n  float: left;\n  margin: 20px;\n  border: 0px; }"
	if cssdef.find(".sgimagegallery") < 0:
		cssdef += "\n.sgimagegallery {\n  float: left;\n  margin: 20px;\n  border: 0px; }"
	if cssdef.find(".sgimagethumbs") < 0:
		cssdef += "\n.sgimagethumbs {\n  float: left;\n }"
	if cssdef.find(".sgnote") < 0:
		cssdef += "\n.sgnote {\n  font-size: smaller;\n border: 1px;}"
	if cssdef.find(".sgpostslinelinks") < 0:
		cssdef += "\n.sgpostslinelinks {\n  float: left;\n  padding: 5px;\n  width: 40px; }"
	if cssdef.find(".sgpostslinelinkscontainer") < 0:
		cssdef += "\n.sgpostslinelinkscontainer {\n  border: 1px; }"
	if cssdef.find(".sgpostslisttitle") < 0:
		cssdef += "\n/*.sgpostslisttitle { }*/"
	if cssdef.find(".sgpoststags") < 0:
		cssdef += "\n.sgpoststags {\n  clear: both;\n  font-size: 15px; }"
	if cssdef.find(".sgquote") < 0:
		cssdef += "\n/*.sgquote { }*/"
	if cssdef.find(".sgsummary") < 0:
		cssdef += "\n/*.sgsummary { }*/"
	if cssdef.find(".sgtagslist") < 0:
		cssdef += "\n.sgtagslist { }"
	if cssdef.find(".sgthumb") < 0:
		cssdef += "\n.sgthumb {\n  margin: 0px;\n  padding: 20px 30px; }"
	# page lightbox
	if cssdef.find(".sglightbox1") < 0:
		cssdef += "\n/* [[[ related to page images lightbox ]]]*/"
		cssdef += ".sglightbox1 {\n  text-align: left;\n  width: 75%;\n  float: left; }\n"
	if cssdef.find(".sglightboxbtn") < 0:
		cssdef += ".sglightboxbtn {\n  text-align: right;\n  width: 8%;\n float: left; }\n"
	if cssdef.find(".sglightboxclose") < 0:
		cssdef += ".sglightboxclose {\n  font-family: Sans;\n  color: white;\n  background-color: black;\n  font-size: 120%;\n  "
		cssdef += "font-weight: bolder;\n  text-decoration: none;\n  text-transform: none;\n  width: 10px;}\n"
	if cssdef.find(".sglightboxarrows") < 0:
		cssdef += ".sglightboxarrows {\n  font-family: Sans;\n  color: black;\n  font-size: 150%;\n  font-weight: bolder;\n  "
		cssdef += "text-decoration: none;\n  text-transform: none;\n  width: 20px; }\n"
	if cssdef.find(".sglightboxicon") < 0:
		cssdef += ".sglightboxicon {\n  cursor:pointer; }\n"
	if cssdef.find(".sglightboximage") < 0:
		cssdef += ".sglightboximage {\n  padding: 5px;\n  clear: left; }\n"
	if cssdef.find(".sgoverlayblack") < 0:
		cssdef += ".sgoverlayblack {\n  display: none;\n  position: absolute;\n  top: 0%;\n  left: 0%;\n  width: 100%;\n  "
		cssdef += "min-height: 1000%;\n  background-color: black;\n  z-index:1001;\n  -moz-opacity: 0.8;\n  opacity:.80;\n  filter: alpha(opacity=80); }\n"
	if cssdef.find(".sgoverlaywhite") < 0:
		cssdef += ".sgoverlaywhite {\n  display: none;\n  position: fixed;\n  top: 5%;\n  left: 5%;\n  width: 90%;\n  height: 90%;\n  "
		cssdef += "padding: 5px;\n  border: 4px solid orange;\n  background-color: white;\n  z-index:1002;\n  overflow: auto;\n  text-align: center; }\n"

	if len(cssdef) > tmplen:
		cssdef = cssdef.replace("\n\n", "\n")
		sgutils.file_write(filename, cssdef, "w")


def createdefaultjsfile():
	"""
	:return:
	"""
	res = """// g.static js file
function loadPagePart(toBeFilled, leechingUrl) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        res = this.responseText;
        if (res.includes("<body>") && res.includes("</body>")) {
          m = res.indexOf("<body");
          n = res.indexOf("</body>");
          res = res.substr(m+6, n-m-6);
        }
        document.getElementById(toBeFilled).innerHTML = res;
    }
  };
  xhttp.open("GET", leechingUrl, true);
  xhttp.send();
}
// ---------------------------------------------
function checkPrivacy()
{
  if (checkCookie() == true) {
	// writeCookie('antani',"0000000000",360)
    var nome = readCookie('antani')[0];

    if (nome != "0" && nome != "1"){
        writeCookie('antani',"0000000000",360)}
    if (nome == "0") {
    document.getElementById('privacybar').style.display='block';
    }
  }
}
// ---------------------------------------------
function writeCookie(nomeCookie,valoreCookie,durataCookie)
{
  var scadenza = new Date();
  var adesso = new Date();
  scadenza.setTime(adesso.getTime() + (parseInt(durataCookie) * 60000));
  document.cookie = nomeCookie + '=' + escape(valoreCookie) + '; expires=' + scadenza.toGMTString() + '; path=/';
}
// ---------------------------------------------
function readCookie(nomeCookie)
{
  if (document.cookie.length > 0)
  {
    var inizio = document.cookie.indexOf(nomeCookie + "=");
    if (inizio != -1)
    {
      inizio = inizio + nomeCookie.length + 1;
      var fine = document.cookie.indexOf(";",inizio);
      if (fine == -1) fine = document.cookie.length;
      return unescape(document.cookie.substring(inizio,fine));
    }else{
       return "";
    }
  }
  return "";
}
// ---------------------------------------------
function setPrivacyCookie()
{
  allparam = "1" + readCookie('antani').slice(1, 99)
  writeCookie('antani',allparam,360)
  document.getElementById('privacybar').style.display='none'
}
// ---------------------------------------------
function deleteCookie(nomeCookie)
{
  writeCookie(nomeCookie,'',-1);
}
// ---------------------------------------------
function checkCookie()
{
  document.cookie = 'check_cookie';
  var testcookie = (document.cookie.indexOf('check_cookie') != -1) ? true : false;
  return testcookie;
}"""

	filename = os.path.join(sgconf.cfgget("dirstart"), "site", "js.js")

	if not os.path.exists(filename):
		sgutils.file_write(filename, res, "w")


def createdefaultreplaceconf():
	""" try to check default replace.conf file, with some defaults
		:return: anything, just a pointer
	"""
	filename = os.path.join(sgconf.cfgget("dirstart"), "site", "replace.conf")

	if not os.path.exists(filename):
		sgutils.file_write_csv(filename, ["oldtext", "newtext"], "w")


def createdefaulttagconf():
	""" try to check default tag.conf file, with some defaults
		:return: anything, just a pointer
	"""
	filename = os.path.join(sgconf.cfgget("dirstart"), "site", "replacetag.conf")

	if not os.path.exists(filename):
		sgutils.file_write_csv(filename, ["%%", "<mytag>", "</mytag>"], "w")


def createdefaultvars():
	""" create some vars, with some defaults
	"""
	filename = os.path.join(sgconf.cfgget("dirstart"), "site", "vars", "mark1")
	if not os.path.exists(filename):
		sgutils.file_write(filename, "<mark>", "w")
	filename = os.path.join(sgconf.cfgget("dirstart"), "site", "vars", "mark2")
	if not os.path.exists(filename):
		sgutils.file_write(filename, "</mark>", "w")


def createnewsite(directory):
	"""
	:param directory: This will create a skeleton for a new site
	:return: anything
	"""

	sgconf.cfgset("dirstart", directory)
	if not os.path.exists(directory):
		print(directory + " doesn't exist, please create it before running g.static ...")
		sys.exit()
	# now i create the directory structure of the site
	today = datetime.date.today()
	exyear = int(today.strftime('%Y')) - 1

	lista = [
	directory, os.path.join(directory, "images"), os.path.join(directory, "images", "example"),
	os.path.join(directory, "images", "second-example"), os.path.join(directory, "posts"),
	os.path.join(directory, "posts", str(exyear), "12", "31"),
	os.path.join(directory, "posts", str(exyear), "11", "07"),
	os.path.join(directory, "posts", str(exyear), "09", "10"),
	os.path.join(directory, "posts", str(exyear), "04", "06"), os.path.join(directory, "site", "chunks"),
	os.path.join(directory, "site", "map"), os.path.join(directory, "site", "scripts"),
	os.path.join(directory, "site", "tags"), os.path.join(directory, "site", "tmpl"),
	os.path.join(directory, "site", "vars")
	]

	for d in lista:
		try:
			os.makedirs(d)
			sgutils.showmsg(d + " directory created", 99)
			if not os.path.exists(d):
				print(d + " can't be created, stopping...")
				sys.exit()
		except:
			sgutils.showmsg(d + " directory can't be created", MESSAGE_NORMAL)

	try:
		filename = os.path.join(directory, "index" + sgconf.cfgget("processingext"))
		if not os.path.exists(filename):
			tmplg = gettmphome()
			sgutils.file_write(filename, tmplg.replace("\t", ""), "w")
			sgutils.showmsg("Home file created", MESSAGE_DEBUG)

		filename = os.path.join(directory, "index.jpg")
		if not os.path.exists(filename):
			cmdline = sgconf.cfgget("appconvert") + ' -size 600x400 0x5' + ' plasma:fractal ' + filename
			extruncmd(cmdline, True)
			sgutils.showmsg("An image at home created", MESSAGE_DEBUG)

		filename = os.path.join(directory, "template")
		if not os.path.exists(filename):
			tmplg = gettmplg("${body}")
			sgutils.file_write(filename, tmplg.replace("\t", ""), "w")
			sgutils.showmsg("Template file created", MESSAGE_DEBUG)

		filename = os.path.join(directory, "posts", "timeline.md")
		if not os.path.exists(filename):
			sgutils.file_write(filename, "<span id='dynamic_content'></span>", "w")
			sgutils.showmsg("History of files created", MESSAGE_DEBUG)

		filename = os.path.join(directory, "posts", "template")
		if not os.path.exists(filename):
			tmplg = gettmplg("$postlinks\n$title\n$datedir<br>\n$body\n$tags")
			sgutils.file_write(filename, tmplg.replace("\t", ""), "w")
			sgutils.showmsg("Posts template file created", MESSAGE_DEBUG)

		#TO DO check the name index above
		filename = os.path.join(directory, "images", "index" + sgconf.cfgget("processingext"))
		if not os.path.exists(filename):
			sgutils.file_write(filename, "${listdirindex}", "w")
			sgutils.showmsg("Galleries list file created", MESSAGE_DEBUG)

		filename = os.path.join(directory, "images", "template")
		if not os.path.exists(filename):
			tmplg = gettmplg("<div><a href='${rootdir}posts/index.html'>${sitename}</a></div>\n<div>${dirtitle} - ${autotitle}</div>\n${gallerybuttons}<br>\n${body}")
			sgutils.file_write(filename, tmplg.replace("\t", ""), "w")
			sgutils.showmsg("Images template file created", MESSAGE_DEBUG)

		filename = os.path.join(directory, "images", "template-index")
		if not os.path.exists(filename):
			tmplg = gettmplg("${title}\n${body}")
			sgutils.file_write(filename, tmplg.replace("\t", ""), "w")
			sgutils.showmsg("Images template index file created", MESSAGE_DEBUG)

		filename = os.path.join(directory, "images", "template-index-all")
		if not os.path.exists(filename):
			tmplg = gettmplg("${listgallerieslink}\n<p>\n${title}\n${body}")
			sgutils.file_write(filename, tmplg.replace("\t", ""), "w")
			sgutils.showmsg("Images template file for all created", MESSAGE_DEBUG)

	except:
		sgutils.showmsg("Problems creating the new site", MESSAGE_NORMAL)

	createdefaultcss()
	createdefaultjsfile()
	createdefaultvars()
	createchunks()
	createconfigfile(directory)
	#sgconf.readconf(directory)
	# images for examples
	for i in range(1, 6):
		newfile = os.path.join(directory, 'images', 'example', 'test' + str(i) + '.jpg')
		if not os.path.exists(newfile):
			cmdline = sgconf.cfgget("appconvert") + ' -size 1200x800 0x' + str(i) + ' plasma:fractal ' + newfile
			extruncmd(cmdline, True)
	for i in range(1, 6):
		newfile = os.path.join(directory, 'images', 'second-example', 'test' + str(i) + '.jpg')
		if not os.path.exists(newfile):
			cmdline = sgconf.cfgget("appconvert") + ' -size 1200x800 0x' + str(i) + ' plasma:fractal ' + newfile
			extruncmd(cmdline, True)

	# some posts and images
	d = os.path.join(directory, "posts", str(exyear), "04", "06", "bene-birthday")
	sgutils.file_write(d + ".md", getlorem() * 6, "w")
	cmdline = sgconf.cfgget("appconvert") + "' -size 600x600 0x1 plasma:fractal '" + d + ".jpg'"
	extruncmd(cmdline, False)

	d = os.path.join(directory, "posts", str(exyear), "09", "10", "my-birthday")
	sgutils.file_write(d + ".md", getlorem() * 9, "w")
	cmdline = sgconf.cfgget("appconvert") + "' -size 600x600 0x2 plasma:fractal '" + d + ".jpg'"
	extruncmd(cmdline, False)

	d = os.path.join(directory, "posts", str(exyear), "12", "31", "last-day-of-the-year")
	sgutils.file_write(d + ".md", getlorem() * 12, "w")
	cmdline = sgconf.cfgget("appconvert") + "' -size 600x300 0x3 plasma:fractal '" + d + ".jpg'"
	extruncmd(cmdline, False)

	print("\nA new site structure should be done in " + sgconf.cfgget("dirstart"))
	print("One example actions file has been created in your root site directory")
	print("Make sure of having a backup directory setting before putting images in here")


def gettmplg(bodycontent):
	""" get a default template, if not present another """
	tmplg = """<!DOCTYPE html>
	<html>
	<head>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
	<meta name='Keywords' content='$keywords'>
	<link rel='stylesheet' type='text/css' href='${rootdir}site/styles.css'>
	</head>
	<body>
	<div class="sgdiv1">
	</div>
	<div class="sgdiv2">
	${contenuto}
	</div>
	</body>
	</html>"""

	return sgchunks.process(tmplg, "", {"contenuto":bodycontent})


def getlorem():
	""" return a somple string to fill a text """
	res = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
	return res


def gen_gettemplateindex():
	""" create a simple template for default files
	:return:
	"""
	tmp = "<html>\n<head>\n"
	tmp += "<meta http-equiv='refresh' content='5;url=${lastpost}'>\n"
	tmp += "</head>\n<body>\n$body\n</body>\n</html>"
	return tmp


def gen_getpermatemplate():
	""" create a default template for permalink pages
	:return:
	"""
	tmp = "<html>\n<head>"
	tmp += "</head>\n<body>\n$body\n</body>\n</html>"
	return tmp


def gen_gethtaccess(fileposdir):
	""" return content for an htaccess file
	:param fileposdir: directory where htfile must be created
	:return:
	"""
	sitepath = sgconf.cfgget("sitepath")
	if sitepath == "":
		return ""

	v = "AuthUserFile " + os.path.join(sgconf.cfgget("sitepath"), fileposdir, ".htpasswd") + "\n"
	v += "AuthGroupFile /dev/null\n"
	v += "AuthName \"Restricted access\"\n"
	v += "AuthType Basic\n"
	v += "<Limit GET POST>\n"
	v += "require valid-user\n"
	v += "</Limit>"

	return v


def getlangscript(lingue, titoli):
	""" return language script: this is the script that switch on languages, if configured,
		when landing on a page
	:param lingue:
	:param titoli:
	:return:
	"""

	sdef = lingue.split(",")[0]
	slang = "'" + lingue + "'"
	slang = slang.replace(",", "','")
	v = "<script>\n<!--\n"
	v += "var languages=new Array(" + slang + ");\n"
	if titoli.find(",") > 0:
		v += "var mytitles=new Array(" + titoli + ");\n"
	v += "var mylang=window.navigator.language;\n"
	v += "var usedlang='" + sdef + "';\n"
	v += "var mycaption='';\n"
	v += "document.documentElement.lang='" + sdef + "';\n"
	v += """
	if (mylang.indexOf('-') > 0) {
	  mylang=mylang.slice(0,mylang.indexOf('-')); }
	if (mylang.indexOf('_') > 0) {
	  mylang=mylang.slice(0,mylang.indexOf('_')); }
	  for(var i=0; i<languages.length; i++)
		{ if (languages[i]==mylang) {
		usedlang=mylang;
		break; } }
	var elems = document.getElementsByClassName(usedlang);
	if (elems.length==0) {
	  elems = document.getElementsByClassName(languages[0]); }
	for(var i=0; i<elems.length; i++)
	  {elems[i].style.display='inline'; }
	"""
	if titoli.find(",") > 0:
		# noinspection PyPep8
		v += """
		for(var i=0; i<mytitles.length; i++)
		{ tmp=mytitles[i].slice(0,mytitles[i].indexOf(' '));
		   mycaption=mytitles[i].slice(mytitles[i].indexOf(' ')+1);
		   if (tmp==usedlang) { document.title=mycaption;
		   document.getElementById('sgpagetitle').innerHTML=mycaption;
		   document.title=mycaption; } }
		"""
	v += "//-->\n</script>\n"
	v += "<noscript>This site requires use of Javascript in order to work.</noscript>"
	return v


def gen_getmapindex(cond, index):
	""" return the first or last part of sitemap index files

	:param cond:
	:param index:
	:return: return the first or last part of sitemap index files
	"""

	if index:
		writ = "sitemapindex"
	else:
		writ = "urlset"
	if cond:
		v = '<?xml version="1.0" encoding="UTF-8"?>\n'
		v += '  <' + writ + ' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
	else:
		v = '\n</' + writ + '>'

	return v


def getchunkarchiveslist():
	""" return a simple template for the map
	:return: the map chunk
	"""

	res = "<!-- the list of the archives\n"
	res += "link=the link\n"
	res += "linkmonth=month of archive\n"
	res += "linkyear=year of archive\n"
	res += "-->\n"
	res += "<div>"
	res += "<for repeat><a href='${link}'>${linkyear} - ${linkmonth}</a><br>\n"
	res += "<next repeat></div>"

	return res


def getchunkarticlesquare():
	""" These are used for list index files """

	res = "<!-- blocks in list files\n"
	res += "thumblink=link for thumbnail\n"
	res += "thumbsize=block for bounds of thumbnail\n"
	res += "thumbdesc=thumbnail description\n"
	res += "linkposts=post link\n"
	res += "summary=shortened version of article\n"
	res += "linktofullarticle=link to article\n"
	res += "-->\n"
	res += "<div>\n"
	res += "  <div>\n"
	res += "  <img src='${thumblink}' ${thumbsize} alt='${thumbdesc}' title='${thumbdesc}'> ${title}\n"
	res += "  </div>\n"
	res += "  <div>\n"
	res += "  <span>${linkposts}</span>\n"
	res += "  </div>\n"
	res += "  <div>\n"
	res += "  ${summary} <a href='${linktofullarticle}'>[...]</a>\n"
	res += "  </div>\n"
	res += "  <div>\n"
	res += "  ${tags}\n"
	res += "  </div>\n"
	res += "</div>"

	return res


def getchunkmap():
	""" return a simple template for the map
	:return: the map chunk
	"""

	res = "<!-- from  list\n"
	res += "link=the link\n"
	res += "linktitle=description, rendered as title\n"
	res += "linkpos=directory that is the container\n"
	res += "-->\n"
	res += "<div>"
	res += "<for repeat>${linkpos} / <a href='${link}'>${linktitle}</a><br>\n"
	res += "<next repeat>\n"
	res += "</div>"

	return res


def getchunkgallerybox():
	""" the small gallery chunk

	:return: the default code for this chunk
	"""

	res = "<!-- from  list\n"
	res += "firstimage=default image\n"
	res += "lightboximages=items of images list\n"
	res += "-->\n"
	res += "<script>\n"
	res += "function imageGo(modo) {\n"
	res += "if (modo == -1)\n"
	res += "  {if (pos > 0)\n"
	res += "    {pos = pos -1}\n"
	res += "  else\n"
	res += "    {pos=maxn}\n"
	res += "  document.getElementById('imglb').src=imagelist[pos]}\n"
	res += "else if (modo==1)\n"
	res += "  {if (pos<maxn)\n"
	res += "    {pos=pos+1}\n"
	res += "  else\n"
	res += "    {pos=0}\n"
	res += "  document.getElementById('imglb').src=imagelist[pos]}\n"
	res += "else\n"
	res += "  {pos=0\n"
	res += "  document.getElementById('imglb').src=imagelist[pos]}\n"
	res += "  document.getElementById('lightboxtext').innerHTML=imagelist[pos]}\n"
	res += "var pos = 0\n"
	res += "var imagelist=${lightboximages};\n"
	res += "var maxn=imagelist.length - 1\n"
	res += "</script>\n"
	res += "<img src='${firstimage}' class='sglightboxicon' onclick=\"document.getElementById('light').style.display"
	res += "='block';imageGo(0);document.getElementById('fade').style.display='block'\">\n"
	res += "<span class='sgnotes it' style='display:none;'>\n"
	res += "  Clicca l'immagine per mostrare la galleria\n</span>\n"
	res += "<span class='sgnotes en' style='display:none;'>\n"
	res += "  Click image to show gallery\n"
	res += "</span>\n"
	res += "<div id='light' class='sgoverlaywhite'>\n"
	res += "<div id='lightboxtext' class='sglightbox1'>Text</div>\n"
	res += "<div class='sglightboxbtn'>\n"
	res += "  <a href = 'javascript:void(0)' class='sglightboxarrows' onclick = 'imageGo(-1)'>&lt;</a>\n"
	res += "</div>\n"
	res += "<div class='sglightboxbtn'>\n"
	res += "  <a href = 'javascript:void(0)' class='sglightboxarrows' onclick='imageGo(1)'>&gt;</a>\n"
	res += "</div>\n"
	res += "<div class='sglightboxbtn'><a href='javascript:void(0)' class='sglightboxclose' onclick=\"document.getElementById('light').style.display"
	res += "='none';document.getElementById('fade').style.display='none'\">X</a></div>\n"
	res += "  <img id='imglb' class='sglightboximage' src=''>\n"
	res += "</div>\n"
	res += "<div id='fade' class='sgoverlayblack'>\n"
	res += "</div><p style='clear:both;'>"

	return res


def getchunkindexdir():
	""" return a simple template for the file where updated files
	are listed: it allows to create a list of commands on new files """

	res = "<!-- link=directory in list -->\n<div>\n<ul>\n"
	res += "<for link><li><a href='${link}'>${linkname}</a></li>\n"
	res += "<next link>\n</ul>\n</div>"

	return res


def getchunkindexdirlist():
	""" return a simple template for the file where are listed directories
	under the actual where there is an index file"""

	res = "<!-- link=directory in list -->\n<div>\n<ul>\n"
	res += "<for link><li><a href='${link}'>${linkname}</a></li>\n"
	res += "<next link>\n</ul>\n</div>"

	return res


def getchunklanguageslinks():
	""" create the chunk file for lang links
	:return: the default chunk content for transforming languages links
	"""

	res = "<!--\n"
	res += "default chunk file for language links\n"
	res += "link=link\n"
	res += "text=text showed\n"
	res += "classes=eventual classes\n"
	res += "displaymode=none if set\n"
	res += "-->\n"
	res += "<div>\n<for repeat><a href='${link}' class='${classes}' ${displaymode}>${text}</a>\n<next repeat></div>\n"

	return res


def getchunklanguagesrows():
	""" create the chunk file for lang links
	:return: the default chunk content for transforming languages rows
	"""

	res = "<!--\n"
	res += "default chunk file for language links\n"
	res += "mode=surrounding html tag\n"
	res += "classes=eventual classes\n"
	res += "displaymode=none if set\n"
	res += "-->\n"
	res += "<div>\n<for repeat><${mode} class='${classes}' ${displaymode}></${mode}>\n<next repeat></div>\n"

	return res


def getchunklinelinks():
	""" create the chunk file for line links
	:return: the default chunk content for transforming lines
	"""

	res = "<!-- links between posts\n"
	res += "home=last post\n"
	res += "prev=previous post\n"
	res += "next=next post\n"
	res += "-->\n"
	res += "<div class='sgpostslinkscontainer'>${home} ${prev} ${next}\n</div>"

	return res


def getchunklocalizeddate():
	""" return the piece of javascript that will show the date in the localized format,
		used with script: due script is mandatory, it will be universal
	:return: the script
	"""

	res = "<!-- localized date\n"
	res += "vyear, vmonth, vday, vhour, vminute, vsecond\n"
	res += "name are self explaining\n"
	res += "-->\n"
	res += "<span id='sglocalizeddate'></span>\n"
	res += "<script>\n"
	res += "var mylang=window.navigator.language;\n"
	res += "d=new Date(${vyear}, ${vmonth}, ${vday}, ${vhour}, ${vminute}, ${vsecond});\n"
	res += "var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };\n"
	res += "if (mylang === '') {\n"
	res += "  document.getElementById('sglocalizeddate').innerHTML = ''\n"
	res += "} else {\n"
	res += "  document.getElementById('sglocalizeddate').innerHTML=d.toLocaleDateString(mylang, options);\n"
	res += "}\n\n"
	res += "</script>"

	return res


def getchunkpageimagegallery():
	""" return the containing the the block of the gallery image
	:return: the tag
	"""

	res = "<!-- main image on all pages\n"
	res += "The tag associated with the main image on the pages\n"
	res += "imagefile=name of image file\n"
	res += "bounds=pixel dimensions of image file\n"
	res += "description=description for an image\n"
	res += "-->\n"
	res += "<img src='${imagefile}' ${bounds} id='sgimagegallery' class='sgimagegallery' alt='${description}' title='${description}'>"

	return res


def getchunkpostlinks():
	""" return a simple template for the links over the pages
	:return: the map chunk
	"""
	res = "<!-- from  list\n"
	res += "rendering of the page links\n"
	res += "value=the row passed by app\n"
	res += "-->\n"
	res += "<div class='sgpostslinelinkscontainer'>"
	res += "<for repeat><div class='sgpostslinelinks'>${value}</div>"
	res += "<next repeat>\n"
	res += "</div>"

	return res


def getchunkpostpagelinks():
	""" return a simple template for the links over the pages
	:return: the map chunk
	"""

	# todo
	res = "<!-- links between posts\n"
	res += "home=last post\n"
	res += "homedesc=homedescription\n"
	res += "prevlink=previous post\n"
	res += "prevexpl=text associated with previous item\n"
	res += "nextlink=next post\n"
	res += "nextexpl=text associated with next item\n"
	res += "-->\n"
	res += "<div>\n"
	res += "${homedesc} ${home} ${prevexpl} ${prevlink} ${nextexpl} ${nextlink}\n"
	res += "</div>"

	return res


def getchunkquote():
	""" return a string for the quote tag """

	res = "<!-- from  list\n"
	res += "the block for quote <q>\n"
	res += "quoted=the quoted text\n"
	res += "-->\n"
	res += "<q>${quoted}</q>"

	return res


def getchunktitlesimple():
	""" return a formatting for the title, when languages are not used """

	res = "<!-- simpliest title, without languages\n"
	res += "title=used page title -->\n"
	res += "<div>\n"
	res += "<h1>${title}</h1>\n"
	res += "</div>\n"

	return res


def getchunktitlemode1():
	""" return a formatting for the title, when languages are not used """

	res = "<!-- titles with more formatting\n"
	res += "languageclass=used for language class\n"
	res += "title=used page title\n"
	res += "-->"
	res += "<div class='${languageclass}' style='display:none;'>\n"
	res += "<h1 id='sgpagetitle'>${title}</h1>\n</div>\n"
	res += "</div>\n"

	return res


def getchunktitlemode3():
	""" return a formatting for the title, when languages are not used """

	res = "<!-- titles with more formatting\n"
	res += "languageclass=used for language class\n"
	res += "title=used page title\n"
	res += "-->"
	res += "<span class='${languageclass}' style='display:none;'>${title}</span>\n"

	return res


def getchunkupdatedfiles():
	""" return a simple template for the file where updated files
	are listed: it allows to create a list of commands on new files """

	res = "<!-- from  list\n"
	res += "upfile=new file -->\n"
	res += "<for upfile>${upfile}\n"
	res += "<next upfile>"

	return res


def getchunkvideolink():
	""" return a string for video links """

	res = "<!-- code block for a video file\n"
	res += "filelink=video file -->\n"
	res += "<video src='${filelink}' controls>\n"
	res += "  Sorry, your browser doesn't support embedded videos,\n"
	res += "  but don't worry, you can <a href='${filelink}'>download it</a>\n"
	res += "  and watch it with your favorite video player\n"
	res += "</video>\n"

	return res


def gettmphome():
	""" the text of the first home page example
	:return: the text
	"""
	res = ":> title:A new site"
	res += "\n# This is my home page"
	res += "\nAnd this is some random text:"
	res += "\n" + getlorem()
	res += "\n" + getlorem()
	res += "\n" + getlorem()

	return res


def getversion(withnumber):
	""" return the version number of the app, mostly intended for future use """
	if not withnumber:
		return "g.static static site generator"
	else:
		return "g.static " + sgconf.cfgget("appversion")


def gen_redirectcontent(cosa):
	"""return a content for index file in posts, that will redirect to last file"""
	if cosa == "":
		cosa = "${lastpost}"

	tmp = "Redirecting to <a href='" + cosa + "'>last post</a>\n"
	tmp += "<script>\n"
	tmp += "self.location='" + cosa + "';\n"
	tmp += "</script>"

	return tmp


def gen_getredirectfilecontent(nomefile):
	""" content for a redirect file

	:param nomefile: work file
	:return: the script code
	"""

	tmp = "<html>\n<head>\n"
	tmp += "<meta http-equiv='refresh' content='5;url=" + nomefile + "'>\n"
	tmp += "</head>\n<body>\n"
	tmp += "<script>\n"
	tmp += "self.location='" + nomefile + "';\n"
	tmp += "</script>\n"
	tmp += "</body>\n</html>"

	return tmp


if __name__ == "__main__":
	sgutils.showmsg(ERROR_LAUNCHED_SCRIPT, MESSAGE_NORMAL)
