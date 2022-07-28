
import itertools
from simplekml import Kml, Style
import shapefile

#TODO: add arguments




def write_kml(waypts):
    
    kml = Kml()
    
    # Style --> https://simplekml.readthedocs.io/en/latest/styling.html
    
    fol = kml.newfolder(name="A Folder")
    pnt_sharedstyle = Style()
    
    # Creating MultiGeometry
    multipnt = kml.newmultigeometry(name="Points")
    multipnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
    
    multilin = kml.newmultigeometry(name="Flight Paths")
    multilin.style.linestyle.width = 2   
    
    lolabels = kml.newfolder(name="Mark") 
    
    iterators  = itertools.cycle(waypts)
    next_waypt = next(iterators)
    linecoords = []
    no_recs = len(waypoints)
    i = 0
    for prev_waypt in waypts:
            
        next_waypt = next(iterators)
        
        # Do not the draw last point back to first point 
        i = i + 1
        if i == no_recs:
            break
        
        pnt1 = kml.newpoint(description="Start " + str(prev_waypt[0]),
            coords=[(prev_waypt[1], prev_waypt[2], prev_waypt[3])])                # lon, lat, optional height
        pnt1.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
        pnt1.style.balloonstyle.text = 'Strip {0}\n Lon   {1}\n Lat   {2}\n Alt   {3}\n'.format(prev_waypt[0],prev_waypt[1],prev_waypt[2], prev_waypt[3])
        
        lo = lolabels.newpoint(name=str(prev_waypt[0]), coords=[(prev_waypt[1],prev_waypt[2])])
        lo.iconstyle.icon.href = ""
        
        
        if i % 2 == 1: 
            linecoords = [(prev_waypt[1], prev_waypt[2], prev_waypt[3]), (next_waypt[1], next_waypt[2], next_waypt[3])]
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
                strip_list.append(fields)
                #print("StartStrip ", strip,waypt,lat,lon,alt)
                fields = [strip, str(lat), str(lon), str(alt)]
                strip_list.append(fields)
            else:    
                #print("StartStrip ", strip,waypt,lat,lon,alt)    # Only prints on the first iteration
                fields = [strip, str(lat), str(lon), str(alt)]
                strip_list.append(fields)
                
        start_strip = strip
        
        
    # Last record   
    fields = [strip, str(lat), str(lon), str(alt)]
    strip_list.append(fields)
    
    return strip_list
        

if __name__ == "__main__":
    
    waypoints = get_waypts()
    write_kml(waypoints)
    