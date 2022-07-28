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

    for i in range(tot_records):
        rec = sf.record(i)
        _strip    = rec[0]
        _waypt    = rec[1]
        _lat      = rec[2]
        _lon      = rec[3]
        _alt      = rec[4]
        
        _start_waypt
        print(_strip,_waypoint,_lat,_lon,_alt)
  
        
if __name__ == "__main__":
    start = time()
    test1()
    end = time()
     