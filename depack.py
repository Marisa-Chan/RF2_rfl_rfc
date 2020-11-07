#!/usr/bin/python3

import sys
import re

class FileEntry:
	Name = ""
	sz = 0
	offset = 0

def readcstr(hndl):
	tmp = bytearray()
	
	while(True):
		a = hndl.read(1)[0]
		if (a == 0):
			break
		tmp.append(a)
	
	return tmp.decode("ascii")

def read4u(hndl):
	return int.from_bytes(hndl.read(4), byteorder="little")


toc = open(sys.argv[1], "rb")
tocName = readcstr(toc)
pathName = readcstr(toc)
print(read4u(toc), read4u(toc))

packFile = readcstr(toc)

fileList = list()

num = read4u(toc)
i = 0
while i < num:
	fe = FileEntry()
	fe.Name = readcstr(toc)
	fe.sz = read4u(toc)
	fe.offset = read4u(toc)
	
	fileList.append(fe)
	
	i += 1

pack = open(re.sub("\\\\","/", packFile), "rb")

for f in fileList:
	pack.seek(f.offset, 0)
	data = pack.read(f.sz)
	out = open(sys.argv[2] + "/" + f.Name, "wb")
	out.write(data)
	out.close()
	
