Readers/OBJ converter of Red Factions 2 rfl/rfc files

System requirements:
	- Python3 
	- Python3 Pillow lib

Usage:
	
	Depack files:
	
	- Create dir for depack All_Levels.toc_group or Permanent_data.toc_group
	- In RF2 dir do python depack.py pc_media/All_Levels.toc_group out/dir
	
	RFL: python rfl_read.py levelsdir/lvl.rfl out/to/lvl.obj
	RFC: python rfc_read.py levelsdir/model.rfc out/to/model.obj
	
	Peg reader only for create materials and extract only first frame.
	Advanced peg reader can be found [here](https://github.com/gibbed/Gibbed.Volition/tree/master/projects/Gibbed.RedFaction2.ConvertPEG)


