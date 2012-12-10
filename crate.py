#!/usr/bin/python

import fnmatch
import getopt
import glob
import os
import string 
import sys

import myplistlib
import finkUtils

REC_DIR="/Library/Receipts"
APP_DIR="/Applications"
KEXTS_DIR="/System/Library/Extensions"

LSBOM="/usr/bin/lsbom"


# blip
# blip
class PackageList:
	def __init__(self):
		self.pkg_globs = ["*"]

	def setGlobs(self, glob_patterns):
		self.pkg_globs = glob_patterns

	def listAllApps(self):
		self.getListAllApps()
		apps = self.installed_apps.keys()
		apps.sort()
		for app in apps:
			print "a: %s" % app

	def listAllKexts(self):
		self.getListAllKexts()
		kexts = self.installed_kexts.keys()
		kexts.sort()
		for kext in kexts:
			print "k: %s" % kext

	def listAllPkgs(self):
		self.getListAll()
		pkgs = self.installed_pkgs.keys()
		pkgs.sort()
		for pkg in pkgs:
			print "p: %s" % pkg

	def listAllFinks(self):
		self.getListAllFinks()
		finks = self.installed_finks.keys()
		finks.sort()
		for fink in finks:
			print "f: %s" % fink

	def listAll(self):
		self.listAllPkgs()
		self.listAllFinks()
		self.listAllApps()
		self.listAllKexts()

	def getListAllFinks(self):
		finkDict = finkUtils.parseDpkgStatus()
		self.installed_finks = finkDict

	def getListAllApps(self):
		installed_apps = {}
		for root, dirs, files in os.walk(APP_DIR):
			if root[-4:] == ".app":
				dir_name = os.path.basename(root)
				parts = string.split(dir_name, ".app")
				app_name = parts[0]

				for pkg_glob in self.pkg_globs:
					if fnmatch.fnmatch(app_name, pkg_glob):
						installed_apps[app_name] = app_name
		self.installed_apps = installed_apps

	def getListAllKexts(self):
		installed_kexts = {}
		for root, dirs, files in os.walk(KEXTS_DIR):
			if root[-5:] == ".kext":
				dir_name = os.path.basename(root)
				parts = string.split(dir_name, ".kext")
				kext_name = parts[0]

				installed_kexts[kext_name] = kext_name
		self.installed_kexts = installed_kexts	

	def getListAll(self):	
		glob_pattern = "%s/*.pkg" % REC_DIR 
		pkg_dirs = glob.glob(glob_pattern)
		installed_pkgs = {}
		# we could find all the pkg names, then ask for info on each of them
		# but that seems a bit redundant
		for pkg_dir in pkg_dirs:
			dir_name = os.path.basename(pkg_dir)
			parts = string.split(dir_name, ".pkg")
			pkg_name = parts[0]
			
			for pkg_glob in self.pkg_globs:
				if fnmatch.fnmatch(pkg_name, pkg_glob):
					# could uniq later as well...
					installed_pkgs[pkg_name] = pkg_name	
		self.installed_pkgs	= installed_pkgs

class Package:
	def __init__(self):
		pass

	def getFiles(self):
		pass
		
	def getVersion(self):
		pass

	def getName(self):
		pass

	def getRelease(self):
		pass

class FinkPackage:
	def __init__(self, finkDict):
		self.dict = finkDict
		self.name = self.dict['Package']
		self.version_string = self.dict['Version']
		self.version, self.release, self.epoch = self._parseVersion(self.version_string)	

	def _parseVersion(self, version):
		# pass implement bits to parse 
		# version string into epoch:version:release
		return ('1.0', '2', '0')
	
	def getVersion(self):
		return self.dict['Version']
	
	def getName(self):
		return self.dict['Name']

	def getRelease(self):
		return self.dict['Release']

class PackagePile:
	def __init__(self):
		pass
	
	# returns somthing implementing the Package interface
	def getPackage(self, name):
		pass

	# return a list of Packages that match at least 
	# one of the globs
	def getPackagesByGlobs(self, globs):
		pass

	# return a list of all Package's
	def getAllPackages(self, name):
		pass


class FinkPackagePile(PackagePile):
	def __init__(self):
		self.finks = finkUtils.parseDpkgStatus()

	def getPackage(self, name):
		pkg = FinkPackage(self.finks[name])
		return pkg

	def getAllPackages(self):
		pkg_list = []
		for name in self.finks.keys():
			pkg = self.finks[name]
			pkg_list.append(pkg)
		return pkg_list
	
	def getPackagesByGlobs(self, globs):
		pkg_list = []
		for name in self.finks.keys():
			for globstring in globs:
				if fnmatch.fnmatch(name, globstring):
					pkg = self.finks[name]
					pkg_list.append(pkg)
					# once we match a glob, dont bother
					# trying the rest of the globs
					continue
		return pkg_list



	
	

