import subprocess
import glob
import os
import datetime
import sys

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