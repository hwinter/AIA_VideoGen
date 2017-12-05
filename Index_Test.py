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

directory = "test_fits_files/set1/"

def Fits_Index(DIR):
	fits_list = []
	count = 0
	for fits_file in sorted(glob.glob(DIR + "/*.fits")):
		print("\r Adding file: " + str(fits_file) + " Entries: " + str(count), end = " ")
		fits_list.append(str(fits_file))
		count = count + 1
	print(fits_list) 
	return(fits_list)

def AIA_DecimateIndex(LIST, SKIP):
	list_in = LIST

	list_out = [list_in[i] for i in xrange(0, len(list_in), SKIP)]

	return(list_out)

i1 = Fits_Index(directory)


for f in glob.glob(str(directory) + "*"):
	if os.path.isdir(f):
		print("Opening directory: " + str(f))
		database = Fits_Index(f)
	

