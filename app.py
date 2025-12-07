import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuration de la page
st.set_page_config(page_title="Champagne Rating", page_icon="🥂", layout="centered")

# --- CONSTANTES ---
FILE_NOTES = "notes_v2.csv"
FILE_CHAMPAGNES = "liste_champagnes.csv"
ADMIN_PASSWORD = "admin"

AROMES_NEZ = {
    "🍋 Agrumes": "Citron, Pamplemousse",
    "🍐 Fruits Blancs": "Poire, Pomme, Pêche",
    "🌸 Floral": "Fleurs blanches, Acacia",
    "🍞 Brioche": "Toast, Beurre, Levure",
    "🌰 Fruits Secs": "Noisette, Amande",
    "🍯 Miel": "Miel, Cire"
}

AROMES_BOUCHE = {
    "⚡ Acidité": "Vif, Tranchant",
    "🍬 Sucre": "Dosé, Rond",
    "🧈 Gras": "Beurré, Crémeux",
    "💎 Minéral": "Craie, Salin",
    "🪵 Boisé": "Fût, Vanille",
    "🍒 Fruits Rouges": "Fraise, Framboise (Rosé)"
}

# --- FONCTIONS DE GESTION DE DONNÉES ---
def load_data(file, columns):
    if not os.path.exists(file):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(file)

def save_data(df, file):
    df.to_csv(file, index=False)

# --- INTERFACE ---
st.title("🥂 Champagne Battle")
st.markdown("---")

# 1. BARRE LATÉRALE (USER + ADMIN)
with st.sidebar:
    st.header("👤 Identité")
    user_name = st.text_input("Ton Prénom", key="user_name")
    
    st.markdown("---")
    st.header("⚙️ Admin")
    admin_pwd = st.text_input("Mot de passe", type="password")
    
    # Gestion des Champagnes (Admin seulement)
    if admin_pwd == ADMIN_PASSWORD:
        st.success("Mode Admin activé")
        new_champ = st.text_input("Ajouter un Champagne à la liste")
        if st.button("Ajouter"):
            df_champs = load_data(FILE_CHAMPAGNES, ["Nom"])
            if new_champ and new_champ not in df_champs["Nom"].values:
                new_row = pd.DataFrame({"Nom": [new_champ]})
                df_champs = pd.concat([df_champs, new_row], ignore_index=True)
                save_data(df_champs, FILE_CHAMPAGNES)
                st.success(f"{new_champ} ajouté !")
                st.rerun()

# Chargement des données
df_notes = load_data(FILE_NOTES, ["User", "Champagne", "Robe", "Bulles", "Nez", "Bouche", "Finale", "Tags_Nez", "Tags_Bouche"])
df_champs = load_data(FILE_CHAMPAGNES, ["Nom"])

# Si aucun champagne n'existe, on en met un par défaut
if df_champs.empty:
    df_champs = pd.DataFrame({"Nom": ["Exemple: Ruinart Blanc de Blancs"]})
    save_data(df_champs, FILE_CHAMPAGNES)

# Bouton de rafraîchissement global
if st.button("🔄 Actualiser les résultats (Voir les notes des potes)"):
    st.rerun()

# 2. LISTE DES CHAMPAGNES (ACCORDÉON)
st.subheader("🍾 La Carte des Vins")

champagne_list = df_champs["Nom"].unique()

