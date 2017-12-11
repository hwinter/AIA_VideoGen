import subprocess
import glob
import os
import datetime
import sys

from astropy.io import fits

wavelength = sys.argv[1]
directory = sys.argv[2]

def Parse_Directory(WLEN):

        fits_list = []

        for folder in sorted(glob.glob(str(directory) + "H*")):
		print("FOLDER: " + str(folder))
                for file in sorted(glob.glob(str(folder) + "/*" + str(WLEN).zfill(4) + ".fits")):
                        print("ADDING: " + str(file))
                        fits_list.append(str(file))

        return(fits_list)

new_index = Parse_Directory(wavelength)

print(new_index[1])
print("IS IT A PATH? " + (os.path.exists(new_index[1].strip())))

hdulist = fits.open(str(new_index[1].strip()))

