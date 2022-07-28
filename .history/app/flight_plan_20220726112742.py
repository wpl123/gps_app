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
        _waypoint = rec[1]
        _lat      = rec[2]
        @admin.register()
        class Admin(admin.ModelAdmin):
            
        
        print(_strip,_waypoint)
  
        
if __name__ == "__main__":
    start = time()
    test1()
    end = time()
     