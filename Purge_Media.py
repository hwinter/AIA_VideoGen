import subprocess
import glob
import os

for f in glob.glob("*.mp4"):
	    os.remove(f)
for f in glob.glob("*.png"):
	    os.remove(f)
for f in glob.glob("working/*.png"):
	    os.remove(f)