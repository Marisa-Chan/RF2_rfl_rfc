#!/usr/bin/python3

import sys
import os
import re
import struct
from enum import Enum
from rf2 import xyz, read4u, read4S, read2u, read1u, read1S, readNstr, readCstr, readFixNstr, readflt, readXYZ, readMt33
from rfc_read import LoadRfc
from peg_read import ReadPeg


LVLVersion = 0

### Extracted from entity.tbl
EntityDict = {	"molov" : "molov.rfc",
			"testchar" : "molovnano.rfc",
			"burke" : "burke.rfc",
			"repta" : "repta.rfc",
			"reptaplus" : "repta_plus.rfc",
			"quill" : "quill.rfc",
			"tangier" : "tangier.rfc",
			"tangier_cloak" : "tangier_cloak.rfc",
			"shrike" : "shrike.rfc",
			"echo" : "echo.rfc",
			"sopot" : "sopot.rfc",
			"sopot_mm" : "sopot_mm.rfc",
			"businessman 1" : "business_man1.rfc",
			"businessman 2" : "business_man2.rfc",
			"businesswoman 1" : "business_woman1.rfc",
			"businesswoman 2" : "business_woman2.rfc",
			"military grunt" : "military_grunt.rfc",
			"military sarge" : "military_grunt.rfc",
			"military officer" : "MO.rfc",
			"sniper" : "sniper.rfc",
			"elite guard" : "sopot_guard.rfc",
			"elite guard leader" : "sopot_guard.rfc",
			"city police" : "technician.rfc",
			"security guard" : "security_guard.rfc",
			"nano civ" : "nano_civilian.rfc",
			"nano elite" : "nano3.rfc",
			"nano grunt" : "nano1.rfc",
			"rf grunt m1" : "military_grunt.rfc",
			"rf grunt m2" : "fodder_cop.rfc",
			"rf grunt f1" : "rf_femgrunt1.rfc",
			"technician" : "technician.rfc",
			"scientist" : "scientist.rfc",
			"fodder cop" : "fodder_cop.rfc",
			"auto turret" : "geomod_turret.rfc",
			"ceiling turret" : "ceiling_turret.rfc",
			"auto turret0" : "geomod_turret_R.rfc",
			"mini sub" : "submarine.v3d",
			"gunship" : "chopper_gunship.rfc",
			"shrike gunship" : "Shrike_gunship.rfc",
			"dropship" : "gunship_2.rfc",
			"sopot_jeep" : "sopot_jeep.rfc",
			"semi" : "semi.rfc",
			"car_sport" : "car_sport.rfc",
			"swarmer bot" : "swarmer.rfc",
			"camera bot" : "cambot.rfc",
			"mech suit" : "mech_suit.rfc",
			"tread tank" : "tread_tank.rfc" }


class FFLAGS(Enum): #Face flags. Seems it may be wrong
	COL = 0x8
	NOTRENDER1 = 0x10
	NOTRENDER = 0x2000 

class Room:
	Bounds = None
	t     = 0
	unk1  = 0
	unk2  = 0.
	unk3  = 0.
	unk4  = 0.
	unk5  = 0.
	unk6  = 0
	unk7  = 0.
	unk8  = 0
	unk9  = 0.
	unk10  = 0.
	unk11  = 0.
	unk12  = 0.
	unusedStr = "None"
	
	SubRoom = None
	ParentRoom = -1
	URoom = -1 #Unknown room link
	
	def __init__(self):
		self.Bounds = ()
		self.SubRoom = list()

class Portal:
	Room1 = -1
	Room2 = -1
	Bounds = None
	
	def __init__(self):
		self.Bounds = list()

class FaceVtx:
	ID = -1
	R = 128
	G = 128
	B = 128
	A = 255
	U = 0.
	V = 0.

class Face:
	N = xyz()
	D = 0.
	TexID = -1
	Flags = 0
	unk1 = -1
	unk2 = -1
	Vtx = None
	RoomID = -1
	
	def __init__(self):
		self.Vtx = list()

class Geom:
	Textures = None
	Rooms = None
	Portals = None
	Verticies = None
	Faces = None
	
	def __init__(self):
		self.Textures = list()
		self.Rooms = list()
		self.Portals = list()
		self.Verticies = list()
		self.Faces = list()

class MoverBrush:
	Pos = xyz()
	Mt33 = []
	Geom = None
	ID = -1
	Flags = 0

class Entity:
	Pos = xyz()
	Mt33 = []
	Tp = ""

