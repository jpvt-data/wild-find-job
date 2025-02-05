import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_modal import Modal


# point à garder en tête: il faut qu'à l'exécution de ce code soit automatisé avec le scraping; actuellement nous considérons que la base 
# chargement des données
df_offres = pd.read_csv("df_offres.csv", sep=',')
df_offres2 = pd.read_csv("df_offres_x.csv", sep=',')

st.write(df_offres2.head(5))
# barre de navigation HTML + CSS
st.markdown(
    """
    <style>
        .nav-bar {
            display: flex;
            align-items: center; /* Alignement vertical */
            padding: 10px 50px;
        }

        .logo-container {
            margin-right: auto; /* Pousse le logo à gauche */
        }

        .nav-links {
            display: flex;
            gap: 20px;
        }

        .nav-link-box {
            background-color: white;
            border-radius: 20px; /* Bords arrondis */
            padding: 10px 20px; /* Marge intérieure */
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Ombre légère */
        }
        .nav-links a {
            text-decoration: none;
            color: green;
            font-weight: bold;
            font-size: 25px;
        }

        .nav-links a:hover {
            color: #004aad;
        }

        .welcome-message {
            margin-top: 1000px; /* Espacement entre la barre de navigation et le message */
        }
    </style>

    <div class="nav-bar">
        <div class="logo-container">
            <h1 class="logo-text"style="font-size: 45px; font-weight: bold; color:rgb(245, 247, 248); font-family: Arial, sans-serif; text_align: left;">Wild Find Job</h1>
        </div>
        <div class="nav-links">
            <div class="nav-link-box">
                <a href="/?nav=accueil">Accueil</a>
            </div>
            <div class="nav-link-box">
                <a href="/?nav=recherche">A propos</a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# image de fond
st.markdown("""
<style>
body {
    background-image: url('C:/Users/Lenovo/Documents/WCS/GitHub/wild-find-job/images/Capture.PNG');
    background-size: cover;
    background-position: center center;
}
</style>
""", unsafe_allow_html=True)

# fonction permettant de filtrer les données selon les choix de l'utilisateur
def filtrer_offres(df, intitule_poste, localisation, niveau_experience, secteur_d_activite, taille_entreprise, type_de_contrat, teletravail):
    masque = pd.Series([True] * len(df))
    if intitule_poste:
        masque &= df["intitule_poste"].str.contains(intitule_poste, case=False, na=False)
    if localisation:
        masque &= df["departement"].isin(localisation)
    if niveau_experience:
        masque &= df["niveau_experience"].isin(niveau_experience)
    if secteur_d_activite:
        masque &= df["secteur_d_activite"].isin(secteur_d_activite)
    if taille_entreprise:
        masque &= df["taille_entreprise"].isin(taille_entreprise)
    if type_de_contrat:
        masque &= df["type_de_contrat"].isin(type_de_contrat)
    if teletravail:
        if teletravail: 
            masque &= df["teletravail"].isin(teletravail)
    return df[masque]

# définir les fonctionnalités de la page d'acceuil
def accueil():

    # quelques lignes sur les fonctionnalités du projet
    # st.markdown("""
    #         **Bienvenue sur Wild Find Job!**"  
    #         Sur cette plateforme d'analyse du marché de l'emploi, vous explorerez un large éventail d'offres d'emploi dans le domaine de la DATA, des analyses approfondies sur les métiers, et tendances du marché. Trouvez le poste idéal, et prenez votre carrière en main.
    #         """)
    
    st.markdown(
            """
            <h1 style="font-size: 2em;">  Devenez l'expert DATA <br> que vous souhaitez être.</h1>
            """,
            unsafe_allow_html=True,)

    # formulaire de recherche
    with st.container():
        col1, col2, col3 = st.columns(3)
        intitule_poste = col1.selectbox("Intiule de poste", sorted(df_offres["intitule_poste"].unique()), index=None, placeholder="Choisissez un métier")
        localisation = col2.multiselect("Localisation", sorted(df_offres["departement"].unique()), placeholder="Choisissez une localisation")
        with col3.popover("Filtres avancés"): # affichage des filtres sous forme de pop up
                niveau_experience = st.multiselect("Niveau d'expérience", ["Junior", "Intermédiaire", "Senior"])
                secteur_d_activite = st.multiselect("Secteur d'activité", ["Tech", "Finance", "Industrie", "Santé", "Marketing", "Autre"])
                taille_entreprise = st.multiselect("Taille d'entreprise", ["Startup", "PME", "Grande entreprise"])
                type_de_contrat = st.multiselect("Type de contrat", ["CDI", "CDD", "Freelance", "Stage", "Alternance"])
                teletravail = st.multiselect("Télétravail", ["Complet", "Partiel", "Occasionnel"])

        resultats = None 
              
        results = filtrer_offres(df_offres, intitule_poste, localisation, niveau_experience, secteur_d_activite, taille_entreprise, type_de_contrat, teletravail)
        if teletravail:
                    results = filtrer_offres(df_offres, intitule_poste, localisation, niveau_experience, secteur_d_activite, taille_entreprise, type_de_contrat, teletravail) 
        else:
            results = filtrer_offres(df_offres, intitule_poste, localisation, niveau_experience, secteur_d_activite, taille_entreprise, type_de_contrat, teletravail= None) 

        # ajouter les colonnes offres et lien à la table filtrée utilisée à l'affichage
        resultats = pd.DataFrame(results).reset_index()
        new = df_offres[['annonce', 'lien']].reset_index()
        resultats = pd.merge(resultats, new, left_index=True, right_index=True, how='left')
        resultats.drop(columns=['index_y', 'annonce_y', 'lien_y'], inplace=True)
        resultats.to_csv("resultats.csv")
        
        # initialisation des valeurs des kpis à afficher
        nombre_annonces = len(resultats)
        nombre_entreprises = resultats["nom_entreprise"].nunique()
        nombre_cdi = len(resultats[resultats["type_de_contrat"] == "CDI"])
        nombre_teletravail = len(resultats[resultats["teletravail"] != "Aucun"])

    # code d'affichage des kpis sur l'ensemble des annonces
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(f"📢 Annonces", value=nombre_annonces)
        col2.metric(f"💼 CDI", value=nombre_cdi)
        col3.metric(f"🏢 Entreprises", value=nombre_entreprises)
        col4.metric(f"🏠 Télétravail", value=nombre_teletravail)
        with col5: 
            st.markdown("""
            <style>
                .link-box {
                    display: inline-block;
                    background-color: white;
                    border-radius: 20px; /* Bords arrondis */
                    padding: 10px 20px; /* Marge intérieure */
                    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Ombre légère */
                    text-decoration: none; /* Supprime le surlignement */
                    color: black; /* Couleur du texte */
                    font-weight: bold;
                    transition: 0.3s; /* Effet de transition */
                }
        
                .link-box:hover {
                    background-color: #c0c0c0; /* Changement de couleur au survol */
                }
            </style>

            <a href="https://ton-lien-ici.com" class="link-box">
                📊 Analyser le métier
            </a>
        """, unsafe_allow_html=True)

    # code pour afficher un résumé des offres               
    col6, col7 = st.columns(2)
    
    offre_selectionnee = None
    
    for i in range(len(resultats)):
        if i % 2 == 0:
            with col6:
                st.write(f"{resultats.iloc[i]['intitule_poste']} ({resultats.iloc[i]['niveau_experience']})")
                st.write(f"{resultats.iloc[i]['nom_entreprise']}")
                with st.container():
                    col8, col9, col10, col11 = st.columns(4)
                    col8.write(f"{resultats.iloc[i]['departement']}")
                    col9.write(f"{resultats.iloc[i]['type_de_contrat']}")
                    col10.write(f"{resultats.iloc[i]['salaire']}€ / an")
                    with col11:
                        if st.button(f"Voir l'offre", key=i):
                            offre_selectionnee = i
                st.write(f"🏠Télétravail {resultats.iloc[i]['teletravail']}")
        else:
            with col7:
                st.write(f"{resultats.iloc[i]['intitule_poste']} ({resultats.iloc[i]['niveau_experience']})")
                st.write(f"{resultats.iloc[i]['nom_entreprise']}")
                with st.container():
                    col8, col9, col10, col11 = st.columns(4)
                    col8.write(f"{resultats.iloc[i]['departement']}")
                    col9.write(f"{resultats.iloc[i]['type_de_contrat']}")
                    col10.write(f"{resultats.iloc[i]['salaire']} € / an")
                    with col11:
                        if st.button(f"Voir l'offre", key=i):
                            offre_selectionnee = i
                st.write(f"🏠Télétravail {resultats.iloc[i]['teletravail']}")
    
    # code d'affichage du détail de l'offre
    modal = Modal("Détails de l'offre", key="offre_modal")
    if offre_selectionnee is not None:
        annonce_affichee = resultats.iloc[offre_selectionnee]
        if modal.open():
            with modal.container():
                st.markdown(annonce_affichee['annonce_x'], unsafe_allow_html=True) 
                if pd.notna(annonce_affichee["lien_x"]):
                    st.markdown(f"[Voir l'offre complète]({annonce_affichee['lien_x']})", unsafe_allow_html=True)
    if offre_selectionnee is not None:
        modal.open()
    # if offre_selectionnee is not None:
    #     st.switch_page(f"{offre_selectionnee}")
    #     afficher_detail_offre(resultats)
    return

def analyser_tendances(df, poste):
    return

def afficher_detail_offre(df):
    params = st.query_params
    offre_id = int(params.get("offre", [None])[0])

    if offre_id is not None:
        annonce_affichee = df.iloc[offre_id]

        st.title("Détails de l'offre")
        st.markdown(annonce_affichee['annonce_x'], unsafe_allow_html=True)
        
        if pd.notna(annonce_affichee["lien"]):
            st.markdown(f"[Voir l'offre complète]({annonce_affichee['lien']})", unsafe_allow_html=True)

def afficher_raison_wildfindjob():
    st.title("A propos de Wild Find Job")
    st.text("Wild Find Job est un projet de......")


# Récupération des paramètres d'URL (méthode recommandée)
params = st.query_params
nav = params.get("nav", ["accueil"])[0]
metier = params.get("metier", [None])[0]

if nav == "accueil":
    accueil()
    
elif nav == "recherche":
    afficher_raison_wildfindjob()
elif nav == "tendance" and metier:
    analyser_tendances(metier)
else:
    st.write("Page non trouvée")
