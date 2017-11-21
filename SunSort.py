import os
import glob
import subprocess

directory = "test_fits_files/set1/"


def AIA_Sort(DIR):
	newdirs = []
	for f in glob.glob(DIR + "*.fits"):
		wavelen = f.split("_")[4].split(".")[0]
		newdir = wavelen
		if os.path.isdir(DIR + newdir) == False:
			subprocess.call("mkdir " + DIR + newdir, shell = True)
			newdirs.append(newdir)
		subprocess.call("cp " + f + " " + directory + wavelen, shell = True)
	print(newdirs)



AIA_Sort(directory)