class RFL:
	Geom = None
	Entities = None
	Movers   = None
	Peg = None
	
	def __init__(self):
		self.Entities = list()
		self.Movers   = list()



def GeomReader(hndl):
	g = Geom()
	
	if ( LVLVersion == 200 ):
		read4u(hndl)			# SKIP
	
	fname = readNstr(hndl)      # max 0x3F bytes; SKIP
	read4u(hndl)				# SKIP
	
	num = read4u(hndl)
	for i in range(num):				#Textures
		f = readNstr(hndl)
		g.Textures.append(f)
	
	if ( LVLVersion == 200 ):
		n = read4u(hndl)
		for j in range(n):
			read4u(hndl)	#SKIP
			readflt(hndl)	#SKIP
			readflt(hndl)	#SKIP
	
	if ( LVLVersion > 200 and LVLVersion < 212 ):
		read4u(hndl)	#SKIP
	
	num = read4u(hndl)
	for i in range(num): #Rooms
		
		room = Room()
		room.t = read4u(hndl)
		
		if ( LVLVersion > 233 ):
			
			# Seems room bound box		
			room.Bounds = (readXYZ(hndl), readXYZ(hndl))
			
			
			room.unk1 = read4u(hndl)
			room.unk2 = readflt(hndl)
			
			room.unusedStr = readNstr(hndl)
			
			room.unk3 = readflt(hndl)
			room.unk4 = readflt(hndl)
			room.unk5 = readflt(hndl)
			
			room.unk6 = read4u(hndl)
			room.unk7 = readflt(hndl)
			
			room.unk8 = read4u(hndl)
			
			if ( LVLVersion < 284 ):
				read4u(hndl) #SKIP
				read4u(hndl) #SKIP
				readflt(hndl, 0, 0.0) #SKIP
				read4u(hndl) #SKIP
			
			room.unk9 = readflt(hndl)
			room.unk10 = readflt(hndl)
			
			if ( LVLVersion < 284 ):
				room.unk11 = 0.
				room.unk12 = 0.
			else:
				room.unk11 = readflt(hndl)
				room.unk12 = readflt(hndl)
			
			if ( LVLVersion < 284 ):
				read4u(hndl) #SKIP
				read4u(hndl) #SKIP
			
			if ( LVLVersion < 284 and (room.unk1 & (1 << 13)) != 0 ):
				readNstr(hndl) #SKIP
		
		else:
			## Is needed another versions?
			print("Needed Room Reading for version <= 233")
			pass
		
		if ( LVLVersion >= 231 and LVLVersion < 252 ):
			n = read4u(hndl)
			for j in range(n):
				read4u(hndl) #SKIP

		g.Rooms.append(room)		
	
	num = read4u(hndl) ## Version > 113. Else = 0
	for i in range(num): #Sub Rooms
		roomID = read4u(hndl)
		subCount = read4u(hndl)
		
		rp = g.Rooms[roomID]
		
		for j in range(subCount):
			subRoomID = read4u(hndl)
			
			sr = g.Rooms[subRoomID]
			sr.ParentRoom = roomID
			
			rp.SubRoom.append(sr)

	
	if LVLVersion > 216:  # Some Room thing...
		num = read4u(hndl)
		for i in range(num):
			roomID = read4u(hndl)			
			room2ID = read4u(hndl) ## In roomID field write room2ID
			
			rm = g.Rooms[roomID]
			rm.URoom = room2ID
	
	num = read4u(hndl) # Room Portals
	for i in range(num):
		prt = Portal()
		
		room1ID = read4u(hndl)
		room2ID = read4u(hndl)
		
		prt.Room1 = room1ID
		prt.Room2 = room2ID		
		
		# Seems portal bound box	
		prt.Bounds = (readXYZ(hndl), readXYZ(hndl))
		
		g.Portals.append(prt)
	
	num = read4u(hndl)  # Vertex
	for i in range(num):
		g.Verticies.append( readXYZ(hndl) )		
	
	num = read4u(hndl)  # Faces
	for i in range(num):
		face = Face()
		
		if LVLVersion >= 167:
			# A B C D ?
			face.N = readXYZ(hndl)
			face.D = readflt(hndl)
		
		face.TexID = read4S(hndl) #if tex id <= -1, then use misc-static.tga
		
		v123 = -1
		if LVLVersion < 212:
			v123 = read4u(hndl)
		
		read4u(hndl)   # SKIP. From version >= 266
		face.unk1 = read4u(hndl) # From version >= 49
		
		if ( LVLVersion >= 66 and LVLVersion < 212 ):
			read4u(hndl)   #SKIP
			read4u(hndl)   #SKIP
		
		face.unk2 = read4u(hndl) # From version >= 63
		
		face.Flags = 0
		if LVLVersion >= 77:
			face.Flags = read4u(hndl)
		elif LVLVersion >= 75:
			face.Flags = read1u(hndl)
		
		read4u(hndl) #SKIP From version 79
		
		if (LVLVersion >= 295 and (face.Flags & 0x8000) != 0):
			readflt(hndl) #skip
			tmp = readflt(hndl)
			if tmp == 1.0:
				face.Flags |= 0x100000
			elif tmp == 1.35:
				face.Flags |= 0x200000
			elif tmp == 1.5:
				face.Flags |= 0x400000
			else:
				face.Flags |= 0x800000
		
		if ((LVLVersion >= 217 and LVLVersion < 234) or LVLVersion >= 250):
			read1u(hndl) #SKIP
			read1u(hndl) #SKIP
			read1u(hndl) #SKIP
			readflt(hndl) #Compare with 0.0 and do flags on FPU state test |= 0x4000000
			
		if (LVLVersion >= 230 and LVLVersion < 252):
			for j in range(6):
				read1u(hndl) #SKIP
		
		face.RoomID = read4u(hndl) # Room ID for this face

		vnum = read4u(hndl)
		for j in range(vnum):
			vtx = FaceVtx()
			vtx.ID = read4u(hndl)
			vtx.U = readflt(hndl)
			vtx.V = readflt(hndl)
			
			if LVLVersion >= 212:
				vtx.R = read1u(hndl)
				vtx.G = read1u(hndl)
				vtx.B = read1u(hndl)
				vtx.A = read1u(hndl)
			elif v123 > -1:
				readflt(hndl) #SKIP
				readflt(hndl) #SKIP			
			
			face.Vtx.append(vtx)
		
		g.Faces.append(face)
	
	return g



