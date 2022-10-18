# Script qui permet de découper le tif original en sous imagettes de tailles WxH
# avec possibilité d'un overlap entre les images
# et qui produit aussi les fichiers texte associés indiquant les coordonnées des boites de texte


from shapely.geometry import Polygon, shape
from shapely.strtree import STRtree
import fiona
import rasterio
import pathlib
from rasterio.windows import Window

def translate_coords(new_x_origin, new_y_origin, coords):
    return [[c[0] - new_x_origin, c[1] - new_y_origin] for c in coords]

W, H = 256, 256 # 1280, 720 # taille de l'imagette à découper
OVERLAP = 0 # 1/3 # recouvrement entre imagettes
INTERSECTING_RATIO = 0.05 # pourcentage minimale d'intersection d'une boite de texte avec l'image pour prise en compte

PREFIX = '' #'r4_r10' #'r1_r3'
tiff_file = '../../data/raw/cassini_bnf_52.tif'
text_boxes = '../../data/raw/merged_partially_corrected3.geojson'
output_img_path = f'../../data/train_img'
output_label_path = f'../../data/train_gt'

boxes = fiona.open(text_boxes, 'r')
boxes = [b for b in boxes if b is not None]
box_geoms = [shape(b['geometry']) for b in boxes]
index_by_id = dict((id(poly), i) for i, poly in enumerate(box_geoms))

tree = STRtree(box_geoms)

dataset = rasterio.open(tiff_file)
width, height = dataset.width, dataset.height

print(width, height)


c = 0
for x in range(0, width, int(W * (1 - OVERLAP))):
    r = 0
    for y in range(0, height, int(H * (1 - OVERLAP))):
        left = width - W if (width - x) < W else x
        top = height - H if (height - y) < H else y
        right, bottom = left + W, top + H
        lt_l93, rt_l93 = dataset.transform * (left, top), dataset.transform * (right, top)
        lb_l93, rb_l93 = dataset.transform * (left, bottom), dataset.transform * (right, bottom)
        #tile = Polygon([[left, top], [right, top], [right, bottom], [left ,bottom], [left, top]])
        tile_georef = Polygon([[lt_l93[0], lt_l93[1]], [rt_l93[0], rt_l93[1]], [rb_l93[0], rb_l93[1]], [lb_l93[0], lb_l93[1]], [lt_l93[0], lt_l93[1]]])
        text_boxes = tree.query(tile_georef)
        ids = []
        big_enough = []
        for b in text_boxes:
            inters = b.intersection(tile_georef)
            ratio = inters.area / b.area
            if ratio >= INTERSECTING_RATIO:
                ids.append(index_by_id[id(b)])
                big_enough.append(inters)

        print(r, c, tile_georef, len(big_enough))
        root_name = f'{PREFIX}_{r}_{c}' if PREFIX != '' else f'{r}_{c}'
        # write tif (not georeferenced)
        w = dataset.read(window=Window(left, top, W, H))
        with rasterio.open(f'{output_img_path}/{root_name}.tif', 'w', driver='GTiff', width=W, height=H, count=4, dtype=w.dtype) as dst:
            dst.write(w)

        # write label in icdar format : bottom_left, bottom_right, top_right, top_left
        label_filename = f'{output_label_path}/gt_{root_name}.txt'
        txt = []
        for i, b in enumerate(big_enough): 
            label = boxes[ids[i]]['properties']['label']
            # bounds => (minx, miny, maxx, maxy)
            bl, br, tr, tl = (b.bounds[0], b.bounds[3]), (b.bounds[2], b.bounds[3]), (b.bounds[2], b.bounds[1]), (b.bounds[0], b.bounds[1])
            coords = [dataset.index(*corner) for corner in (bl, br, tr, tl)]
            coords = [(c[1], c[0]) for c in coords] # dataset.index returns row and column we have to invert
            coords = translate_coords(left, top, coords)
            s = f'{coords[3][0]},{coords[3][1]},{coords[2][0]},{coords[2][1]},{coords[1][0]},{coords[1][1]},{coords[0][0]},{coords[0][1]},{label}'
            txt.append(s)
            #print(s)
        with open(label_filename,'w') as f:
            f.write('\n'.join(txt))
        print("------------------------------------------")
        r += 1
    c += 1

# nb_img = r * c
# print(nb_img, len(boxes))
# print(f'POINT{dataset.xy(0, 8000)}')
# print(dataset.index(759739.676905012, 6499340.673632674))
# print(dataset.profile)
