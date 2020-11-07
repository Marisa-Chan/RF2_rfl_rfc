#!/usr/bin/python3

import sys
import os
import re
from rf2 import xyz, read4u, read4S, read2u, read1u, read1S, readNstr, readCstr, readflt, readXYZ, readMt33
from peg_read import ReadPeg

FVER = 0

class FLT4:
	a = 0.
	b = 0.
	c = 0.
	d = 0.
	
	def __init__(self, _a = 0., _b = 0., _c = 0., _d = 0.):
		self.a = _a
		self.b = _b
		self.c = _c
		self.d = _d

def readFLT4(hndl):
	return FLT4(readflt(hndl), readflt(hndl), readflt(hndl), readflt(hndl))

class RFC_s1:
	Name = ""
	field_18 = 0
	pos = xyz()
	field_28 = 0.

class RFC_s2:
	Name = ""
	field_40 = 0
	pos = xyz()
	field_50 = FLT4()

class Bone:
	Name = ""
	field_4C = 0
	pos = xyz()
	mtx = None

class VtxWeights: ## I think
	boneID = 0
	w = 0.

class Vertex:
	pos = xyz()
	normal = xyz()
	sh1 = 0
	Weights = None #weights
	
	def __init__(self):
		self.Weights = list()
	
	
class Skin:
	Textures = None
	fl1 = 0.
	Pos = xyz()
	Bounds = (xyz(), xyz())
	field_40 = 0
	vtxCount = 0
	vtxList = None
	numGeom = 0
	GeomList = None
	
	def __init__(self):
		self.Textures = list()
		self.vtxList = list()
		self.GeomList = list()
	

class RFC_s42:
	Bt1 = 0
	nstr = ""


class SimpleVertex:
	pos = xyz()
	normal = xyz()

class Geom:
	numSimpleVertex = 0
	SimpleVertexes = None
	TrianglesCount = 0
	Triangles = None
	unk = 0
	TexID = 0
	fl1 = 0.
	bts = None
	
	def __init__(self):
		self.SimpleVertexes = list()
		self.Triangles = list()

class FaceVtx:
	VtxID = -1
	u = 0.
	v = 0.
	
	def __init__(self, _id = 0, _u = 0., _v = 0.):
		self.VtxID = _id
		self.u = _u
		self.v = _v
	
class LodObj:
	name1 = ""
	name2 = ""
	dword1 = 0
	dword2 = 0
	skin = None
	t42lst = None
	
	def __init__(self):
		self.skin = Skin()
		self.t42lst = list()
	

class Object:
	numFlt = 0
	LodList  = None
	flts = None
	
	def __init__(self):
		self.LodList = list()
		self.flts = list()


class RFC:
	Lst1 = None
	Lst2 = None
	Bones = None
	rfc4num = 0
	LodHeap = None
	ObjNum = 0
	ObjList = None
	Peg = None
	
	def __init__(self):
		self.Lst1 = list()
		self.Lst2 = list()
		self.Bones = list()
		self.LodHeap = list()
		self.ObjList = list()



