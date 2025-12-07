import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuration de la page
st.set_page_config(page_title="Champagne Battle", page_icon="🥂", layout="centered")

# --- CONSTANTES & SETUP ---
FILE_NOTES = "notes_v4.csv"
FILE_CHAMPAGNES = "liste_champagnes.csv"
DIR_PHOTOS = "photos_bouteilles" # Dossier pour stocker les images
ADMIN_PASSWORD = "admin"

# Création du dossier photo s'il n'existe pas
if not os.path.exists(DIR_PHOTOS):
    os.makedirs(DIR_PHOTOS)

# Listes d'arômes
AROMES_NEZ = {
    "🍋 Agrumes": "Citron, Pamplemousse, Clémentine",
    "🍏 Fruits Blancs": "Pomme verte, Poire, Pêche",
    "🍑 Fruits Jaunes": "Abricot, Mirabelle",
    "🍍 Exotique": "Ananas, Mangue, Passion",
    "🍓 Fruits Rouges": "Fraise, Framboise, Cerise",
    "🌸 Floral": "Fleurs blanches, Acacia, Rose",
    "🌿 Végétal": "Herbe, Menthe, Fougère",
    "🌰 Fruits Secs": "Noisette, Amande, Figue",
    "🍞 Boulangerie": "Brioche, Toast, Levure",
    "🧈 Pâtisserie": "Beurre, Crème, Biscuit",
    "🍯 Miel/Cire": "Miel, Cire, Pain d'épices",
    "🪵 Boisé": "Vanille, Chêne, Fumé",
    "🔥 Torréfié": "Café, Cacao, Grillé"
}

AROMES_BOUCHE = {
    "⚡ Vif": "Tranchant, Nerveux, Citronné",
    "☁️ Rond": "Ample, Velouté, Gras",
    "🫧 Bulles Fines": "Élégant, Crémeux",
    "💥 Bulles Fortes": "Pétillant, Agressif",
    "🍬 Sucré": "Dosé, Gourmand",
    "💎 Minéral": "Salin, Craie, Iode",
    "🍂 Oxydatif": "Pomme blette, Noix, Mature",
    "⏱️ Long": "Persistant, Interminable"
}

# --- FONCTIONS ---
def load_data(file, columns):
    if not os.path.exists(file):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(file)

def save_data(df, file):
    df.to_csv(file, index=False)

# --- INTERFACE ---

st.title("🥂 Champagne Battle")

# 1. IDENTIFICATION SIMPLE
user_name = st.text_input("👤 Ton Prénom (pour noter)", placeholder="Ex: Julien")

# Bouton d'actualisation simple
if st.button("🔄 Actualiser les graphiques", type="primary", use_container_width=True):
    st.rerun()

st.markdown("---")

# 2. SIDEBAR ADMIN
with st.sidebar:
    st.header("⚙️ Admin")
    admin_pwd = st.text_input("Mot de passe", type="password")
    is_admin = (admin_pwd == ADMIN_PASSWORD)
    
    if is_admin:
        st.success("Mode Admin activé")
        st.markdown("### Ajouter un vin")
        new_champ = st.text_input("Nom du Champagne")
        if st.button("Ajouter"):
            df_champs = load_data(FILE_CHAMPAGNES, ["Nom"])
            if new_champ and new_champ not in df_champs["Nom"].values:
                new_row = pd.DataFrame({"Nom": [new_champ]})
                df_champs = pd.concat([df_champs, new_row], ignore_index=True)
                save_data(df_champs, FILE_CHAMPAGNES)
                st.success(f"{new_champ} ajouté !")
                st.rerun()

# Chargement des données
df_notes = load_data(FILE_NOTES, ["User", "Champagne", "Acidite", "Bulles", "Nez", "Bouche", "Finale", "Tags_Nez", "Tags_Bouche"])
df_champs = load_data(FILE_CHAMPAGNES, ["Nom"])

if df_champs.empty:
    df_champs = pd.DataFrame({"Nom": ["Exemple: Ruinart Blanc de Blancs"]})
    save_data(df_champs, FILE_CHAMPAGNES)

# 3. LISTE DES VINS
st.subheader("🍾 La Carte des Vins")

# On itère sur les champagnes
# Note: On utilise une liste pour pouvoir supprimer sans casser la boucle
champagnes_to_display = df_champs["Nom"].unique().tolist()

