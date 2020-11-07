#!/usr/bin/python3


import struct

class xyz:
	x = 0.
	y = 0.
	z = 0.
	
	def __init__(self, _x = 0., _y = 0., _z = 0.):
		self.x = _x
		self.y = _y
		self.z = _z
	
	def __add__(self, o):
		return xyz(self.x + o.x, self.y + o.y, self.z + o.z)
	
	def __str__(self):
		return "{:f} {:f} {:f}".format(self.x, self.y, self.z)
	
	def TransformBy(self, mtx):
		if (mtx != None):
			return xyz(mtx[0] * self.x + mtx[1] * self.y + mtx[2] * self.z ,
				       mtx[3] * self.x + mtx[4] * self.y + mtx[5] * self.z ,
					   mtx[6] * self.x + mtx[7] * self.y + mtx[8] * self.z )
		else:
			return xyz(self.x, self.y, self.z)



def read4u(hndl):
	return int.from_bytes(hndl.read(4), byteorder="little")

def read4S(hndl):
	return int.from_bytes(hndl.read(4), byteorder="little", signed=True)

def read2u(hndl):
	return int.from_bytes(hndl.read(2), byteorder="little")
	
def read1u(hndl):
	return int.from_bytes(hndl.read(1), byteorder="little")

def read1S(hndl):
	return int.from_bytes(hndl.read(1), byteorder="little", signed=True)

def readNstr(hndl):
	num = read2u(hndl)
	tmp = hndl.read(num)
	st = ""
	for c in tmp:
		if (c == 0):
			break
		st += chr(c)
	return st

def readCstr(hndl):
	tmp = ""
	while True:
		a = read1u(hndl)
		if (a == 0):
			break
		
		tmp += chr(a)
		
	return tmp

def readFixNstr(hndl, num):
	tmp = hndl.read(num)
	st = ""
	for c in tmp:
		if (c == 0):
			break
		st += chr(c)
	return st

def readflt(hndl):
	return struct.unpack("<f", hndl.read(4))[0]

def readXYZ(hndl):
	x = readflt(hndl)
	y = readflt(hndl)
	z = readflt(hndl)
	return xyz(x, y, z)

def readMt33(hndl):
	mtx =  [readflt(hndl), readflt(hndl), readflt(hndl),
			readflt(hndl), readflt(hndl), readflt(hndl),
			readflt(hndl), readflt(hndl), readflt(hndl)]
	return [mtx[3], mtx[6], mtx[0],
	        mtx[4], mtx[7], mtx[1],
			mtx[5], mtx[8], mtx[2]]