def Chunk0x7001(hndl):
	num = read4u(hndl) # Maximum 48 characters
	print("Chunk 0x7001 (load characters):")
	
	for i in range(num):
		fname = readNstr(hndl) # max 0x40 bytes
		unkStr = readNstr(hndl) # max 0x80 bytes; if LvLVersion >= 200    // Always NULL?
		
		fname = fname[:fname.find(".")] + ".rfc"
		
		print("\t", fname, unkStr)

	for i in range(num):
		read4u(hndl) # not used 


def Chunk0x7002(hndl):
	num = read4u(hndl)
	print("Chunk 0x7002:")
	
	for i in range(num):
		fname = readNstr(hndl) # max 0x20 bytes
		fname = fname[:fname.find(".")] + ".rfa"
		
		print("\t", fname)

	for i in range(num):
		read4u(hndl) # not used 


def Chunk0x7003(hndl):
	num = read4u(hndl)
	print("Chunk 0x7003:")
	
	for i in range(num):
		fname = readNstr(hndl) # max 0x20 bytes
		fname = fname[:fname.find(".")] + ".rfm"
		
		print("\t", fname)

	for i in range(num):
		read4u(hndl) # not used 


def Chunk0x7004(hndl):
	num = read4u(hndl)
	print("Chunk 0x7004:")
	
	for i in range(num):
		fname = readNstr(hndl) # max 0x20 bytes
		fname = fname[:fname.find(".")] + ".rfe"
		
		print("\t", fname)
	
	for i in range(num):
		read4u(hndl) # not used 


def Chunk0x7005(hndl):
	num = read4u(hndl)
	print("Chunk 0x7005:")
	
	for i in range(num):
		fname = readNstr(hndl) # max 0x20 bytes
		fname = fname[:fname.find(".")] + ".peg"
		
		print("\t", fname)
	
	for i in range(num):
		read4u(hndl) # not used 


def Chunk0x900(hndl):
	print("Chunk 0x900:")
	
	fname = readNstr(hndl) # max 0x28 bytes
	print("\t", fname)
	
	read4u(hndl) ##SKIP
	
	clr1 = hndl.read(4) # RGBA?
	useflag1 = hndl.read(1)[0] # if == 1 -> use default, else use clr1
	
	clr2 = hndl.read(4) # RGBA?
	flt1 = readflt(hndl)
	flt2 = readflt(hndl)
	clr3 = None
	byte_71BD1F  = None
	
	if ( LVLVersion >= 247 ):
		hndl.read(4)			# SKIP
		readflt(hndl)			# SKIP
		readflt(hndl)			# SKIP
		if ( LVLVersion >= 272 ):
			readflt(hndl)		# SKIP

	if ( LVLVersion >= 258 ):
		readflt(hndl)			# SKIP
		
	if ( LVLVersion >= 270 ):
		clr3 = hndl.read(4)		# RGBA?
		byte_71BD1F = read4u(hndl)

	if ( LVLVersion >= 287 ):
		readflt(hndl)			# SKIP
	
	print("\t", clr1.hex(), useflag1, clr2.hex(), flt1, flt2, clr3.hex(), byte_71BD1F)