for champ in champagnes_to_display:
    with st.expander(f"🥂 {champ}", expanded=False):
        
        # --- A. HEADER DU VIN (PHOTO + SUPPRESSION) ---
        c_info, c_del = st.columns([5, 1])
        
        # Gestion Photo
        photo_path = os.path.join(DIR_PHOTOS, f"{champ}.png")
        if os.path.exists(photo_path):
            with c_info:
                st.image(photo_path, width=150)
        else:
            with c_info:
                # N'importe qui peut ajouter la photo s'il n'y en a pas (plus convivial), 
                # ou restreindre à "if is_admin:" si tu préfères.
                uploaded_photo = st.file_uploader(f"Ajouter une photo pour {champ}", type=['png', 'jpg', 'jpeg'], key=f"upl_{champ}")
                if uploaded_photo is not None:
                    with open(photo_path, "wb") as f:
                        f.write(uploaded_photo.getbuffer())
                    st.rerun()

        # Bouton Suppression (Admin Only)
        if is_admin:
            with c_del:
                # On utilise un popover ou une session state pour confirmer
                if st.button("❌", help="Supprimer ce vin", key=f"del_btn_{champ}"):
                    st.session_state[f"confirm_del_{champ}"] = True
                
                if st.session_state.get(f"confirm_del_{champ}"):
                    st.warning("Sûr ?")
                    if st.button("Oui, supprimer", key=f"conf_del_{champ}"):
                        # Suppression du vin
                        df_champs = df_champs[df_champs["Nom"] != champ]
                        save_data(df_champs, FILE_CHAMPAGNES)
                        # Suppression des notes associées (optionnel, mais plus propre)
                        df_notes = df_notes[df_notes["Champagne"] != champ]
                        save_data(df_notes, FILE_NOTES)
                        # Suppression photo
                        if os.path.exists(photo_path):
                            os.remove(photo_path)
                        st.rerun()

        # --- B. VISUALISATION ---
        df_this_champ = df_notes[df_notes["Champagne"] == champ]
        
        if not df_this_champ.empty:
            cols_score = ["Acidite", "Bulles", "Nez", "Bouche", "Finale"]
            categories = cols_score
            fig = go.Figure()

            # 1. Les 5 premiers dégustateurs (Traits ÉPAISSIS)
            colors = ['#FF4D4D', '#4DFF4D', '#4D4DFF', '#FFFF4D', '#FF4DFF']
            for i, (idx, row) in enumerate(df_this_champ.head(5).iterrows()):
                fig.add_trace(go.Scatterpolar(
                    r=row[cols_score],
                    theta=categories,
                    fill=None, # Pas de remplissage
                    name=str(row['User']),
                    line=dict(color=colors[i % len(colors)], width=3), # Trait plus épais (3)
                    opacity=0.6,
                    showlegend=True
                ))

            # 2. La Moyenne (Juste le contour, PAS de surface colorée)
            avg_scores = df_this_champ[cols_score].mean().tolist()
            fig.add_trace(go.Scatterpolar(
                r=avg_scores,
                theta=categories,
                fill=None, # ON ENLÈVE L'AIR (Surface colorée)
                name='Moyenne Globale',
                line=dict(color='gold', width=5), # Trait très épais (5)
                opacity=1
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                margin=dict(l=40, r=40, t=20, b=20),
                height=350,
                legend=dict(orientation="h", y=-0.2)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Nuage de mots (Tags)
            all_tags = []
            if "Tags_Nez" in df_this_champ.columns:
                all_tags += [tag.strip() for tags in df_this_champ["Tags_Nez"].dropna() for tag in tags.split(",")]
            if "Tags_Bouche" in df_this_champ.columns:
                all_tags += [tag.strip() for tags in df_this_champ["Tags_Bouche"].dropna() for tag in tags.split(",")]
            
            if all_tags:
                from collections import Counter
                counts = Counter(all_tags)
                st.markdown("**🏷️ Ce qu'on en dit :**")
                tags_html = ""
                for tag, count in counts.most_common(6):
                    tags_html += f"<span style='background-color:#262730; border:1px solid #4B4B4B; color:white; padding:4px 8px; border-radius:10px; margin-right:5px; font-size:0.8em'>{tag} ({count})</span>"
                st.markdown(tags_html, unsafe_allow_html=True)
                st.write("")

        else:
            st.info("Aucune note pour le moment.")

        # --- C. FORMULAIRE DE NOTATION ---
        st.markdown("#### 📝 Ma Note")
        
        if not user_name:
            st.warning("⚠️ Rentre ton prénom en haut pour noter.")
        else:
            with st.form(key=f"form_{champ}"):
                c1, c2 = st.columns(2)
                with c1:
                    score_acidite = st.slider("Acidité", 0, 10, 5, key=f"ac_{champ}")
                    score_bulles = st.slider("Bulles", 0, 10, 5, key=f"bu_{champ}")
                    score_nez = st.slider("Nez", 0, 10, 5, key=f"ne_{champ}")
                with c2:
                    score_bouche = st.slider("Bouche", 0, 10, 5, key=f"bo_{champ}")
                    score_finale = st.slider("Finale", 0, 10, 5, key=f"fi_{champ}")
                
                with st.expander("Détails (Arômes) - Optionnel"):
                    tags_nez = st.multiselect("Au Nez", list(AROMES_NEZ.keys()), key=f"tn_{champ}")
                    tags_bouche = st.multiselect("En Bouche", list(AROMES_BOUCHE.keys()), key=f"tb_{champ}")
                
                submitted = st.form_submit_button("Envoyer 🚀", use_container_width=True)
                
                if submitted:
                    new_entry = {
                        "User": user_name,
                        "Champagne": champ,
                        "Acidite": score_acidite,
                        "Bulles": score_bulles,
                        "Nez": score_nez,
                        "Bouche": score_bouche,
                        "Finale": score_finale,
                        "Tags_Nez": ",".join(tags_nez),
                        "Tags_Bouche": ",".join(tags_bouche)
                    }
                    
                    df_current = load_data(FILE_NOTES, list(new_entry.keys()))
                    df_current = df_current[~((df_current["User"] == user_name) & (df_current["Champagne"] == champ))]
                    df_new = pd.DataFrame([new_entry])
                    df_final = pd.concat([df_current, df_new], ignore_index=True)
                    save_data(df_final, FILE_NOTES)
                    
                    st.success("Noté !")
                    st.rerun()
