from __future__ import print_function

import matplotlib
matplotlib.use('agg')

from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects
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

fontpath = "BebasNeue Regular.otf"     
font = ImageFont.truetype(fontpath, 56)

FRAMESKIP = 6
database = []

if len(sys.argv) == 3:
	directory = sys.argv[1]
	skipframes = int(sys.argv[2])
else:
	print("This script takes exactly two arguments. Proceeding with default values. ")
	directory = "test_fits_files/set1/"
	skipframes = 6

print("Dataset: " + str(directory))

#Sorts AIA fits files in to new directories by spectrum
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

def AIA_ArrangeByTemp(LIST):
	list_in = LIST
	list_order = [0, 5, 3 , 2, 1, 4]

	list_out = [list_in[i] for i in list_order]

	return(list_out)

def AIA_DecimateIndex(LIST, SKIP):
	list_in = LIST
	print("DECIMATING")
	list_out = [list_in[i] for i in xrange(0, len(list_in), SKIP)]

	return(list_out)

def Video_List():
	videolist = []
	for f in sorted(glob.glob("*.mp4")):
		videolist.append(str(f))
		# print(videolist)
	return videolist

def Fits_Index(DIR):
	fits_list = []
	count = 0
	for fits_file in sorted(glob.glob(DIR + "/*.fits")):
		print("\r Adding file: " + str(fits_file) + " Entries: " + str(count), end = " ")
		fits_list.append(str(fits_file))
		count = count + 1
	print(fits_list) 
	return(fits_list)

def Clean_Frames():
	for f in glob.glob("working/*.png"):
	    os.remove(f)

	for f in glob.glob("Frame_Out*.png"):
	    os.remove(f)

def Build_Outname(FILE):
	entry = FILE 

	if os.stat(entry).st_size != 0: #Check to see if our fits file is empty (this apparently happens sometimes)
		hdulist = fits.open(entry)
		priheader = hdulist[1].header
		date_obs = priheader['DATE-OBS']
		wavelength = priheader['WAVELNTH']
		if wavelength == '94':
			wavelength = '094'
	
	date = date_obs.split("T")[0]
	OUTNAME = str(date) + "_" + str(wavelength) + ".mp4"

	return OUTNAME
	

#Turns a directory full of AIA files in to a video with annotations based on HEADER data
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
		if glob.glob("working/" + str(framenum) + ".png"):
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
		else:
			print("Could not locate working/" + str(framenum) + ".png. Dropping frame")
	else:
		print("Entry header contains no date. Skipping...")
	
def VideoBaseGen(TEMPLATE, FEATURE, DURATION, VIDEONAME): #The template for video arrangement, EG: TEMPLATE_2x2.png

	im = ImageClip(TEMPLATE) 
	regions = findObjects(im)
	vlist = Video_List()
	vlist = AIA_ArrangeByTemp(vlist) #Video_List() will sort by wavelength, but we want to sort by temperature
	print("vlist: " + str(vlist))
	clips = [VideoFileClip(n) for n in
		["misc/black.mp4",
		vlist[0],#The order they appear here is the order they appear on the Thermometer (?)
		vlist[1],
        vlist[2],
        vlist[3],
        vlist[4],
        vlist[5],
		FEATURE, #Second to last is our featured video
		"misc/black.mp4"]]

	comp_clips = [c.resize(r.size).set_mask(r.mask).set_pos(r.screenpos) for c,r in zip(clips,regions)] #We build our composite here.

	cc = CompositeVideoClip(comp_clips,im.size)

	cc.set_duration(DURATION).write_videofile(VIDEONAME, fps = 24)

