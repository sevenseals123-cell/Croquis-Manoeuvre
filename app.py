import streamlit as st
import math
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="SAD Pilotage NWM", layout="wide", initial_sidebar_state="expanded")

# --- DONNÉES TECHNIQUES (Tirées du Pilot Handbook) ---
# Capacité de la flotte de remorquage de NWM
TUG_BOLLARD_PULL = 80  # Tonnes (Damen ASD Tug 2813)
TOTAL_TUGS_AVAILABLE = 4

# Base de données simplifiée des navires types pour NWM
VESSEL_DATABASE = {
    "ULCV (Terminal TCE)": {"LOA": 399, "beam": 59, "draft": 16.0, "windage_lateral": 14000},
    "Pétrolier Suezmax (Poste PP3)": {"LOA": 275, "beam": 48, "draft": 16.5, "windage_lateral": 4500}, # Chargé
    "Navire Roulier (TRV)": {"LOA": 200, "beam": 32, "draft": 8.5, "windage_lateral": 8000}
}

# --- EN-TÊTE ---
st.title("⚓ Système d'Aide à la Décision & Manœuvres - Nador West Med")
st.markdown("Interface de préparation pour l'agrément de pilotage : Calculs hydro-météorologiques et tracés cinématiques.")

# --- BARRE LATÉRALE : OUTILS DE DESSIN ---
st.sidebar.header("✏️ Outils de Tracé")
drawing_mode = st.sidebar.selectbox("Mode", ("freedraw", "line", "rect", "circle", "transform"))
stroke_width = st.sidebar.slider("Épaisseur du trait", 1, 10, 3)
stroke_color = st.sidebar.color_picker("Couleur du trait (Navire/Route)", "#FF0000") # Rouge par défaut
tug_color = st.sidebar.color_picker("Couleur (Remorqueurs)", "#0000FF") # Bleu par défaut

# --- INTERFACE PRINCIPALE : DEUX COLONNES ---
col_calc, col_canvas = st.columns([1, 2.5]) # La carte prendra plus de place

with col_calc:
    st.header("⚙️ Paramètres & Calculs")
    
    # 1. Choix du Navire
    st.subheader("1. Navire")
    vessel_choice = st.selectbox("Type de navire", list(VESSEL_DATABASE.keys()))
    v_data = VESSEL_DATABASE[vessel_choice]
    st.write(f"**LOA:** {v_data['LOA']}m | **Largeur:** {v_data['beam']}m | **Surface Fardagée (Lat):** {v_data['windage_lateral']} m²")
    
    # 2. Conditions Environnementales
    st.subheader("2. Environnement")
    wind_speed = st.number_input("Vitesse du vent (Nœuds)", min_value=0, max_value=60, value=15)
    wind_angle = st.slider("Angle d'impact du vent sur la coque (°)", min_value=0, max_value=90, value=90, 
                           help="0° = vent de bout, 90° = vent de travers plein (impact maximum)")
    
    # 3. Moteur de Calcul (Règle de base du pilotage pour la force du vent)
    # Formule : Force (Tonnes) = (Vitesse_Noeuds^2 / 18) * (Surface / 1000) * Sin(Angle)
    force_vent_t = (wind_speed**2 / 18) * (v_data["windage_lateral"] / 1000) * math.sin(math.radians(wind_angle))
    
    st.markdown("---")
    st.subheader("📊 Résultats SAD")
    st.metric(label="Force Latérale du vent (Poussée)", value=f"{force_vent_t:.1f} Tonnes")
    
    # Calcul des remorqueurs nécessaires
    # On ajoute une marge de sécurité de 20% pour le Bollard Pull requis
    required_bp = force_vent_t * 1.2
    tugs_needed = math.ceil(required_bp / TUG_BOLLARD_PULL)
    
    if tugs_needed > TOTAL_TUGS_AVAILABLE:
        st.error(f"⚠️ DANGER : {tugs_needed} remorqueurs requis. La flotte de NWM (4 remorqueurs) est insuffisante pour ces conditions.")
    else:
        st.success(f"✅ SÉCURITÉ : {tugs_needed} remorqueur(s) Damen ASD requis pour contrer la dérive (incluant 20% de marge).")


with col_canvas:
    st.header("🗺️ Tableau d'Évolution")
    
    # Gestion de l'image de fond
    try:
        bg_image = Image.open("assets/plan_nwm.png")
        bg_width, bg_height = bg_image.size
        # Redimensionnement pour s'adapter à l'écran sans perdre les proportions
        ratio = 800 / bg_width
        new_width = int(bg_width * ratio)
        new_height = int(bg_height * ratio)
        bg_image = bg_image.resize((new_width, new_height))
    except FileNotFoundError:
        st.warning("⚠️ L'image 'assets/plan_nwm.png' est introuvable. Affichage d'un fond bleu marin de secours.")
        bg_image = None
        new_width, new_height = 800, 600

    # Zone de dessin interactive
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Remplissage orange transparent pour les zones d'évitage
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#0a192f" if not bg_image else "", # Couleur si pas d'image
        background_image=bg_image,
        update_streamlit=True,
        height=new_height,
        width=new_width,
        drawing_mode=drawing_mode,
        key="canvas",
    )
    
    st.caption("Instructions : Sélectionnez vos outils à gauche. Utilisez le mode 'transform' pour déplacer/supprimer un tracé existant.")

# --- EXPORTATION ET RAPPORTS ---
if canvas_result.image_data is not None:
    st.markdown("---")
    st.write("💡 *Astuce pour le comité : Vous pouvez faire un clic droit sur le dessin ci-dessus pour l'enregistrer comme image et l'intégrer dans votre présentation finale.*")
