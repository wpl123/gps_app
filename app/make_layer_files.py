#
# Program to extract GPS Logger waypoints metadata and apply to images extracted from MP4 
# in cronological order 1 second apart 
#
# Instructions:
#
# Prior to arriving over the mapping site:
#
# 1. Start GPS Logger on the Phone first and put on the dash of the plane (where gets best GPS signal)
# 2. Start the Camera App 
# 3. Start the camera recording on 1 second delay
# 3. 
#
#import cv2
from distutils.file_util import move_file
import os, sys, glob
import subprocess
import math
import geopandas as gpd
import gpxpy
import gpxpy.gpx
import numpy as np
import pandas as pd
import exifread
import json
#import piexif
#import pyexiv2


import exiftool

from datetime import datetime
from dateutil import tz
from datetime import timedelta
from pprint import pprint # for printing Python dictionaries in a human-readable way
from exif import Image, DATETIME_STR_FORMAT
from pygeodesy.sphericalNvector import LatLon

#https://stackoverflow.com/questions/1260792/import-a-file-from-a-subdirectory#%E2%80%A6
sys.path.extend([f'./{name}' for name in os.listdir(".") if os.path.isdir(name)])

from flutils import *

# 0. Create python environment
#   a. pip install virtualenv
#   b. virtualenv venv
#   c. source venv/bin/activate
#   d. venv/bin/python -m pip install --upgrade pip
#   f. pip install gpxpy    --> https://ourpython.com/python/how-to-extract-gpx-data-with-python
#                           -->  https://pypi.python.org/pypi/gpxpy
#	g. Install exiftool-perl --> https://exiftool.org/install.html
#
#
# 1. Open GPS Log file and create df with waypoints 1 second apart
# 2. Open video capture file and extract images that coincide with timestamp from the waypoints
# 3. Update the metadata of the image files with time and gps coords
# 4. save the extracted images to a subdirectory

#
#workingdir = "/home/admin/dockers/ODM/Bridge-Test3"
img_dir = "/home/admin/dockers/ODM/mine1/"
processed_img_dir = "/home/admin/dockers/ODM/mine1/images/"
GPS_LOGGER_TRACK_FILE = '20220729-121016 - Mine1.gpx'
#logs_dir = ".src/test9/logs/"

# i.e if video of duration 30 seconds, saves 10 frame per second = 300 frames saved in total
SAVING_FRAMES_PER_SECOND = 1
LOCAL_ZONE = 'Australia/Brisbane'



def deg_to_dms(deg, pretty_print=None, ndp=4):
# https://scipython.com/book/chapter-2-the-core-python-language-i/additional-problems/converting-decimal-degrees-to-deg-min-sec/

	m, s = divmod(abs(deg)*3600, 60)
	d, m = divmod(m, 60)
	if deg < 0:
		d = -d
	#d, m = float(d), float(m)
	s = math.floor(s * (10 ** ndp)) / (10 ** ndp)
	if pretty_print:
		if pretty_print=='latitude':
			hemi = 'N' if d>=0 else 'S'
		elif pretty_print=='longitude':
			hemi = 'E' if d>=0 else 'W'
		else:
			hemi = '?'

	return abs(d), m, s, hemi


 

def change_timezone(from_time, local_zone):
	
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz(local_zone)
	utc = datetime.datetime.strptime(from_time, '%Y-%m-%d %H:%M:%S')
	utc = utc.replace(tzinfo=from_zone)
	to_time = utc.astimezone(to_zone)

	return(to_time)


def get_polygon_coords1():
	data = gpd.read_file(open("data/aoi.geojson"))
	print(data['geometry'])
	return data


def get_polygon_coords():
    data = json.load(open("data/aoi.geojson"))
    
    point = []
    points = []
    
    for i in data['features']:
        cord = i['geometry']['coordinates']
        for j in cord:
            for k in j:
                for point in k:
                    point = [LatLon(point[0],point[1])]
                    print(point)  #TODO: return a tuple not list https://stackoverflow.com/questions/48837384/how-to-create-tuple-with-a-loop-in-python
                points.append(point)	
    return points            


