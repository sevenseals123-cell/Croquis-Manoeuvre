import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# Configuration de la page
st.set_page_config(page_title="SAD & Manœuvres - NWM", layout="wide")

st.title("⚓ Simulateur de Manœuvre & Croquis - Nador West Med")
st.markdown("Interface d'aide à la décision et de préparation à l'agrément de pilotage.")

# --- BARRE LATÉRALE (PARAMÈTRES) ---
st.sidebar.header("⚙️ Paramètres du Navire")
vessel_type = st.sidebar.selectbox(
    "Type de Navire", 
    ["ULCV (Terminal TCE)", "Pétrolier 170k DWT (Poste PP3)", "Navire Roulier (TRV)"]
)
tea = st.sidebar.number_input("Tirant d'eau (m)", min_value=5.0, max_value=18.5, value=16.5)

st.sidebar.header("🌪️ Environnement")
wind_dir = st.sidebar.slider("Provenance Vent (°)", 0, 360, 60) # 60° = ENE dominant
wind_speed = st.sidebar.slider("Vitesse Vent (Noeuds)", 0, 40, 15)

st.sidebar.header("✏️ Outils de Dessin")
drawing_mode = st.sidebar.selectbox(
    "Mode de tracé", 
    ("freedraw", "line", "rect", "circle", "transform")
)
stroke_width = st.sidebar.slider("Épaisseur du trait", 1, 10, 3)
stroke_color = st.sidebar.color_picker("Couleur du trait", "#FF0000") # Rouge par défaut pour la route fond

# --- ZONE DE DESSIN ---
st.subheader("Plan d'eau et Tracé de la Manœuvre")
st.write("Utilisez les outils pour tracer la cinématique, le cercle d'évitage et la position des remorqueurs Damen.")

# Chargement de l'image de fond (Plan du port)
# Assurez-vous d'avoir une image nommée "plan_nwm.png" dans le même dossier
try:
    bg_image = Image.open("plan_nwm.png")
    bg_width, bg_height = bg_image.size
except FileNotFoundError:
    st.warning("⚠️ L'image du plan 'plan_nwm.png' est introuvable. Affichage d'un fond vierge.")
    bg_image = None
    bg_width, bg_height = 800, 600 # Dimensions par défaut

# Création du Canvas interactif
canvas_result = st_canvas(
    fill_color="rgba(0, 150, 255, 0.3)",  # Couleur de remplissage pour les formes (ex: cercle d'évitage)
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_image=bg_image,
    update_streamlit=True,
    height=600,
    width=bg_width if bg_image else 800,
    drawing_mode=drawing_mode,
    key="canvas",
)

# --- ANALYSE DES DONNÉES (Pour la partie Décision) ---
if canvas_result.json_data is not None:
    objects = canvas_result.json_data["objects"]
    if len(objects) > 0:
        st.success(f"✅ Tracé actif : {len(objects)} élément(s) dessiné(s).")
        # Vous pourrez ajouter ici du code pour calculer des distances d'arrêt 
        # ou l'évolution du pivot point en fonction de ce qui est dessiné.
