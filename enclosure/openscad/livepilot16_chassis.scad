// ============================================================================
// LivePilot 16 — Modélisation Paramétrique du Châssis Incliné à 15°
// Logiciel : OpenSCAD (100% Gratuit & Open-Source)
// Slogan   : "Ne regardez plus l'écran, pilotez votre son."
// ============================================================================

$fn = 60;

// Dimensions générales du contrôleur (en mm) — Format aéré pro pour confort de jeu
box_width       = 370.0; // Largeur élargie pour intégrer l'encodeur Master 17, [VALID] et la navigation
box_depth       = 220.0; // Profondeur
height_front    = 25.0;  // Hauteur avant
tilt_angle      = 15.0;  // Inclinaison scénique ergonomique en degrés
wall_thickness  = 3.0;   // Épaisseur des parois

// Découpes Double Écran TFT 3.5" (2x 480x320) - Vue Mix & Vue Plugins
screen_w        = 83.0;  // Fenêtre active LCD 3.5"
screen_h        = 55.0;
screen_gap      = 8.0;   // Séparation fine entre les 2 écrans
screen_total_w  = (2 * screen_w) + screen_gap; // 174 mm
screen_left_x   = 28.0;
screen_right_x  = screen_left_x + screen_w + screen_gap;
screen_pos_y    = 145.0;

// Espacement des 16 Encodeurs Rotatifs de Paramètres (2 rangées de 8)
enc_rows        = 2;
enc_cols        = 8;
enc_spacing_x   = 32.0;  // 32mm d'entraxe pour manipulation aisée sans toucher le bouton voisin
enc_spacing_y   = 32.0;
enc_hole_dia    = 7.2;   // Trou pour axe fileté Bourns PEC11R (M7)
enc_origin_x    = 32.0;
enc_origin_y    = 78.0;

// 17ᵉ ENCODEUR MASTER & BOUTON [VALID] (9ᵉ colonne, dans l'alignement des encodeurs) :
// - Rangée Haute (alignée sur Encodeurs 1-8) : 17ᵉ Encodeur Master (BPM / Jog / Paramètres)
enc17_pos       = [enc_origin_x + 8 * enc_spacing_x, enc_origin_y + enc_spacing_y]; // x = 288, y = 110
// - Rangée Basse (alignée sur Encodeurs 9-16) : Bouton Poussoir [VALID] (Validation / Sélection)
btn_valid_pos   = [enc_origin_x + 8 * enc_spacing_x, enc_origin_y];                 // x = 288, y = 78
btn_valid_size  = 14.0;

// Matrice stricte des 16 Boutons de Pistes RGB (2 rangées de 8 — STRICTEMENT 16 TOUCHES)
btn_rows        = 2;
btn_cols        = 8;
btn_size        = 16.0;  // Cabochons silicone carrés
btn_spacing_x   = 32.0;  // Aligné 1:1 avec les 8 colonnes d'encodeurs au-dessus
btn_spacing_y   = 28.0;
btn_origin_x    = 32.0;
btn_origin_y    = 18.0;

// BOUTONS DE NAVIGATION DÉDIÉS :
nav_btn_size    = 14.0;
nav_col_1_x     = 324.0;
nav_col_2_x     = 348.0;

// 1) CLUSTER SUPÉRIEUR (Niveau Plugins / Encodeurs) :
// - Rangée Supérieure : DEVICE - et DEVICE + (Navigation plugins assignés)
dev_prev_pos    = [nav_col_1_x, enc_origin_y + enc_spacing_y]; // y = 110.0
dev_next_pos    = [nav_col_2_x, enc_origin_y + enc_spacing_y]; // y = 110.0

// - Rangée Inférieure (directement sous DEVICE -/+) : Flèches ◄ et ► (Navigation écran)
nav_left_pos    = [nav_col_1_x, enc_origin_y];                 // y = 78.0
nav_right_pos   = [nav_col_2_x, enc_origin_y];                 // y = 78.0

