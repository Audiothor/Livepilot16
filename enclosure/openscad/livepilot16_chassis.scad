// ============================================================================
// LivePilot 16 — Modélisation Paramétrique du Châssis Incliné à 15°
// Logiciel : OpenSCAD (100% Gratuit & Open-Source)
// Slogan   : "Ne regardez plus l'écran, pilotez votre son."
// ============================================================================

$fn = 60;

// Dimensions générales du contrôleur (en mm)
box_width       = 280.0; // Largeur pour loger 8 colonnes + cluster navigation
box_depth       = 210.0; // Profondeur
height_front    = 25.0;  // Hauteur avant
tilt_angle      = 15.0;  // Inclinaison scénique en degrés
wall_thickness  = 3.0;   // Épaisseur des parois

// Découpes Double Écran TFT 3.5" (2x 480x320) - Vue Mix & Vue Plugins
screen_w        = 83.0;  // Fenêtre active LCD 3.5"
screen_h        = 55.0;
screen_gap      = 8.0;   // Séparation fine entre les 2 écrans
screen_total_w  = (2 * screen_w) + screen_gap; // 174 mm
screen_left_x   = (box_width - screen_total_w) / 2;
screen_right_x  = screen_left_x + screen_w + screen_gap;
screen_pos_y    = 135.0;

// Espacement des 16 Encodeurs Rotatifs (2 rangées de 8)
enc_rows        = 2;
enc_cols        = 8;
enc_spacing_x   = 26.0;
enc_spacing_y   = 28.0;
enc_hole_dia    = 7.2;   // Trou pour axe fileté Bourns PEC11R (M7)
enc_origin_x    = (box_width - ((enc_cols - 1) * enc_spacing_x)) / 2;
enc_origin_y    = 85.0;

// Matrice des 16 Boutons de Pistes RGB (2 rangées de 8)
btn_rows        = 2;
btn_cols        = 8;
btn_size        = 15.2;  // Pour cabochons silicone 15x15mm
btn_spacing_x   = 24.0;
btn_spacing_y   = 22.0;
btn_origin_x    = 25.0;
btn_origin_y    = 22.0;

// Cluster des 6 Boutons de Navigation (3 rangées de 2 à droite : TRACK -/+, GROUP -/+, DEVICE -/+)
nav_rows        = 3;
nav_cols        = 2;
nav_size        = 11.0;  // Switches navigation 11x11mm
nav_spacing_x   = 18.0;
nav_spacing_y   = 16.0;
nav_origin_x    = 232.0;
nav_origin_y    = 18.0;

module livepilot_base() {
    echo("Génération du châssis LivePilot 16 (Double Écran 3.5\", 2x8 encodeurs, 2x8 boutons, 3x2 nav)...");
    difference() {
        // Coque extérieure inclinée
        cube([box_width, box_depth, height_front + box_depth * tan(tilt_angle)]);
        
        // Évidement intérieur
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([box_width - 2*wall_thickness, box_depth - 2*wall_thickness, 70]);
            
        // Découpe Écran Gauche (Vue Mix & Session)
        translate([screen_left_x, screen_pos_y, 0])
            cube([screen_w, screen_h, 80]);

        // Découpe Écran Droit (Vue Plugins & Paramètres)
        translate([screen_right_x, screen_pos_y, 0])
            cube([screen_w, screen_h, 80]);

        // Perçages 16 Encodeurs (2 rangées de 8)
        for (r = [0 : enc_rows - 1]) {
            for (c = [0 : enc_cols - 1]) {
                translate([enc_origin_x + c * enc_spacing_x, enc_origin_y + r * enc_spacing_y, 0])
                    cylinder(h = 80, d = enc_hole_dia);
            }
        }

        // Découpes 16 Boutons Pistes RGB (2 rangées de 8)
        for (r = [0 : btn_rows - 1]) {
            for (c = [0 : btn_cols - 1]) {
                translate([btn_origin_x + c * btn_spacing_x - btn_size/2, btn_origin_y + r * btn_spacing_y - btn_size/2, 0])
                    cube([btn_size, btn_size, 80]);
            }
        }

        // Découpes 6 Boutons Navigation (TRACK -/+, GROUP -/+, DEVICE -/+)
        for (r = [0 : nav_rows - 1]) {
            for (c = [0 : nav_cols - 1]) {
                translate([nav_origin_x + c * nav_spacing_x - nav_size/2, nav_origin_y + r * nav_spacing_y - nav_size/2, 0])
                    cube([nav_size, nav_size, 80]);
            }
        }
    }
}

// Aperçu dans OpenSCAD
livepilot_base();