def OverlayComposite(BASE, OVERLAY, OUTNAME): #BASE: Output of VideoBaseGen(), Overlay: the graphical overlay image EG: NASM_Wall_Base2x2.mp4, OVERLAY_2x2.png
	
	cap = cv2.VideoCapture(BASE)
	fg = cv2.imread(OVERLAY,-1)

	i = 0;

	while(cap.isOpened()):
	    ret, frame = cap.read()
	    if ret == True:

	        # Read the foreground image with alpha channel
	        foreGroundImage = fg

	        # Split png foreground image
	        b,g,r,a = cv2.split(foreGroundImage)

	        # Save the foregroung RGB content into a single object
	        foreground = cv2.merge((b,g,r))

	        # Save the alpha information into a single Mat
	        alpha = cv2.merge((a,a,a))

	        foreground = foreground.astype(float)

	        background = frame

	        # Convert uint8 to float
	        background = background.astype(float)
	        alpha = alpha.astype(float)/255

	        # Perform alpha blending
	        foreground = cv2.multiply(alpha, foreground)
	        background = cv2.multiply(1.0 - alpha, background)
	        outImage = cv2.add(foreground, background)

	        # write the processed frame
	        # out.write(outImage)
	        cv2.imwrite("NASM_out" + str(i) + ".png", outImage)
	        i = i + 1
	
	        print("\rOverlaying frame: " + str(i), end = "")
	        stdout.flush() 
	        # cv2.imshow('frame',outImage)
	        if cv2.waitKey(1) & 0xFF == ord('q'):
	            break
	    else:
	        break

	subprocess.call('ffmpeg -r 24 -i NASM_out%01d.png -vcodec libx264 -b:v 4M -pix_fmt yuv420p -y ' + str(OUTNAME), shell=True)

	for f in glob.glob("NASM_out*.png"):
	    os.remove(f)

	# Release everything if job is finished
	cap.release()


AIA_Sort(directory)

for f in glob.glob(str(directory) + "*"):
	if os.path.isdir(f):
		print("Opening directory: " + f)
		
		database = Fits_Index(f)
		print("DATABASE")
		print(database)

		OUTNAME = Build_Outname(database[0]) #build a filename for our video from header data from a file in our database

		pool = Pool()

		# print("MAPPING: " + str(f))
		pool.map(AIA_MakeFrames, database)
		pool.close()
		pool.join()

		print("OUTNAME: " + OUTNAME)
		subprocess.call('ffmpeg -r 24 -i Frame_Out%01d.png -vcodec libx264 -filter "minterpolate=mi_mode=blend" -b:v 4M -pix_fmt yuv420p  -y ' + str(OUTNAME), shell=True)
		Clean_Frames()


# Generate a base video composite -> add graphical overlay -> Repeat. Each overlay is numerically matched to the base video, so synchronize temperature data.
for n in range (0, 6):
	vlist = Video_List()
	vlist = AIA_ArrangeByTemp(vlist)
	feature = vlist[n]
	templateIn = "misc/TEMPLATE_2x3.png"
	videoOut = "NASM_BaseSegment_" + str(n) + "_.mp4"
	
	print("Video In: " + feature + ", using template: " + templateIn)
	
	VideoBaseGen(templateIn, feature, 2, videoOut)

	baseVideoIn = "NASM_BaseSegment_" + str(n) + "_.mp4"
	segmentVideoOut = "NASM_SegmentOverlay_" + str(n) + "_.mp4"
	# overlayIn = "misc/OVERLAY_2x3_WHITEc.png" 
	overlayIn = "misc/OVERLAY_2x3_WHITE_" + str(n) + ".png"
	OverlayComposite(baseVideoIn, overlayIn, segmentVideoOut)

	subprocess.call('killall ffmpeg', shell = True) #This is a temporary fix for the leaky way that Moviepy calls ffmpeg

# Take all the clips we've generated, and stitch them in to one long video.
clip1 = VideoFileClip("NASM_SegmentOverlay_0_.mp4")
clip2 = VideoFileClip("NASM_SegmentOverlay_1_.mp4")
clip3 = VideoFileClip("NASM_SegmentOverlay_2_.mp4")
clip4 = VideoFileClip("NASM_SegmentOverlay_3_.mp4")
clip5 = VideoFileClip("NASM_SegmentOverlay_4_.mp4")
clip6 = VideoFileClip("NASM_SegmentOverlay_5_.mp4")

# final_clip = concatenate_videoclips([clip6,clip5,clip4,clip3,clip2,clip1])
final_clip = concatenate_videoclips([clip6, clip5.crossfadein(1), clip4.crossfadein(1), clip3.crossfadein(1), clip2.crossfadein(1), clip1.crossfadein(1)], padding = -1, method = "compose")
final_clip.write_videofile("NASM_VideoWall_Concatenated.mp4")

# Cleanup the directory when we're done
for f in glob.glob("NASM_BaseSegment_*.mp4"):
	    os.remove(f)

for f in glob.glob("NASM_SegmentOverlay_*.mp4"):
	    os.remove(f)

