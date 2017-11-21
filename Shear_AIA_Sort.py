import os
import glob

newdirs = []
for f in glob.glob("*.fits"):
	wavelen = f.split("_")[2].split(".")[0]
	newdir = wavelen
	if os.path.isdir(newdir) == False:
		subprocess.call("mkdir " + newdir, shell = True)
		newdirs.append(newdir)
	subprocess.call("mv " + f + " " + directory + wavelen, shell = True)
	# os.remove(f)
print("sorted: " + str(newdirs))