def check_coords(lon, lat):
    
    #Big Polygon over the entire mine
    # open the geojson file and extract polygon coords as a list

	#-30.53768,150.11591
	#-30.53382,150.14552
	#-30.56713,150.16114
	#-30.58170,150.14627
	#-30.58169,150.13367
	#-30.59498,150.12159
	#-30.58078,150.11080
	#-30.57447,150.11375
	#-30.57263,150.11503
	#-30.56990,150.11143
	#-30.55955,150.11265
	#-30.55257,150.12177
	polygon_coords = LatLon(-30.53768,150.11591), LatLon(-30.53382,150.14552), LatLon(-30.56713,150.16114), LatLon(-30.58170,150.14627), LatLon(-30.58169,150.13367), LatLon(-30.59498,150.12159), LatLon(-30.58078,150.11080), LatLon(-30.57447,150.11375), LatLon(-30.57263,150.11503), LatLon(-30.56990,150.11143), LatLon(-30.55955,150.11265), LatLon(-30.55257,150.12177)
	
	#Small Polygon over the pit water
	# -30.557432,150.143222
	# -30.565235,150.152065
	# -30.577436,150.139139
	# -30.567266,150.128804
	
	#polygon_coords = LatLon(-30.557432,150.143222), LatLon(-30.565235,150.152065), LatLon(-30.577436,150.139139), LatLon(-30.567266,150.128804)
    #TODO: replace hard coded coords with geojson file created by QGIS. Need to remove items from list
    #polygon_coords = get_polygon_coords()
	image_coord = LatLon(lat,lon)
	#print(image_coord)
	#print(polygon_coords)
	return image_coord.isenclosedBy(polygon_coords)      #(polygon_coords)


def get_orig_tags(fname):

	_orig_lon     = ''
	_orig_lon_ref = ''
	_orig_lat     = '' 
	_orig_lat_ref = '' 
	_orig_alt     = '' 	
	_orig_alt_ref = ''
 
	with exiftool.ExifToolHelper() as et:
		orig_lon     = et.get_tags(fname,"GPSLongitude")
		orig_lon_ref = et.get_tags(fname,"GPSLongitudeRef")
		orig_lat     = et.get_tags(fname,"GPSLatitude")
		orig_lat_ref = et.get_tags(fname,"GPSLatitudeRef")
		orig_alt     = et.get_tags(fname,"GPSAltitude")
		orig_alt_ref = et.get_tags(fname,"GPSAltitudeRef")
		
	for _lon in orig_lon:
		try:
			# print(_lon['EXIF:GPSLongitude'])
			_orig_lon = _lon['EXIF:GPSLongitude']
			
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
   
	return [_orig_lon, _orig_lon_ref, _orig_lat, _orig_lat_ref, _orig_alt, _orig_alt_ref]





def update_images(df_images, df_waypoints):
# https://exif.readthedocs.io/en/latest/usage.html#add-geolocation
	
	images_updated = 0
	images_rejected = 0
	move_fail = 0
	tags = []
	record_changed = []
	
 
	for i in range(len(df_images)):
		datetime_obj = get_datetime_from_image_exif_orig(df_images.iloc[i,0])
		
		for j in range(len(df_waypoints)):
			
			if df_waypoints.iloc[j,3] == datetime_obj:  #TODO: Resolve datetime equality issue
				fpath = (img_dir + str(df_images.iloc[i,0]))
				
				lat_deg, lat_min, lat_sec, lat_ref = deg_to_dms(df_waypoints.iloc[j,0], 'latitude')
				lon_deg, lon_min, lon_sec, lon_ref = deg_to_dms(df_waypoints.iloc[j,1], 'longitude')
				
				#with exiftool.ExifToolHelper() as et:
				#	metadata = et.get_metadata(fpath)
				#	for d in metadata:
				#		print("{:20.20} {:20.20}".format(d["SourceFile"],
				#                     d["EXIF:DateTimeOriginal"]))
				
				# https://www.youtube.com/watch?v=HXS1FN7ywYg&t=929s
    
	#			with exiftool.ExifToolHelper() as et:
	#				et.execute("-GPSLongitude=" + str(df_waypoints.iloc[j,1]), fpath)
	#				et.execute("-GPSLongitudeRef=" + lon_ref, fpath)
	#				et.execute("-GPSLatitude=" + str(df_waypoints.iloc[j,0]), fpath)
	#				et.execute("-GPSLatitudeRef=" + lat_ref, fpath)
	#				et.execute("-GPSAltitude=" + str(df_waypoints.iloc[j,2]), fpath)
	#				et.execute("-GPSAltitudeRef=0", fpath)

