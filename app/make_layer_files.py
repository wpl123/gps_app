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
# 3. Start the camera recording on 3 second delay
# 3. 
#
import cv2
import os, sys, glob
import math
import gpxpy
import gpxpy.gpx
import numpy as np
import pandas as pd
import exifread
import piexif


#import exiftool

from datetime import datetime
from dateutil import tz
from datetime import timedelta
from pprint import pprint # for printing Python dictionaries in a human-readable way
from exif import Image, DATETIME_STR_FORMAT
#from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS

from flutils import *

# 0. Create python environment
#   a. pip install virtualenv
#   b. virtualenv venv
#   c. source venv/bin/activate
#   d. venv/bin/python -m pip install --upgrade pip
#   e. pip install opencv-python
#   f. pip install gpxpy    --> https://ourpython.com/python/how-to-extract-gpx-data-with-python
#                           -->  https://pypi.python.org/pypi/gpxpy

#	g. pip install ffmpeg-python
#   g. pip install virtualenvwrapper
#   h. Install exiftool-perl --> https://exiftool.org/install.html
#	h. 
#
#
# 1. Open GPS Log file and create df with waypoints 1 second apart
# 2. Open video capture file and extract images that coincide with timestamp from the waypoints
# 3. Update the metadata of the image files with time and gps coords
# 4. save the extracted images to a subdirectory

#
workingdir = "./app/"
img_dir = "./Campark-Test2/"
logs_dir = ".src/test9/logs/"

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
	print(abs(d), m, s, hemi)
	return abs(d), m, s, hemi


   

def update_images(df_images, df_waypoints):
# https://exif.readthedocs.io/en/latest/usage.html#add-geolocation
	
	images_updated = 0
	
	for i in range(len(df_images)):
		
		for j in range(len(df_waypoints)):
			
			if df_waypoints.iloc[j,3] == df_images.iloc[i,1]:  #TODO: Resolve datetime equality issue
				fpath = (img_dir + str(df_images.iloc[i,0]))
				new_fpath = (img_dir + "mod_" + str(df_images.iloc[i,0]))
				last_fpath = (img_dir + "mod2_" + str(df_images.iloc[i,0]))
				print("Update_images " + fpath + " " + str(df_images.iloc[i,1]))
				print("Update_images " + new_fpath + " " + str(df_images.iloc[i,1]))
				lat_deg, lat_min, lat_sec, lat_ref = deg_to_dms(df_waypoints.iloc[j,0], 'latitude')
				lon_deg, lon_min, lon_sec, lon_ref = deg_to_dms(df_waypoints.iloc[j,1], 'longitude')
				ele = df_waypoints.iloc[j,2]
				print("About to open ", fpath)
				
				with open(fpath, 'rb') as img_file:
					img = Image(img_file)
					
				print("About to copy to ", new_fpath)	
				with open(new_fpath, 'w+b') as new_img_file:
					
					new_img_file.write(img.get_file())
					print("About to open ", new_fpath)
					new_img = Image(new_img_file)

					print("About to set gps_longitude_ref ", lon_ref)
					new_img.set("gps_longitude_ref",lon_ref)
     
					print("About to copy to ", last_fpath)	
					with open(last_fpath, 'wb') as last_img_file:
					
						last_img_file.write(new_img.get_file())
						print("Completed copy of ", last_fpath)
      
#					new_img.write()
#					new_img.close()	
#					print(sorted(img.list_all()))
#					print(dir(img))
#                    if img.has_exif:
#                        status = f"contains EXIF (version {img.exif_version}) information."
#                    else:
#                        status = "does not contain any EXIF information."
#                    print(f"Image {fpath} {status}")
					#img.gps_latitude = (lat_deg, lat_min, lat_sec)
					#print("my_image object gps_latitude update for ", fpath)
					#img.gps_latitude_ref = "E" # lat_ref
					#img.gps_latitude_ref = lat_ref
					#img.gps_longitude = (lon_deg, lon_min, lon_sec)
					#img.gps_longitude_ref = lon_ref
					#img.gps_altitude = df_waypoints.iloc[j,2]
					#img.gps_altitude_ref = 0  # Above Sea Level
					#img.set("gps_longitude_ref",lon_ref)
     
				#print("About to save newfile", new_fpath)
				# save image
				#with open(new_fpath, 'wb') as new_img:
				#	new_img.write()
				#	new_img.close()    
				
					
				images_updated = images_updated + 1
				
	return images_updated




def get_datetime_from_image_exif_orig(fname):
	
	fpath = img_dir + fname
	with open(fpath, 'rb') as img_file:
		print(fpath)
		img = Image(img_file)
		print(sorted(img.list_all()))
		
		img_dt_obj = img.get("datetime_original")  
		dt_obj = datetime.datetime.strptime(str(img_dt_obj),'%Y:%m:%d %H:%M:%S')
	#image_file.seek(0) #TODO Does this work?
	#image_file.close() 
   
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
	
	#filelist = [(x[0], x[2]) for x in os.walk(file_dir)]
	filelist = glob.glob(file_path)
	return filelist


