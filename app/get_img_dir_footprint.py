#
# Program to extract GPS EXIF from images in a directory and create a kml file
#
#

import os, sys
import itertools
import shapefile
import pandas as pd
import exifread
import exiftool

from simplekml import Kml, Style

#https://stackoverflow.com/questions/1260792/import-a-file-from-a-subdirectory#%E2%80%A6
sys.path.extend([f'./{name}' for name in os.listdir(".") if os.path.isdir(name)])

from flutils import *


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
 
 
def write_kml_multipnt(waypts):
    
    kml = Kml()
    
    # Style --> https://simplekml.readthedocs.io/en/latest/styling.html
    
    fol = kml.newfolder(name="A Folder")
    pnt_sharedstyle = Style()
    
    # Creating MultiGeometry
    multipnt = kml.newmultigeometry(name="Points")
    multipnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
    
    multilin = kml.newmultigeometry(name="Flight Paths")
    multilin.style.linestyle.width = 2   
    
    lolabels = kml.newfolder(name="Mark") 
    
    iterators  = itertools.cycle(waypts)
    next_waypt = next(iterators)
    linecoords = []
    no_recs = len(waypts)
    i = 0
    for prev_waypt in waypts:
            
        next_waypt = next(iterators)
        
        # Do not the draw last point back to first point 
        i = i + 1
        if i == no_recs:
            break
        
        pnt1 = kml.newpoint(description="Start " + str(prev_waypt[0]),
            coords=[(prev_waypt[1], prev_waypt[2], prev_waypt[3])])                # lon, lat, optional height
        pnt1.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
        pnt1.style.balloonstyle.text = 'Strip {0}\n Lon   {1}\n Lat   {2}\n Alt   {3}\n'.format(prev_waypt[0],prev_waypt[1],prev_waypt[2], prev_waypt[3])
        
        lo = lolabels.newpoint(name=str(prev_waypt[0]), coords=[(prev_waypt[1],prev_waypt[2])])
        lo.iconstyle.icon.href = ""
        
        
        if i % 2 == 1: 
            linecoords = [(prev_waypt[1], prev_waypt[2], prev_waypt[3]), (next_waypt[1], next_waypt[2], next_waypt[3])]
            multilin.newlinestring(coords=linecoords)
        
    multipnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
#    multilin.style.linestyle.color = simplekml.Color.blue
#    multilin.style.linestyle.width = 3  
    # save KML to a file
    kml.save("FlyoverWaypoints_inner_pit.kml")



def get_image_gps_coords(flist):
	
	glist = []
	fields = []
	for fpath in flist:
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



def load_filenames(file_path):
	
	filelist = glob.glob(file_path)
	return filelist



def get_img_files(file_dir):    
	
	files = []
	filelist = load_filenames(file_dir + "*.JPG")
	
 #Remove directory from filename
 
	for filename in filelist:  #TODO Error checking for bad file
		filename = os.path.basename(filename) 
		
		files.append(filename)

	return files


def main():
    
	img_dir = "/home/admin/dockers/ODM/mine1/InnerPit images - GPSLogger Exif/"
	data_dir = "data/"
	logs_dir = "/home/admin/dockers/ODM/gps_app/data/logs/"
	prefix   = "make_gps_coords_"
	setupLogging(logs_dir, prefix)
	img_list = load_filenames(img_dir + "*.JPG")
	waypoints = get_image_gps_coords(img_list)
	
	write_kml_pnt(waypoints,data_dir + "gps_coords.kml")
	write_log('Finished ')
    
    
if __name__ == "__main__":
    main()    