def Chunk0x100(hndl):
	print("Chunk 0x100: Level Geometry")
	Geom = GeomReader(hndl)
	return Geom

def Chunk0x400(hndl): ##Cutscene and camera related
	print("Chunk 0x400: Cutscene and camera related")
	num = read4u(hndl)
	for i in range(num):
		 read4u(hndl)
		 readNstr(hndl)
		 readXYZ(hndl)
		 readMt33(hndl)
		 readNstr(hndl)
		 read1u(hndl)

def Chunk0x500(hndl): ##Scene sounds?
	print("Chunk 0x500: Scene sounds?")
	num = read4u(hndl)
	for i in range(num):
		 read4u(hndl)
		 readXYZ(hndl)
		 read1u(hndl)
		 readNstr(hndl)
		 readflt(hndl)
		 readflt(hndl)
		 readflt(hndl)
		 read4u(hndl)

def Chunk0x700(hndl):
	print("Chunk 0x700:")
	num = read4u(hndl)
	for i in range(num):
		 read4u(hndl)
		 readXYZ(hndl)
		 readMt33(hndl)
		 readNstr(hndl)
		 read1u(hndl)
		 read4u(hndl)
		 read1u(hndl)
		 read1u(hndl)
		 read1u(hndl)

def Chunk0xD00(hndl):
	print("Chunk 0xD00:")
	num = read4u(hndl)
	for i in range(num):
		 read4u(hndl)
		 readNstr(hndl)
		 readXYZ(hndl)
		 readMt33(hndl)
		 readNstr(hndl)
		 read1u(hndl)
		 read4u(hndl)
		 readXYZ(hndl)

def Chunk0x1000(hndl):
	print("Chunk 0x1000: Decals")
	num = read4u(hndl)
	for i in range(num):
		 read4u(hndl) #SKIP
		 readNstr(hndl) #SKIP
		 readXYZ(hndl)
		 readMt33(hndl)
		 readNstr(hndl) #SKIP
		 read1u(hndl) #SKIP
		 readflt(hndl)
		 readflt(hndl)
		 readflt(hndl)
		 readNstr(hndl)
		 read4u(hndl)
		 read1u(hndl)
		 if (LVLVersion >= 265 ):
		    read1u(hndl)
		 if (LVLVersion >= 294 ):
		    read1u(hndl)
		 if (LVLVersion >= 280 ):
		    read1u(hndl)
		    read1u(hndl)
		 read4u(hndl)
		 readflt(hndl)
		 if (LVLVersion >= 261 ):
		    read4u(hndl)
		 if (LVLVersion >= 262 ):
		    read4u(hndl)


def Chunk0x1100(hndl):
	print("Chunk 0x1100: Push Region???")
	num = read4u(hndl)
	for i in range(num):
		read4u(hndl)
		readNstr(hndl)
		readXYZ(hndl)
		readMt33(hndl)
		readNstr(hndl)
		read1u(hndl)
		a = read4u(hndl)
		if (a == 3):
			readXYZ(hndl)
		elif (a == 2):
			readXYZ(hndl)
		else:
			readflt(hndl)
		readflt(hndl)
		read4u(hndl)
		

def Chunk0x7677(hndl):
	print("Chunk 0x7677: ??")
	num = read4u(hndl)
	for i in range(num):
		read4u(hndl)
		readNstr(hndl)
		readXYZ(hndl)
		readMt33(hndl)
		readNstr(hndl)
		read1u(hndl)
		readXYZ(hndl)
		readflt(hndl)
		read1u(hndl)
		readflt(hndl)
		read1u(hndl)

