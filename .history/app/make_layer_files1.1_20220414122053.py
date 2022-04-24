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
import os, sys, glob
import subprocess
import math
import gpxpy
import gpxpy.gpx
import numpy as np
import pandas as pd
import exifread
#import piexif
#import pyexiv2


import exiftool

from datetime import datetime
from dateutil import tz
from datetime import timedelta
from pprint import pprint # for printing Python dictionaries in a human-readable way
from exif import Image, DATETIME_STR_FORMAT


from flutils import *

# 0. Create python environment
#   a. pip install virtualenv
#   b. virtualenv venv
#   c. source venv/bin/activate
#   d. venv/bin/python -m pip install --upgrade pip
#   f. pip install gpxpy    --> https://ourpython.com/python/how-to-extract-gpx-data-with-python
#                           -->  https://pypi.python.org/pypi/gpxpy
#
#
# 1. Open GPS Log file and create df with waypoints 1 second apart
# 2. Open video capture file and extract images that coincide with timestamp from the waypoints
# 3. Update the metadata of the image files with time and gps coords
# 4. save the extracted images to a subdirectory

#
#workingdir = "/home/admin/dockers/ODM/Bridge-Test3"
img_dir = "/home/admin/dockers/ODM/Bridge-Test3"
#logs_dir = ".src/test9/logs/"

# i.e if video of duration 30 seconds, saves 10 frame per second = 300 frames saved in total
SAVING_FRAMES_PER_SECOND = 1
LOCAL_ZONE = 'Australia/Brisbane'


def change_timezone(from_time, local_zone):
	
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz(local_zone)
	utc = datetime.datetime.strptime(from_time, '%Y-%m-%d %H:%M:%S')
	utc = utc.replace(tzinfo=from_zone)
	to_time = utc.astimezone(to_zone)

	return(to_time)



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


   

def update_images(df_images, df_waypoints):
# https://exif.readthedocs.io/en/latest/usage.html#add-geolocation
	
	images_updated = 0
	
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
    
				with exiftool.ExifToolHelper() as et:
					et.execute("-GPSLongitude=" + str(df_waypoints.iloc[j,1]), fpath)
					et.execute("-GPSLongitudeRef=" + lon_ref, fpath)
					et.execute("-GPSLatitude=" + str(df_waypoints.iloc[j,0]), fpath)
					et.execute("-GPSLatitudeRef=" + lat_ref, fpath)
					et.execute("-GPSAltitude=" + str(df_waypoints.iloc[j,2]), fpath)
					et.execute("-GPSAltitudeRef=0", fpath)
				
					
				images_updated = images_updated + 1
				
	return images_updated




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
	filelist = load_filenames(file_dir + "*.jpg")
	
	for filename in filelist:  #TODO Error checking for bad file
		filename = os.path.basename(filename) 
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

if __name__ == "__main__":

	df_points = load_track_points('20220318-103354_Test8.gpx')
	df_img_files = get_img_files(img_dir)
	
	updated = update_images(df_img_files,df_points)
 
	print("{} images updated".format(updated))