def LoadRfc(fname):
	global FVER
	rfc = RFC()
	
	fl = open(fname, "rb")
	
	fl.seek(0, 2)
	SZ = fl.tell()
	fl.seek(0, 0) 
	
	if (read4u(fl) != 0x87128712):
		print("Not a RFC")
		exit(-1)
	
	pegname = fname
	if (pegname.rfind(".") >= 0):
		if pegname.rfind(".rfc") >= 0:
			pegname = pegname[:pegname.rfind(".")] + "_vcm.peg"
		else:
			pegname = pegname[:pegname.rfind(".")] + "_v3d.peg"
		if os.path.exists(pegname):
			rfc.Peg = ReadPeg(pegname)
		
	FVER = read4u(fl) # RFC valid version == 0x114
	
	flg1 = read1u(fl)
	
	num = read4u(fl)
	for i in range(num):
		sub = RFC_s1()
		sub.Name = readCstr(fl)
		sub.field_18 = read4u(fl)
		sub.pos = readXYZ(fl)
		sub.field_28 = readflt(fl)
		
		rfc.Lst1.append(sub)
	
	num = read4u(fl)
	for i in range(num):
		sub = RFC_s2()
		sub.Name = readCstr(fl)
		sub.field_40 = read4u(fl)
		sub.pos = readXYZ(fl)
		sub.field_50 = readFLT4(fl)
		
		rfc.Lst2.append(sub)
		#print(sub.Name)
		
	
	num = read4u(fl)
	if flg1:
		for i in range(num):
			bon = Bone()
			bon.Name = readCstr(fl)
			bon.field_4C = read4u(fl)
			bon.mtx = readMt33(fl)
			bon.pos = readXYZ(fl)
		
			rfc.Bones.append(bon)
	
	rfc.ObjNum = read4u(fl)
	
	### Pre allocate
	for i in range(rfc.ObjNum):
		rfc.ObjList.append(Object())
	
	LodNum = read4u(fl)
	rfc.rfc4num = LodNum * rfc.ObjNum
	
	### Pre allocate
	for i in range(rfc.rfc4num):
		rfc.LodHeap.append(LodObj())
	
	jj = 0
	
	for i in range(rfc.ObjNum):
		obj = rfc.ObjList[i]
		obj.numFlt = read4u(fl) # Seems always == LodNum

		for j in range(obj.numFlt):
			obj.LodList.append( rfc.LodHeap[jj] )
			obj.flts.append(readflt(fl))
			jj += 1

	for i in range(rfc.ObjNum):
		obj = rfc.ObjList[i]
		for j in range(LodNum):
			lodObj = obj.LodList[j]
			lodObj.name1 = readCstr(fl)
			lodObj.name2 = readCstr(fl)
			lodObj.dword1 = read4u(fl)
			lodObj.dword2 = read4u(fl)
	
	
	for i in range(rfc.rfc4num): ## Load LODs
		sub = rfc.LodHeap[i]
		
		num = read4u(fl)
		for j in range(num):
			sub.skin.Textures.append( readCstr(fl) )
		
		sub.dword2 = read4u(fl)
		for j in range(sub.dword2):
			t42 = RFC_s42()
			sub.t42lst.append(t42)
			
			read4u(fl) #SKIP
			read4u(fl) #SKIP
			t42.Bt1 = read1u(fl)
			read1u(fl) #SKIP
			read1u(fl) #SKIP
			read1u(fl) #SKIP
			read1u(fl) #SKIP
			read4u(fl) #SKIP
			
			for k in range(2):
				if ( read1u(fl) ):
					read4u(fl) #SKIP
					readNstr(fl) #SKIP
					read4u(fl) #SKIP
					readflt(fl) #SKIP
					read4u(fl) #SKIP
					
			read4u(fl) #SKIP
			for k in range( read4u(fl) ):
				readflt(fl) #SKIP
				
			readflt(fl) #SKIP
			readflt(fl) #SKIP
			readflt(fl) #SKIP
			
			t42.nstr = readNstr(fl)
			
			read4u(fl) #SKIP
			
			for k in range( read4u(fl) ):
				readflt(fl) #SKIP
			
			readflt(fl) #SKIP
			
			for k in range( read4u(fl) ):
				readflt(fl) #SKIP
		
		sub.numGeom = read4u(fl)
		for j in range(sub.numGeom):
			g = Geom()
			sub.skin.GeomList.append(g)
			
			if (len(rfc.Bones) == 0): #In some RFM only?
				g.numSimpleVertex = read4u(fl)
				for k in range(g.numSimpleVertex):
					sv = SimpleVertex()
					sv.pos = readXYZ(fl)
					sv.normal = readXYZ(fl)
					g.SimpleVertexes.append( sv )
			
			g.TrianglesCount = read4u(fl)
			for k in range(g.TrianglesCount):
				FCvtxEs = ( FaceVtx(read4u(fl), readflt(fl), readflt(fl)),
							FaceVtx(read4u(fl), readflt(fl), readflt(fl)),
							FaceVtx(read4u(fl), readflt(fl), readflt(fl)) )
				g.Triangles.append( FCvtxEs )
			
			g.TexID = read4u(fl) #TexID
			g.unk = read4u(fl) 
			g.fl1 = readflt(fl)
			if (len(rfc.Bones) != 0):
				g.bts = (read1u(fl), read1u(fl), read1u(fl), read1u(fl))
		
		sub.skin.Pos = readXYZ(fl)
		sub.skin.fl1 = readflt(fl)
		sub.skin.Bounds = ( readXYZ(fl), readXYZ(fl) )
		
		if (len(rfc.Bones) != 0):
			sub.skin.vtxCount = read4u(fl)
			sub.skin.field_40 = read4S(fl) #Signed!

			for k in range(sub.skin.vtxCount):
				vtx = Vertex()
				sub.skin.vtxList.append(vtx)
				
				vtx.pos = readXYZ(fl) ## Vertex
				vtx.normal = readXYZ(fl) ## Normal
				#print("v {:f} {:f} {:f}".format(vtx.pos.x, vtx.pos.y, vtx.pos.z))
				
				if (sub.skin.field_40 > 0):
					vtx.sh1 = read2u(fl)
					
				for l in range(4):
					wght = VtxWeights()
					vtx.Weights.append(wght)
					
					wght.boneID = read4u(fl) #Really it's 1 Signed BYTE, so 255 == -1
					wght.w = readflt(fl)
					
					if (wght.boneID & 0x80): # Fix it 
						wght.boneID = -128 + (wght.boneID & 0x7F) # (255 -> -1)
	return rfc

