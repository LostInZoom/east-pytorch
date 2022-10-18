# script cradoss qui génère les positions approximatives des bôites de texte à partir des geopackages
# commenter ou décommenter la partie idoine..

from collections import OrderedDict
import fiona
from fiona.crs import from_epsg

from shapely.wkt import loads
from shapely.geometry import mapping

chefs_gpkg = "/home/mac/hdd/mac/work/donnees_julien/cassini_52/chefs_lieux.gpkg"
topon_gpkg = "/home/mac/hdd/mac/work/donnees_julien/cassini_52/toponymes.gpkg"

boxes_schema = {
    'geometry': 'Polygon',
    'properties': OrderedDict([('id', 'int'),('label', 'str')])
    }
    
boxes_crs = from_epsg(2154)
output_driver = "GeoJSON"

##############################################################################
# chef_lieux
##############################################################################
features = []
letter_length = 200.
with fiona.open(chefs_gpkg) as c:
    for e in c:
        props = e['properties']
        label = props['label']
        fid = e['id']
        nb_letters = len(props['Etiquette_1']) if props['Etiquette_1'] is not None else 10.
        ht = 600
        ht = ht*2 if (props['Etiquette_2'] is not None and props['Ligne2AlaSuite'] is False) else ht
        if props['X_etiquette'] is not None: #and props['Etiquette_2'] is not None and props['Ligne2AlaSuite'] is True: # and props['police_bold'] is False:
            nb_letters = len(props['nomcart'])
            xll, yll = props['X_etiquette'] - 100, props['Y_etiquette'] - 100
            wkt = f'POLYGON(({xll} {yll}, {xll + letter_length*nb_letters} {yll}, {xll + letter_length*nb_letters} {yll+ht}, {xll} {yll+ht}, {xll} {yll}))'
            poly = loads(wkt)
            feature =  {'geometry': mapping(poly), 'properties': OrderedDict([('id', fid), ('label', label)])}
            features.append(feature)
            print(f'{fid};{wkt};{label}')
to_write = 'chefslieux.geojson'
with fiona.open(to_write, 'w', driver=output_driver,crs=boxes_crs, schema=boxes_schema) as c:
    for f in features:
        c.write(f)
print('chefs_lieux done')

##############################################################################
# Toponymes
##############################################################################
features = []
letter_length = 120.
offsetX, offsetY = -35, -35
with fiona.open(topon_gpkg) as c:
    for e in c:
        fid = e['id']
        label = e['properties']['etiquette']
        X, Y = coords = e['geometry']['coordinates'][0] + offsetX, e['geometry']['coordinates'][1] +offsetY
        #print(X, Y, label, len(label))
        nb_letters = len(label) if len(label) is not None else 0.
        ht = 300
        wkt = f'POLYGON(({X} {Y}, {X + letter_length*nb_letters} {Y}, {X + letter_length*nb_letters} {Y+ht}, {X} {Y+ht}, {X} {Y}))'
        poly = loads(wkt)
        feature =  {'geometry': mapping(poly), 'properties': OrderedDict([('id', fid), ('label', label)])}
        features.append(feature)
        print(f'{fid};{wkt};{label}')
to_write = 'toponymes.geojson'
with fiona.open(to_write, 'w', driver=output_driver,crs=boxes_crs, schema=boxes_schema) as c:
    for f in features:
        c.write(f)


