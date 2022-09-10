#
# Program to check for blurry images. Moves images to a subdirectory and creates a kml of the blurry images gps coords
#
#

import os, sys
import cv2
import exiftool

from simplekml import Kml, Style

#https://stackoverflow.com/questions/1260792/import-a-file-from-a-subdirectory#%E2%80%A6
sys.path.extend([f'./{name}' for name in os.listdir(".") if os.path.isdir(name)])

from flutils import *

BLUR = 10		# Change this value to increase the sensitivity of the blur test
				# Change image directory in main()

def write_kml_pnt(waypts,kname):
    
	kml = Kml()
    
	# Style --> https://simplekml.readthedocs.io/en/latest/styling.html
    
	fol = kml.newfolder(name="A Folder")
	pnt_sharedstyle = Style()
	for waypnt in waypts:
		
		pnt = kml.newpoint(description=str(waypnt[0]), coords=[(waypnt[1], waypnt[2], waypnt[3])])                # lon, lat, optional height
		pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
		pnt.style.balloonstyle.text = 'File {0}\n Lon   {1}\n Lat   {2}\n Alt   {3}\n'.format(waypnt[0],waypnt[1],waypnt[2], waypnt[3])

	kml.save(kname)
 
 


def get_image_gps_coords(flist):
	
	glist = []
	fields = []
	for fpath in flist:
		if os.path.exists(fpath) == False:
			write_log('Blurry image ' + fpath + ' doesn\'t exist')
			continue
		print(fpath)
		fname = os.path.basename(fpath)
		img = open(fpath, 'rb')

		with exiftool.ExifToolHelper() as et:
			orig_lon     = et.get_tags(fpath,"GPSLongitude")
			orig_lon_ref = et.get_tags(fpath,"GPSLongitudeRef")
			orig_lat     = et.get_tags(fpath,"GPSLatitude")
			orig_lat_ref = et.get_tags(fpath,"GPSLatitudeRef")
			orig_alt     = et.get_tags(fpath,"GPSAltitude")
			orig_alt_ref = et.get_tags(fpath,"GPSAltitudeRef")
   
		for _lon in orig_lon:
			try:
				# print(_lon['EXIF:GPSLongitude'])
				_orig_lon = _lon['EXIF:GPSLongitude']
				_comp_lon = _lon['Composite:GPSLongitude']
				
			except:
				# print('Error: No EXIF:GPSLongitude')
				_orig_lon = None
					
		for _lon_ref in orig_lon_ref:
			try:
				# print(_lon_ref['EXIF:GPSLongitudeRef'])
				_orig_lon_ref = _lon_ref['EXIF:GPSLongitudeRef']
			except:
				# print('Error: No EXIF:GPSLongitudeRef')
				_orig_lon_ref = None
	
		for _lat in orig_lat:
			try:
				# print(_lat['EXIF:GPSLatitude'])
				_orig_lat = _lat['EXIF:GPSLatitude']
				_comp_lat = _lat['Composite:GPSLatitude']
			except:
				# print('Error: No EXIF:GPSLatitude')
				_orig_lat = None
	
		for _lat_ref in orig_lat_ref:
			try:
				# print(_lat_ref['EXIF:GPSLatitudeRef'])
				_orig_lat_ref = _lat_ref['EXIF:GPSLatitudeRef']
			except:
				# print('Error: No EXIF:GPSLatitudeRef')
				_orig_lat_ref = None
	
		for _alt in orig_alt:
			try:
				# print(_alt['EXIF:GPSAltitude'])
				_orig_alt = _alt['EXIF:GPSAltitude']
				_comp_alt = _alt['Composite:GPSAltitude']
			except:
				# print('Error: No EXIF:GPSAltitude')
				_orig_alt = None
					
		for _alt_ref in orig_alt_ref:
			try:
				# print(_alt_ref['EXIF:GPSAltitudeRef'])
				_orig_alt_ref = _alt_ref['EXIF:GPSAltitudeRef']			
			except:
				# print('Error: No EXIF:GPSAltitudeRef')
				_orig_alt_ref = None
	
		#return [_orig_lon, _orig_lon_ref, _orig_lat, _orig_lat_ref, _orig_alt, _orig_alt_ref]

		#fields = [orig_lon,orig_lon_ref,orig_lat,orig_lat_ref,orig_alt,orig_alt_ref]
		fields = [fname, _comp_lon, _comp_lat, _comp_alt]
		img.close()
		glist.append(fields) 
	
	return glist


def get_blurry(fpath,bpath):
	blurry_list = []
	
	for fname in fpath:
		
		img = cv2.imread(fname,0)
		
		laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
		if laplacian_var < BLUR:
			bfname = os.path.basename(fname)
			bfpath = bpath + bfname
			blurry_list.append(bfpath)
			moveFile(fname, bpath, action='move')

		print(fname + " laplacian_val: {0}".format(laplacian_var) )
	return blurry_list


def load_filenames(file_path):
	
	filelist = glob.glob(file_path)
	return filelist


def make_blurry_dir(bdir):
	write_log('Checking for blurry subdirectory ' + bdir)
	if not check_dir_writable(bdir):
		try:
			os.mkdir(bdir)
			write_log('Made directory ' + bdir )
		except:
			write_log('Could not write directory ' + bdir)
			quit()
	else:
		write_log(bdir + ' already exists')
	return

def main():
    
	img_dir = "/home/admin/dockers/ODM/mine1/AOI_images/"
	blurry_dir = img_dir + '/blurry/'
	data_dir = "data/"
	logs_dir = "/home/admin/dockers/ODM/gps_app/data/logs/"
	prefix   = "del_blurry_"
	setupLogging(logs_dir, prefix)
	make_blurry_dir(blurry_dir)
	

	img_list = load_filenames(img_dir + "*.JPG")
	blurry_list = get_blurry(img_list,blurry_dir)		# Check for blurry images
	waypoints = get_image_gps_coords(blurry_list)		# Move blurry images to "blurry" sub-directory
	write_kml_pnt(waypoints,data_dir + "blurry_img.kml")
	write_log('Finished ')
    
    
if __name__ == "__main__":
    main()    