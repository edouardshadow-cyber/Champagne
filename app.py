import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuration de la page
st.set_page_config(page_title="Champagne Battle", page_icon="🥂", layout="centered")

# --- CONSTANTES ---
FILE_NOTES = "notes_v6.csv" 
FILE_CHAMPAGNES = "liste_champagnes.csv"
DIR_PHOTOS = "photos_bouteilles"
ADMIN_PASSWORD = "admin"

# Création dossier photo (Sécurité)
try:
    if not os.path.exists(DIR_PHOTOS):
        os.makedirs(DIR_PHOTOS)
except Exception as e:
    st.error(f"Erreur création dossier photo: {e}")

# Listes d'arômes de base (Suggestions)
AROMES_NEZ = {
    "🍋 Agrumes": "Citron, Pamplemousse",
    "🍏 Fruits Blancs": "Pomme, Poire",
    "🍑 Fruits Jaunes": "Abricot, Mirabelle",
    "🍓 Fruits Rouges": "Fraise, Framboise",
    "🌸 Floral": "Fleurs blanches, Acacia",
    "🍞 Brioche": "Toast, Levure, Beurre",
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

def close_loop(values):
    # Fermer la forme du graphique radar
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

# En-tête
col_titre, col_admin = st.columns([6, 1])
with col_titre:
    st.title("🥂 Champagne Battle")
with col_admin:
    st.write("") 
    st.write("") 
    if st.button("⚙️"):
        open_admin_login()

# Identification
user_name = st.text_input("👤 Ton Prénom", placeholder="Ex: Camille")
if st.button("🔄 Actualiser les résultats", type="primary", use_container_width=True):
    st.rerun()

# Zone Admin Ajout Vin
if st.session_state.is_admin:
    with st.expander("🔓 Admin: Ajouter un Champagne"):
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
df_notes = load_data(FILE_NOTES, ["User", "Champagne", "Acidite", "Bulles", "Nez", "Bouche", "Finale", "Tags_Nez", "Tags_Bouche", "Commentaire"])
df_champs = load_data(FILE_CHAMPAGNES, ["Nom"])

if df_champs.empty:
    df_champs = pd.DataFrame({"Nom": ["Exemple: Ruinart"]})
    save_data(df_champs, FILE_CHAMPAGNES)

# LISTE DES VINS
champagnes_list = df_champs["Nom"].unique().tolist()

for champ in champagnes_list:
    with st.expander(f"🥂 {champ}", expanded=False):
        
        # --- A. PHOTO ---
        c_photo, c_info = st.columns([1, 2])
        photo_path = os.path.join(DIR_PHOTOS, f"{champ}.png")
        
        with c_photo:
            if os.path.exists(photo_path):
                st.image(photo_path)
                if st.button("🗑️", key=f"del_img_{champ}"):
                    os.remove(photo_path)
                    st.rerun()
            else:
                # Upload avec gestion d'erreur basique
                uploaded = st.file_uploader("Photo", type=['png', 'jpg', 'jpeg'], key=f"upl_{champ}", label_visibility="collapsed")
                if uploaded:
                    try:
                        with open(photo_path, "wb") as f:
                            f.write(uploaded.getbuffer())
                        st.success("Photo OK")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur upload: {e}")
        
        # Admin delete vin
        if st.session_state.is_admin:
            with c_info:
                if st.button("❌ Supprimer Vin", key=f"del_vin_{champ}"):
                    df_champs = df_champs[df_champs["Nom"] != champ]
                    save_data(df_champs, FILE_CHAMPAGNES)
                    st.rerun()

        # --- B. GRAPHIQUE ---
        df_this = df_notes[df_notes["Champagne"] == champ]
        
        if not df_this.empty:
            cols = ["Acidite", "Bulles", "Nez", "Bouche", "Finale"]
            cats = cols + [cols[0]]
            
            fig = go.Figure()

            # 1. Notes individuelles (Top 5)
            colors_line = ['#FF4D4D', '#4DFF4D', '#4D4DFF', '#FFFF4D', '#FF4DFF']
            for i, (idx, row) in enumerate(df_this.head(5).iterrows()):
                vals = close_loop(row[cols].tolist())
                # Calcul moyenne perso
                moyenne_perso = row[cols].mean()
                
                fig.add_trace(go.Scatterpolar(
                    r=vals, theta=cats,
                    fill='toself',
                    fillcolor='rgba(128, 128, 128, 0.08)',
                    name=f"{row['User']} ({moyenne_perso:.1f})", # Ajout note moyenne dans légende
                    line=dict(color=colors_line[i % len(colors_line)], width=2),
                    opacity=1
                ))

            # 2. Moyenne Globale
            avg_vals = df_this[cols].mean().tolist()
            avg_global = df_this[cols].mean().mean() # Moyenne de la moyenne
            avg_vals_closed = close_loop(avg_vals)
            
            fig.add_trace(go.Scatterpolar(
                r=avg_vals_closed, theta=cats,
                fill='toself',
                fillcolor='rgba(128, 128, 128, 0.12)',
                name=f'MOYENNE ({avg_global:.1f})',
                line=dict(color='gold', width=4),
                opacity=1
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                margin=dict(l=30, r=30, t=20, b=20),
                height=300,
                legend=dict(orientation="h", y=-0.2)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # --- C. COMMENTAIRES & TAGS ---
            st.markdown("#### 💬 L'avis du groupe")
            
            # 1. Affichage des Tags (Nuage)
            all_tags = []
            if "Tags_Nez" in df_this.columns:
                all_tags += [t.strip() for ts in df_this["Tags_Nez"].dropna() for t in ts.split(",")]
            if "Tags_Bouche" in df_this.columns:
                all_tags += [t.strip() for ts in df_this["Tags_Bouche"].dropna() for t in ts.split(",")]
            # Nettoyage des tags vides
            all_tags = [t for t in all_tags if len(t) > 1]
            
            if all_tags:
                from collections import Counter
                counts = Counter(all_tags)
                tags_html = ""
                for tag, count in counts.most_common(8):
                    tags_html += f"<span style='background-color:#333; color:white; padding:3px 8px; border-radius:10px; margin-right:5px; font-size:0.8em'>{tag} ({count})</span>"
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # 2. Affichage des Commentaires signés
            df_coms = df_this[["User", "Commentaire"]].dropna()
            for idx, row in df_coms.iterrows():
                if len(str(row['Commentaire'])) > 2:
                    st.info(f"**{row['User']}** : {row['Commentaire']}")

        else:
            st.info("Pas encore de notes.")

        # --- D. FORMULAIRE ---
        st.markdown("#### 📝 Noter ce vin")
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
                
                st.markdown("**Tags & Arômes**")
                # Sélecteurs standards
                t_nez = st.multiselect("Nez (Liste)", list(AROMES_NEZ.keys()), key=f"tn{champ}")
                t_bou = st.multiselect("Bouche (Liste)", list(AROMES_BOUCHE.keys()), key=f"tb{champ}")
                
                # Champ TEXTE LIBRE pour les tags perso
                custom_tag = st.text_input("Ajouter un arôme perso (ex: Café, Pétrole...)", key=f"cust_{champ}")
                
                user_comment = st.text_area("Mon avis écrit", placeholder="Ce vin me rappelle...", key=f"com_{champ}")

                if st.form_submit_button("Envoyer 🚀", use_container_width=True):
                    # Fusion des tags
                    final_tags_nez = ",".join(t_nez)
                    if custom_tag: # Si tag perso, on l'ajoute au Nez par défaut
                        final_tags_nez += f",{custom_tag}"
                    
                    final_tags_bouche = ",".join(t_bou)

                    new_entry = {
                        "User": user_name,
                        "Champagne": champ,
                        "Acidite": s_ac, "Bulles": s_bu, "Nez": s_ne, "Bouche": s_bo, "Finale": s_fi,
                        "Tags_Nez": final_tags_nez,
                        "Tags_Bouche": final_tags_bouche,
                        "Commentaire": user_comment
                    }
                    
                    df_cur = load_data(FILE_NOTES, list(new_entry.keys()))
                    df_cur = df_cur[~((df_cur["User"] == user_name) & (df_cur["Champagne"] == champ))]
                    df_final = pd.concat([df_cur, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(df_final, FILE_NOTES)
                    st.success("Enregistré !")
                    st.rerun()
        else:
            st.warning("⚠️ Rentre ton prénom tout en haut pour débloquer le formulaire.")
