# Script pour merger les geojsons des saisies de boites de texte qui ont la même structure
from collections import OrderedDict
import fiona
from fiona.crs import from_epsg

geojsons = ["chefslieux.geojson", "toponymes.geojson", "addendum.geojson"]
out_json = "merged_partially_corrected2.geojson"


boxes_schema = {
    'geometry': 'Polygon',
    'properties': OrderedDict([('id', 'int'),('label', 'str')])
    }
    
boxes_crs = from_epsg(2154)
output_driver = "GeoJSON"

features = []
for gj in geojsons:
    with fiona.open(gj) as c:
        for e in c:
            feature =  {'geometry': e['geometry'], 'properties': e['properties']}
            #print(feature)
            features.append(feature)
    print(f'******************  {gj} added')

with fiona.open(out_json, 'w', driver=output_driver,crs=boxes_crs, schema=boxes_schema) as c:
    for f in features:
        c.write(f)
print(f'merging done for {len(features)} features -- {out_json} written')
