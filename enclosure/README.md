# LivePilot 16 — Modélisation 3D & Châssis Scénique

Ce dossier regroupe tous les fichiers de modélisation mécanique pour l'impression 3D du boîtier **LivePilot 16**.

## 1. Organisation du Répertoire
* `openscad/` : Scripts de conception paramétrique en code OpenSCAD (`livepilot16_chassis.scad`).
* `stl/` : Fichiers STL exportés prêts pour le trancheur (Bambu Studio, PrusaSlicer, OrcaSlicer).
* `step/` : Fichiers STEP pour l'import dans FreeCAD ou Fusion 360 si modifications manuelles souhaitées.

## 2. Spécifications Mécaniques du Boîtier
* **Angle d'inclinaison** : 15° (ergonomie optimale pour jeu debout sur table ou assis en studio).
* **Façade supérieure** : Démontable, fixée par 6 vis M3 tête fraisée noire sur inserts laiton M3 thermo-insérés.
* **Accès arrière** : Découpe ajustée pour embase USB-C avec dégagement pour connecteur de câble blindé.
* **Pieds** : 4 empreintes circulaires sous le châssis pour patins antidérapants silicone 3M Bumpon.
* **Matériau recommandé** : PETG mat noir ou PLA-CF (fibre de carbone) pour la rigidité et la tenue aux projecteurs de scène.
