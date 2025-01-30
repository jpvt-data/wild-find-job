import streamlit as st
import pandas as pd
import plotly.express as px


# point à garder en tête: il faut qu'à l'exécution de ce code soit automatisé avec le scraping; actuellement nous considérons que la base 
# chargement des données
df_offres = pd.read_csv("df_offres.csv", sep=',')

# configuration de la page
st.set_page_config(page_title="Analyse du marché de l'emploi DATA", layout="wide")

# Barre de navigation HTML + CSS
st.markdown(
    """
    <style>
        .nav-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #ffffff;
            padding: 10px 50px;
            border-bottom: 2px solid #ddd;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-links a {
            text-decoration: none;
            color: black;
            font-weight: bold;
            font-size: 16px;
        }
        .nav-links a:hover {
            color: #004aad;
        }
    </style>
    <div class="nav-bar">
        <div>
            <img src="https://upload.wikimedia.org/wikipedia/fr/thumb/c/c3/Logo_de_la_R%C3%A9publique_fran%C3%A7aise_%282020%29.svg/120px-Logo_de_la_R%C3%A9publique_fran%C3%A7aise_%282020%29.svg.png" width="100">
        </div>
        <div class="nav-links">
            <a href="/?nav=accueil">Accueil</a>
            <a href="/?nav=recherche">A propos</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)



# barre de navigation horizontale
menu = ["Accueil", "A propos"]
page = st.radio("Navigation", menu, horizontal=True)

# définir les fonctionnalités de la page d'acceuil
def accueil():
    # quelques lignes sur les fonctionnalités du projet
    st.title("Bienvenue sur Wild Find Job!")
    st.text("""Sur cette plateforme d'analyse du marché de l'emploi, vous explorerez un large éventail d'offres d'emploi dans le domaine de la DATA, des analyses 
            approfondies sur les métiers, et tendances du marché.  
            Trouvez le poste idéal, et prenez votre carrière en main.""")
    
    st.markdown("<h1>Devenez l'expert DATA que vous souhaitez être.</h1>", unsafe_allow_html=True)

    # initialiser la liste de suggestions d'intitulé de poste
    suggestions = ["Data Ingenieur", "Data Engineer", "Data Analyst", "Data Analyste", "Data Scientist"]
    # initialiser la liste de suggestions des localisations
    departements = ["France", "Ain", "Aisne", "Allier", "Alpes-de-Haute-Provence", "Hauts-de-Seine", "Seine-Saint-Denis", "Val-de-Marne", "Val-d'Oise"]

    # formulaire de recherche
    col1, col2 = st.columns(2)
    with col1:
        intitule_poste = st.selectbox("Intitulé du poste", suggestions)
    with col2:
        localisation = st.multiselect("Localisation", departements)

    with st.expander("Filtres"):
        niveau_experience = st.multiselect("Niveau d'expérience", ["Junior", "Intermédiaire", "Senior"])
        secteur_d_activite = st.multiselect("Secteur d'activité", ["Tech", "Finance", "Industrie", "Santé", "Marketing", "Autre"])
        taille_entreprise = st.multiselect("Taille d'entreprise", ["Startup", "PME", "Grande entreprise"])
        type_de_contrat = st.multiselect("Type de contrat", ["CDI", "CDD", "Freelance", "Stage", "Alternance"])
        teletravail = st.multiselect("Télétravail", ["Total", "Partiel", "Aucun"])

        if st.button("Appliquer les filtres"):
            def filtrer_offres(intitule_poste, localisations, niveaux_experience, secteurs_activite, tailles_entreprise, types_contrat, teletravail):
                # filtrer les données en fonction des critères
                masque = pd.Series([True] * len(df_offres))  # initialise un masque booléen indiquant si chaque ligne du DataFrame doit être conservée ou non.
                # Pour chaque critère, le masque est modifié en utilisant l'opération logique "&" qui combine plusieurs conditions de filtrage
                if intitule_poste:
                    masque &= df_offres["intitule_poste"].str.contains(intitule_poste, case=False, na=False) 

                if localisations:
                    masque &= df_offres["localisation"].isin(localisations)

                if niveaux_experience:
                    masque &= df_offres["niveau_experience"].isin(niveaux_experience)
                
                if secteur_d_activite:
                    masque &= df_offres["secteur_d_activite"].isin(secteur_d_activite)

                if teletravail:
                    masque &= df_offres["teletravail"].isin(teletravail)
                
                if type_de_contrat:
                    masque &= df_offres["type_de_contrat"].isin(type_de_contrat)

                if taille_entreprise:
                    masque &= df_offres["taille_entreprise"].isin(taille_entreprise)
                return df_offres[masque]
            
            resultats = filtrer_offres(intitule_poste, localisation, niveau_experience, secteur_d_activite, taille_entreprise, type_de_contrat, teletravail)
            nombre_annonces = len(resultats)
            nombre_cdi = len(resultats[resultats["type_de_contrat"] == "CDI"])
            nombre_teletravail = len(resultats[resultats["teletravail"] != "Aucun"])
            tendances = analyser_tendances(resultats)
            
            col1, col2 = st.columns([1, 2]) 
            with col1:
                st.markdown(
                    f"""
                    <div class='annonce-box'>
                        {nombre_annonces} annonces <br>
                        {nombre_cdi} CDI <br>
                        {nombre_teletravail} en télétravail
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                    <a href="#tendances" target="_self">
                        <div class='tendances-box'>
                            {tendances}
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
            
            st.write(resultats)  # affiche les résultats filtrés

        if st.button("Réinitialiser les filtres"):
            pass

def afficher_raison_wildfindjob():
    st.title("A propos de Wild Find Job")
    st.text("Wild Find Job est un projet de......")

def afficher_detail_offre():
    st.title("Détail de l'offre")

def analyser_tendances(df_offres_filtree):
    intitule_poste = df_offres_filtree['metier']
    st.title("Analyse du métier de ")
    st.markdown("<h1>Analysez le marché de l'emploi DATA</h1>", unsafe_allow_html=True)

# affichage de la page sélectionnée par l'utilisateur
if page == "Accueil":
    accueil()
elif page == "A propos":
    afficher_raison_wildfindjob()
