import os
import math
import itertools
from time import time
from decimal import Decimal
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



#def xy_to_deg():
#    concat(y(transform($geometry, layer_property(@layer_name, 'crs'), 'EPSG:4326')),' ',x(transform($geometry, layer_property(@layer_name, 'crs'), 'EPSG:4326')))

def write_kml(waypts):
    kml = simplekml.Kml()
    
    # Creating MultiGeometry
    multipnt = kml.newmultigeometry(name="MultiPoint") # SA (Hartebeeshoek94) Grid Intersections
    multilin = kml.newmultigeometry(name="MultiLine") # SA (Hartebeeshoek94) Lo. Lines
    
    iterators  = itertools.cycle(waypts)
    next_waypt = next(iterators)
    linecoords = []
    
    for waypt in waypts:
        next_waypt = next(iterators)
        prev_waypt = waypt
        #linecoords = (Decimal(waypt[1].strip("'")), Decimal(waypt[2].strip("'")), Decimal(next_waypt[1].strip("'")), Decimal(next_waypt[2].strip("'")))
        linecoords = [(waypt[1], waypt[2]), (next_waypt[1], next_waypt[2])]
            
        #print(linecoords)
        mpnt = multipnt.newpoint(name='Point: {0},coords=[(waypt[1], waypt[2])])
        multipnt.style.balloonstyle.text = 'lon ' + str(waypt[1]) + ', lat ' + str(waypt[2]) + ', alt ' + str(waypt[3])
        multipnt.newpoint(coords=[(next_waypt[1], next_waypt[2])])
        multilin.newlinestring(coords=linecoords)  

    multipnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
#    multilin.style.linestyle.color = simplekml.Color.blue
#    multilin.style.linestyle.width = 3  
    # save KML to a file
    kml.save("FlyoverWaypoints.kml")



def get_waypts():
    # https://pythonhosted.org/Python%20Shapefile%20Library/
    
    sf = shapefile.Reader("app/AddedFields.dbf")
    tot_records = len(sf.records())
    
#   Record #0: ['0001', '00001', 222992.13, 6615527.690000001, 887.1, 0.0, 0.0, 70.0, 150.112113479, -30.5607252593]
#   Record #1: ['0001', '00002', 223053.69, 6615696.83, 887.1, 0.0, 0.0, 70.0, 150.1127997815, -30.5592150994]
    start_strip = 0
    strip_list = []
    for i in range(tot_records):
        rec = sf.record(i)
        #print(rec)
        strip    = rec[0]
        waypt    = rec[1]
        alt      = rec[4]
        lat      = rec[8]
        lon      = rec[9]
        if start_strip != strip:                            # Mismatch of strip no 
            
            if start_strip != 0:                            # if not the beginning and records don't match print last record
                prec = sf.record(i - 1)
                pstrip    = prec[0]
                pwaypt    = prec[1]
                palt      = prec[4]
                plat      = prec[8]
                plon      = prec[9]
                #print("EndStrip ", pstrip,pwaypt,plat,plon,palt)
                fields = [pstrip, str(plat), str(plon), str(palt)]    # end strip
                #fields = [pstrip,plat,plon,palt]    # end strip
                strip_list.append(fields)
                #print("StartStrip ", strip,waypt,lat,lon,alt)
                fields = [strip, str(lat), str(lon), str(alt)]
                #fields = [strip,lat,lon,alt]       # start strip
                strip_list.append(fields)
            else:    
                #print("StartStrip ", strip,waypt,lat,lon,alt)    # Only prints on the first iteration
                fields = [strip, str(lat), str(lon), str(alt)]
                #fields = [strip,lat,lon,alt]       # start strip
                strip_list.append(fields)
                
        start_strip = strip
        
        
    # Last record
    #print("EndStrip ", strip,waypt,lat,lon,alt)    
    fields = [strip, str(lat), str(lon), str(alt)]
    #fields = [strip,lat,lon,alt]# end Strip
    strip_list.append(fields)

    return strip_list
        

if __name__ == "__main__":
    start = time()
    waypoints = get_waypts()
    #print(waypoints)
    
    write_kml(waypoints)
    end = time()
     