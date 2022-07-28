import os
import math
from time import time
import simplekml
import shapefile

#TODO: add arguments



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



def write_kml(waypts):
    kml = simplekml.Kml()
    for waypt in waypts:
        lat_deg, lat_min, lat_sec, lat_ref = deg_to_dms(waypt[1], 'latitude')
		lon_deg, lon_min, lon_sec, lon_ref = deg_to_dms(waypt[2], 'longitude')
        kml.newpoint(description=waypt[0],
            coords=[(waypt[1], waypt[2])])  # lon, lat, optional height
    # save KML to a file
    kml.save("test.kml")



def get_waypts():
    # https://pythonhosted.org/Python%20Shapefile%20Library/
    
    sf = shapefile.Reader("app/ProjectionCenters.dbf")
    tot_records = len(sf.records())
    
#   Record #0: ['0001', '00001', 16709905.77, -3578744.11, 887.1, 0.0, 0.0, 68.0]
#   Record #1: ['0001', '00002', 16709973.2, -3578577.22, 887.1, 0.0, 0.0, 68.0]
    start_strip = 0
    strip_list = []
    for i in range(tot_records):
        rec = sf.record(i)
        strip    = rec[0]
        waypt    = rec[1]
        lat      = rec[2]
        lon      = rec[3]
        alt      = rec[4]
        
        if start_strip != strip:                            # Mismatch of strip no 
            
            if start_strip != 0:                            # if not the beginning and records don't match print last record
                prec = sf.record(i - 1)
                pstrip    = prec[0]
                pwaypt    = prec[1]
                plat      = prec[2]
                plon      = prec[3]
                palt      = prec[4]
                #print("EndStrip ", pstrip,pwaypt,plat,plon,palt)
                fields = ["End Strip " + str(pstrip), str(plat), str(plon)]
                strip_list.append(fields)
                #print("StartStrip ", strip,waypt,lat,lon,alt)
                fields = ["Start Strip " + str(strip), str(lat), str(lon)]
                strip_list.append(fields)
            else:    
                #print("StartStrip ", strip,waypt,lat,lon,alt)    # Only prints on the first iteration
                fields = ["Start Strip " + str(strip), str(lat), str(lon)]
                strip_list.append(fields)
                
        start_strip = strip
        
        
    # Last record
    #print("EndStrip ", strip,waypt,lat,lon,alt)    
    fields = ["End Strip " + str(strip), str(lat), str(lon)]
    strip_list.append(fields)

    return strip_list
        

if __name__ == "__main__":
    start = time()
    waypoints = get_waypts()
    print(waypoints)
    
    write_kml(waypoints)
    end = time()
     