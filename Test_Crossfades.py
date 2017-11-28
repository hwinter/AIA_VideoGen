from __future__ import print_function

import matplotlib
matplotlib.use('agg')

from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects
from PIL import ImageFont, ImageDraw, Image
from astropy.io import fits
# from sunpy.database import Database
from sys import stdout as stdout

import aia_mkmovie as mm
import numpy as np
import sunpy.instr.aia as aia
import matplotlib.pyplot as plt

# import sunpy.map
import cv2
import subprocess
import glob
import os
import datetime
import sys


clip1 = VideoFileClip("1.mp4")
clip2 = VideoFileClip("2.mp4")
clip3 = VideoFileClip("3.mp4")
clip4 = VideoFileClip("4.mp4")


final_clip = concatenate_videoclips([clip4,clip3.crossfadein(1),clip2.crossfadein(1),clip1.crossfadein(1)], padding = -1, method = "compose")
final_clip.write_videofile("Test_Crossfades_Out.mp4")