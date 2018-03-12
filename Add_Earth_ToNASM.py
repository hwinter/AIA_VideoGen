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

#NOTE: iter_frames(fps=None, with_times=False, progress_bar=False, dtype=None) <- returns all the frames of the video as H W N numpy arrays


main_video = [VideoFileClip("0171.mp4")]
mainvideo_length = main_video[0].duration
print("MAIN LENGTH: ", str(mainvideo_length))

mlength = mainvideo_length

earth_g = VideoFileClip("misc/Earth_Whitebox_TBG.gif", has_mask = True, fps_source = "fps") #It's important to specify the FPS source here because otherwise Moviepy for some reason assumes it's not 24 fps, which skews our speed calculations later on.

earthvideo_length = earth_g.duration #I'm having a problem with Moviepy (go figure) skipping to what seems to be an arbitrary frame at the very end of the video, rather than looping seemlessly. It also does not accurately measure the duration of the gif.
print("EARTH LENGTH: ", str(earthvideo_length))

speedmult = (earthvideo_length / mainvideo_length) #our Earth gif completes a full rotation in 60 seconds (to be completely accurate, it's 59.97. framerates). Here we're figuring out how much slower or faster the video needs to be to align our Earth rotation speed with the speed of our timelapse.
print("SPEEDMULT: ", str(speedmult))

# earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_pos((0.7, 0.7), relative = True).resize(lambda t : 1-0.01*t)
# earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_position(lambda t: (0.85-t*0.1, 0.85-t*0.1), relative = True).resize(0.071)
earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_pos((0.8, 0.8), relative = True).resize(0.0671) # to account for the downsized resolution of our template video


#The above statement is the meat and potatos of this script.
#We use fl_time to match the rotational speed of earth to our timelapse. where t = realtime speed of the video, we multiply t by the ratio of our Earth gif's length (1 min) to our main video length, assuming that our main video is a 24 hour timelapse of varying speed.
#We use set_position() to position the Earth, using relative percentages of overall screen size. EG: 0.85, 0.85 means 85% of the way across the screen along the x and y axes.
#resize() resizes our Earth gif by a percentage, in this case derived by Earth's diameter in pixels (407 in our Whiteboxed example) divided by the sun's (3178 at native AIA resolution). 
#set_position() and resize() both accept lambda t: values, so our Earth gif can be resized and moved dynamically.

main_video.extend( [earth_g] )
out_video = CompositeVideoClip(main_video)

out_video.set_duration(mlength).write_videofile("Test.mp4", fps = 24, threads = 8)