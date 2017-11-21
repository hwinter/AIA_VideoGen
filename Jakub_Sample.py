import aia_mkmovie as mm 

import matplotlib
matplotlib.use('agg')

import os
import glob
import subprocess
import random

from multiprocessing import Pool

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
		os.remove(f)
	print("sorted: " + str(newdirs))
	return(newdirs)

def Jakub_Frames(DIR):

	i = 1
	spectrum = random.randint(0, 128)
	# print(DIR)
	print(path)
	for f in glob.glob(DIR + "/*.fits"):
		# print(f)
		im = mm.aia_mkimage(f, w0 = 4096, h0 = 4096, time_stamp = False)
		mm.aia_mkimage.format_img(im)
	for f in glob.glob("working/*.png"):
		subprocess.call("mv " + f + " working/" + str(i) + ".png", shell = True)
		i = i + 1

	subprocess.call('ffmpeg -r 24 -i working/%01d.png -vcodec libx264 -b:v 4M -pix_fmt yuv420p -y ' + str(spectrum) + '_TEST_OUT.mp4', shell=True)

AIA_Sort(directory)

for path in glob.glob(directory + "*"):
	if os.path.isdir(path):
		# print(path)
		# pool = Pool()
		# # print(path)
		# pool.map(Jakub_Frames, path)
		# pool.close()
		# pool.join()
		Jakub_Frames(path)
		for f in glob.glob("working/*.png"):
			os.remove(f)