for champ in champagne_list:
    # On crée un container extensible pour chaque champagne
    with st.expander(f"🥂 {champ}", expanded=False):
        
        # --- A. VISUALISATION (Le Graphique) ---
        df_this_champ = df_notes[df_notes["Champagne"] == champ]
        
        if not df_this_champ.empty:
            # Calcul de la moyenne
            cols_score = ["Robe", "Bulles", "Nez", "Bouche", "Finale"]
            avg_scores = df_this_champ[cols_score].mean().tolist()
            
            # Graphique Radar
            categories = cols_score
            fig = go.Figure()
            
            # Moyenne du groupe
            fig.add_trace(go.Scatterpolar(
                r=avg_scores,
                theta=categories,
                fill='toself',
                name='Moyenne Groupe',
                line_color='gold'
            ))
            
            # Note de l'utilisateur (s'il a voté)
            if user_name and user_name in df_this_champ["User"].values:
                user_scores = df_this_champ[df_this_champ["User"] == user_name].iloc[-1][cols_score].tolist()
                fig.add_trace(go.Scatterpolar(
                    r=user_scores,
                    theta=categories,
                    fill='toself',
                    name=f'Note de {user_name}',
                    line_color='pink',
                    opacity=0.4
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                margin=dict(l=40, r=40, t=20, b=20),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Affichage des tags populaires (Aromes)
            st.markdown("**🏷️ Ce qu'on en dit :**")
            all_tags = []
            if "Tags_Nez" in df_this_champ.columns:
                all_tags += [tag for tags in df_this_champ["Tags_Nez"].dropna() for tag in tags.split(",")]
            if "Tags_Bouche" in df_this_champ.columns:
                all_tags += [tag for tags in df_this_champ["Tags_Bouche"].dropna() for tag in tags.split(",")]
            
            if all_tags:
                from collections import Counter
                counts = Counter(all_tags)
                # Affichage sous forme de badges
                cols = st.columns(len(counts))
                tags_html = ""
                for tag, count in counts.most_common(5):
                    tags_html += f"<span style='background-color:#f0f2f6; padding:5px; border-radius:5px; margin-right:5px;'>{tag} ({count})</span>"
                st.markdown(tags_html, unsafe_allow_html=True)
                
            st.write(f"*Nombre de votants : {len(df_this_champ)}*")
            
        else:
            st.info("Pas encore de note pour ce champagne.")

        # --- B. FORMULAIRE DE NOTATION ---
        st.markdown("---")
        st.write(f"📝 **Noter {champ}**")
        
        if not user_name:
            st.warning("Rentre ton prénom dans la barre latérale pour noter !")
        else:
            # On utilise un formulaire pour ne pas recharger la page à chaque clic
            with st.form(key=f"form_{champ}"):
                c1, c2 = st.columns(2)
                with c1:
                    score_robe = st.slider("Robe", 0, 10, 5)
                    score_bulles = st.slider("Bulles", 0, 10, 5)
                    score_nez = st.slider("Nez (Qualité)", 0, 10, 5)
                with c2:
                    score_bouche = st.slider("Bouche", 0, 10, 5)
                    score_finale = st.slider("Finale", 0, 10, 5)
                
                st.markdown("**👃 Arômes (Nez)**")
                tags_nez = st.multiselect("Sélectionne les marqueurs", list(AROMES_NEZ.keys()), key=f"nez_{champ}")
                
                st.markdown("**👅 Sensations (Bouche)**")
                tags_bouche = st.multiselect("Sélectionne les marqueurs", list(AROMES_BOUCHE.keys()), key=f"bouche_{champ}")
                
                submitted = st.form_submit_button("Envoyer ma note 🚀")
                
                if submitted:
                    # Création de la ligne de données
                    new_entry = {
                        "User": user_name,
                        "Champagne": champ,
                        "Robe": score_robe,
                        "Bulles": score_bulles,
                        "Nez": score_nez,
                        "Bouche": score_bouche,
                        "Finale": score_finale,
                        "Tags_Nez": ",".join(tags_nez),
                        "Tags_Bouche": ",".join(tags_bouche)
                    }
                    
                    # Sauvegarde
                    df_current = load_data(FILE_NOTES, list(new_entry.keys()))
                    # On supprime l'ancienne note de cet user pour ce champagne s'il y en a une (mise à jour)
                    df_current = df_current[~((df_current["User"] == user_name) & (df_current["Champagne"] == champ))]
                    
                    df_new = pd.DataFrame([new_entry])
                    df_final = pd.concat([df_current, df_new], ignore_index=True)
                    save_data(df_final, FILE_NOTES)
                    
                    st.success("Note enregistrée ! Clique sur 'Actualiser' pour voir le graph.")
