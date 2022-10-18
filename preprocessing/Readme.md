Ensemble des petits scripts qui servent à générer les données à partir de l'extrait au format "tif" et des geopackages des points des toponymes et chefs-lieux fournis par Julien.
* gpkg_to_boxes.py => génére l'ensemble des coordonnées approximatives des boîtes de texte à partir des geopackages de Julien, pour les toponymes et chefs-lieux
* merge_jsons.py => merge les geojsons de boies de texte qui ont la même structure ((id, label) en gros)
* cassini_to_icdar.py => crée les imagettes et boites de texte associées au bon format pour le modèle à partir d'une grosse image tif et d'un geojson référencant les boites de texte
* eval_results => evalue sommairement les sorties du modèle à partir d'un jeu de test

_tiles_ et _cassini\_ref_ contiennent les imagettes d'évaluation et les coordonnées des boites de texte associées.

Dépendances principales :
* Fiona           1.8.18
* rasterio        1.1.8
* Shapely         1.7.1