def Chunk0x7678(hndl):
	print("Chunk 0x7678: Lights glare/corona/beams")
	num = read4u(hndl)
	for i in range(num):
		read4u(hndl)
		readNstr(hndl)
		readXYZ(hndl)
		readMt33(hndl)
		readNstr(hndl)
		read1u(hndl)
		read4u(hndl)
		if (LVLVersion >= 259 ):
		    read1u(hndl)
		if (LVLVersion >= 288 ):
		    read1u(hndl)
		if (LVLVersion >= 289 ):
		    read1u(hndl)
		if (LVLVersion >= 292 ):
		    read1u(hndl)
		if (LVLVersion < 232 ):
			read4u(hndl)
		if (LVLVersion >= 232 ):
			read1u(hndl)
			
		s = readNstr(hndl)
		if (s != ""):
			readflt(hndl)
			readflt(hndl)
			readflt(hndl)
			readflt(hndl)
			readflt(hndl)
			
		s = readNstr(hndl)
		if (s != ""):
			readflt(hndl)
			readflt(hndl)
			readflt(hndl)
			
		if (LVLVersion >= 276 ):
			read1u(hndl)
		
		for j in range( read4u(hndl) ):
			read4u(hndl)
		
def Chunk0x7777(hndl):
	print("Chunk 0x7777: Event - conversation")
	num = read4u(hndl)
	for i in range(num):
		read4u(hndl)
		readNstr(hndl)
		readXYZ(hndl)
		readMt33(hndl)
		readNstr(hndl)
		read1u(hndl)
		for j in range(read4u(hndl)):
			read4u(hndl)
			read4u(hndl)
			readflt(hndl)
			readFixNstr(hndl, 0x18)
			read4u(hndl)
			read4u(hndl)
			read4u(hndl)
			readFixNstr(hndl, 0x10)
		readflt(hndl)
	
		
		
		
		
def Chunk0x7680(hndl):
	print("Chunk 0x7680: Related to effects??")
	num = read4u(hndl)
	for i in range(num):
		read4u(hndl)
		readNstr(hndl)
		readXYZ(hndl)
		readMt33(hndl)
		readNstr(hndl)
		read1u(hndl)
		read4u(hndl)
		read4u(hndl) #SKIP
		read4u(hndl)
		if (LVLVersion >= 260):
			read4u(hndl)
		read4u(hndl)
		read4u(hndl)
		if (LVLVersion >= 228):
			read4u(hndl)
			read1u(hndl)
			read1u(hndl)
		if (LVLVersion >= 240):
			readflt(hndl)
			readflt(hndl)
			readNstr(hndl)
			read1u(hndl)


def Chunk0x30000(hndl):
	print("Chunk 0x30000: Entities")
	EntLst = list()
	num = read4u(hndl)
	for i in range(num):
		ent = Entity()
		EntLst.append(ent)
		
		read4u(hndl)
		ent.Tp = readNstr(hndl) # Type
		ent.Pos = readXYZ(hndl)
		ent.Mt33 = readMt33(hndl)
		readNstr(hndl)  # Name
		read1u(hndl)
		read4u(hndl)
		read4u(hndl)
		if (LVLVersion >= 274):
			read4u(hndl)
		read4u(hndl)
		readNstr(hndl)
		readNstr(hndl)
		
		v65 = 0
		 ### Read flags
		if (LVLVersion >= 248):
			flg = read4u(hndl)
			if (LVLVersion >= 263):
				read4u(hndl)
			
			if (flg & (1 << 17)) != 0:
				v65 = 1
		else:
			read1u(hndl) ##SKIP
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl) ##SKIP
			read1u(hndl)
		
		read4u(hndl)
		read4u(hndl)
		if (LVLVersion < 248):
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
		
		readflt(hndl)
		readflt(hndl)
		if (LVLVersion >= 242):
			readflt(hndl)
			readflt(hndl)
		
		read4u(hndl)
		
		readNstr(hndl)
		readNstr(hndl)
		readNstr(hndl)
		readNstr(hndl)
		readNstr(hndl)
		readNstr(hndl)
		readNstr(hndl)
		if (LVLVersion >= 254):
			readNstr(hndl)
		
		read1u(hndl)
		read1u(hndl)
		
		if (LVLVersion < 232):
			for j in range( read4u(hndl) ):
				readNstr(hndl)
				read4u(hndl)
		
		read4u(hndl)
		read4u(hndl)
		read4u(hndl) #SKIP
		
		if (LVLVersion < 248):
			read1u(hndl)
			read1u(hndl)
			read1u(hndl) #SKIP
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			if (LVLVersion >= 246):
				read1u(hndl)
			read1u(hndl)
			read1u(hndl)
			v65 = read1u(hndl)
		
		if (v65):
			readflt(hndl)
			if (LVLVersion >= 214):
				readflt(hndl)
				
		if (LVLVersion < 254):
			readNstr(hndl)
			readNstr(hndl)
		
		if (LVLVersion >= 218):
			read4u(hndl)
			read1u(hndl)
		
		if (LVLVersion >= 253):
			readflt(hndl)
		
		if (LVLVersion >= 255):
			readflt(hndl)
			
		if (LVLVersion >= 281):
			readflt(hndl)
		
		if (LVLVersion >= 241 and LVLVersion < 248):
			read1u(hndl)
		
		n = 18
		if (LVLVersion >= 267):
			n = 19
		
		for j in range(n):
			readNstr(hndl)
			readNstr(hndl)
	
	return EntLst


