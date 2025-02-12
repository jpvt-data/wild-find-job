import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_modal import Modal
import ast


# point à garder en tête: il faut qu'à l'exécution de ce code soit automatisé avec le scraping; actuellement nous considérons que la base 
# chargement des données en cache afin d'alléger le chargement des données sur la plateforme
@st.cache_data
def load_data():
    return pd.read_csv("df_final2.csv", sep=',', nrows=200)

df_offres2 = load_data() # appel de la fonction précédemmentcrée

# code dde transformation de certaines colonnes nécessaires pour l'affichage
# extraire les départements uniques
def transfo_departements(dept):
    if isinstance(dept, str):
        return ast.literal_eval(dept)
    else:
        return dept

df_offres2["Departement"] = df_offres2["Departement"].apply(transfo_departements)
df_offres2["Departement_affichage"] = df_offres2["Departement"].apply(lambda x: " - ".join(x))

all_departments = set()
for department in df_offres2["Departement"]:
    all_departments.update(department)
    localisations_uniques = sorted(all_departments)

# extraire la durée de publication
df_offres2['PublishDate'] = pd.to_datetime(df_offres2['PublishDate'], errors='coerce')
now = pd.Timestamp.now()
df_offres2['OfferDuration'] = (now - df_offres2['PublishDate']).dt.total_seconds() / 3600  # Convertir en heures

def categoriser_duree(heures):
    if heures < 24:
        return f"{int(heures)}h"
    elif heures < 24 * 30:
        return f"{int(heures // 24)} jours"
    elif heures < 24 * 90:
        return "3 mois"
    else:
        return "plus de 3 mois"

df_offres2['TimesincePublication'] = df_offres2['OfferDuration'].apply(categoriser_duree)

