import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import time

# Configuration de la page
st.set_page_config(page_title="Champagne Battle", page_icon="🥂", layout="centered")

# --- CONSTANTES ---
FILE_NOTES = "notes_v3.csv"
FILE_CHAMPAGNES = "liste_champagnes.csv"
ADMIN_PASSWORD = "admin"

# Listes étoffées
AROMES_NEZ = {
    "🍋 Agrumes": "Citron, Pamplemousse, Clémentine, Zeste",
    "🍏 Fruits Blancs": "Pomme verte, Poire, Pêche de vigne",
    "🍑 Fruits Jaunes": "Abricot, Mirabelle, Pêche jaune",
    "🍍 Exotique": "Ananas, Mangue, Passion, Litchi",
    "🍓 Fruits Rouges": "Fraise, Framboise, Groseille, Cerise (Rosé)",
    "🌸 Floral": "Fleurs blanches, Acacia, Chèvrefeuille, Rose, Tilleul",
    "🌿 Végétal": "Herbe coupée, Fougère, Menthe, Thé",
    "🌰 Fruits Secs": "Noisette, Amande fraîche, Figue sèche",
    "🍞 Boulangerie": "Brioche, Toast grillé, Mie de pain, Levure",
    "🧈 Pâtisserie": "Beurre frais, Crème, Biscuit, Pâte d'amande",
    "🍯 Miel/Cire": "Miel d'acacia, Cire d'abeille, Pain d'épices",
    "🪵 Boisé/Épicé": "Vanille, Fût de chêne, Poivre blanc, Cannelle",
    "🔥 Empyreumatique": "Fumé, Cacao, Café, Craie mouillée"
}

AROMES_BOUCHE = {
    "⚡ Attaque Vive": "Tranchant, Nerveux, Droit",
    "☁️ Attaque Souple": "Rond, Ample, Velouté",
    "🫧 Effervescence": "Bulles fines, Mousse crémeuse, Pétillant agressif",
    "⚖️ Équilibre": "Bien dosé, Trop sucré, Trop acide, Vineux",
    "💎 Minéralité": "Salin, Craie, Calcaire, Iode",
    "🍂 Évolution": "Oxydatif (Pomme blette), Rancio, Mature",
    "⏱️ Longueur": "Courte, Moyenne, Persistante, Interminable"
}

# --- FONCTIONS ---
def load_data(file, columns):
    if not os.path.exists(file):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(file)

def save_data(df, file):
    df.to_csv(file, index=False)

# --- INTERFACE ---

# 1. EN-TÊTE & IDENTIFICATION (Mobile Friendly)
st.title("🥂 Champagne Battle")

# Zone d'identification mise en avant pour le mobile
col_id, col_live = st.columns([2, 1])
with col_id:
    user_name = st.text_input("👤 Ton Prénom (Obligatoire)", placeholder="Ex: Thomas")
with col_live:
    st.write("") # Spacer
    st.write("") 
    auto_refresh = st.toggle("🔄 Mode Live", value=False, help="Active ceci pour voir les notes des autres arriver en direct sans toucher à rien.")

if auto_refresh:
    time.sleep(5)
    st.rerun()

st.markdown("---")

# 2. GESTION ADMIN (Cachée dans un expander en bas ou sidebar discrète)
with st.sidebar:
    st.header("⚙️ Admin")
    admin_pwd = st.text_input("Mot de passe", type="password")
    
    if admin_pwd == ADMIN_PASSWORD:
        st.success("Mode Admin")
        new_champ = st.text_input("Ajouter un Champagne")
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
    df_champs = pd.DataFrame({"Nom": ["Exemple: Bollinger Special Cuvée"]})
    save_data(df_champs, FILE_CHAMPAGNES)

# 3. LISTE DES VINS
st.subheader("🍾 La Carte des Vins")

champagne_list = df_champs["Nom"].unique()

