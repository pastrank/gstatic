#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" module for external apps calling"""

import os
import subprocess
import shutil
import time

import sgconf
import sgutils


def extbackup(fn):
	# noinspection PyPep8
	"""backup an image should copy a backup of the modified images in a directory, and adding a number at the end if it is
		already present a file with that name

		:param fn: filename
		:return: none
		"""

	today = time.strftime("%Y-%m-%d")
	db = os.path.join(sgconf.cfgget("dirbackup"), today)
	if not db == "":
		if not os.path.exists(db):
			os.makedirs(db)

		if os.path.exists(db):
			newfile = os.path.join(db, os.path.basename(fn))
			if not os.path.exists(newfile):
				shutil.copy(fn, newfile)
			else:
				for numero in range(1, 99):
					newfile = os.path.join(db, os.path.basename(fn) + "." + str(numero))
					if not os.path.exists(newfile):
						shutil.copy(fn, newfile)
						return


def extgetcmd(comando):
	""" run a program and get the results
	:param comando: the command line that will be launched
	:return: output of the command line
	"""
	if os.name == "nt":
		comando = comando.replace("'", "\"")

	arr = []
	p = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		try:
			arr.append(line.strip().decode('ascii'))
		except:
			try:
				arr.append(line.strip().decode('utf-8'))
			except:
				arr.append(line.strip().decode('ascii', 'ignore'))
		p.wait()

	return "\n".join(arr)


def extgraphicinfo(immagine, cosa):
	""" extracts the information for image

	:param immagine: name of image file
	:param cosa: what to extract linksize=800x600 arrdim=[800, 600]
	:return:
	"""
	arr = [0, 0]

	if cosa == "linksize":
		cmdl = sgconf.cfgget("appidentify") + " -format \'%w %h\' '" + immagine + "'"
		v = extgetcmd(cmdl)
		arr = v.split(" ")
		v = "width='" + arr[0] + "' height='" + arr[1] + "'"
		return v
	elif cosa == "exif":
		cmdl = sgconf.cfgget("appidentify") + " -format %[exif:*] '" + immagine + "'"
		v = extgetcmd(cmdl)
		return v
	elif cosa == "arrdim":
		cmdl = sgconf.cfgget("appidentify") + " -format \'%w %h\' '" + immagine + "'"
		v = extgetcmd(cmdl)
		arr = v.split(" ")
		# if an image is corrupted, it will return strings, not numbers
		if not arr[0].isnumeric():
			arr[0] = 1
		if not arr[1].isnumeric():
			arr[1] = 1
		return arr


def extgraphicresize(immagine, larghezza, thumb):
	"""imagemagick command that resizes images

	:param immagine: image file
	:param larghezza: width
	:param thumb: is a thumbnail?
	:return: none
	"""

	compressione = sgconf.cfgget("imagescompression")
	densita = sgconf.cfgget("imagesresolution")
	if thumb == "":
		extbackup(immagine)
		cmdline = sgconf.cfgget("appmogrify") + ' ' + sgconf.cfgget("imagestriptags") + ' -density ' + str(densita) + ' -quality ' + str(compressione) + ' -scale ' + str(larghezza) + ' "' + immagine + '"'
		extruncmd(cmdline, True)
	else:
		cmdline = sgconf.cfgget("appconvert") + ' ' + sgconf.cfgget("imagestriptags") + ' -quality ' + str(compressione) + ' -scale ' + str(larghezza) + '  "' + immagine + '" "' + thumb + '"'
		extruncmd(cmdline, True)
		# this will resize thumbnails if width < height
		arr = extgraphicinfo(thumb, "arrdim")
		w = int(arr[0])
		h = int(arr[1])
		if w < h:
			cmdline = sgconf.cfgget("appmogrify") + ' ' + sgconf.cfgget("imagestriptags") + ' -quality ' + str(compressione) + ' -crop ' + str(larghezza) + 'x' + str(larghezza) + '+0-' + str(round((h - w) / 2)) + ' "' + thumb + '"'
			extruncmd(cmdline, True)  #


def extruncmd(comando, showoutput):
	"""
	:param comando:
	:param showoutput:
	:return:
	run a program without getting results """
	if os.name == "nt":
		comando = comando.replace("'", "\"")

	arr = []
	p = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	if showoutput:
		for line in p.stdout.readlines():
			arr.append(line.strip().decode('ascii'))
		sgutils.showmsg("  executing:\n" + comando, 0)
		p.wait()
