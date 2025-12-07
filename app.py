import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuration de la page
st.set_page_config(page_title="Champagne Rating", page_icon="🥂")

# Titre
st.title("🥂 Dégustation de Champagne entre Potes")

# 1. Gestion des données (Système simple avec fichier CSV)
DATA_FILE = "notes.csv"

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["User", "Champagne", "Robe", "Bulles", "Nez", "Bouche", "Finale"])
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# 2. Barre latérale pour la saisie
st.sidebar.header("🍾 Ta Dégustation")
user = st.sidebar.text_input("Ton Prénom")
champagne = st.sidebar.text_input("Nom du Champagne", "Cuvée Mystère")

st.sidebar.subheader("Tes Notes (0-10)")
robe = st.sidebar.slider("👀 La Robe (Couleur)", 0, 10, 5)
bulles = st.sidebar.slider("🫧 Les Bulles (Finesse)", 0, 10, 5)
nez = st.sidebar.slider("👃 Le Nez (Arômes)", 0, 10, 5)
bouche = st.sidebar.slider("👄 La Bouche (Goût/Equilibre)", 0, 10, 5)
finale = st.sidebar.slider("⏱️ La Finale (Longueur)", 0, 10, 5)

if st.sidebar.button("Envoyer ma note"):
    if user and champagne:
        new_entry = pd.DataFrame({
            "User": [user],
            "Champagne": [champagne],
            "Robe": [robe],
            "Bulles": [bulles],
            "Nez": [nez],
            "Bouche": [bouche],
            "Finale": [finale]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        st.sidebar.success("Note enregistrée !")
        st.rerun() # Rafraîchir pour voir les résultats
    else:
        st.sidebar.error("Remplis ton nom et le champagne !")

# 3. Affichage des Résultats
st.header(f"Résultats pour : {champagne}")

if not df.empty and champagne in df["Champagne"].values:
    # Filtrer sur le champagne en cours
    df_champ = df[df["Champagne"] == champagne]
    
    # Calcul des moyennes
    avg_scores = df_champ[["Robe", "Bulles", "Nez", "Bouche", "Finale"]].mean().reset_index()
    avg_scores.columns = ["Critère", "Note"]
    
    # Affichage du Graphique Radar (Spider Chart)
    categories = ["Robe", "Bulles", "Nez", "Bouche", "Finale"]
    
    fig = go.Figure()

    # Ajout de la moyenne globale
    fig.add_trace(go.Scatterpolar(
        r=avg_scores["Note"],
        theta=categories,
        fill='toself',
        name='Moyenne du Groupe',
        line_color='gold'
    ))

    # Ajout de la note de l'utilisateur actuel (si dispo)
    if user and user in df_champ["User"].values:
        user_scores = df_champ[df_champ["User"]==user].iloc[-1][categories]
        fig.add_trace(go.Scatterpolar(
            r=user_scores,
            theta=categories,
            fill='toself',
            name=f'Note de {user}',
            line_color='pink',
            opacity=0.5
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Tableau des notes détaillées
    st.subheader("Détail des notes")
    st.dataframe(df_champ)

else:
    st.info("Aucune note pour ce champagne pour l'instant. Sois le premier à noter !")