def get_img_files(file_dir):    
	
	filename_returned = []
	filelist = load_filenames(file_dir + "*.jpg")
	
	for filename in filelist:  #TODO Error checking for bad file
		filename = os.path.basename(filename) 
		datetime_obj = get_datetime_from_image_exif_orig(filename)
		#print("Adding " + filename + " " + str(datetime_obj))
		fields = [filename, datetime_obj]
		filename_returned.append(fields)
		#print(filename_returned)
	
	#print("before create df")
	df_filename = pd.DataFrame(filename_returned,columns=['fname','datetime_obj'])
	#print("finished get_img_files")
	return df_filename



def load_track_points(xmlFile):
# 1. Open GPS Log
	points_returned = []
	gpx_file = open(xmlFile, 'r')
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

	df_points = load_track_points('./Campark-Test2/20220323-144534.gpx')
	df_img_files = get_img_files(img_dir)
	print(df_points)
	print(df_img_files)
	updated = update_images(df_img_files,df_points)
 
	print("{} images updated".format(updated))



# Old stuff


def get_datetime_from_filename(fname):   # used for android phone testing only
	date_str = fname[4:12] # './Test3/IMG_20220316_092117.jpg'
	time_str = fname[13:19] # './Test3/IMG_20220316_092117.jpg'
	dt_str = (date_str + time_str)
	dt_obj = datetime.datetime.strptime(dt_str,'%Y%m%d%H%M%S')
	return dt_obj



def update_images_exif_orig(df_images, df_waypoints):
# https://exif.readthedocs.io/en/latest/usage.html#add-geolocation
	
	images_updated = 0
	
	# lat_deg = 0
	# lat_min = 0
	# lat_sec = 0
	# lon_deg = 0 
	# lon_min = 0 
	# lon_sec = 0
	# lat_ref = ''
	# lon_ref = '' 
	
	# print(df_images.dtypes)
	# print(df_waypoints.dtypes)
	for i in range(len(df_images)):
		
		for j in range(len(df_waypoints)):
			
			if df_waypoints.iloc[j,3] == df_images.iloc[i,1]:  #TODO: Resolve datetime equality issue
				fpath = (img_dir + str(df_images.iloc[i,0]))
				new_fpath = (img_dir + "mod_" + str(df_images.iloc[i,0]))
				print("Update_images " + fpath + " " + str(df_images.iloc[i,1]))
				print("Update_images " + new_fpath + " " + str(df_images.iloc[i,1]))
				lat_deg, lat_min, lat_sec, lat_ref = deg_to_dms(df_waypoints.iloc[j,0], 'latitude')
				lon_deg, lon_min, lon_sec, lon_ref = deg_to_dms(df_waypoints.iloc[j,1], 'longitude')
				ele = df_waypoints.iloc[j,2]
				print("Elevation ",ele)
				print("About to open ", fpath)
				
				with open(fpath, 'rb') as img_file:
					img_file.seek(0)
					print("Openning ", fpath)
					img = Image(img_file)
					print("Openned ", fpath)
#					print(sorted(img.list_all()))
#					print(dir(img))
#                    if img.has_exif:
#                        status = f"contains EXIF (version {img.exif_version}) information."
#                    else:
#                        status = "does not contain any EXIF information."
#                    print(f"Image {fpath} {status}")
					#img.gps_latitude = (lat_deg, lat_min, lat_sec)
					#print("my_image object gps_latitude update for ", fpath)
					#img.gps_latitude_ref = "E" # lat_ref
					#img.gps_latitude_ref = lat_ref
					#img.gps_longitude = (lon_deg, lon_min, lon_sec)
					#img.gps_longitude_ref = lon_ref
					#img.gps_altitude = df_waypoints.iloc[j,2]
					#img.gps_altitude_ref = 0  # Above Sea Level
					img.set("gps_longitude_ref",lon_ref)
     
				print("About to save newfile", new_fpath)
				# save image
		#        with open(new_fpath, 'wb') as new_img_file:
		#            new_img_file.write(img.get_file())
		#            new_img_file.close()    
				
					
				images_updated = images_updated + 1
				
	return images_updated 


def update_images_piexif(df_images, df_waypoints):
# https://exif.readthedocs.io/en/latest/usage.html#add-geolocation
	
	images_updated = 0
	
	for i in range(len(df_images)):
		
		for j in range(len(df_waypoints)):
			
			if df_waypoints.iloc[j,3] == df_images.iloc[i,1]:
				fpath = (img_dir + str(df_images.iloc[i,0]))
				new_fpath = (img_dir + "mod_" + str(df_images.iloc[i,0]))
				print("Update_images " + fpath + " " + str(df_images.iloc[i,1]))
				print("Update_images " + new_fpath + " " + str(df_images.iloc[i,1]))
				lat_deg, lat_min, lat_sec, lat_ref = deg_to_dms(df_waypoints.iloc[j,0], 'latitude')
				lon_deg, lon_min, lon_sec, lon_ref = deg_to_dms(df_waypoints.iloc[j,1], 'longitude')
				ele = df_waypoints.iloc[j,2]
			
				gps_ifd = {
					piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
					piexif.GPSIFD.GPSAltitudeRef: 0,
					piexif.GPSIFD.GPSAltitude: ele,
					piexif.GPSIFD.GPSLatitudeRef: lat_ref,
					piexif.GPSIFD.GPSLatitude: (lat_deg, lat_min, lat_sec),
					piexif.GPSIFD.GPSLongitudeRef: lon_ref,
					piexif.GPSIFD.GPSLongitude: (lon_deg, lon_min, lon_sec),
				}
    
				exif_dict = {"GPS": gps_ifd}
				exif_bytes = piexif.dump(exif_dict)
				piexif.insert(exif_bytes, fpath)
       
				images_updated = images_updated + 1
				
	return images_updated 


