from importlib.metadata import files
import os, sys

#https://stackoverflow.com/questions/1260792/import-a-file-from-a-subdirectory#%E2%80%A6
sys.path.extend([f'./{name}' for name in os.listdir(".") if os.path.isdir(name)])

from flutils import *
#TODO: add arguments


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


def write_gcp(gcp_fname,gcp_nname,img_list): 
	
	with open(gcp_fname, 'r') as ro, \
		open(gcp_nname, 'a') as rw:
	
		lines = ro.readlines()
		for line in lines:
			
			if line.find("EPSG") > -1:
				rw.write(line)
			
			else:
				for img in img_list:
					if line.find(img) > -1:
						rw.write(line)

	return        


def main():
    
	img_dir = "/home/admin/dockers/ODM/mine1/InnerPit images - GPSLogger Exif/"
	gcp_file = "/home/admin/dockers/ODM/mine1/InnerPit images - GPSLogger Exif/gcp_file_2.txt"
	gcp_nfile = "data/gcp_file_2_upd.txt"
	logs_dir = "/home/admin/dockers/ODM/gps_app/data/logs/"
	prefix   = "make_gcp_"
	setupLogging(logs_dir, prefix)
	write_log('Running get_img_files')
	img_files = get_img_files(img_dir)
	write_log('Running write_gcp')
	gcps = write_gcp(gcp_file,gcp_nfile,img_files)
	write_log('Finished')
    
    
if __name__ == "__main__":
    main()    