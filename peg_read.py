#!/usr/bin/python3

import sys
import re
from rf2 import xyz, read4u, read4S, read2u, read1u, read1S, readNstr, readFixNstr, readCstr, readflt, readXYZ, readMt33
from PIL import Image as pimg

class Texx:
	Name = ""
	width = 0
	height = 0
	fmt = 0
	fmt2 = 0
	flgs = 0
	frmCnt = 0
	animDelay = 0
	mipCount = 0
	unk1 = 0
	unk2 = 0
	offset = 0
	sz = 0
	img = None
	

class Peg:
	Texturies = None
	
	def __init__(self):
		self.Texturies = list()


def DecodeA1B5G5R5(tx, inp):
	img = pimg.new('RGBA', (tx.width, tx.height))
	pix = img.load()
	
	ipos = 0
	for y in range(tx.height):
		for x in range(tx.width):
		
			wrd = int.from_bytes(inp[ipos : ipos + 2], byteorder="little")
			
			a = 255 * (wrd >> 15)
			b = int(((wrd >> 10) & 0x1F) * 8.23)
			g = int(((wrd >> 5) & 0x1F) * 8.23)
			r = int((wrd & 0x1F) * 8.23)
			
			pix[ x , y ] = (r, g, b, a)
			ipos += 2
	return img

def DecodeA8B8G8R8(tx, inp):
	img = pimg.new('RGBA', (tx.width, tx.height))
	pix = img.load()
	
	ipos = 0
	for y in range(tx.height):
		for x in range(tx.width):
		
			bts = inp[ipos : ipos + 4]
			
			a = bts[3]
			b = bts[2]
			g = bts[1]
			r = bts[0]
			
			if (a != 0):
				a = 255
			pix[ x , y ] = (r, g, b, a)
			ipos += 4
	return img

def DecodeIndexed(tx, inp):
	img = pimg.new('RGBA', (tx.width, tx.height))
	pix = img.load()
	
	palette = []
	
	ipos = 0

	for p in range(256):
		if (tx.fmt2 == 1):
			wrd = int.from_bytes(inp[ipos : ipos + 2], byteorder="little")
		
			a = 255 * (wrd >> 15)
			b = int(((wrd >> 10) & 0x1F) * 8.23)
			g = int(((wrd >> 5) & 0x1F) * 8.23)
			r = int((wrd & 0x1F) * 8.23)
		
			palette.append( (r, g, b, a) )
			ipos += 2
		elif (tx.fmt2 == 2):
			bts = inp[ipos : ipos + 4]
		
			a = bts[3]
			b = bts[2]
			g = bts[1]
			r = bts[0]
			
			if (a != 0):
				a = 255
		
			palette.append( (r, g, b, a) )
			ipos += 4
		else:
			print("Fmt2:", tx.fmt2)
		
	for y in range(tx.height):
		for x in range(tx.width):
		
			idx = inp[ipos]
			
			## PS2 CLUT index Swizzle 
			idx = idx & 0xE7 | (idx >> 1) & 8 | (idx << 1) & 0x10
			
			pix[ x , y ] = palette[idx]
			ipos += 1
	
	return img
			
			

def ReadPeg(filename):
	fl = open(filename, "rb")
	
	fl.seek(0, 2)
	SZ = fl.tell()
	fl.seek(0, 0)
	
	Sign = read4u(fl)
	if (Sign != 0x564B4547):
		return None
		
	Version = read4u(fl)
	if (Version != 6):
		return None
	
	pg = Peg()
	
	hdrSz = read4u(fl)
	datSz = read4u(fl)
	texCount = read4u(fl)
	unknown14 = read4u(fl)
	frameCount = read4u(fl)
	unknown1C = read4u(fl)
	
	## Pre allocate
	for i in range(texCount):
		pg.Texturies.append(Texx())
	
	## Read headers
	for i in range(texCount):
		tx = pg.Texturies[i]
		tx.width = read2u(fl)
		tx.height = read2u(fl)
		tx.fmt = read1u(fl)
		tx.fmt2 = read1u(fl)
		tx.flgs = read1u(fl)
		tx.frmCnt = read1u(fl)
		tx.animDelay = read1u(fl)
		tx.mipCount = read1u(fl)
		tx.unk1 = read1u(fl)
		tx.unk2 = read1u(fl)
		tx.Name = readFixNstr(fl, 48)
		tx.offset = read4u(fl)
		
		if (i > 0):
			pg.Texturies[i - 1].sz = tx.offset - pg.Texturies[i - 1].offset
		
		if (i == texCount - 1):
			tx.sz = SZ - tx.offset
	
	# Decode
	for tx in pg.Texturies:	
		fl.seek(tx.offset, 0)
		pkd = fl.read(tx.sz)	
		
		if (tx.fmt == 3):
			tx.img = DecodeA1B5G5R5(tx, pkd)
		elif (tx.fmt == 4):
			tx.img = DecodeIndexed(tx, pkd)
		elif (tx.fmt == 7):
			tx.img = DecodeA8B8G8R8(tx, pkd)
		else:
			print("Unknown format :", tx.fmt)
	
	return pg
			


def main():
	PEG = ReadPeg(sys.argv[1])
	
	for tx in PEG.Texturies:	
		if (tx.img != None):
			tx.img.save(tx.Name + ".png")


if __name__ == '__main__':
	main()
	