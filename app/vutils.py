#vutils.py


# Old stuff

#   e. pip install opencv-python
#   f. pip install gpxpy    --> https://ourpython.com/python/how-to-extract-gpx-data-with-python
#                           -->  https://pypi.python.org/pypi/gpxpy

#	g. pip install ffmpeg-python
#   g. pip install virtualenvwrapper
#   h. Install exiftool-perl --> https://exiftool.org/install.html
#	h. 
#

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