class PackageInfo:
	def __init__(self, pkg_name):
		self.pkg_dirname = "%s/%s.pkg" % (REC_DIR, pkg_name)
		self.files = []
		self.dirs = []	
		self.links = []
		self.devs = []
		self.info = {}
		self.plist_info = {}
		self.populateInfo()

		self.long = None 

	def _runLsbom(self, bom_file):
		# hmm, excev would be better here since file names are sorta
		# untrusted...
		f = os.popen("%s \"%s\"" % (LSBOM,self.bom_file))
		self.__raw_data = f.read()
		f.close()

	def getValue(self, dict, key):
		tmpvalue = dict[key]
		#print "->>>>>>>type: %s" % type(tmpvalue)
		# er, not very efficent, lots of objects created for no reason, etc
		types = [type(""),type(u""), type([]), type(True), type(1), type(1.0)]
		if type(tmpvalue) not in types:
			for key2 in tmpvalue:
				value = self.getValue(tmpvalue, key2)
				return value
		return tmpvalue
		

	def __parseInfoPlist(self):
		self.info_plist = "%s/Contents/Info.plist" % self.pkg_dirname
		try:
			pl = myplistlib.Plist.fromFile(self.info_plist)
		except IOError, e:
			print "%s has no Archive.bom file, skipping" % self.pkg_dirname
			pl = {}
		# this copies the raw data out of the plist
		for pl_key in pl.keys():
			#print pl_key
			#print pl[pl_key]
			value = self.getValue(pl, pl_key)
			#print "******************* %s" % value					
			self.plist_info[pl_key] = value

	def populateInfo(self):
		self.bom_file = "%s/Contents/Archive.bom" % self.pkg_dirname
		self._runLsbom(self.bom_file)
	
		lines = string.split(self.__raw_data, "\n")	
		for line in lines:
			foo = string.split(line, '\t')
			fileinfo = []
			# [type, name, perm, uid/gid, size, checksum, destpath, dev] 
			if len(foo) == 3:
				self.dirs.append(foo)
			if len(foo) == 5:
				self.files.append(foo)
			if len(foo) == 6:
				self.links.append(foo)
			if len(foo) == 4:
				self.devs.append(foo)
		
		# sigh, the included plist parser blows up on stock
		# plist files. Probably need to create our own copy of plistlib
		# and fix the bug since it doesnt seem be be easy to workaround
		self.__parseInfoPlist()
		


	def showDirs(self):
		for dir in self.dirs:
			print "%s perm: %s uid/gid: %s" % (dir[0], dir[1], dir[2])

	def __octalToLs(self, octal):
		msb = octal[-3:]
		total = ""
		for bit in msb:
			out = list("---")
			ibit = int(bit)
			if ibit & 4:
				out[0] = "r"
			if ibit & 2:
				out[1] = "w"
			if ibit & 1:
				out[2] = "x"
			total = total + string.join(out, '')
		return total

	def showAllFiles(self, long = None, info = None):
		all = []
		
		
		if long:
			file_out_format = u"-%(perms)s %(uid)s %(gid)s %(size)-10s %(name)s"
			dir_out_format = u"d%(perms)s %(uid)s %(gid)-12s %(name)s"
		
			#all = map(lambda a: ['d'] + a, self.dirs)
			#all = all + map(lambda a: ['-'] + a, self.files)
			#all = all + map(lambda a: ['s'] + a, self.links)
			for dir in self.dirs:
				perms = self.__octalToLs(dir[1])
				uid, gid = string.split(dir[2], '/')
				# trim the . off of ./
				name = dir[0][1:]
				out = dir_out_format % locals()
				all.append(out) 

			for file in self.files:
				perms = self.__octalToLs(file[1])
				uid, gid = string.split(file[2], '/')
				size = file[3]
				# trim the . off of ./
				name = file[0][1:]
				out = file_out_format % {'name':name, 'perms':perms,
										'uid':uid, 'gid':gid, 'size':size}
				all.append(out)
			out = u""   			 
			for i in all:
				out = out + i
			return out

		if info:
			out = u""
			outlist = [""]
			for pl_key in self.plist_info.keys():
				outlist.append("%-30s: %s" % (pl_key, self.plist_info[pl_key]))
			outlist.sort()
			out = string.join(outlist, "\n")
			return out
		
		# sort them and print just the path
		all = self.files + self.dirs + self.devs + self.links
		all.sort()
		for path in all:
			# trim off leading .
			print path[0][1:]

	def showRawData(self):
		print self.__raw_data		

	
