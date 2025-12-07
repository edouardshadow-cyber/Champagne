import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuration de la page
st.set_page_config(page_title="Champagne Battle", page_icon="🥂", layout="centered")

# --- CONSTANTES ---
FILE_NOTES = "notes_v5.csv" # Changement de version pour la nouvelle colonne commentaire
FILE_CHAMPAGNES = "liste_champagnes.csv"
DIR_PHOTOS = "photos_bouteilles"
ADMIN_PASSWORD = "admin"

# Création dossier photo
if not os.path.exists(DIR_PHOTOS):
    os.makedirs(DIR_PHOTOS)

# Listes d'arômes
AROMES_NEZ = {
    "🍋 Agrumes": "Citron, Pamplemousse",
    "🍏 Fruits Blancs": "Pomme, Poire, Pêche",
    "🍑 Fruits Jaunes": "Abricot, Mirabelle",
    "🍍 Exotique": "Ananas, Mangue",
    "🍓 Fruits Rouges": "Fraise, Framboise",
    "🌸 Floral": "Fleurs blanches, Acacia",
    "🌿 Végétal": "Herbe, Menthe",
    "🍞 Brioche": "Toast, Levure, Beurre",
    "🍯 Miel": "Miel, Cire",
    "🪵 Boisé": "Vanille, Chêne"
}

AROMES_BOUCHE = {
    "⚡ Vif": "Tranchant, Nerveux",
    "☁️ Rond": "Ample, Velouté",
    "🍬 Sucré": "Gourmand, Dosé",
    "💎 Minéral": "Salin, Craie",
    "🍂 Oxydatif": "Pomme blette, Noix",
    "⏱️ Long": "Persistant"
}

# --- FONCTIONS ---
def load_data(file, columns):
    if not os.path.exists(file):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(file)

def save_data(df, file):
    df.to_csv(file, index=False)

# Fonction pour fermer la boucle du graphique (ajouter le 1er point à la fin)
def close_loop(values):
    return values + [values[0]]

# --- GESTION SESSION (Admin) ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

@st.dialog("🔐 Mode Administrateur")
def open_admin_login():
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Valider"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.rerun()
        else:
            st.error("Mauvais mot de passe")

# --- INTERFACE ---

# En-tête avec bouton admin aligné
col_titre, col_admin = st.columns([6, 1])
with col_titre:
    st.title("🥂 Champagne Battle")
with col_admin:
    st.write("") 
    st.write("") # Petits espaces pour aligner verticalement
    if st.button("⚙️"):
        open_admin_login()

# Identification User
user_name = st.text_input("👤 Ton Prénom", placeholder="Ex: Camille")
if st.button("🔄 Actualiser les graphiques", type="primary", use_container_width=True):
    st.rerun()

# Zone Admin (visible seulement si connecté)
if st.session_state.is_admin:
    st.info("🔓 Mode Admin Actif")
    with st.expander("Ajouter un Champagne"):
        new_champ = st.text_input("Nom du vin")
        if st.button("Ajouter à la liste"):
            df_champs = load_data(FILE_CHAMPAGNES, ["Nom"])
            if new_champ and new_champ not in df_champs["Nom"].values:
                new_row = pd.DataFrame({"Nom": [new_champ]})
                df_champs = pd.concat([df_champs, new_row], ignore_index=True)
                save_data(df_champs, FILE_CHAMPAGNES)
                st.success("Ajouté !")
                st.rerun()

st.markdown("---")

# CHARGEMENT DATA
# On ajoute la colonne "Commentaire"
df_notes = load_data(FILE_NOTES, ["User", "Champagne", "Acidite", "Bulles", "Nez", "Bouche", "Finale", "Tags_Nez", "Tags_Bouche", "Commentaire"])
df_champs = load_data(FILE_CHAMPAGNES, ["Nom"])

if df_champs.empty:
    df_champs = pd.DataFrame({"Nom": ["Exemple: Ruinart"]})
    save_data(df_champs, FILE_CHAMPAGNES)

# LISTE DES VINS
champagnes_list = df_champs["Nom"].unique().tolist()

