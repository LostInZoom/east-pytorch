# Script qui permet d'évaluer sommairement les résultats produits par le modèle EAST par rapport à un jeu de test
# attend en entrée une liste de répertoires avec les fichiers textes de sortie du modèle 
# et un répertoire des "vérités terrain" des coordonnées des boîtes de texte au format geojson
# les noms des fichiers à évaluer et des fichiers de ref doivent correspondre : 
# resultat_a_evaluer/image_1.txt <-> verite_terrain/image_1.geojson

from os import listdir
import os.path
from locale import format_string, setlocale, LC_NUMERIC

import fiona
from shapely.geometry import Polygon, shape
from shapely.affinity import scale
from shapely.ops import unary_union

ref_jsons = '/home/mac/hdd/mac/code/python/bigtiff/cassini_ref'
res_root_dir = '/home/mac/hdd/mac/code/python/EAST'
res_dirs = ['res_base', 'res_am6',
            'fots',
            'res_cas_1ep', 'res_cas_2ep', 'res_cas_3ep', 'res_cas_4ep', 'res_cas_5ep', 'res_cas_tuned',
            'res_cas2_2ep',
            'res_cas_corr_1ep', 'res_cas_corr_2ep', 'res_cas_corr_3ep', 'res_cas_corr_5ep',
            'res_cas_rec',
            'res_cas_ext_5ep', 'res_cas_ext2_1ep', 'res_cas_ext2_5ep',
            'res_cas_ext_rec_1ep', 'res_cas_ext_rec_2ep', 'res_cas_ext_rec_3ep', 'res_cas_ext_rec_5ep',
            'res_cas_ext2_rec_1ep',
            'res_am6_cas_1ep', 'res_am6_cas_2ep', 'res_am6_cas_3ep', 'res_am6_cas_4ep', 'res_am6_cas_5ep', 'res_am6_cas_tuned', 
            'res_am6_cas_rec',
            'res_am6_cas_ext_1ep', 'res_am6_cas_ext_2ep', 'res_am6_cas_ext_3ep', 'res_am6_cas_ext_4ep', 'res_am6_cas_ext_5ep', 'res_am6_cas_ext',
            'res_am6_cas_ext_rec_1ep', 'res_am6_cas_ext_rec_2ep', 'res_am6_cas_ext_rec_3ep', 'res_am6_cas_ext_rec_4ep', 'res_am6_cas_rec_ext',
            'res_cas_rec_ext_1ep', 'res_cas_rec_ext_5ep',]

# returns a shapely Polygon from ICDAR text line
def poly_from_line(line):
    coords = [int(c) if int(c) >=0 else 0 for c in line.split(',') ] # get positive numbers for x and y
    coords = [ coords[i:i+2] for i in range(0, len(coords), 2)] # group by (x,y)
    poly = Polygon(coords)
    return poly

# list of polygons from icdar format text file
def polys_from_txtfile(txt_file):
    with open(txt_file) as f:
        lines = [line.rstrip() for line in f.readlines()] # remove \n for each line
    polys = [poly_from_line(l) for l in lines]
    return polys

# polygons from json file with y inverted to fit image coordinates
def polys_from_json(json_file):
    polys = []
    with fiona.open(json_file) as j:
        for e in j:
            geom_json = e['geometry']
            poly = scale(shape(geom_json), yfact = -1, origin = (0, 0))
            polys.append(poly)
    return polys

def false_positives(polys_res, polys_ref):
    n, R = 0, 0.05
    uref = unary_union(polys_ref)
    for p in polys_res:
        if (not p.intersects(uref)) or (p.intersection(uref).area / p.area) <= R:
            n += 1
    return n / len(polys_res)

def intersection_over_union(polys_res, polys_ref):
    ures = unary_union(polys_res)
    uref = unary_union(polys_ref)
    return uref.intersection(ures).area / ures.union(uref).area

def not_found(polys_res, polys_ref):
    n = 0
    ures = unary_union(polys_res)
    for r in polys_ref:
        if not ures.intersects(r):
            n += 1
    return n / len(polys_res)

ref_files = [f for f in listdir(ref_jsons) if f.endswith('.geojson')]
nb_tiles = len(ref_files)

header = 'file,FP,Not_Found,IoU'
print(header)
setlocale(LC_NUMERIC, '') # simpler to paste in libreoffice with comma as decimal separator
W_IOU, W_FP, W_NF = 6,1,3

for dir in res_dirs:
    fps, nfs, ious = 0, 0, 0
    for i, gjson in enumerate(ref_files):
        (base, _) = os.path.splitext(gjson)
        ref_file = f'{ref_jsons}/{gjson}'
        res_file = f'{res_root_dir}/{dir}/{base}.txt'
        polys_ref = polys_from_json(ref_file)
        polys_res = polys_from_txtfile(res_file)
        fp, nf, iou = false_positives(polys_res, polys_ref), not_found(polys_res, polys_ref), intersection_over_union(polys_res, polys_ref)
        fps, nfs, ious = fps + fp, nfs + nf, ious +iou
        res = f'{dir}/{base},{fp},{nf},{iou}'
        #print(res)
    fps, nfs, ious = fps/nb_tiles, nfs/nb_tiles, ious/nb_tiles
    #score = (6*ious - 1*fps - 3*nfs) / 10
    score = (W_IOU*ious + W_FP*(1-fps) + W_NF*(1-nfs)) / (W_IOU + W_FP + W_NF)
    #print(f'{dir :<23} | false_pos: {fps :.4f} | not_found: {nfs :.4f}  | iou: {ious:.4f} | score: {score:.3f}')
    print(f'{dir} {format_string("%.5f", fps)} {format_string("%.5f", nfs)} {format_string("%.5f", ious)}')
        


# import matplotlib.pyplot as plt
# ref_json = './cassini_ref/cassini_1.geojson'
# east_res = './test/cassini_1_am6_cas_rec.txt'
# polys_res = polys_from_txtfile(east_res)
# polys_ref = polys_from_json(ref_json)
# for p in polys_res:
#     pp = scale(p, yfact = -1, origin = (0, 0))
#     plt.plot(*pp.exterior.xy, color="red")
# for p in polys_ref:
#     pp = scale(p, yfact = -1, origin = (0, 0))
#     plt.plot(*pp.exterior.xy, color="green")
# plt.show()