// 2) CLUSTER INFÉRIEUR (Niveau Pads de Pistes) :
// - Rangée Haute (même niveau que Pistes 1-8) : GROUP - et GROUP +
group_prev_pos  = [nav_col_1_x, btn_origin_y + btn_spacing_y]; // y = 46.0
group_next_pos  = [nav_col_2_x, btn_origin_y + btn_spacing_y]; // y = 46.0

// - Rangée Basse (même niveau que Pistes 9-16) : TRACK - et TRACK +
track_prev_pos  = [nav_col_1_x, btn_origin_y];                 // y = 18.0
track_next_pos  = [nav_col_2_x, btn_origin_y];                 // y = 18.0

module livepilot_base() {
    echo("Génération du châssis LivePilot 16 (16 encodeurs + Enc 17 Master + [VALID] + 16 pads + Nav)...");
    difference() {
        // Coque extérieure inclinée
        cube([box_width, box_depth, height_front + box_depth * tan(tilt_angle)]);
        
        // Évidement intérieur
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([box_width - 2*wall_thickness, box_depth - 2*wall_thickness, 75]);
            
        // Découpe Écran Gauche (Vue Mix & Session)
        translate([screen_left_x, screen_pos_y, 0])
            cube([screen_w, screen_h, 85]);

        // Découpe Écran Droit (Vue Plugins & Paramètres)
        translate([screen_right_x, screen_pos_y, 0])
            cube([screen_w, screen_h, 85]);

        // Perçages des 16 Encodeurs de Paramètres (2 rangées de 8)
        for (r = [0 : enc_rows - 1]) {
            for (c = [0 : enc_cols - 1]) {
                translate([enc_origin_x + c * enc_spacing_x, enc_origin_y + r * enc_spacing_y, 0])
                    cylinder(h = 85, d = enc_hole_dia);
            }
        }

        // Perçage du 17ᵉ Encodeur Master (Jog / BPM / Menu)
        translate([enc17_pos[0], enc17_pos[1], 0])
            cylinder(h = 85, d = enc_hole_dia);

        // Découpe Bouton [VALID] (sous le 17ᵉ encodeur)
        translate([btn_valid_pos[0] - btn_valid_size/2, btn_valid_pos[1] - btn_valid_size/2, 0])
            cube([btn_valid_size, btn_valid_size, 85]);

        // Découpes des 16 Boutons de Pistes RGB (STRICTEMENT 2 rangées de 8)
        for (r = [0 : btn_rows - 1]) {
            for (c = [0 : btn_cols - 1]) {
                translate([btn_origin_x + c * btn_spacing_x - btn_size/2, btn_origin_y + r * btn_spacing_y - btn_size/2, 0])
                    cube([btn_size, btn_size, 85]);
            }
        }

        // Découpes Touches Haut Droit : DEVICE - / DEVICE + (Rangée du haut)
        translate([dev_prev_pos[0] - nav_btn_size/2, dev_prev_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);
        translate([dev_next_pos[0] - nav_btn_size/2, dev_next_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);

        // Découpes Touches Haut Droit : Flèches ◄ / ► (Rangée du dessous)
        translate([nav_left_pos[0] - nav_btn_size/2, nav_left_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);
        translate([nav_right_pos[0] - nav_btn_size/2, nav_right_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);

        // Découpes Touches Bas Droit : GROUP - / GROUP + (Niveau Pistes 1-8)
        translate([group_prev_pos[0] - nav_btn_size/2, group_prev_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);
        translate([group_next_pos[0] - nav_btn_size/2, group_next_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);

        // Découpes Touches Bas Droit : TRACK - / TRACK + (Niveau Pistes 9-16)
        translate([track_prev_pos[0] - nav_btn_size/2, track_prev_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);
        translate([track_next_pos[0] - nav_btn_size/2, track_next_pos[1] - nav_btn_size/2, 0])
            cube([nav_btn_size, nav_btn_size, 85]);

        // Gravure Laser en creux du Titre "LivePilot 16"
        translate([285.0, 185.0, height_front + 185.0 * tan(tilt_angle) - 1.0])
            linear_extrude(height = 2.0)
                text("LivePilot 16", size = 8.5, font = "Liberation Sans:style=Bold");
    }
}

// Aperçu dans OpenSCAD
livepilot_base();

