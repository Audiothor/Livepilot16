# Fichiers de Fabrication PCB Express (Gerber RS-274X)

Ce dossier contient l'ensemble des fichiers de fabrication prêts pour l'usine, ainsi que l'archive zippée prête à être glissée-déposée sur [JLCPCB.com](https://jlcpcb.com) ou [PCBWay.com](https://www.pcbway.com).

---

## 1. L'Archive Prête à l'Emploi

👉 **Fichier à téléverser sur JLCPCB** : 
[`LivePilot16_Gerber_JLCPCB.zip`](LivePilot16_Gerber_JLCPCB.zip) *(chemin complet : `hardware/gerber/LivePilot16_Gerber_JLCPCB.zip`)*

---

## 2. Comment Commander votre Circuit en 3 Clics sur JLCPCB :

1. **Rendez-vous sur [JLCPCB.com](https://jlcpcb.com)**.
2. Cliquez sur le bouton bleu **"Order Now"** ou **"Add Gerber file"**.
3. **Glissez-déposez le fichier `LivePilot16_Gerber_JLCPCB.zip`** directement dans la zone de téléversement :
   * Le visualiseur 3D de JLCPCB va s'ouvrir automatiquement et vous afficher la carte en temps réel !
4. **Vérifiez les paramètres par défaut** (ils sont déjà parfaits) :
   * **Dimensions** : Détectées automatiquement à `100 mm × 100 mm`.
   * **Layers (Couches)** : `2 Layers`.
   * **PCB Qty** : `5` (le minimum standard pour 2 $).
   * **PCB Thickness** : `1.6 mm`.
   * **PCB Color** : Noir (*Matte Black*) ou Vert selon votre préférence esthétique.
   * **Surface Finish** : `HASL (with lead)` ou `LeadFree HASL`.
5. Cliquez sur **"Save to Cart"** puis procédez au paiement (~2 $ pour 5 circuits + ~4 € de frais de port).

---

## 3. Contenu Détaillé du Fichier ZIP

Pour information technique, l'archive contient les couches standardisées au format RS-274X et perçage Excellon :

| Nom du Fichier | Rôle / Couche |
|---|---|
| `LivePilot16_Mainboard-Edge_Cuts.gbr` | Contour mécanique de la plaque (100 × 100 mm) |
| `LivePilot16_Mainboard-F_Cu.gbr` | Pistes de cuivre face avant (Bus I2C, signaux SPI et données) |
| `LivePilot16_Mainboard-B_Cu.gbr` | Pistes de cuivre face arrière (Bus d'alimentation 5V et 3.3V) |
| `LivePilot16_Mainboard-F_Mask.gbr` | Vernis épargne de soudure face avant (ouvertures des pastilles) |
| `LivePilot16_Mainboard-B_Mask.gbr` | Vernis épargne de soudure face arrière |
| `LivePilot16_Mainboard-F_Silkscreen.gbr` | Sérigraphie blanche face avant (marquage des puces U1-U5, broches et noms) |
| `LivePilot16_Mainboard-B_Silkscreen.gbr` | Sérigraphie face arrière |
| `LivePilot16_Mainboard.drl` | Fichier de perçage numérique Excellon (trous CI 0.8mm, headers 1.0mm, vis M3 3.2mm) |