def update_images_PIL(df_images, df_waypoints):
# https://exif.readthedocs.io/en/latest/usage.html#add-geolocation
	
	images_updated = 0
	
	for i in range(len(df_images)):
		
		for j in range(len(df_waypoints)):
			
			if df_waypoints.iloc[j,3] == df_images.iloc[i,1]:
				fpath = (img_dir + str(df_images.iloc[i,0]))
				new_fpath = (img_dir + "mod_" + str(df_images.iloc[i,0]))
				print("Update_images " + fpath + " " + str(df_images.iloc[i,1]))
				print("Update_images " + new_fpath + " " + str(df_images.iloc[i,1]))
				lat_deg, lat_min, lat_sec, lat_ref = deg_to_dms(df_waypoints.iloc[j,0], 'latitude')
				lon_deg, lon_min, lon_sec, lon_ref = deg_to_dms(df_waypoints.iloc[j,1], 'longitude')
				ele = df_waypoints.iloc[j,2]
			
				img = Image.open(fpath)
				img_exif = img._getexif()
    
				geotagging = {}
				for (idx, tag) in TAGS.items():
					if tag == 'GPSInfo':
						if idx not in img_exif:
							raise ValueError("No EXIF geotagging found")

						for (key, val) in GPSTAGS.items():
							if key in img_exif[idx]:
								geotagging[val] = img_exif[idx][key]


				print(geotagging)
				images_updated = images_updated + 1
				
	return images_updated 



# All MP4 stuff that doesn't work
def format_timedelta(td):
	"""Utility function to format timedelta objects in a cool way (e.g 00:00:20.05) 
	omitting microseconds and retaining milliseconds"""
	result = str(td)
	try:
		result, ms = result.split(".")
	except ValueError:
		return result + ".00".replace(":", "-")
	ms = int(ms)
	ms = round(ms / 1e4)
	return f"{result}.{ms:02}".replace(":", "-")


#def get_mp4_metadata(video_file):
	
	#pprint(ffmpeg.probe(video_file)["streams"])
	


def getImages_test(video_file, df_points):
	
	# Read the video from specified path
	filename, _ = os.path.splitext(video_file)
	filename += "-opencv"
	# make a folder by the name of the video file
	if not os.path.isdir(filename):
		os.mkdir(filename)
	# read the video file    
	cap = cv2.VideoCapture(video_file)
	
	for i in range(len(df_points)):
		print(df_points.loc[i])
		cap.set
	

def get_saving_frames_durations(cap, saving_fps):
	"""A function that returns the list of durations where to save the frames"""
	s = []
	# get the clip duration by dividing number of frames by the number of frames per second
	clip_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
	# use np.arange() to make floating-point steps
	for i in np.arange(0, clip_duration, 1 / saving_fps):
		s.append(i)
	return s


def getImages_old(video_file, points):
	
	# Read the video from specified path
	filename, _ = os.path.splitext(video_file)
	filename += "-opencv"
	# make a folder by the name of the video file
	if not os.path.isdir(filename):
		os.mkdir(filename)
	# read the video file    
	cap = cv2.VideoCapture(video_file)
	# get the FPS of the video
	fps = cap.get(cv2.CAP_PROP_FPS)
	# if the SAVING_FRAMES_PER_SECOND is above video FPS, then set it to FPS (as maximum)
	saving_frames_per_second = min(fps, SAVING_FRAMES_PER_SECOND)
	# get the list of duration spots to save
	saving_frames_durations = get_saving_frames_durations(cap, saving_frames_per_second)
	# start the loop
	count = 0
	while True:
		is_read, frame = cap.read()
		if not is_read:
			# break out of the loop if there are no frames to read
			break
		# get the duration by dividing the frame count by the FPS
		frame_duration = count / fps
		try:
			# get the earliest duration to save
			closest_duration = saving_frames_durations[0]
		except IndexError:
			# the list is empty, all duration frames were saved
			break
		if frame_duration >= closest_duration:
			# if closest duration is less than or equals the frame duration, 
			# then save the frame
			frame_duration_formatted = format_timedelta(timedelta(seconds=frame_duration))
			cv2.imwrite(os.path.join(filename, f"frame{frame_duration_formatted}.jpg"), frame) 
			# drop the duration spot from the list, since this duration spot is already saved
			try:
				saving_frames_durations.pop(0)
			except IndexError:
				pass
		# increment the frame count
		count += 1
