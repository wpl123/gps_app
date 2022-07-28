import os
import codecs
from time import time
import simplekml
import shapefile

#TODO: add arguments



def write_kml(waypts):
    f = open("KML.txt", "w")
    f.write("<KML_File>\n")
    f.write("<Document>\n")
    for waypt in waypts:
        f.write("\t<Placemark>")
        f.write("\t\t<decription>" + str(waypt[0]) + "</description>")
        f.write("\t\t<Point>")
        f.write("\t\t\t<coordinates>" + str(waypt[2]) + str(waypt[1]) + "</coordinates>")
        f.write("\t\t</Point>")
        f.write("\t</Placemark>")
    f.write("</Document>\n")
    f.write("</kml>\n")
    f.close()



def get_waypts():
    
    sf = shapefile.Reader("app/Projection Centers.dbf")
    fields = sf.fields
    
    tot_records = len(sf.records())
    
    #shapeRecs = sf.shapeRecords()    # only for .shp

    print (fields)
    
#   Record #0: ['0001', '00001', 16709905.77, -3578744.11, 887.1, 0.0, 0.0, 68.0]
#   Record #1: ['0001', '00002', 16709973.2, -3578577.22, 887.1, 0.0, 0.0, 68.0]
    start_strip = 0
    end_strip = 0
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
                print("EndStrip ", pstrip,pwaypt,plat,plon,palt)
                fields = ["End Strip " + str(pstrip), str(plat), str(plon)]
                strip_list.a
                print("StartStrip ", strip,waypt,lat,lon,alt)
                fields = ["Start Strip " + str(strip), str(lat), str(lon)]
            else:    
                print("StartStrip ", strip,waypt,lat,lon,alt)    # Only prints on the first iteration
                fields = ["Start Strip " + str(strip), str(lat), str(lon)]
                
        start_strip = strip
        
    # Last record
    print("EndStrip ", strip,waypt,lat,lon,alt)    
    fields = ["End Strip " + str(strip), str(lat), str(lon)]
    
    
    return strip_list
        
if __name__ == "__main__":
    start = time()
    waypoints = get_waypts()
    write_kml(waypoints)
    end = time()
     