def Chunk0x2000(hndl):
	print("Chunk 0x2000: Level Geometry")
	num = read4u(hndl)
	tmp = list()
	
	for i in range(num):
		mvr = MoverBrush()
		mvr.ID = read4u(hndl)
		mvr.Pos = readXYZ(hndl)
		mvr.Mt33 = readMt33(hndl)
		mvr.Geom = GeomReader(hndl)
		
		tmp.append(mvr)
		
		v5 = read4u(hndl)
		read4u(hndl)
		read4u(hndl)
		
		if (v5 & 8):
			read4u(hndl)
			read4u(hndl)
			read4u(hndl)
			read4u(hndl)
			readflt(hndl)
			readflt(hndl)
			readflt(hndl)
			readflt(hndl)
			read4u(hndl)
			readflt(hndl)
			read1u(hndl)
	### i in range(num)
	
	return tmp


def ReadRFL(fname):
	global LVLVersion
	rfl = RFL()
	
	fl = open(fname, "rb")
	fl.seek(0, 2)
	SZ = fl.tell()
	fl.seek(0, 0)
	
	if (read4u(fl) != 0xD4BADA55):
		print("Not a RFL")
		exit(-1)
	
	pegname = fname
	if (pegname.rfind(".") >= 0):
		pegname = pegname[:pegname.rfind(".")] + ".peg"
		if os.path.exists(pegname):
			rfl.Peg = ReadPeg(pegname)
		
	LVLVersion = read4u(fl) # RF2 valid versions >= 201 && <= 295
	
	print("Level version ", LVLVersion)
	
	read4u(fl)  # from version 114. Before = 0
	read4u(fl)
	read4u(fl)
	read4u(fl)  # from version 160. Before = 35
	read4u(fl)  # from version 160. Before = 0
	
	lvlName = readNstr(fl)     # from version 170. Before = "<untitled>"
	print("Level name :", lvlName)
	
	NextPos = fl.tell()
	while fl.tell() < SZ:
		if (fl.tell() != NextPos):
			print("Missing data? at ", hex(fl.tell()), " size ", hex(NextPos - fl.tell()))
		fl.seek(NextPos, 0)
		ChunkID = read4u(fl)
		ChunkSize = read4u(fl)
		NextPos = fl.tell() + ChunkSize
	
		if (ChunkID == 0x600 or ##Events?
			ChunkID == 0xE00 or
			ChunkID == 0xF00 or
			ChunkID == 0x3000 or
			ChunkID == 0x4000 or
			ChunkID == 0x6000 or
			ChunkID == 0x7679 or
			ChunkID == 0x7681 or ##VFX??
			ChunkID == 0x7779 or ##Spline path
			ChunkID == 0x7900 or
			ChunkID == 0x7901 or
			ChunkID == 0x10000 or
			ChunkID == 0x20000 or
			ChunkID == 0x40000 or
			ChunkID == 0x50000 or
			ChunkID == 0x60000 or
			ChunkID == 0x70000 ):
			print("Chunk ID: ", hex(ChunkID), " NOT IMPLEMENTED    Size:", hex(ChunkSize), " at: ", hex(fl.tell()))
			fl.seek(ChunkSize, 1)
		elif (ChunkID == 0x7001):
			Chunk0x7001(fl)
		elif (ChunkID == 0x7002):
			Chunk0x7002(fl)
		elif (ChunkID == 0x7003):
			Chunk0x7003(fl)
		elif (ChunkID == 0x7004):
			Chunk0x7004(fl)
		elif (ChunkID == 0x7005):
			Chunk0x7005(fl)
		elif (ChunkID == 0x900):
			Chunk0x900(fl)
		elif (ChunkID == 0x100):    ### SCENE GEOMETRY
			rfl.Geom = Chunk0x100(fl)
		elif (ChunkID == 0x2000):   ### SCENE GEOMETRY
			rfl.Movers = Chunk0x2000(fl)
		elif (ChunkID == 0x400):
			Chunk0x400(fl)
		elif (ChunkID == 0x500):
			Chunk0x500(fl)
		elif (ChunkID == 0x700):
			Chunk0x700(fl)
		elif (ChunkID == 0xD00):
			Chunk0xD00(fl)
		elif (ChunkID == 0x1000):
			Chunk0x1000(fl)
		elif (ChunkID == 0x1100):
			Chunk0x1100(fl)
		elif (ChunkID == 0x7680):
			Chunk0x7680(fl)
		elif (ChunkID == 0x7677):
			Chunk0x7677(fl)
		elif (ChunkID == 0x7678):
			Chunk0x7678(fl)
		elif (ChunkID == 0x7777):
			Chunk0x7777(fl)
		elif (ChunkID == 0x30000):
			rfl.Entities = Chunk0x30000(fl)
		elif (ChunkID == 0):
			pass
		else :
			print("Chunk ID: ", hex(ChunkID), " NOT USED    Size:", hex(ChunkSize), " at: ", hex(fl.tell()))
			if (ChunkSize > 0):
				fl.seek(ChunkSize, 1)
	
	return rfl
	