class PackageQuery:
	def __init__(self):
		self.pkg_globs = []
		self.long_query  = None
		self.info_query = None

	def setLongQuery(self, long_query):
		self.long_query = long_query

	def setInfoQuery(self, info_query):
		self.info_query = info_query

	def setGlobs(self, glob_patterns):
		self.pkg_globs = glob_patterns

	def query(self, pkg_names):
		if len(self.pkg_globs):
			pkgs = self.__listAll()
			# everything the glob hit, plus the explicity reqa
			pkg_names = pkg_names + pkgs

		for pkg_name in pkg_names:
			self.queryPkg(pkg_name)

	def queryPkg(self, pkg_name):
		package_info = PackageInfo(pkg_name)	
		try:
			print  package_info.showAllFiles(self.long_query, self.info_query)
		except UnicodeEncodeError, e:
			print "GOT UNICODE ERROR on %s, %s" % (pkg_name, e)
		#package_info.showRawData()

	def __listAll(self):
		pkg_list = PackageList()
		pkg_list.setGlobs(self.pkg_globs)
		pkg_list.getListAll()
		pkgs = pkg_list.installed_pkgs.keys()
		return pkgs

	def queryAll(self):
		# find all the packages, then query each one
		pkgs = self.__listAll()
		self.query(pkgs)



def mainQuery(args):
	print "mainQuery"
	try:
		opts, args = getopt.getopt(args, "ailv", ["all", "info", "long", "verbose"])
	except getopt.error, e:
		sys.exit(1)
	query_all = None
	query_info = None
	query_long = None
	query_verbose = None
	for (opt, val) in opts:
		if opt in ["-a", "--all"]:
			query_all = 1
		if opt in ["-i", "--info"]:
			query_info = 1
		if opt in ["-l", "--long"]:
			query_long = 1
		if opt in ["-v", "--verbose"]:
			query_verbose = 1
	
	package_names = args
	glob_patterns = []
	for package_name in package_names:
		for glob_char in '*?[]':
			if string.find(package_name, glob_char) >= 0:
				# this insnt a package name but a glob 
				glob_patterns.append(package_name)
				package_names.remove(package_name)

	package_query = PackageQuery()
	package_query.setLongQuery(query_long)
	package_query.setInfoQuery(query_info)
	if query_all:
		package_query.setGlobs(["*"])
	if len(glob_patterns):
		package_query.setGlobs(glob_patterns)
	if query_all:
		package_query.queryAll()
	else:
		package_query.query(package_names)


def mainList(args):
	print "gothere mainList"
	try:
		opts, args = getopt.getopt(args, "ailv", ["all", "info", "long", "verbose"])
	except getopt.error, e:
		print "Error parsing args: %s" % e
		sys.exit(1)

	list_all = None
	for (opt, val) in opts:
		if opt in ["-a", "--all"]:
			list_all = 1
		
	package_names = []
	if len(args):
		package_names = args
	else:
		# assume we want to see everything
		list_all = 1
	glob_patterns = []
	for package_name in package_names:
		for glob_char in '*?[]':
			if string.find(package_name, glob_char) >= 0:
				# this insnt a package name but a glob 
				glob_patterns.append(package_name)
				package_names.remove(package_name)

	packageList = PackageList()
	if len(glob_patterns):
		packageList.setGlobs(glob_patterns)
	packageList.listAll()



def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
	except:
		print "Error parsing commandline arguments"
		sys.exit(1)

	if not len(args):
		print "need a commandline argument"
		sys.exit(1)

	for (opt, val) in opts:
		if opt in ["-h", "--help"]:
			print "help!"
			sys.exit(1)

	try:
		mode = args[0]
	except IndexError:
		print "need to specify a mode"
		sys.exit()

	modeargs = args[args.index(mode)+1:]
	print "mode: %s" % mode
	if mode not in ["list", "query", "remove", "install"]:
		print "%s is not a valid mode" % mode
		sys.exit()

	if mode == "list":
		mainList(modeargs)

	if mode == "query":
		mainQuery(modeargs)
	
	sys.exit(1)

if __name__ == "__main__":
	main()
	
