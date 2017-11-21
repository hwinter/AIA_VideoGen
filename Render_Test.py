import numpy
import sunpy
import cv2
from PIL import ImageFont, ImageDraw, Image
from astropy.io import fits
from sunpy.database import Database



#Load an opentype font (requires PIL)
font = ImageFont.truetype("BebasNeue Regular.otf", 80)
b,g,r,a = 191,191,191,0 

#create and initialize our sunpy database
database = Database('sqlite:///sunpydata.sqlite')

#add an entire directory of fits files to our database, ignoring duplicates
database.add_from_dir("test_fits_files/set1", ignore_already_added=True)

#fits.getdata grabs a fits file and stores it as a numpy array, 
#which we can conveniently manipulate with OpenCV and PIL.
for i in range(0,16):      
	entry = database[i]
	img = fits.getdata(entry.path)     
	valbuff = 0

	for fits_header_entry in entry.fits_header_entries[:15]:
		#Index through the header of each fits file looking for the DATE tag
		keybuff = '{entry.key}'.format(entry=fits_header_entry)
		if keybuff == "DATE":
			#If we find it, we store it, to overlay on the frame
			valbuff = '{entry.value}'.format(entry=fits_header_entry)
	print valbuff


	fontpath = "BebasNeue Regular.otf"     
	font = ImageFont.truetype(fontpath, 56)


	#Convert our image from a numpy array to something PIL can deal with
	img_pil = Image.fromarray(img)
	# Convert to RGB mode. Do I want to do this? I should maybe try RGBA
	if img_pil.mode != "RGB":
		img_pil = img_pil.convert("RGB")
	#Render it to a frame
	draw = ImageDraw.Draw(img_pil)
	#Put our text on it
	draw.text((3468, 710), str(valbuff), font = font, fill = (b, g, r, a))
	#Turn it back in to a numpy array for OpenCV to deal with
	frameStamp = numpy.array(img_pil)

	cv2.imwrite("Test_Out" + str(i + 1) + ".png", frameStamp)
	