TexDict = dict()
tuID = 1 #Texture coordinate index

def WriteLvlGeom(out, g, pos = xyz(), rot = None, vtxOff = 0):
	global tuID
	
	i = 0
	for vtx in g.Verticies:
		v = vtx.TransformBy(rot) + pos
		#out.write("# VtxID {:d}\n".format(vtxOff + i))
		out.write("v {:f} {:f} {:f}\n".format(-v.x, v.y, v.z))
		i += 1

	for f in g.Faces:
		if (f.Flags & (FFLAGS.NOTRENDER.value | FFLAGS.NOTRENDER1.value)) == 0 and f.TexID != -1: ### Do not export invisible?
			if (f.TexID != -1):
				out.write("usemtl {:s}\n".format( TexDict[g.Textures[f.TexID].lower()] ))
			
			for v in f.Vtx:
				out.write("vt {:f} {:f}\n".format(v.U, 1.0 - v.V))
			
			#out.write("# Flags {:X} unk1 {:X} unk2 {:d}\n".format(f.Flags, f.unk1, f.unk2))
			out.write("f ")
			i = 0
			for v in f.Vtx:
				out.write(" {:d}/{:d}".format(v.ID + vtxOff, tuID + i))
				i += 1
			out.write("\n")
			
			tuID += len(f.Vtx)
	
	return vtxOff + len(g.Verticies)


def WriteRfcGeom(out, model, pos = xyz(), rot = None, vtxOff = 0):
	global tuID
	if len(model.Bones) > 0:
		for obj in model.ObjList:
			lod = obj.LodList[0]
			
			for vtx in lod.skin.vtxList:
				v = vtx.pos.TransformBy(rot) + pos
				out.write("v {:f} {:f} {:f}\n".format(-v.x, v.y, v.z))
			
			for geom in lod.skin.GeomList:
				out.write("usemtl {:s}\n".format( TexDict[ lod.skin.Textures[ geom.TexID ].lower() ] )  )
				
				for tr in geom.Triangles:
					out.write("vt {:f} {:f}\nvt {:f} {:f}\nvt {:f} {:f}\n".format(tr[0].u, 1.0 - tr[0].v, tr[1].u, 1.0 - tr[1].v, tr[2].u, 1.0 - tr[2].v))
					out.write("f {0:d}/{3:d} {1:d}/{4:d} {2:d}/{5:d}\n".format(tr[0].VtxID + vtxOff, tr[1].VtxID + vtxOff, tr[2].VtxID + vtxOff,
																			                   tuID,             tuID + 1,              tuID + 2 ))
					tuID += 3
			
			vtxOff += len(lod.skin.vtxList)
	else:
		for obj in model.ObjList:
			lod = obj.LodList[0]
			
			for geom in lod.skin.GeomList:
				for vtx in geom.SimpleVertexes:
					v = (vtx.pos + lod.skin.Pos).TransformBy(rot) + pos
					out.write("v {:f} {:f} {:f}\n".format(-v.x, v.y, v.z))
				
				out.write("usemtl {:s}\n".format( TexDict[ lod.skin.Textures[ geom.TexID ].lower() ] )  )
				
				for tr in geom.Triangles:
					out.write("vt {:f} {:f}\nvt {:f} {:f}\nvt {:f} {:f}\n".format(tr[0].u, 1.0 - tr[0].v, tr[1].u, 1.0 - tr[1].v, tr[2].u, 1.0 - tr[2].v))
					out.write("f {0:d}/{3:d} {1:d}/{4:d} {2:d}/{5:d}\n".format(tr[0].VtxID + vtxOff, tr[1].VtxID + vtxOff, tr[2].VtxID + vtxOff,
																			                   tuID,             tuID + 1,              tuID + 2 ))
					tuID += 3
				vtxOff += geom.numSimpleVertex
	return vtxOff


