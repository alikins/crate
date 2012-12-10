#!/usr/bin/python

import glob
import os
import string
import sys

FINK_DPKG_DIR='/sw/var/lib/dpkg/info'
def runDpkgList():
	fink_pkgs = {}
	files = glob.glob("%s/*.list" % FINK_DPKG_DIR)
	for file in files:
		file_name = os.path.basename(file)
		fink_name = file_name[:-5]
		fink_pkgs[fink_name] = fink_name

	fink_pkg_list = fink_pkgs.keys()
	return fink_pkg_list

def parseDpkgStatus():
	file = "/sw/var/lib/dpkg/status"
	f = open(file, "r")
	info = f.read()
	lines = string.split(info, "\n")
#	print lines
	pkg_info = {}
	reading = None
	new_pkg = []
	for line in lines:
		name = None
		if line[:8] == "Package:":
			print "start of new package"
			tmp, name = string.split(line, "Package: ")
			pkg_info[name] = new_pkg
			new_pkg = []
		else:
			new_pkg.append(line)
	info_dict = {}
	for key in pkg_info.keys():
		data = {}
		keyvalues = pkg_info[key]
		for keyvalue in keyvalues:
			bits = string.split(keyvalue, ':', 1)
			print bits
			data[bits[0]] = bits[1][1:]
		info_dict[key] = data
	return info_dict

#ret = runDpkgList()
#for pkg in ret:
#	print pkg

print parseDpkgStatus()