# TODO: check if the gps coords are inside the area of interest. Move images inside the polygon to webODM directory				
# https://stackoverflow.com/questions/43892459/check-if-geo-point-is-inside-or-outside-of-polygon
# Export the AOI as a polygon from QGIS. 				
		
				include_image = check_coords(df_waypoints.iloc[j,1],df_waypoints.iloc[j,0]) #lon, lat
				
				if include_image == True:
					#print("Including" + fpath)
					tpath = (processed_img_dir + str(df_images.iloc[i,0]))
					result = moveFile(fpath,processed_img_dir,'copy')
					#TODO: update image file on tpath with GPS data, create log of the difference in the GPS data
					if result == True:
						write_log("Reading GPS Data from file: {0}".format(tpath))
						tags = get_orig_tags(tpath)
        
						#write_log("_orig_lon: {0}, orig_lon_ref: {1}, orig_lat: {2}, orig_lat_ref: {3}, orig_alt: {4}, orig_alt_ref: {5}. tpath: {6}".format(_orig_lon,orig_lon_ref,orig_lat,orig_lat_ref,orig_alt,orig_alt_ref,tpath))	
						with exiftool.ExifToolHelper() as et:
							et.execute("-GPSLongitude=" + str(df_waypoints.iloc[j,1]), fpath)
							et.execute("-GPSLongitudeRef=" + lon_ref, fpath)
							et.execute("-GPSLatitude=" + str(df_waypoints.iloc[j,0]), fpath)
							et.execute("-GPSLatitudeRef=" + lat_ref, fpath)
							et.execute("-GPSAltitude=" + str(df_waypoints.iloc[j,2]), fpath)
							et.execute("-GPSAltitudeRef=0", fpath)
						
						fields = [tpath,tags[0],tags[1],tags[2],tags[3],tags[4],tags[5],str(df_waypoints.iloc[j,1]),lon_ref,str(df_waypoints.iloc[j,0]),lat_ref,str(df_waypoints.iloc[j,2]),'0']
						record_changed.append(fields)
						images_updated = images_updated + 1
					else:
						move_fail = move_fail + 1
				else:
					#print("rejecting" + fpath)
					images_rejected = images_rejected + 1
	df = pd.DataFrame(record_changed, columns=['Fname','Orig_Lon','Orig_Lon_Ref','Orig_Lat','Orig_Lat_Ref','Orig_Alt','Orig_Alt_Ref','Upd_Lon','Upd_Lon_Ref','Upd_Lat','Upd_Lat_Ref','Upd_Alt','Upd_Alt_Ref'])
	return images_updated, images_rejected, move_fail, df




def get_datetime_from_image_exif_orig(fname):
	
	fpath = img_dir + fname
	with open(fpath, 'rb') as img_file:
		img = Image(img_file)		
		img_dt_obj = img.get("datetime_original")  
		dt_obj = datetime.datetime.strptime(str(img_dt_obj),'%Y:%m:%d %H:%M:%S')

	return dt_obj


def get_datetime_from_image_exif(fname):
	
	fpath = img_dir + fname
	img = open(fpath, 'rb')
	tags = {}
	tags = exifread.process_file(img, stop_tag = 'EXIF DateTimeOriginal') # EXIF DateTimeOriginal
	for tag in tags.keys():
		print ("Key: %s, value %s" % (tag, tags[tag]))
		if tag in ('EXIF DateTimeOriginal'):
			img_dt_obj = tags[tag]
			dt_obj = datetime.datetime.strptime(str(img_dt_obj),'%Y:%m:%d %H:%M:%S')
	img.close()
	
	
	return dt_obj



def load_filenames(file_path):
	
	filelist = glob.glob(file_path)
	return filelist


def get_img_files(file_dir):    
	
	filename_returned = []
	filelist = load_filenames(file_dir + "*.JPG")
	
	for filename in filelist:  #TODO Error checking for bad file
		filename = os.path.basename(filename) 
		#print(filename)
		#datetime_obj = get_datetime_from_image_exif_orig(filename)
		#print("Adding " + filename + " " + str(datetime_obj))
		fields = [filename]
		filename_returned.append(fields)
		#print(filename_returned)
	
	#print("before create df")
	df_filename = pd.DataFrame(filename_returned,columns=['fname'])
	#print("finished get_img_files")
	return df_filename



def load_track_points(xmlFile):
# 1. Open GPS Log
	points_returned = []
	xmlFile_path = img_dir + xmlFile
	gpx_file = open(xmlFile_path, 'r')
	gpx = gpxpy.parse(gpx_file)
	
	for track in gpx.tracks:
		for segment in track.segments:
			for point in segment.points:
				local_time_dt = change_timezone(point.time.strftime('%Y-%m-%d %H:%M:%S'), LOCAL_ZONE)
				local_time = local_time_dt.replace(tzinfo=None)
				fields = [point.latitude, point.longitude, point.elevation, local_time]
				points_returned.append(fields)
	
	df_points = pd.DataFrame(points_returned,columns=['point_lat','point_lon','point_elev','point_time'])
	return df_points



def main():

	updated = 0
	rejected = 0
	move_failled = 0
 
	logs_dir = "/home/admin/dockers/ODM/gps_app/data/logs/"
	setupLogging(logs_dir)
	write_log('Running load_track_points ')
	df_points = load_track_points(GPS_LOGGER_TRACK_FILE)
	write_log('Running get_img_files ')
	df_img_files = get_img_files(img_dir)
	
	write_log('Running update_images ')
	updated, rejected, move_failled, df = update_images(df_img_files,df_points)
	write_csv_data(df, 'EXIF_Updates', logs_dir)
 
	print("{0} images updated. {1} rejected. {2} file move failled".format(updated, rejected, move_failled))


if __name__ == "__main__":
    main()