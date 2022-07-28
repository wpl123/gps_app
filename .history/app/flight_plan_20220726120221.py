import os
import codecs
from time import time

import shapefile

#TODO: add arguments




def test1():
    
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
        
        if start_strip != strip:                            # Beginning 
            
            if start_strip != 0:                            # print last record
                prec = sf.record(i - 1)
                pstrip    = prec[0]
                pwaypt    = prec[1]
                plat      = prec[2]
                plon      = prec[3]
                palt      = prec[4]
                print("EndStrip ", pstrip,pwaypt,plat,plon,alt)
                
            print("StartStrip ", strip,waypt,lat,lon,alt)
            start_strip = strip
        elif end_strip != strip:                            # end of strip
            print("EndStrip ", strip,waypt,lat,lon,alt)
            end_strip = strip
        else:
            start_strip = strip
        #    end_strip = strip
        
  
        
if __name__ == "__main__":
    start = time()
    test1()
    end = time()
     