# barre de navigation HTML + CSS 
st.markdown(
    """
    <style>
        .nav-bar {
            display: flex;
            align-items: center; /* alignement vertical de la page*/
            padding: 10px 50px; /* taille des éléments d'affichage dans la barre de nav
            width: 100%; /* s'assurer que la barre s'étend sur la largeur*/
        }

        .logo-container {
            margin-right: auto; /* si logo, il est aligné à gauche de la barre automatiquement */
        }

        .nav-links {
            display: flex; /* créee des mises en page flexibles et réactives */
            gap: 20px; /* créee un espace entre les éléments de la barre de navigation */ 
        }

        .nav-link-box {
            background-color: white; /* couleur de fond des éléments */
            border-radius: 20px; /* bords arrondis */
            padding: 10px 20px; /* marge intérieure */
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* ombre légère */
        }
        .nav-links a {
            text-decoration: none;
            color: green;
            font-weight: bold;
            font-size: 25px;
        }

        .nav-links a:hover { /* style visuel  des éléments lorque l'on passe la souris dessus */
            color: #004aad;
        }

        .welcome-message {
            margin-top: 50px; /* espace entre la barre de navigation et le message */
        }

        .stApp {
            width: 100% !important;
        }
    </style>

    <div class="nav-bar">
        <div class="logo-container">
            <h1 class="logo-text"style="font-size: 45px; font-weight: bold; color:black; font-family: Arial, sans-serif; text_align: left;">Wild Find Job</h1>
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

# fonction permettant de filtrer les données selon les choix de l'utilisateur
def filtrer_offres(df, OfferTitle, Departement, Domaine, ContractType, Salaire, Telework):
    masque = pd.Series([True] * len(df))
    if OfferTitle:
        masque &= df["OfferLabel"].str.contains(OfferTitle, case=False, na=False)
    if Departement:
        masque &= df["Departement"].isin(localisations_uniques) # à modifier pour récupérer plutôt le département/ville
    if Domaine:
        masque &= df["Domaine"].isin(Domaine)
    if ContractType:
        masque &= df["ContractType"].isin(ContractType)
    if Salaire:
        masque &= df["Salaire"].isin(Salaire)
    if Telework:
        if Telework: 
            masque &= df["Telework"].isin(Telework)
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
        intitule_poste = col1.selectbox("Intitulé du poste", sorted(df_offres2["OfferLabel"].unique()), index=None, placeholder="Choisissez un métier")
        localisation = col2.multiselect("Département", localisations_uniques, placeholder="Choisissez un département")
        
        with col3.popover("Filtres avancés"): # affichage des filtres sous forme de pop up à proximité de l'élément
                type_de_contrat = st.multiselect("Type de contrat", sorted(df_offres2["ContractType"].unique()))
                salaire = st.multiselect("Salaire", sorted(df_offres2["DisplayedSalary"].unique()))
                secteur_d_activite = st.multiselect("Secteur d'activité", sorted(df_offres2["Domaine"].unique()))
                teletravail_options = []
                for option in df_offres2["Telework"].unique():
                    if option != "NC":
                        teletravail_options.append(option)
                teletravail = st.multiselect("Télétravail", sorted(teletravail_options))

    resultats = None 
              
    results = filtrer_offres(df_offres2, OfferTitle=intitule_poste, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire=salaire, Telework=teletravail)
    if teletravail != "NC":
        results = filtrer_offres(df_offres2, OfferTitle=intitule_poste, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire=salaire, Telework=teletravail) 
    else:
        results = filtrer_offres(df_offres2, OfferTitle=intitule_poste, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire=salaire, Telework=None) 
    
    # ajouter les colonnes description, profil et lien à la table filtrée utilisée pour les filtres
    resultats = pd.DataFrame(results)
    new = df_offres2[['Description', 'Profile', 'UrlOffre']] # definition d'un df n'utilisant que les colonnes à ajouter
    resultats = pd.merge(resultats, new, left_index=True, right_index=True, how='inner').reset_index() # merge des colonnes des 2 df
        
    resultats.drop(columns='Unnamed: 0', inplace=True) # suppression des colonnes inutiles
    resultats.to_csv("resultats.csv") # df pour imprévu
        
    # initialisation des valeurs des kpis à afficher
    nombre_annonces = len(resultats)
    nombre_entreprises = resultats["CompanyName"].nunique()
    nombre_cdi = len(resultats[resultats["ContractType"] == "CDI"])
    nombre_teletravail = len(resultats[resultats["Telework"] != "NC"])

    # code d'affichage des kpis sur l'ensemble des annonces
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(f"📢 Annonces", value=nombre_annonces)
        col2.metric(f"💼 CDI", value=nombre_cdi)
        col3.metric(f"🏢 Entreprises", value=nombre_entreprises)
        col4.metric(f"🏠 Télétravail", value=nombre_teletravail)
        with col5: 
            if st.button("📊 Analyser le métier"):
                st.query_params["nav"] = "tendance"
                st.rerun()

    nbr_offre_par_page = 20
    if "page_offset" not in st.session_state:
        st.session_state["page_offset"] = 0
    resultats = resultats.sort_values(by="TimesincePublication", ascending=True)
    offres_a_afficher = resultats.iloc[: st.session_state["page_offset"] + nbr_offre_par_page]

    # code pour afficher un résumé des offres   
    if "offre_selectionnee" not in st.session_state:
        st.session_state.offre_selectionnee = None
        
    modal = Modal("", key="offre_modal")
    st.markdown("---")  # Séparateur entre les offres
    for i in range(len(offres_a_afficher)):
            colA, colB = st.columns([1, 4])
            with st.container():
                if pd.notna(resultats.iloc[i]['CompanyLogo']) and resultats.iloc[i]['CompanyLogo']!= "":
                    with colA:
                        st.markdown(f"""
                        <style>
                            .logo {{
                                width: 200px;
                                height: auto; 
                                margin-right: 10px;
                                border-radius: 20px; 
                                border: 1px solid #ccc; 
                                padding: 10px; 
                                background-color: white;
                                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                            }}
                        </style>
                        <div>
                            <img class="logo" src="{resultats.iloc[i]['CompanyLogo']}">
                        </div>
                        """, unsafe_allow_html=True)
                    with colB:
                        st.markdown(f"**{resultats.iloc[i]['OfferTitle']}**") # ({resultats.iloc[i]['niveau_experience']})
                        st.write(f"{resultats.iloc[i]['CompanyName']}")
                    
                        col8, col9, col10, col11, col12, col13 = st.columns(6)
                        col8.write(f"📍 {(resultats.iloc[i]['Departement_affichage'])}")
                        col9.write(f"💼 {resultats.iloc[i]['ContractType']}")
                        with col10 :
                            if resultats.iloc[i]['DisplayedSalary'] != "NC":
                                st.write(f"💰 {resultats.iloc[i]['DisplayedSalary']}")
                            else:
                                ("")
                        
                        if resultats.iloc[i]['Telework'] != "NC":
                            st.write(f"🏠Télétravail {resultats.iloc[i]['Telework']}")
                        else:
                            ("")
                        st.markdown(f"*`Publiée depuis {resultats.iloc[i]['TimesincePublication']}`*")
                        with col13:
                            if st.button(f"Voir l'offre", key=f"btn_{i}"):
                                st.session_state.offre_selectionnee = i
                                modal.open()
                    st.markdown("---")  # séparateur entre les offres
    
    # bouton charger plus pour afficher plus d'offres
    if len(offres_a_afficher) < len(resultats):
        if st.button("Charger plus"):
            st.session_state["page_offset"] += nbr_offre_par_page
            st.rerun()  # Recharge la page avec les nouvelles offres
        
    # code d'affichage du détail de l'offre
    if modal.is_open() and st.session_state.offre_selectionnee is not None:
        offre = resultats.iloc[st.session_state.offre_selectionnee]
        
        with modal.container():
            st.markdown(f"# **{offre['OfferTitle']}**")
            st.write(offre['CompanyName'])
            st.markdown(f"📍 **{(offre['Departement_affichage'])}**")
            col13, col14, col5 = st.columns(3, gap="small")
            col13.markdown(f"**{offre['ContractType']}**")
            col14.markdown(f"""`{offre['DisplayedSalary']}`""")
            col5.markdown(f"**Télétravail:** {offre['Telework']}")
            
            st.markdown("### 📌 Description du poste")
            st.write(offre["Description_x"])

            st.markdown("### 🎯 Profil recherché")
            st.write(offre["Profile_x"])

            if pd.notna(offre["UrlOffre_x"]) and offre["UrlOffre_x"].strip() != "":
                url_complet = f"https://www.hellowork.com{offre['UrlOffre_x']}"
                st.link_button("Voir l'offre complète", url_complet)
            else:
                st.write("Aucun lien disponible.")
    return

def analyser_tendances(poste):
    st.title(f"📊 Analyse des tendances pour {poste}")
    st.write("Ici, j'afficherai les tendances du métier.")
    
    # retour à l'accueil
    if st.button("⬅ Retour"):
        st.query_params["nav"] = "accueil"
        st.rerun()

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
elif nav == "tendance":
    analyser_tendances()
else:
    st.write("Page non trouvée")