######################## START ##############################


def main():
	if(len(sys.argv) < 2):
		print("Usage: python rfc_read.py path/file.(rfc|rfm) [out.obj]")
		exit(0)

	model = LoadRfc(sys.argv[1])
	objname = "out.obj"
	
	if (len(sys.argv) > 2):
		objname = sys.argv[2]
	
	print("Writing into {:s}".format(objname))
	
	mtlName = objname + ".mtl"
	
	peg = None
	
	mtlDict = dict()
	
	if (model.Peg):
		if not os.path.exists("rfc_tex"): 
			os.mkdir("rfc_tex")
		MTL = open(mtlName,"w")
		i = 0
		for ff in model.Peg.Texturies:
			ff.img.save("rfc_tex/{:s}.png".format(ff.Name))
			MTL.write("newmtl Tex{:d}\n\tmap_Kd rfc_tex/{:s}.png\n".format(i, ff.Name))
			mtlDict[ ff.Name.lower() ] = "Tex{:d}".format(i)
			i += 1
		MTL.close()
			
				

	vtxn = 1
	txN = 1
	oooo = 0
	
	OBJ = open(objname, "w")
	
	if (model.Peg):
		OBJ.write("mtllib {:s}\n".format(mtlName))

	if len(model.Bones) > 0:
		for obj in model.ObjList:
			lod = obj.LodList[0]
			for vtx in lod.skin.vtxList:
				OBJ.write("v {:f} {:f} {:f}\n".format(vtx.pos.x, vtx.pos.y, vtx.pos.z))
				if (model.Peg):
					OBJ.write("vn {:f} {:f} {:f}\n".format(vtx.normal.x, vtx.normal.y, vtx.normal.z))
			for geom in lod.skin.GeomList:
				if (model.Peg):
					OBJ.write("usemtl {:s}\n".format( mtlDict[ lod.skin.Textures[ geom.TexID ].lower() ] )  )
				for tr in geom.Triangles:
					if (model.Peg):
						OBJ.write("vt {:f} {:f}\n".format(tr[0].u, 1.0 - tr[0].v))
						OBJ.write("vt {:f} {:f}\n".format(tr[1].u, 1.0 - tr[1].v))
						OBJ.write("vt {:f} {:f}\n".format(tr[2].u, 1.0 - tr[2].v))
						OBJ.write("f {0:d}/{1:d}/{0:d} {2:d}/{3:d}/{2:d} {4:d}/{5:d}/{4:d}\n".format(tr[0].VtxID + vtxn, txN, 
														tr[1].VtxID + vtxn, txN + 1,
														tr[2].VtxID + vtxn, txN + 2 ))
						txN += 3
					else:
						OBJ.write("f {:d} {:d} {:d}\n".format(tr[0].VtxID + vtxn, tr[1].VtxID + vtxn, tr[2].VtxID + vtxn ))
						
					
			vtxn += len(lod.skin.vtxList)
	else:
		for obj in model.ObjList:
			OBJ.write("o Obj{:d}\n".format(oooo))
			oooo += 1
			lod = obj.LodList[0]
			for geom in lod.skin.GeomList:
				if (model.Peg):
					OBJ.write("usemtl {:s}\n".format( mtlDict[ lod.skin.Textures[ geom.TexID ].lower() ] )  )
				for vtx in geom.SimpleVertexes:
					vtt = vtx.pos + lod.skin.Pos
					OBJ.write("v {:f} {:f} {:f}\n".format(vtt.x, vtt.y, vtt.z))
					if (model.Peg):
						OBJ.write("vn {:f} {:f} {:f}\n".format(vtx.normal.x, vtx.normal.y, vtx.normal.z))
				for tr in geom.Triangles:
					if (model.Peg):
						OBJ.write("vt {:f} {:f}\n".format(tr[0].u, 1.0 - tr[0].v))
						OBJ.write("vt {:f} {:f}\n".format(tr[1].u, 1.0 - tr[1].v))
						OBJ.write("vt {:f} {:f}\n".format(tr[2].u, 1.0 - tr[2].v))
						OBJ.write("f {0:d}/{1:d}/{0:d} {2:d}/{3:d}/{2:d} {4:d}/{5:d}/{4:d}\n".format(tr[0].VtxID + vtxn, txN, 
														tr[1].VtxID + vtxn, txN + 1,
														tr[2].VtxID + vtxn, txN + 2))
						txN += 3
					else:
						OBJ.write("f {:d} {:d} {:d}\n".format(tr[0].VtxID + vtxn, tr[1].VtxID + vtxn, tr[2].VtxID + vtxn ))
				vtxn += geom.numSimpleVertex
	OBJ.close()

if __name__ == '__main__':
	main()

