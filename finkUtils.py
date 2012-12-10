#!/usr/bin/python

import glob
import os
import string
import sys


def parseDpkgStatus():
	file = "/sw/var/lib/dpkg/status"
	f = open(file, "r")
	info = f.read()
	lines = string.split(info, "\n")
	pkg_info = {}
	reading = None
	new_pkg = {}

	info_dict = {}
	descr = ""
	# ignore description for now, I'm lazy
	for line in lines:
		bits = string.split(line, ':', 1)
		if bits[0] not in ['Package', 'Essential', 'Status', 'Section',
							'Installed-Size', 'Maintainer', 'Source',
							'Version', 'Replaces', 'Depends']:
			continue
		if bits[0] == "Package":
			pkg_name = bits[1][1:]
			pkg_info[pkg_name] = new_pkg
			new_pkg = {}
		else:
			new_pkg[bits[0]] = bits[1][1:]
	
	return pkg_info

if __name__ == "__main__":
	blip = parseDpkgStatus()
	print blip.keys()
	print blip['tar']
