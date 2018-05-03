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

timestart = datetime.datetime.now()

fontpath = "ReplicaFrostStencil-Regular.otf"

font = ImageFont.truetype(fontpath, 19)

database = []
target_wavelengths = ["0094", "0171", "0193", "0211", "0304", "0335"]

segment_length = 0

global_date = datetime.datetime.now()
global_date = str(global_date)
year = global_date.split("-")[0]
month = global_date.split("-")[1]
day = str(int(global_date.split("-")[2].split(" ")[0]) - 1).zfill(2)


if len(sys.argv) == 3:
	directory = sys.argv[1]
	skipframes = int(sys.argv[2])
else:
	print("This script takes exactly two arguments. Proceeding with default values. ")
	directory = "/data/SDO/AIA/synoptic/" + str(year) + "/" + str(month) +"/" + str(day) + "/"
	skipframes = 2

print("Dataset: " + str(directory))

#build and return a database of fits files in a given directory.
def Fits_Index(DIR):
	fits_list = []
	count = 0
	for fits_file in sorted(glob.glob(DIR + "/*.fits")):
		print("\r Adding file: " + str(fits_file) + " Entries: " + str(count), end = " ")
		fits_list.append(str(fits_file))
		count = count + 1
	print(fits_list) 
	return(fits_list)

#Exactly the same as Fits_Index, but modified to work with the file structure of /data/SDO
def Parse_Directory(WLEN):

	fits_list = []

	for folder in sorted(glob.glob(str(directory) + "H*")):
		print("FOLDER: " + str(folder))
		for file in sorted(glob.glob(str(folder) + "/*" + str(WLEN).zfill(4) + ".fits")):
				print("ADDING: " + str(file))
				fits_list.append(str(file))

	return(fits_list)

#This lets us pick and choose which frames to render from our index. Feed it in a list, and this will spit out a list of every <SKIP> index.
def AIA_DecimateIndex(LIST, SKIP):
	list_in = LIST
	print("DECIMATING")
	list_out = [list_in[i] for i in xrange(0, len(list_in), SKIP)]

	return(list_out)

#Sort AIA fits files in to new directories by spectrum. 
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

#Create a list of all videos in the directory, sorted alphanumerically
def Video_List():
	videolist = []
	for f in sorted(glob.glob("*.mp4")):
		videolist.append(str(f))

	return videolist

#This is a hack to sort the output of Video_List() by temperature, rather than spectrum
def AIA_ArrangeByTemp(LIST):
	list_in = LIST
	list_order = [0, 5, 3 , 2, 1, 4]

	list_out = [list_in[i] for i in list_order]

	return(list_out)

#smooth out frame numbering in the event that individual frames failed to render properly
def AIA_PruneDroppedFrames(DIR):  
	frame_number = 0
	for f in sorted(glob.glob(str(DIR) + "Frame_Out*.png")):
		subprocess.call("mv " + f + " working/" + "Frame_Out" + str(frame_number).zfill(4) + ".png", shell = True)
		print("SORTING: " + str(f))
		frame_number = frame_number + 1

#purge the working directory of .png files
def Purge_Media():
	for f in glob.glob("working/*.png"):
	    os.remove(f)

	for f in glob.glob("working/Frame_Out*.png"):
	    os.remove(f)

#Build output file names based on .fits header data
def Build_Outname(FILE):
	entry = FILE 

	if os.stat(entry).st_size != 0: #Check to see if our fits file is empty (this apparently happens sometimes)
		hdulist = fits.open(entry)
		priheader = hdulist[1].header
		date_obs = priheader['DATE-OBS']
		wavelength = str(priheader['WAVELNTH']).zfill(4)
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

	b,g,r,a = 223,199,0,0
	framenum = database.index(FILE)
	framenum = str(framenum).zfill(4)

	print("FRAMENUM: " + str(framenum))
	entry = FILE 


	# img = aia.aiaprep(img)       #leaving this here because it might be useful, but right now we're working with pre-prepped images.
	print("working on " + str(entry))

	if os.stat(entry).st_size != 0: #Check to see if our fits file is empty (this apparently happens sometimes)
		hdulist = fits.open(entry)
		priheader = hdulist[0].header #Changed to 0 for newer synoptic files. 1 for older level1 fits files.
		date_obs = priheader['DATE-OBS']
		wavelength = priheader['WAVELNTH']

	else:
		date_obs = 0 
		print("File is empty.")
		
		
	if date_obs != 0:

		date = date_obs.split("T")[0]
		global_date = date
		time = date_obs.split("T")[1]
		img = mm.aia_mkimage(entry, w0 = 1024, h0 = 1024, time_stamp = False, synoptic = True)
		outfi = mm.aia_mkimage.format_img(img)

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
			draw.text((870, 97), str(date), font = font, fill = (b, g, r, a))
			draw.text((870, 119), str(time), font = font, fill = (b, g, r, a))
			draw.text((102, 930), "Earth Added for Size Scale", font = ImageFont.truetype(fontpath, 15), fill = (b, g, r, a))
			# 	# #Turn it back in to a numpy array for OpenCV to deal with
			frameStamp = np.array(img_pil)

			print("printing frame: " + str(framenum))
			cv2.imwrite("working/Frame_Out" + str(framenum) + ".png", cv2.cvtColor(frameStamp, cv2.COLOR_RGB2BGR)) #It's critical to convert from BGR to RGB here, because OpenCV sees things differently from everyone else
		else:
			print("Could not locate working/" + str(framenum) + ".png. Dropping frame")
	else:
		print("Entry header contains no date. Skipping...")
	
