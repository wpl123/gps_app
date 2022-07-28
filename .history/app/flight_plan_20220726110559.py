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
        print(sf.record(i).split(','))
        #ln = (line.decode('utf-8').replace('\n','')).split(',')
    #    for _record in sf.record(i):
    #        print(_record)
#        get first and last record of each strip
        
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
     