for champ in champagne_list:
    with st.expander(f"🥂 {champ}", expanded=False):
        
        # --- A. VISUALISATION ---
        df_this_champ = df_notes[df_notes["Champagne"] == champ]
        
        if not df_this_champ.empty:
            cols_score = ["Acidite", "Bulles", "Nez", "Bouche", "Finale"]
            
            # Graphique Radar
            categories = cols_score
            fig = go.Figure()

            # 1. Les notes individuelles (5 premières max) pour voir les avis divergents
            colors = ['#FF9999', '#99FF99', '#9999FF', '#FFFF99', '#FF99FF']
            for i, (idx, row) in enumerate(df_this_champ.head(5).iterrows()):
                fig.add_trace(go.Scatterpolar(
                    r=row[cols_score],
                    theta=categories,
                    fill=None,
                    name=str(row['User']),
                    line_color=colors[i % len(colors)],
                    opacity=0.3,
                    showlegend=True
                ))

            # 2. La Moyenne (Grosse ligne)
            avg_scores = df_this_champ[cols_score].mean().tolist()
            fig.add_trace(go.Scatterpolar(
                r=avg_scores,
                theta=categories,
                fill='toself',
                name='Moyenne',
                line=dict(color='gold', width=4),
                opacity=0.9
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                margin=dict(l=40, r=40, t=20, b=20),
                height=350,
                legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tags populaires
            all_tags = []
            if "Tags_Nez" in df_this_champ.columns:
                all_tags += [tag.strip() for tags in df_this_champ["Tags_Nez"].dropna() for tag in tags.split(",")]
            if "Tags_Bouche" in df_this_champ.columns:
                all_tags += [tag.strip() for tags in df_this_champ["Tags_Bouche"].dropna() for tag in tags.split(",")]
            
            if all_tags:
                from collections import Counter
                counts = Counter(all_tags)
                st.markdown("**🏷️ Mots clés du groupe :**")
                tags_html = ""
                for tag, count in counts.most_common(6):
                    tags_html += f"<span style='background-color:#31333F; color:white; padding:4px 8px; border-radius:10px; margin-right:5px; font-size:0.8em'>{tag} ({count})</span>"
                st.markdown(tags_html, unsafe_allow_html=True)
                st.write("") # Spacer

        else:
            st.info("Soyez le premier à noter !")

        # --- B. FORMULAIRE DE NOTATION ---
        st.markdown("#### 📝 Ma Note")
        
        if not user_name:
            st.error("⚠️ Rentre ton prénom tout en haut de la page pour pouvoir noter !")
        else:
            with st.form(key=f"form_{champ}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("Structure")
                    score_acidite = st.slider("Acidité / Vivacité", 0, 10, 5, key=f"ac_{champ}")
                    score_bulles = st.slider("Bulles (Finesse)", 0, 10, 5, key=f"bu_{champ}")
                    score_nez = st.slider("Nez (Intensité/Qualité)", 0, 10, 5, key=f"ne_{champ}")
                with c2:
                    st.caption("Plaisir")
                    score_bouche = st.slider("Bouche (Plaisir global)", 0, 10, 5, key=f"bo_{champ}")
                    score_finale = st.slider("Longueur en bouche", 0, 10, 5, key=f"fi_{champ}")
                
                with st.expander("Voir les arômes détaillés (Optionnel)"):
                    st.markdown("**👃 Au Nez**")
                    tags_nez = st.multiselect("Choisis...", list(AROMES_NEZ.keys()), key=f"tn_{champ}")
                    
                    st.markdown("**👅 En Bouche**")
                    tags_bouche = st.multiselect("Choisis...", list(AROMES_BOUCHE.keys()), key=f"tb_{champ}")
                
                submitted = st.form_submit_button("Envoyer ma note 🚀", use_container_width=True)
                
                if submitted:
                    # Traitement des tags (on concatène les valeurs des dictionnaires pour simplifier)
                    str_tags_nez = ",".join([AROMES_NEZ[k] for k in tags_nez]) # On stocke les descriptions
                    str_tags_bouche = ",".join([AROMES_BOUCHE[k] for k in tags_bouche])
                    # Ou juste les clés si on préfère que ce soit court. Ici je garde les clés pour l'affichage plus propre
                    # Modif : On va stocker les CLÉS (ex: "Agrumes") pour que le nuage de mots soit lisible
                    final_tags_nez = ",".join(tags_nez)
                    final_tags_bouche = ",".join(tags_bouche)

                    new_entry = {
                        "User": user_name,
                        "Champagne": champ,
                        "Acidite": score_acidite,
                        "Bulles": score_bulles,
                        "Nez": score_nez,
                        "Bouche": score_bouche,
                        "Finale": score_finale,
                        "Tags_Nez": final_tags_nez,
                        "Tags_Bouche": final_tags_bouche
                    }
                    
                    df_current = load_data(FILE_NOTES, list(new_entry.keys()))
                    # Update si déjà noté
                    df_current = df_current[~((df_current["User"] == user_name) & (df_current["Champagne"] == champ))]
                    
                    df_new = pd.DataFrame([new_entry])
                    df_final = pd.concat([df_current, df_new], ignore_index=True)
                    save_data(df_final, FILE_NOTES)
                    
                    st.success("C'est noté !")
                    time.sleep(1) # Petit temps pour lire le message
                    st.rerun()
