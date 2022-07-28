import simplekml

kml = simplekml(open=1)

kml = simplekml.Kml(open=1)

# Creating MultiGeometry
multipnt = kml.newmultigeometry(name="MultiPoint") # SA (Hartebeeshoek94) Grid Intersections
multilin = kml.newmultigeometry(name="MultiLine") # SA (Hartebeeshoek94) Lo. Lines
multipolodd = kml.newmultigeometry(name="MultiPolyOdd") # SA (Hartebeeshoek94) Lo. Regions
multipoleven = kml.newmultigeometry(name="MultiPolyEven") # SA (Hartebeeshoek94) Second Lo. Regions for styling
lolabels = kml.newfolder(name="Lo. Regions") # The labels of the Lo. Regions (17-33)

# Create all the coordinates to populate the South African Coordinate System
polycoordsodd = []
polycoordseven = []
firstrun = True
for x in range(16, 36, 2):
    linecoords = []
    if x < 34: # Label region
        lo = lolabels.newpoint(name=str(x+1), coords=[(x+1, -29)])
        lo.style.iconstyle.icon.href = "" # Remove the icons
    for y in range(-35, -19, 2):
        multipnt.newpoint(coords=[(x, y)])
        linecoords.append((x,y))
    multilin.newlinestring(coords=linecoords)
    polycoordsodd.append(linecoords)
    if len(polycoordsodd) == 2:
        end = polycoordsodd[1][:]
        end.reverse()
        multipolodd.newpolygon(outerboundaryis=polycoordsodd[0]+end)
        polycoordsodd = []
    if firstrun:
        firstrun = False
    else:
        polycoordseven.append(linecoords)
        if len(polycoordseven) == 2:
            end = polycoordseven[1][:]
            end.reverse()
            multipoleven.newpolygon(outerboundaryis=polycoordseven[0]+end)
            polycoordseven = []

# Style everything
multipnt.style.labelstyle.scale = 0.0 # Hide the labels of the points
multipnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
multilin.style.linestyle.color = Color.black
multilin.style.linestyle.width = 5
multipoleven.style.polystyle.color = Color.changealpha("77", Color.orange)
multipoleven.style.linestyle.color = Color.changealpha("77", Color.orange)
multipolodd.style.polystyle.color = Color.changealpha("77", Color.lightblue)
multipolodd.style.linestyle.color = Color.changealpha("77", Color.lightblue)

kml.save("Tut_MultiGeometry.kml")