def Add_Earth(FILE):
	print("ADDING EARTH TO: " + str(FILE))
	main_video = [VideoFileClip(FILE)]
	mainvideo_length = main_video[0].duration
	print("MAIN LENGTH: ", str(mainvideo_length))

	mlength = mainvideo_length

	earth_g = VideoFileClip("misc/Earth_Whitebox_TBG.gif", has_mask = True, fps_source = "fps") #It's important to specify the FPS source here because otherwise Moviepy for some reason assumes it's not 24 fps, which skews our speed calculations later on.

	earthvideo_length = 60 #I'm having a problem with Moviepy (go figure) skipping to what seems to be an arbitrary frame at the very end of the video, rather than looping seemlessly. It also does not accurately measure the duration of the gif.
	print("EARTH LENGTH: ", str(earthvideo_length))

	speedmult = (earthvideo_length / mainvideo_length) #our Earth gif completes a full rotation in 60 seconds (to be completely accurate, it's 59.97. framerates). Here we're figuring out how much slower or faster the video needs to be to align our Earth rotation speed with the speed of our timelapse.
	print("SPEEDMULT: ", str(speedmult))

	# earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_pos((0.7, 0.7), relative = True).resize(lambda t : 1-0.01*t)
	# earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_position(lambda t: (0.85-t*0.1, 0.85-t*0.1), relative = True).resize(0.071)
	earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_pos((0.1, 0.88), relative = True).resize(0.0293) # to account for the downsized resolution of our template video. Current Earth size = 320 pixels


	#The above statement is the meat and potatos of this script.
	#SPEED: We use fl_time to match the rotational speed of earth to our timelapse. where t = realtime speed of the video, we multiply t by the ratio of our Earth gif's length (1 min) to our main video length, assuming that our main video is a 24 hour timelapse of varying speed.
	#SET POSITION: We use set_position() to position the Earth, using relative percentages of overall screen size. EG: 0.85, 0.85 means 85% of the way across the screen along the x and y axes.
	#RESIZE: resize() resizes our Earth gif by a percentage, in this case derived by Earth's diameter in pixels (407 in our Whiteboxed example) divided by the sun's (3178 at native AIA resolution). 
	#set_position() and resize() both accept lambda t: values, so our Earth gif can be resized and moved dynamically.

	main_video.extend( [earth_g] )
	out_video = CompositeVideoClip(main_video)

	out_video.set_duration(mlength).write_videofile("o_" + str(FILE), fps = 24, threads = 4, audio = False, progress_bar = False)
	os.rename("o_" + str(FILE),FILE)

	
def AIA_GenerateBackground(TEMPLATE, FEATURE, DURATION, VIDEONAME): #The template for video arrangement, EG: TEMPLATE_2x2.png

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

	cc.set_duration(DURATION).write_videofile(VIDEONAME, fps = 24, threads = 4, audio = False, progress_bar = False)

