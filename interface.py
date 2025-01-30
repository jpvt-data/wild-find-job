import streamlit as st
import pandas as pd
import plotly.express as px

# configuration de la page
st.set_page_config(page_title="Analyse du marché de l'emploi DATA", layout="wide")

# barre de navigation horizontale
menu = ["Accueil", "Rechercher des offres", "Analyser des tendances"]
page = st.radio("Navigation", menu, horizontal=True)

def accueil():
    st.title("Bienvenue sur Wild Find Job, plateforme d'analyse du marché de l'emploi DATA")
    st.write("Cette plateforme vous permet de rechercher des offres d'emploi et d'analyser les tendances du marché de l'emploi dans la DATA.")

def rechercher_offres():
    st.title("Recherche d'offres d'emploi")
    
    # formulaire de recherche
    with st.form("search_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            job_title = st.text_input("Intitulé du poste", "Data Analyst")
