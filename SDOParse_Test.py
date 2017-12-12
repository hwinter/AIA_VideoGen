import subprocess
import glob
import os
import datetime
import sys

from astropy.io import fits

wavelength = sys.argv[1]
directory = sys.argv[2]

#This let's us pick and choose which frames to render from our index. Feed it in a list, and this will spit out a list of every <SKIP> index.
def AIA_DecimateIndex(LIST, SKIP):
	list_in = LIST
	print("DECIMATING")
	list_out = [list_in[i] for i in xrange(0, len(list_in), SKIP)]

	return(list_out)

def Parse_Directory(WLEN):

	fits_list = []

	for folder in sorted(glob.glob(str(directory) + "H*")):
		print("FOLDER: " + str(folder))
			for file in sorted(glob.glob(str(folder) + "/*" + str(WLEN).zfill(4) + ".fits")):
					print("ADDING: " + str(file))
					fits_list.append(str(file))
	print("TOTAL SIZE: " + str(len(fits_list)))
	return(fits_list)

new_index = Parse_Directory(wavelength)
new_index = AIA_DecimateIndex(new_index, 12)

print(new_index[1])
print("IS IT A PATH? " + str((os.path.exists(new_index[1].strip()))))

hdulist = fits.open(str(new_index[1].strip()))

print("DATABASE LENGTH: " + str(len(new_index)))
print("TOTAL VIDEO TIME: " + str(len(new_index) / 24))