def GetFileName(path, filename): ## Case-insensitive
	for f in os.listdir(path):
		if f.lower() == filename.lower():
			return os.path.normpath( "{:s}/{:s}".format(path, f ) )
	return ""

def main():
	global MTL

	if (len(sys.argv) < 2):
		print("Usage: rfl_read.py level.rfl outName.obj")
		exit(0)
	path = os.path.dirname(sys.argv[1])
	
	lvl = ReadRFL(sys.argv[1])
	numvtx = 1
	
	MTL = None
	OBJ = None
	
	if (len(sys.argv) > 2):
		OBJ = open(sys.argv[2], "w")
		MTL = open(sys.argv[2] + ".mtl", "w")
		OBJ.write("mtllib {:s}\n".format(sys.argv[2] + ".mtl"))
	else:
		OBJ = open("out.obj", "w")
		MTL = open("out.mtl", "w")
		OBJ.write("mtllib out.mtl\n")
	
	if not os.path.exists("outtex"): 
		os.mkdir("outtex")
	
	texID = 0
	##Write misc-static.tga (from Permanent_data/perma.peg)
	MTL.write("newmtl Tex{:d}\n\tmap_Kd outtex/{:s}.png\n".format(texID, "misc-static.tga"))
	TexDict[ "misc-static.tga" ] = "Tex{:d}".format(texID)
	texID += 1
	
	##Missing textures!
	TexDict[ "mtl_122_grate2.tga" ] = TexDict[ "misc-static.tga" ]
	TexDict[ "building1.tga" ] = TexDict[ "misc-static.tga" ]
	TexDict[ "gls_smoked01_a.tga" ] = TexDict[ "misc-static.tga" ]
	TexDict[ "green_grime.tga" ] = TexDict[ "misc-static.tga" ]
	
	
	## Write level textures
	if (lvl.Peg):
		for pg in lvl.Peg.Texturies:
			pg.img.save("outtex/{:s}.png".format(pg.Name))
			MTL.write("newmtl Tex{:d}\n\tmap_Kd outtex/{:s}.png\n".format(texID, pg.Name))
			TexDict[ pg.Name.lower() ] = "Tex{:d}".format(texID)
			texID += 1	
	
	#Write static mesh
	OBJ.write("o Lvl static\n")
	numvtx = WriteLvlGeom(OBJ, lvl.Geom, xyz(), None, numvtx)
	
	#Write mover mesh
	i = 0
	for movr in lvl.Movers:
		OBJ.write("o Lvl Mover Brush {:d}\n".format(i))
		numvtx = WriteLvlGeom(OBJ, movr.Geom, movr.Pos, movr.Mt33, numvtx)
		i += 1
	
	#Write entities
	i = 0
	for ent in lvl.Entities:
		if not (ent.Tp.lower() in EntityDict):
			print("Entity \"{:s}\" not in dict".format(ent.Tp))
			continue
		
		filename = GetFileName(path, EntityDict[ent.Tp.lower()])
		if filename == "" or (not os.path.isfile(filename)):
			print("Can't open entity object {:s}".format(filename))
			continue
		
		
		print("Loading Entity file :", filename)
		model = LoadRfc(filename)
		
		
		## Write Entity textures
		if (model.Peg):
			for pg in model.Peg.Texturies:
				if not pg.Name.lower() in TexDict:
					pg.img.save("outtex/{:s}.png".format(pg.Name))
					MTL.write("newmtl Tex{:d}\n\tmap_Kd outtex/{:s}.png\n".format(texID, pg.Name))
					TexDict[ pg.Name.lower() ] = "Tex{:d}".format(texID)
					texID += 1
		
		OBJ.write("o Entity {:d}\n".format(i))
		numvtx = WriteRfcGeom(OBJ, model, ent.Pos, ent.Mt33, numvtx)
		i += 1
	
	OBJ.close()
	MTL.close()

if __name__ == '__main__':
	main()