for champ in champagnes_list:
    with st.expander(f"🥂 {champ}", expanded=False):
        
        # --- A. PHOTO & SUPPRESSION ---
        c_photo, c_info = st.columns([1, 2])
        photo_path = os.path.join(DIR_PHOTOS, f"{champ}.png")
        
        with c_photo:
            if os.path.exists(photo_path):
                st.image(photo_path)
                # Bouton suppression photo accessible à tous
                if st.button("🗑️ Photo", key=f"del_img_{champ}", help="Supprimer la photo"):
                    os.remove(photo_path)
                    st.rerun()
            else:
                uploaded = st.file_uploader("Ajouter photo", type=['png', 'jpg'], key=f"upl_{champ}", label_visibility="collapsed")
                if uploaded:
                    with open(photo_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    st.rerun()
        
        # Bouton suppression Vin (Admin seulement)
        if st.session_state.is_admin:
            with c_info:
                st.write("Gestion Admin:")
                if st.button("❌ Supprimer ce vin", key=f"del_vin_{champ}"):
                    # Suppression simple sans double confirm pour aller vite (ou ajouter logique confirm si besoin)
                    df_champs = df_champs[df_champs["Nom"] != champ]
                    save_data(df_champs, FILE_CHAMPAGNES)
                    st.rerun()

        # --- B. GRAPHIQUE ---
        df_this = df_notes[df_notes["Champagne"] == champ]
        
        if not df_this.empty:
            cols = ["Acidite", "Bulles", "Nez", "Bouche", "Finale"]
            cats = cols + [cols[0]] # On ferme la catégorie aussi
            
            fig = go.Figure()

            # 1. Notes individuelles (Gris 8%)
            colors_line = ['#FF4D4D', '#4DFF4D', '#4D4DFF', '#FFFF4D', '#FF4DFF']
            for i, (idx, row) in enumerate(df_this.head(5).iterrows()):
                vals = close_loop(row[cols].tolist())
                fig.add_trace(go.Scatterpolar(
                    r=vals, theta=cats,
                    fill='toself',
                    fillcolor='rgba(128, 128, 128, 0.08)', # GRIS 8%
                    name=str(row['User']),
                    line=dict(color=colors_line[i % len(colors_line)], width=2),
                    opacity=1
                ))

            # 2. Moyenne (Gris 12% + Or)
            avg = close_loop(df_this[cols].mean().tolist())
            fig.add_trace(go.Scatterpolar(
                r=avg, theta=cats,
                fill='toself',
                fillcolor='rgba(128, 128, 128, 0.12)', # GRIS 12%
                name='Moyenne',
                line=dict(color='gold', width=4),
                opacity=1
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                margin=dict(l=30, r=30, t=20, b=20),
                height=300,
                legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Affichage des commentaires perso des autres
            comments = df_this["Commentaire"].dropna().unique()
            if len(comments) > 0:
                st.markdown("**💬 Avis des potes :**")
                for c in comments:
                    if len(str(c)) > 1: # On affiche pas les trucs vides
                        st.caption(f"• {c}")

        else:
            st.info("Pas encore de notes.")

        # --- C. FORMULAIRE ---
        st.markdown("#### 📝 Ma Note")
        if user_name:
            with st.form(key=f"f_{champ}"):
                c1, c2 = st.columns(2)
                with c1:
                    s_ac = st.slider("Acidité", 0, 10, 5, key=f"ac{champ}")
                    s_bu = st.slider("Bulles", 0, 10, 5, key=f"bu{champ}")
                    s_ne = st.slider("Nez", 0, 10, 5, key=f"ne{champ}")
                with c2:
                    s_bo = st.slider("Bouche", 0, 10, 5, key=f"bo{champ}")
                    s_fi = st.slider("Finale", 0, 10, 5, key=f"fi{champ}")
                
                # Case Commentaires libres
                user_comment = st.text_area("Mes idées / Commentaires libres", placeholder="Ex: Superbe avec le fromage...")

                with st.expander("Tags (Optionnel)"):
                    t_nez = st.multiselect("Nez", list(AROMES_NEZ.keys()), key=f"tn{champ}")
                    t_bou = st.multiselect("Bouche", list(AROMES_BOUCHE.keys()), key=f"tb{champ}")
                
                if st.form_submit_button("Envoyer 🚀", use_container_width=True):
                    new_entry = {
                        "User": user_name,
                        "Champagne": champ,
                        "Acidite": s_ac, "Bulles": s_bu, "Nez": s_ne, "Bouche": s_bo, "Finale": s_fi,
                        "Tags_Nez": ",".join(t_nez),
                        "Tags_Bouche": ",".join(t_bou),
                        "Commentaire": user_comment
                    }
                    # Update
                    df_cur = load_data(FILE_NOTES, list(new_entry.keys()))
                    df_cur = df_cur[~((df_cur["User"] == user_name) & (df_cur["Champagne"] == champ))]
                    df_final = pd.concat([df_cur, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(df_final, FILE_NOTES)
                    st.success("Noté !")
                    st.rerun()
        else:
            st.warning("Prénom requis en haut !")
