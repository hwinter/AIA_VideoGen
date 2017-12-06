import subprocess
import glob
import os
import datetime
import sys



def AIA_ArrangeFrames(DIR):  ##SORT FRAME_OUT, NOT THE WORKING DIRECTORY
	frame_number = 0
	for f in sorted(glob.glob(str(DIR) + "Frame_Out*.png")):
		subprocess.call("mv " + f + " working/" + "Frame_Out" + str(frame_number).zfill(4) + ".png", shell = True)
		print("SORTING: " + str(f))
		frame_number = frame_number + 1

AIA_ArrangeFrames("working/")