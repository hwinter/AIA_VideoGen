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



main_vid = [VideoFileClip("2017-04-12_0171.mp4")]
mainvideo_length = main_vid[0].duration
print("MAIN LENGTH: ", str(mainvideo_length))

mlength = mainvideo_length

earth_g = VideoFileClip("misc/Earth_Whitebox_TBG.gif", has_mask = True, fps_source = "fps")

earthvideo_length = 58
print("EARTH LENGTH: ", str(earthvideo_length))

speedmult = (earthvideo_length / mainvideo_length)
print("SPEEDMULT: ", str(speedmult))

# earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_pos((0.7, 0.7), relative = True).resize(lambda t : 1-0.01*t)
earth_g = earth_g.set_duration(earthvideo_length).fl_time(lambda t: speedmult*t).set_pos((0.85, 0.85), relative = True).resize(0.071)

main_vid.extend( [earth_g] )
outvideo2 = CompositeVideoClip(main_vid)

outvideo2.set_duration(mlength).write_videofile("Test.mp4", fps=24)