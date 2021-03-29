"""
TODO:
make modular
"""

import csv, json
from geojson import Feature, FeatureCollection, Point 

### START CONFIG ###
infile_path = 'geo_schools.csv'
outfile_path = 'geo_schools.geojson'
### END CONFIG ###

infile = open(infile_path)
incsv = [x for x in csv.DictReader(infile)]

def geojsonify(schools_list):
    """ 
    takes list of dicts
    and returns geojson
    """
    features = []
    for school in schools_list:
        point = Point(coordinates=(float(school['lat']),float(school['lon'])))
        properties = { 
                      'name': school['Closed School'],
                      'address': school['Address'],
                      'repurposed': school['Repurposed?'],
                      'comm_area': school['Community area'],
                     }
        features.append(Feature(geometry=point,properties=properties))
    return FeatureCollection(features)

outfile = open(outfile_path,'w')
json.dump(geojsonify(incsv),outfile)
outfile.close()
~                                                                                                                                                                        
~                                                                                                                                                                        
~                               
