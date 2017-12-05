from __future__ import print_function

import matplotlib
matplotlib.use('agg')
# from moviepy.editor import *
# from moviepy.video.tools.segmenting import findObjects
from PIL import ImageFont, ImageDraw, Image
from astropy.io import fits
from sys import stdout as stdout
from numba import jit
from multiprocessing import Pool

import aia_mkmovie as mm
import numpy as np
import sunpy.instr.aia as aia
import matplotlib.pyplot as plt

import cv2
import subprocess
import glob
import os
import datetime
import sys



def Fits_Index(DIR):
	fits_list = []
	count = 0
	for fits_file in sorted(glob.glob(DIR + "*.fits")):
		print("\r Adding file: " + str(fits_file) + " Entries: " + str(count), end = " ")
		fits_list.append(str(fits_file))
	print(fits_list) 
	return(fits_list)

def AIA_MakeFrames(FILE):
	print("FILE: " + str(FILE))
	date = 0
	time = 0
	wavelength = 0

	b,g,r,a = 191,191,191,0
	framenum = database.index(FILE)

	print("FRAMENUM: " + str(framenum))
	entry = FILE 


	# img = aia.aiaprep(img)
	print("working on " + str(entry))

	if os.stat(entry).st_size != 0: #Check to see if our fits file is empty (this apparently happens sometimes)
		hdulist = fits.open(entry)
		priheader = hdulist[1].header
		date_obs = priheader['DATE-OBS']
		wavelength = priheader['WAVELNTH']
		if wavelength == '94':
			wavelength = '094'
	else:
		date_obs = 0 
		print("File is empty.")
		
		
	if date_obs != 0:


		date = date_obs.split("T")[0]
		time = date_obs.split("T")[1]

		img = mm.aia_mkimage(entry, w0 = 4096, h0 = 4096, time_stamp = False)
		outfi = mm.aia_mkimage.format_img(img)
		# for f in glob.glob("working/" + wavelength + "*.png"):
		subprocess.call("mv " + outfi + " working/" + str(framenum) + ".png", shell = True)

		# 	#Convert our image from a numpy array to something PIL can deal with
		img_pil = Image.open("working/" + str(framenum) + ".png")
		# 	# Convert to RGB mode. Do I want to do this? I should maybe try RGBA
		if img_pil.mode != "RGB":
			img_pil = img_pil.convert("RGB")
		#	# Render it to a frame
		draw = ImageDraw.Draw(img_pil)
		# 	# #Put our text on it
		print("applying timestamp... " + str(date_obs))
		draw.text((3468, 710), str(date), font = font, fill = (b, g, r, a))
		draw.text((3468, 770), str(time), font = font, fill = (b, g, r, a))
		# 	# #Turn it back in to a numpy array for OpenCV to deal with
		frameStamp = np.array(img_pil)

		print("printing frame: " + str(framenum + 1))
		cv2.imwrite("Frame_Out" + str(framenum + 1) + ".png", cv2.cvtColor(frameStamp, cv2.COLOR_RGB2BGR))
		# framenum = framenum + 1
			
	else:
		print("Entry header contains no date. Skipping...")

database = Fits_Index("/Users/miles/Documents/Sunpy/test_fits_files/0171/0171/")
print("DATABASE")
print(database)

pool = Pool()

# print("MAPPING: " + str(f))
pool.map(AIA_MakeFrames, database)
pool.close()
pool.join()

subprocess.call('ffmpeg -r 24 -i Frame_Out%01d.png -vcodec libx264 -filter "minterpolate=mi_mode=blend" -b:v 4M -pix_fmt yuv420p  -y ' + str(OUTNAME), shell=True)
Clean_Frames()




	