def AIA_AddInfographic(BASE, OVERLAY, OUTNAME): #BASE: Output of AIA_GenerateBackground(), Overlay: the graphical overlay image EG: NASM_Wall_Base2x2.mp4, OVERLAY_2x2.png
	
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

	        cv2.imwrite("NASM_out" + str(i) + ".png", outImage)
	        i = i + 1
	
	        print("\rOverlaying frame: " + str(i), end = "")
	        stdout.flush() 

	        if cv2.waitKey(1) & 0xFF == ord('q'):
	            break
	    else:
	        break

	subprocess.call('ffmpeg -r 24 -i NASM_out%01d.png -vcodec libx264 -b:v 4M -pix_fmt yuv420p -y ' + str(OUTNAME), shell=True)

	for f in glob.glob("NASM_out*.png"):
	    os.remove(f)

	# Release everything if job is finished
	cap.release()


for target in target_wavelengths:
		
		print("Building video of WAVELENGTH: " + str(target))

		database = Parse_Directory(target)
		database = AIA_DecimateIndex(database, skipframes)

		segment_length = (len(database) / 24) #the number of frames in the database divided by 24 frames per second (our video framerate) to give us the length in seconds for each segment 

		OUTNAME = (str(target) + ".mp4")

		pool = Pool()

		# Using multiprocess.pool() to parallelize our frame rendering
		pool.map(AIA_MakeFrames, database)
		pool.close()
		pool.join()

		AIA_PruneDroppedFrames("working/") #Sometimes frames get dropped. Since their names are based on the database index, this can cause ffmpeg to trip over itself when it expects rigidly sequenced numbering.

		print("OUTNAME: " + OUTNAME)
		subprocess.call('ffmpeg -r 24 -i working/Frame_Out%04d.png -vcodec libx264 -filter "minterpolate=mi_mode=blend" -b:v 4M -pix_fmt yuv420p  -y ' + str(OUTNAME), shell=True)
		Add_Earth(OUTNAME) #Overwrites the video we just made with one that has the earth added to scale
		Purge_Media() #erases all the individually generated frames after our movie is produced


# Generate a base video composite -> add graphical overlay -> Repeat. Each overlay is numerically matched to the base video, to synchronize temperature data.
for n in range (0, 6):
	vlist = Video_List()
	vlist = AIA_ArrangeByTemp(vlist)
	feature = vlist[n]
	templateIn = "misc/TEMPLATE_2x3.png"
	videoOut = "working/NASM_BaseSegment_" + str(n) + "_.mp4"
	
	print("Video In: " + feature + ", using template: " + templateIn)
	print("Segment Length: " + str(segment_length))
	
	AIA_GenerateBackground(templateIn, feature, segment_length, videoOut)

	baseVideoIn = "working/NASM_BaseSegment_" + str(n) + "_.mp4"
	segmentVideoOut = "working/NASM_SegmentOverlay_" + str(n) + "_.mp4"
	overlayIn = "misc/OVERLAY_2x3_FROST_" + str(n) + ".png"
	AIA_AddInfographic(baseVideoIn, overlayIn, segmentVideoOut)

	subprocess.call('killall ffmpeg', shell = True) #This is a temporary fix for the leaky way that Moviepy calls ffmpeg

# Take all the clips we've generated, and stitch them in to one long video.
clip1 = VideoFileClip("working/NASM_SegmentOverlay_0_.mp4")
clip2 = VideoFileClip("working/NASM_SegmentOverlay_1_.mp4")
clip3 = VideoFileClip("working/NASM_SegmentOverlay_2_.mp4")
clip4 = VideoFileClip("working/NASM_SegmentOverlay_3_.mp4")
clip5 = VideoFileClip("working/NASM_SegmentOverlay_4_.mp4")
clip6 = VideoFileClip("working/NASM_SegmentOverlay_5_.mp4")

final_outname = str(year) + "_" + str(month) + "_" + str(day) + "_FROST_VideoWall_Concatenated.mp4"

# final_clip = concatenate_videoclips([clip6,clip5,clip4,clip3,clip2,clip1])
final_clip = concatenate_videoclips([clip6, clip5.crossfadein(1), clip4.crossfadein(1), clip3.crossfadein(1), clip2.crossfadein(1), clip1.crossfadein(1)], padding = -1, method = "compose")
final_clip.write_videofile("daily_mov/" + str(final_outname), fps = 24, threads = 4, audio = False, progress_bar = False)

# os.rename(final_outname, "~/daily_mov/" + str(final_outname))
# os.remove(final_outname)
# Cleanup the directory when we're done
for f in glob.glob("NASM_BaseSegment_*.mp4"):
	    os.remove(f)

for f in glob.glob("NASM_SegmentOverlay_*.mp4"):
	    os.remove(f)

timeend = datetime.datetime.now()
finaltime = timeend - timestart
print("Final Runtime: " + str(finaltime))

