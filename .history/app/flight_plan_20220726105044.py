import os
import codecs
from time import time

import shapefile

#TODO: add arguments




def test1():
    
    sf = shapefile.Reader("app/Projection Centers.dbf")
    fields = sf.fields
    record = sf.records(1)
    
    #shapeRecs = sf.shapeRecords()    # only for .shp

    print (fields)
    print (shapeRecs)
    print (record)
    #for flight_paths in shapes:
    #    for lon, lat in flight_paths.lat:
    #    print(polygon)
    
    
#    fp = open("Projection Centers.dbf",'rb')
#    lines = fp.readlines()
#    fp.close
#
#    #TODO
#    # 1. Strip off the non asci characters
#
#    lns = []
#    line_count = 0
#    for line in lines:
#        line_count = line_count + 1
#        #if line_count > 1:             # skip header lines
#            #ln = (line.decode('utf-8').replace('\n','')).split(',')
#            #ln = (line.decode('utf-8'))
#
#
#        print("line: " + str(line_count) + " " + line)
#            #lns.append(ln)
        
        
if __name__ == "__main__":
    start = time()
    test1()
    end = time()
     