import streamlit as st
import pandas as pd
import numpy as np
from streamlit_modal import Modal
import ast
import altair as alt
from wordcloud import WordCloud


#***********************************************************************************
# configuration de la page
st.set_page_config(layout="wide")
 
# initialisation de la page si n'existe pas encore dans session_state
if "page" not in st.session_state:
    st.session_state["page"] = "accueil"

#***********************************************************************************

# chargement des données en cache afin d'alléger le chargement des données sur la plateform

@st.cache_data
def load_data():
    df = pd.read_csv("./data/datasets/propre/df_clean3_nlp.csv", sep=',', index_col=0)
    if df is None or df.empty:
        st.error("Erreur : Le fichier CSV est vide ou introuvable.")
    return df

df_offres2 = load_data()

#***********************************************************************************

# fonction de tranformation des données
def preprocess_data(df):

    # fonction pour transformer les départements
    def transfo_departements(dept):
        if isinstance(dept, str):
            return ast.literal_eval(dept)
        else:
            return dept

    # fonction pour catégoriser la durée de publication
    def categoriser_duree(heures):
        if heures < 24:
            return f"{int(heures)}h"
        elif heures < 24 * 30:
            return f"{int(heures // 24)} jours"
        elif heures < 24 * 90:
            return "3 mois"
        else:
            return "plus de 3 mois"

    # transformer les départements
    df["Departement"] = df["Departement"].apply(transfo_departements)
    df["Departement_affichage"] = df["Departement"].apply(lambda x: " - ".join(x))

    # extraire toutes les localisations uniques
    all_departments = set()
    for department in df["Departement"]:
        all_departments.update(department)
    localisations_uniques = sorted(all_departments)

    # nettoyer et formater la colonne Telework
    df["Telework"] = df["Telework"].str.replace("Télétravail ", "").replace("NC", "Non communiqué")
    df["Telework"] = df["Telework"].str.capitalize()

    # nettoyer la colonne DisplayedSalary
    df["DisplayedSalary"] = df["DisplayedSalary"].replace("NC", "Non communiqué")

    # extraire la durée de publication
    df['PublishDate'] = pd.to_datetime(df['PublishDate'], errors='coerce')
    now = pd.Timestamp.now()
    df['OfferDuration'] = (now - df['PublishDate']).dt.total_seconds() / 3600  # Convertir en heures

    # catégoriser la durée de publication
    df['TimesincePublication'] = df['OfferDuration'].apply(categoriser_duree)

    # fonction pour transformer les compétences clés
    def transfo_competences(comp):
        if isinstance(comp, str):
            return ast.literal_eval(comp)
        else:
            return comp
    
    # transformer les compétences
    df["Competences_Clés"] = df["Competences_Clés"].apply(transfo_competences)
    df["Competences_Clés_affichage"] = df["Competences_Clés"].apply(lambda x: " - ".join(x))

    # extraire toutes les competences uniques
    all_competences = set()
    for competence in df["Competences_Clés"]:
        all_competences.update(competence)
    competences_uniques = sorted(all_competences)

    # fonction pour transformer les soft skills
    def transfo_soft_skills(skills):
        if isinstance(skills, str):
            return ast.literal_eval(skills)
        else:
            return skills
    
    # transformer les soft skills
    df["Soft_Skills"] = df["Soft_Skills"].apply(transfo_soft_skills)
    df["Soft_Skills_affichage"] = df["Soft_Skills"].apply(lambda x: " - ".join(x))

    # extraire toutes les competences uniques
    all_skills = set()
    for skill in df["Soft_Skills"]:
        all_skills.update(skill)
    skills_uniques = sorted(all_skills)

    # fonction pour transformer les soft skills
    def transfo_outils(outils):
        if isinstance(outils, str):
            return ast.literal_eval(outils)
        else:
            return outils
    
    # transformer les soft outils
    df["Outils"] = df["Outils"].apply(transfo_outils)
    df["Outils_affichage"] = df["Outils"].apply(lambda x: " - ".join(x))

    # extraire toutes les competences uniques
    all_outils = set()
    for skill in df["Outils"]:
        all_outils.update(skill)
    outils_uniques = sorted(all_outils)

    return df, localisations_uniques, competences_uniques, skills_uniques, outils_uniques

#***********************************************************************************

# fonction permettant de filtrer les données selon les choix de l'utilisateur
def filtrer_offres_emploi(df, Work_type, Departement, Domaine, ContractType, Salaire_Affiche, Salaire_Min, Telework, competences_cles, soft_skills, outils):
    masque = pd.Series([True] * len(df))
    masque_competences = pd.Series([True] * len(df))
    masque_soft_skills = pd.Series([True] * len(df))
    masque_outils = pd.Series([True] * len(df))

    if Work_type:
        masque &= df["categorie_metier"].str.contains(Work_type, case=False, na=False)

    if Departement:
        localisations_uniques = df_offres2["Departement"].unique().tolist()
        masque &= df["Departement"].isin(localisations_uniques)

    if Domaine:
        masque &= df["Domaine"].isin(Domaine)

    if ContractType:
        masque &= df["ContractType"].isin(ContractType)

    if Salaire_Affiche: 
        masque &= df["DisplayedSalary"].notna() 
        masque &= df["DisplayedSalary"] != "NC"

    if Salaire_Min is not None:  # Filtrer par salaire minimum
        # convertir la colonne "salaire_min" en numérique si ce n'est pas déjà le cas
        if Salaire_Min is not None and Salaire_Min > 0:
            if df["salaire_min"].dtype != "float64":
                df["salaire_min"] = pd.to_numeric(df["salaire_min"].astype(str).str.replace(" ", ""), errors='coerce')
            masque &= df["salaire_min"] >= Salaire_Min

    if Telework:
        if Telework:
            masque &= df["Telework"].isin(Telework)

    criteres_choisis = 0
    
    if competences_cles:
        masque_competences = df["Competences_Clés"].apply(lambda x: any(comp in competences_cles for comp in x))
        masque &= masque_competences
        criteres_choisis += 1

    if soft_skills:
        masque_soft_skills = df["Soft_Skills"].apply(lambda x: any(skill in soft_skills for skill in x))
        masque &= masque_soft_skills
        criteres_choisis += 1

    if outils:
        masque_outils = df["Outils"].apply(lambda x: any(outil in outils for outil in x))
        masque &= masque_outils
        criteres_choisis += 1

    if criteres_choisis > 0:
        masque_final = pd.Series([False] * len(df))
        for i in range(len(df)):
            if sum([masque_competences.iloc[i], masque_soft_skills.iloc[i], masque_outils.iloc[i]]) >= 3:
                masque_final.iloc[i] = True
        masque &= masque_final

    return df[masque]

#***********************************************************************************

# fonction définissant les fonctionnalités de la page d'acceuil
def accueil(df_offres2):
    if "Type de filtrage" not in st.session_state:
        st.session_state["Type de filtrage"] = "Critères de l'emploi"

    st.markdown(
            """
            <h1 style="font-size: 2em;">  Devenez l'expert DATA que vous souhaitez être.</h1>
            """,
            unsafe_allow_html=True,)
    st.markdown("""
        <div style='font-size:22px;'>
            <br><b>Bienvenue sur votre outil de recherche d’emploi dans la Data !</b><br>
            Que vous soyez étudiant, en transition professionnelle, consultant, employé en quête de nouvelles opportunités ou recruteur, cette plateforme vous aide à explorer le marché de l’emploi dans le secteur de la Data.<br><br>
            Afin de vous accompagner, nous mettons à votre disposition une plateforme qui vous permettra de :<br>
            <ul>
                <li><b>🔍 Affiner vos recherches</b> grâce à des :
                    <ul>
                        <li><b>Filtres personnalisés</b></li>
                        <li><b>Indicateurs clés</b></li>
                    </ul>
                </li>
                <li><b>📊 Analyser les tendances</b> du marché de l'emploi dans le secteur de la Data.</li>
            </ul>
            <br>
            Prêt à trouver votre prochaine opportunité dans la Data ?<b>
            Lancez votre recherche dès maintenant !</b><br>
        </div>
        """, unsafe_allow_html=True)

    # ajouter un espace avant les filtres de recherche
    st.markdown("<br>", unsafe_allow_html=True) 

    # formulaire de recherche
    
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            type_de_metier = st.selectbox("Choisissez une catégorie de métier", sorted(df_offres2["categorie_metier"].unique()), index=None, placeholder="Choisissez un métier")
            
        with col2:
            secteur_d_activite = st.multiselect("Domaine d'activité", sorted(df_offres2["Domaine"].unique()), placeholder="Choisissez un secteur d'activité")
            
        with col3:
            localisations_uniques = [item for sublist in df_offres2["Departement"].dropna() for item in sublist]
            localisations_uniques = list(set(localisations_uniques))
            localisation = st.multiselect("Département", localisations_uniques, placeholder="Choisissez un département")

        with col4:
            st.markdown("<br>", unsafe_allow_html=True)

            with st.popover("Filtres avancés"):
                st.markdown("""<h2 style='font-size: 18px; font-weight: bold;'>Des offres selon des critères de l'emploi ?</h2>""", unsafe_allow_html=True)
                st.markdown("""<p style='font-size: 18px; font-style: italic;'>Choisissez des critères suplémentaires pour affiner votre recherche.</p>""", unsafe_allow_html=True)
                
                type_de_contrat = st.multiselect("Type de contrat", sorted(df_offres2["ContractType"].unique()))

                st.write("Salaire minimum")
                if "salaire_filtre_active" not in st.session_state:
                    st.session_state["salaire_filtre_active"] = False

                afficher_salaire = st.checkbox("Afficher uniquement les offres avec salaire déclaré", value=st.session_state["salaire_filtre_active"])
                
                if "salaire_min" in df_offres2.columns:
                    filtered_salaries = df_offres2["salaire_min"].replace(0, np.nan).dropna()
                
                if not filtered_salaries.empty:
                    min_salary = df_offres2["salaire_min"].min()
                    max_salary = df_offres2["salaire_min"].max()
                    average_salary = df_offres2["salaire_min"].mean()
                    if afficher_salaire:
                        salary_value = st.slider("Sélectionner un salaire minimum", round(min_salary, 0), round(max_salary, 0), 0.0)
                    else:
                        salary_value = st.slider("Sélectionner un salaire minimum", round(min_salary, 0), round(max_salary, 0), 0.0, disabled=True)
                        st.session_state["salaire_filtre_active"] = False

                    # salaire mensuel
                    monthly_salary = round(salary_value / 12, 0)

                    # affichage
                    col4, col5, col6 = st.columns([1, 1, 1])
                    with col4:
                        st.markdown(f"""<p style='font-size: 18px; font-weight: bold;'>Annuel</p>""", unsafe_allow_html=True)
                        st.write(f"{salary_value} €")
                        with col5:
                            st.write(f"""<p style='font-size: 18px; font-weight: bold;'>Moyen</p>""", unsafe_allow_html=True)
                            st.write(f"{round(average_salary, 1)} €")
                        with col6:
                            st.write(f"""<p style='font-size: 18px; font-weight: bold;'>Mensuel</p>""", unsafe_allow_html=True)
                            st.write(f"{round(monthly_salary, 1)} €")
                
                    st.write("*Estimation salaire brut 35h/sem.*")
                else:
                    min_salary = max_salary = average_salary = 0

                
                df_offres2 = df_offres2.reset_index(drop=True)
                teletravail_options = sorted(df_offres2.loc[df_offres2["Telework"] != "Non communiqué", "Telework"].unique())
                if teletravail_options:
                    teletravail = st.multiselect("Télétravail", teletravail_options, key="teletravail_filter")

                st.markdown("---")

                st.markdown("""<h2 style='font-size: 18px; font-weight: bold;'>Des offres selon vos compétences ?</h2>""", unsafe_allow_html=True)
                st.markdown("""<p style='font-size: 18px; font-style: italic;'>Choisissez au moins trois (03) compétences qui correspondent le mieux à votre profil.</p>""", unsafe_allow_html=True)

                competences_cles_possibles = sorted(set(comp for lst in df_offres2["Competences_Clés"].dropna() for comp in lst))
                soft_skills_possibles = sorted(set(skill for lst in df_offres2["Soft_Skills"].dropna() for skill in lst))
                outils_possibles = sorted(set(outil for lst in df_offres2["Outils"].dropna() for outil in lst))

                competences_cles = st.multiselect("Compétences clés", options=competences_cles_possibles)
                soft_skills = st.multiselect("Soft skills", options=soft_skills_possibles)
                outils = st.multiselect("Outils", options=outils_possibles)

    # initialisation de la base contenant uniquement les résultats de recherche de l'utilisateur


    resultats = None 
    results = filtrer_offres_emploi(df_offres2, Work_type=type_de_metier, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire_Affiche=afficher_salaire, Salaire_Min=salary_value if "salaire_min" in df_offres2.columns else None, Telework=teletravail, competences_cles=competences_cles, soft_skills=soft_skills, outils=outils)
    if teletravail != "Non communiqué":
        results = filtrer_offres_emploi(df_offres2, Work_type=type_de_metier, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire_Affiche=afficher_salaire, Salaire_Min=salary_value if "salaire_min" in df_offres2.columns else None, Telework=None, competences_cles=competences_cles, soft_skills=soft_skills, outils=outils)

    # ajouter les colonnes description, profil et lien à la table filtrée utilisée pour les résultats de recherche
    
    resultats = pd.DataFrame(results)
    new = df_offres2[['Description', 'Profile', 'UrlOffre']] # definition d'un df n'utilisant que les colonnes à ajouter
    resultats = pd.merge(resultats, new, left_index=True, right_index=True, how='inner').reset_index() # merge des colonnes des 2 df
 
    # initialisation des valeurs des kpis à afficher

    nombre_annonces = len(resultats)
    nombre_entreprises = resultats["CompanyName"].nunique()
    nombre_cdi = len(resultats[resultats["ContractType"] == "CDI"])
    nombre_teletravail = len(resultats[resultats["Telework"] != "Non communiqué"]) if "Telework" in resultats.columns else 0

    # ajouter un espace avant les kpis
    st.markdown("<br>", unsafe_allow_html=True) 

    # code d'affichage des kpis sur l'ensemble des annonces
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📢 Annonces<br><b>{nombre_annonces}</b></div>""", unsafe_allow_html=True)
        with col2:
            col2.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>💼 CDI<br><b>{nombre_cdi}</b></div>""", unsafe_allow_html=True)
        with col3:
            col3.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🏢 Entreprises<br><b>{nombre_entreprises}</b></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🖥️ Télétravail<br><b>{nombre_teletravail}</b></div>""", unsafe_allow_html=True)
    
        
    # affichage d'un nombre d'offres minimum avec option "Afficher plus" et selon la date de publication
    nbr_offre_par_page = 20
    if "page_offset" not in st.session_state:
        st.session_state["page_offset"] = 0

    resultats = resultats.sort_values(by="TimesincePublication", ascending=True)
    offres_a_afficher = resultats.iloc[: st.session_state["page_offset"] + nbr_offre_par_page]


    # code pour afficher un résumé des offres selon les recherches de l'utilisateur
    # initialiser la variable "offre_selectionnee" à "0" si elle n'existe pas, puis mise à jour à chaque choix de l'utilisateur
    if "offre_selectionnee" not in st.session_state:
        st.session_state.offre_selectionnee = None

    # code d'affichage des offres selon les filtres de l'utilisateur

    modal = Modal("", key="offre_modal")
    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True) # Séparateur entre les offres

    for i in range(len(offres_a_afficher)):
            colA, colB = st.columns([1, 4])
            with st.container():
                if pd.notna(resultats.iloc[i]['CompanyLogo']) and resultats.iloc[i]['CompanyLogo']!= "":
                    with colA:
                        st.markdown(f"""
                        <style>
                            .logo-container {{
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                width: 200px;
                                height: 150px;
                            }}
                            .logo {{
                                width: 200px;
                                height: 120px; 
                                margin-right: 10px;
                                border-radius: 20px; 
                                border: 1px solid #ccc; 
                                padding: 10px; 
                                background-color: white;
                                box-shadow: 2px 2px 2px #C49BDA;
                            }}
                        </style>
                        <div>
                            <img class="logo" src="{resultats.iloc[i]['CompanyLogo']}">
                        </div>
                        """, unsafe_allow_html=True)
                    with colB:
                        st.markdown(f"""<h2 style='font-size: 35px; font-weight: bold;'>{resultats.iloc[i]['OfferTitle']}</h2>""", unsafe_allow_html=True)

                        col7, col8, col9 = st.columns([1, 1, 0.7])
                        col7.write(f"""<p style='font-size: 20px;'>{resultats.iloc[i]['CompanyName']}<p>""", unsafe_allow_html=True)
                        col8.write(f"""<p style='font-size: 20px;'>📍 {(resultats.iloc[i]['Departement_affichage'])}<p>""", unsafe_allow_html=True)
                        col9.markdown(f"""<p style="font-size: 18px; font-weight: none; text-shadow: 2px 2px 2px rgba(0,0,0,0.2);">🕒Publiée depuis {resultats.iloc[i]['TimesincePublication']}<p>""", unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        col10, col11, col12, col13 = st.columns([1, 0.5, 1, 0.5])
                        if resultats.iloc[i]['Telework'] != "NC":
                            col10.write(f"""<p style="font-size: 20px; font-weight: none;">🖥️Télétravail {resultats.iloc[i]['Telework']}<p>""", unsafe_allow_html=True)
                        else:
                            ("")

                        col11.write(f"""<p style="font-size: 20px; font-weight: none;">💼 {resultats.iloc[i]['ContractType']}<p>""", unsafe_allow_html=True)

                        with col12:
                            if resultats.iloc[i]['DisplayedSalary'] != "NC":
                                st.write(f"""<p style="font-size: 20px; font-weight: none;">💰 {resultats.iloc[i]['DisplayedSalary']}<p>""", unsafe_allow_html=True)
                            else:
                                ("")

                        with col13:
                            if st.button(f"Voir l'offre", key=f"btn_{i}"):
                                st.session_state.offre_selectionnee = i
                                modal.open()
                    
                    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)  # séparateur entre les offres
    
    # bouton charger plus d'offres
    if len(offres_a_afficher) < len(resultats):
        if st.button("Charger plus"):
            st.session_state["page_offset"] += nbr_offre_par_page
            st.rerun()  # Recharge la page avec les nouvelles offres
        
    # code d'affichage du détail de l'offre avec pop up
    if modal.is_open() and st.session_state.offre_selectionnee is not None:
        offre = resultats.iloc[st.session_state.offre_selectionnee]
        
        with modal.container():
            st.markdown(f"# **{offre['OfferTitle']}**")

            col13, col14 = st.columns([1,1])
            col13.write(f"""<p style='font-size: 30px;'>{offre['CompanyName']}<p>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col14.markdown(f"""<p style='font-size: 20px;'>📍{(offre['Departement_affichage'])}<p>""", unsafe_allow_html=True)

            col16, col17, col8 = st.columns([0.8, 1, 1])
            col16.markdown(f"""<p style='font-size: px;'>💼 {offre['ContractType']}<p>""", unsafe_allow_html=True)
            col17.markdown(f"""<p style='font-size: 18px;'>💰 {offre['DisplayedSalary']}<p>""", unsafe_allow_html=True)
            col8.markdown(f"""<p style='font-size: 18px;'>🖥️ Télétravail: {offre['Telework']}<p>""", unsafe_allow_html=True)
            
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

#***********************************************************************************

def analyser_tendances():
    import pandas as pd

    st.markdown("""
    <style>
        .block-container {
            padding-top: 60px;
            padding-bottom: 60px;
        }
        .stMarkdown {
            margin-bottom: 60px;
        }
    </style>
    """, unsafe_allow_html=True)



    st.title("📊 Analyse des Tendances des Métiers de la Data")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:28px;'>
    <br>Cette page vous permet d'analyser <b>les tendances actuelles du marché de l'emploi</b> dans les métiers de la Data.<br>
    Cette analyse est réalisée à partir des offres d'emploi récupérées sur divers sites spécialisés,
    assurant ainsi des tendances constamment mises à jour pour refléter le marché en temps réel.<br>
    <br>
    Vous trouverez ici <b>des indicateurs clés et des visualisations interactives</b> pour mieux comprendre
    l'évolution des offres, des salaires et des types de contrats tout en choisissant vos critères à l'aide des filtres ci-dessous.<br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

    # Conversion des dates
    df_offres2["PublishDate"] = pd.to_datetime(df_offres2["PublishDate"])


    # 🔹 **Correction des colonnes contenant des listes**
    def convertir_listes(colonne):
        return colonne.apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else [])

    df_offres2["Competences_Clés"] = convertir_listes(df_offres2["Competences_Clés"])
    df_offres2["Outils"] = convertir_listes(df_offres2["Outils"])
    df_offres2["Soft_Skills"] = convertir_listes(df_offres2["Soft_Skills"])

    # --- Filtres interactifs ---
    st.markdown("## 🔹 Critères d'analyse")
    col1, col2, col3 = st.columns([0.3, 0.2, 0.5])

    with col1:
        Métier = col1.selectbox("Métier", ["Tous"] + sorted(df_offres2["categorie_metier"].unique()))
        Domaine = col1.selectbox("Domaine", ["Tous"] + sorted(df_offres2["Domaine"].unique()))

    with col3:
        # st.markdown("### 🔹 Filtres disponibles")
        st.markdown("""
                    <div style='font-size:24px;'>
                    <br>🔹 Sélectionnez un métier et un domaine pour affiner votre recherche.
                    <br><br>
                    🔹 Les résultats seront mis à jour dynamiquement en fonction de vos choix.<br>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)


    # --- Filtrage des données ---
    filtered_df = df_offres2.copy()
    if Métier != "Tous":
        filtered_df = filtered_df[filtered_df["categorie_metier"] == Métier]
    if Domaine != "Tous":
        filtered_df = filtered_df[filtered_df["Domaine"] == Domaine]


    #####################################################################

    # --- Section 1 : Indicateurs Clés ---
    st.markdown("## 🔹 Indicateurs Clés")

    # --- KPIs Dynamiques ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📌 Nombre d'offres<br><b>{len(filtered_df)}</b></div>""", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🏢 Entreprises<br><b>{filtered_df['CompanyName'].nunique()}</b></div>""", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📆 Offres récentes<br><b>{filtered_df[filtered_df['PublishDate'] >= pd.Timestamp.today() - pd.DateOffset(days=30)].shape[0]}</b></div>""", unsafe_allow_html=True)
    with kpi4:
        filtered_df.rename(columns={"salaire_min": "Salaire Minimum", "salaire_max": "Salaire Maximum"}, inplace=True)
        df_salaire2 = filtered_df[["Salaire Minimum", "Salaire Maximum"]].dropna()  # Supprime les NaN
        df_salaire2["Salaire Moyen"] = df_salaire2[["Salaire Minimum", "Salaire Maximum"]].mean(axis=1)
        salaire_moyen_selection = df_salaire2["Salaire Moyen"].mean()
        st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>💰 Salaire Moyen<br><b>{salaire_moyen_selection:.0f} €</b></div>""", unsafe_allow_html=True)


    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

    ##################################################################

    # --- Section 2 : Contrats & Télétravail ---

    st.markdown("## 🔹 Analyse des Contrats et Télétravail")

    col1, col2 = st.columns(2)

    col1.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Offres par Type de Contrat<b></div>""", unsafe_allow_html=True)

    # 1 Jauges Contrat

    import plotly.graph_objects as go

    df_contrats = filtered_df["ContractType"].value_counts().reset_index()
    df_contrats.columns = ["Type de contrat", "Nombre"]

    # Filtrer uniquement les types de contrats souhaités
    contrats_cibles = ["CDI", "CDD", "Alternance", "Indépendant/Freelance"]
    df_contrats_filtered = df_contrats[df_contrats["Type de contrat"].isin(contrats_cibles)]

    # Définir la plage max pour normaliser les jauges
    max_offres = df_contrats_filtered["Nombre"].max()

    # Définition des positions des jauges avec des **marges verticales améliorées**
    positions = {
        "CDI": {'x': [0, 0.5], 'y': [0.6, 1]},  # Haut gauche
        "CDD": {'x': [0.5, 1], 'y': [0.6, 1]},  # Haut droite
        "Indépendant/Freelance": {'x': [0, 0.5], 'y': [0, 0.4]},  # Bas gauche
        "Alternance": {'x': [0.5, 1], 'y': [0, 0.4]}  # Bas droite
    }

    # Couleurs pour chaque type de contrat
    couleurs = {
        "CDI": "#6a0dad",  # Violet foncé
        "CDD": "#c084fc",  # Violet clair
        "Alternance": "#9b59b6",  # Mauve
        "Indépendant/Freelance": "#d1a3ff"  # Rose-violet
    }

    # Création de la figure avec 4 jauges
    fig_contrats_jauge = go.Figure()

    for contrat, nombre in zip(df_contrats_filtered["Type de contrat"], df_contrats_filtered["Nombre"]):
        fig_contrats_jauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=nombre,
            title={'text': f"<b>{contrat}</b>", 'font': {'size': 16, 'color': 'black'}},  # Taille du titre ajustée
            gauge={
                'axis': {'range': [0, max_offres]},
                'bar': {'color': couleurs[contrat]},
                'steps': [{'range': [0, max_offres], 'color': "#f2e6ff"}]  # Couleur de fond plus claire
            },
            domain=positions[contrat]
        ))

    # Ajustement de la mise en page pour éviter le chevauchement
    fig_contrats_jauge.update_layout(margin=dict(t=80, b=10))  # t = top, b = bottom

    # Affichage dans col1
    col1.plotly_chart(fig_contrats_jauge, use_container_width=True)

    ##################################################################

    #2 Télétravail

    col2.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Répartition du Télétravail<b><br><br></div>""", unsafe_allow_html=True)

    # Filtrer uniquement les valeurs valides (exclure "NC")
    df_telework = filtered_df[filtered_df["Telework"] != "NC"]["Telework"].value_counts().reset_index()
    df_telework.columns = ["Type de Télétravail", "Nombre"]

    # Définir les couleurs
    colors = ["#6a0dad", "#c084fc"]  # Violet foncé et violet clair

    # Graphique en Anneau avec annotations et sans légende
    import plotly.express as px
    fig2 = px.pie(
        df_telework, 
        names="Type de Télétravail", 
        values="Nombre", 
        # title="Répartition du Télétravail", 
        color_discrete_sequence=px.colors.sequential.Purples_r, 
        hole=0.6
    )

    # Mise en forme pour afficher les labels à l'extérieur avec des lignes de liaison
    fig2.update_traces(
        textinfo='text+label',  # Affiche les pourcentages et les labels
        textposition='outside',  # Positionne les labels à l'extérieur
        marker=dict(colors=colors),
        textfont=dict(size=16, color='black'),
        text=df_telework["Nombre"].astype(str) + " offres"
        # pull=[0.1] * len(df_telework)  # Éloigne légèrement les tranches pour meilleure lisibilité
    )

    # Suppression de la légende
    fig2.update_layout(showlegend=False)

    # Affichage dans Streamlit
    col2.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

    ##################################################################

    # --- Section 3 : Salaires ---

    st.markdown("## 🔹 Analyse des Salaires")

    col1, col2, col3 = st.columns([0.45, 0.1, 0.45])

    col1.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Répartition des Salaires<b></div>""", unsafe_allow_html=True)

    import plotly.express as px

    # ---- Nettoyage des données ----
    filtered_df.rename(columns={"salaire_min": "Salaire Minimum", "salaire_max": "Salaire Maximum"}, inplace=True)
    df_salaire = df_salaire2.melt(var_name="Type de Salaire", value_name="Montant")  # Transformation pour boxplot

    # ---- Création du Boxplot ----
    fig_box = px.box(df_salaire, 
                    x="Type de Salaire", 
                    y="Montant", 
                    color="Type de Salaire",
                    color_discrete_sequence=px.colors.sequential.Purples_r,
                    boxmode="overlay")  # Superposition pour voir les différences

    # ---- Mise en page ----
    fig_box.update_layout(yaxis_title="Salaire (€)",
                        xaxis_title="",
                        plot_bgcolor="white",
                        showlegend=False)

    # ---- Affichage dans Streamlit ----
    col1.plotly_chart(fig_box, use_container_width=True)

    col3.markdown("""
                    <div style='font-size:22px;'>
                    <br><br><br><br><br>Ce boxplot compare la répartition des salaires minimum et maximum proposés dans les offres d'emploi.<br>
                    <br>Chaque boîte représente la distribution des salaires, avec la ligne centrale indiquant la médiane.
                    Les extrémités des moustaches montrent l'étendue des salaires, tandis que les points au-delà sont des valeurs atypiques (offres très élevées ou très basses).<br>
                    <br>Ce visuel permet d'identifier la variabilité des rémunérations et de repérer d'éventuelles disparités entre les salaires annoncés.
                    </div>
                    """, unsafe_allow_html=True)

    col3.markdown("<br>", unsafe_allow_html=True)

    ###########

    # ---- histogramme + KDE ----

    col1.markdown("""
                    <div style='font-size:22px;'>
                    <br><br><br><br><br>Ce graphique illustre la distribution des salaires moyens issus des offres d'emploi analysées.<br>
                    <br>L'histogramme représente la fréquence des salaires moyens, tandis que la courbe superposée montre la densité de distribution, permettant d'observer la tendance générale.<br>
                    <br>Ce visuel met en évidence la répartition des salaires en fonction des offres disponibles, en révélant les plages de salaires les plus courantes ainsi que la présence éventuelle de salaires plus rares et extrêmes.<br>
                    </div>
                    """, unsafe_allow_html=True)

    col1.markdown("<br>", unsafe_allow_html=True)

    col3.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Distribution des Salaires Moyens<b></div>""", unsafe_allow_html=True)

    import plotly.figure_factory as ff

    df_salaire = filtered_df[["Salaire Minimum", "Salaire Maximum"]].dropna()  # Suppression des NaN
    df_salaire["Salaire Minimum"] = pd.to_numeric(df_salaire["Salaire Minimum"], errors="coerce")
    df_salaire["Salaire Maximum"] = pd.to_numeric(df_salaire["Salaire Maximum"], errors="coerce")
    df_salaire["Salaire Moyen"] = df_salaire[["Salaire Minimum", "Salaire Maximum"]].mean(axis=1)

    fig_kde = ff.create_distplot(
        [df_salaire["Salaire Moyen"]], 
        group_labels=["Distribution des Salaires"], 
        colors=["#6a0dad"],  # Teinte violette Purples_r
        bin_size=5000,  # Ajuster selon la dispersion des salaires
        show_hist=True,  # Afficher l'histogramme
        show_curve=True,  # Activer la courbe KDE
        curve_type="kde",  # Lissage via KDE
        show_rug=False
    )

    # ---- Mise en page du graphique ----
    fig_kde.update_layout(
        showlegend=False,
        xaxis_title="Salaire (€)",
        yaxis_title="Densité",
        plot_bgcolor="white"
    )

    # ---- Affichage dans Streamlit ----
    col3.plotly_chart(fig_kde, use_container_width=True)

    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

    ##################################################################

    # --- Section 4 : Carte et Graphique Temporelle ---

    st.markdown("## 🔹 Répartition Géographique et Offres dans le temps")

    col1, col2, col3 = st.columns([0.5, 0.1, 0.4])

    #CARTES#
    with col1:
        import pandas as pd
        import folium
        
        # ---- Interface utilisateur ----
        st.markdown(f"""<div style='font-size: 26px; margin-left: 100px;'><b>🗺️ Offres d'Emploi par Région<b></div>""", unsafe_allow_html=True)

        # ---- Étape 1 : Transformer les chaînes en listes et éclater les valeurs ----
        filtered_df["Region"] = filtered_df["Region"].astype(str).apply(lambda x: x.replace("[", "").replace("]", "").replace("'", "").split(", "))  # Nettoyage et conversion en liste
        df_exploded = filtered_df.explode("Region").reset_index(drop=True)  # Éclater les valeurs

        # ---- Étape 2 : Compter le nombre d'offres par région ----
        df_grouped = df_exploded["Region"].value_counts().reset_index()
        df_grouped.columns = ["Region", "Nombre"]

        # ---- Étape 3 : Dictionnaire des coordonnées fixes (évite le géocodage) ----
        coords_regions = {
            "Île-de-France": [48.8566, 2.3522],
            "Auvergne-Rhône-Alpes": [45.75, 4.85],
            "Occitanie": [43.6045, 1.444],
            "Nouvelle-Aquitaine": [44.8378, -0.5792],
            "Provence-Alpes-Côte d'Azur": [43.2965, 5.3698],
            "Grand Est": [48.5734, 7.7521],
            "Bretagne": [48.1173, -1.6778],
            "Pays de la Loire": [47.2184, -1.5536],
            "Hauts-de-France": [50.6292, 3.0573],
            "Normandie": [49.1829, -0.3707],
            "Centre-Val de Loire": [47.9029, 1.9087],
            "Bourgogne-Franche-Comté": [47.322, 5.0415],
            "Corse": [41.9272, 8.7346]
        }

        # ---- Étape 4 : Ajouter les coordonnées depuis le dictionnaire ----
        df_grouped["Latitude"] = df_grouped["Region"].map(lambda x: coords_regions.get(x, [None, None])[0])
        df_grouped["Longitude"] = df_grouped["Region"].map(lambda x: coords_regions.get(x, [None, None])[1])

        # ---- Supprimer les valeurs non géolocalisées ----
        df_grouped = df_grouped.dropna(subset=["Latitude", "Longitude"])

        # ---- Étape 5 : Création de la carte Folium centrée sur la France ----
        m = folium.Map(location=[46.603354, 1.888334], zoom_start=6, tiles="CartoDB positron")  # Zoom ajusté

            # ---- Étape 6 : Ajouter les bulles sur la carte avec taille équilibrée ----
        import numpy as np
        min_radius = 10
        max_radius = 60  # Taille max pour éviter des bulles trop grandes
        df_grouped["radius"] = df_grouped["Nombre"].apply(lambda x: np.log(x + 1) * 4)  # Ajustement logarithmique

        for _, row in df_grouped.iterrows():
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=max(min(row["radius"], max_radius), min_radius),  # Ajustement des tailles
                color="purple",
                fill=True,
                fill_color="purple",
                fill_opacity=0.6,
                popup=f"{row['Region']}: {row['Nombre']} offres"
            ).add_to(m)

        # ---- Ajustement automatique du zoom pour afficher toutes les bulles ----
        bounds = [[row["Latitude"], row["Longitude"]] for _, row in df_grouped.iterrows()]
        if bounds:
            m.fit_bounds(bounds)

        # ---- Étape 7 : Affichage dans Streamlit ----
        st.components.v1.html(m._repr_html_(), height=600)

    with col3:
        
        st.markdown("""
                    <div style='font-size:22px;'>
                    <br><br><br><br><br>Cette carte interactive affiche la répartition des offres d’emploi en France par région et permet d'identifierrapidement les régions les plus dynamiques.<br>
                    <br>Chaque bulle représente une région, avec une taille proportionnelle au nombre d’offres disponibles.<br>
                    Plus la bulle est grande et foncée, plus la région concentre d’opportunités.<br>
                    <br>En cliquant sur une bulle, le nombre total d’offres apparaît. Ce visuel permet d’identifier rapidement les régions les plus dynamiques en matière d’emploi.
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    ###################################################################

    st.markdown(f"""<div style='font-size: 26px; margin-left: 100px;'><b>📈 Évolution quotidienne des offres d'emploi<b></div>""", unsafe_allow_html=True)

    # Évolution journalière des offres
    df_trend_daily = filtered_df.groupby(df_offres2["PublishDate"].dt.strftime('%Y-%m-%d')).size().reset_index(name="Nombre d'offres")

    # Création d'un graphique en aires avec granularité journalière
    fig_area = px.area(
        df_trend_daily,
        x="PublishDate",
        y="Nombre d'offres",
        # title="📈 Évolution quotidienne des offres d'emploi",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#6a0dad"],  # Nuance de violet
    )

    # Améliorations visuelles
    fig_area.update_layout(
        xaxis_title="Date",
        yaxis_title="Nombre d'offres",
        xaxis=dict(type="category", tickangle=-45),
        margin=dict(l=50, r=50, t=50, b=50),
        plot_bgcolor="white",
    )

    # Affichage dans Streamlit
    st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

    ###################################################################

    # --- Section 5 : Entreprises et Secteurs d'Activité ---

    st.markdown("## 🔹 Entreprises et Secteurs d'activité")


    # Domaine
    col1, col2 = st.columns(2)

    df_secteurs = filtered_df["Domaine"].value_counts().reset_index()
    df_secteurs.columns = ["Secteur", "Nombre"]

    # Répartition des domaines
    fig2 = alt.Chart(df_secteurs).mark_bar().encode(
        x='Nombre:Q',
        y=alt.Y('Secteur:N', sort='-x'),
        color=alt.Color('Secteur:N', scale=alt.Scale(scheme='purples'))
    ).properties(title="")
    col1.altair_chart(fig2, use_container_width=True)

    with col2:
        st.markdown(
            """
            ### 🏢 Répartition des offres par secteur d'activité
            <br><div style='font-size:22px;'>
            Ce graphique permet d’identifier les secteurs d'activité les plus 
            dynamiques en termes de recrutement. 
            
            En un coup d'œil, il est possible de repérer les domaines où la demande 
            est la plus forte, offrant ainsi des insights précieux sur les tendances 
            actuelles du marché.</div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    ###################################################################
    # Entreprises
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 📊 Les Entreprises qui recrutent
            <br><div style='font-size:22px;'>
            Ce graphique met en avant les entreprises qui proposent le plus d'offres 
            en fonction des critères de filtrage appliqués. Plus un nom est grand, 
            plus l'entreprise est présente dans les offres disponibles.
            
            Cela permet d’identifier rapidement les principaux employeurs du marché, 
            offrant ainsi une vision des acteurs majeurs du recrutement.</div>
            """,
            unsafe_allow_html=True
        )


    # WordCloud présence Entreprises
    entreprises_freq = filtered_df["CompanyName"].value_counts().to_dict()

    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    wordcloud = WordCloud(
        width=600,
        height=200,
        background_color="white",  # Peut être adapté pour le mode sombre
        colormap="Purples",
        max_words=50  # Limite le nombre d'entreprises affichées
    ).generate_from_frequencies(entreprises_freq)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")  # Supprimer les axes
    col2.pyplot(fig)

    st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)


    ###################################################################

    # --- Section 6 : Analyse des Compétences, Outils et Soft Skills ---

    st.markdown("""
    ## 🔷 Analyse des compétences clés, outils et soft skills demandés

    <div style='font-size:22px;'>
    <br>L’analyse des offres d’emploi permet d’identifier les compétences techniques, les outils utilisés et les soft skills les plus recherchés par les employeurs.

    Ces éléments sont essentiels pour comprendre les attentes du marché et ajuster son profil en conséquence.
    </div>
    """, unsafe_allow_html=True)

    col3, col4, col5 = st.columns(3)
    with col3:
        st.markdown(
            """
            <div style="text-align: center; font-size: 26px; font-weight: bold;">
            Compétences Clés
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
            <div style="text-align: center; font-size: 26px; font-weight: bold;">
            Outils
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            """
            <div style="text-align: center; font-size: 26px; font-weight: bold;">
            Soft Skills
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- Analyse compétences
    df_competences = pd.DataFrame([item for sublist in filtered_df["Competences_Clés"] for item in sublist], columns=["Compétence"])
    df_competences = df_competences["Compétence"].value_counts().reset_index()
    df_competences.columns = ["Compétences", "Nombre d'offres"]

    # --- Analyse outils
    df_outils = pd.DataFrame([item for sublist in filtered_df["Outils"] for item in sublist], columns=["Outil"])
    df_outils = df_outils["Outil"].value_counts().reset_index()
    df_outils.columns = ["Outils", "Nombre d'offres"]

    # --- Analyse Soft Skills
    df_soft_skills = pd.DataFrame([item for sublist in filtered_df["Soft_Skills"] for item in sublist], columns=["Soft Skill"])
    df_soft_skills = df_soft_skills["Soft Skill"].value_counts().reset_index()
    df_soft_skills.columns = ["Soft Skills", "Nombre d'offres"]

    ######################################################
    # 3 WordClouds
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    # --- Fonction mise à jour pour refléter les fréquences correctes ---
    def afficher_wordcloud_v2(df, colonne, titre):
        # Convertir les valeurs et les pondérer selon leur fréquence
        mots_frequences = {row[colonne]: row["Nombre d'offres"] for _, row in df.iterrows()}
        
        wordcloud = WordCloud(width=600, height=300, background_color="white",
                            colormap="Purples", collocations=False,
                            prefer_horizontal=1,  # Favoriser l'affichage horizontal
                            normalize_plurals=False).generate_from_frequencies(mots_frequences)

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.set_title(titre, fontsize=12, loc="left")  # Aligné à gauche
        ax.axis("off")  # Suppression des axes
        
        return fig

    # --- Word Cloud Compétences Clés ---
    fig_wc_comp = afficher_wordcloud_v2(df_competences, "Compétences", "")
    col3.pyplot(fig_wc_comp, use_container_width=True)

    # --- Word Cloud Outils ---
    fig_wc_outils = afficher_wordcloud_v2(df_outils, "Outils", "")
    col4.pyplot(fig_wc_outils, use_container_width=True)

    # --- Word Cloud Soft Skills ---
    fig_wc_soft = afficher_wordcloud_v2(df_soft_skills, "Soft Skills", "")
    col5.pyplot(fig_wc_soft, use_container_width=True)

    ################################################################
    # 3 graphiques en barres

    # Trier les compétences par ordre décroissant
    df_competences = df_competences.sort_values(by="Nombre d'offres", ascending=True)

    fig3 = px.bar(df_competences, x="Nombre d'offres", y="Compétences", orientation='h', 
                title="", 
                color_discrete_sequence=px.colors.sequential.Purples_r)

    # Mettre à jour l'ordre des catégories sur l'axe Y
    fig3.update_layout(yaxis=dict(categoryorder="total ascending"))

    col3.plotly_chart(fig3, use_container_width=True)



    # Trier les outils par ordre décroissant
    df_outils = df_outils.sort_values(by="Nombre d'offres", ascending=True)

    fig4 = px.bar(df_outils, x="Nombre d'offres", y="Outils", orientation='h', 
                title="", 
                color_discrete_sequence=px.colors.sequential.Purples_r)

    # Mettre à jour l'ordre des catégories sur l'axe Y
    fig4.update_layout(yaxis=dict(categoryorder="total ascending"))

    col4.plotly_chart(fig4, use_container_width=True)

    # Trier les Soft Skills par ordre décroissant
    df_soft_skills = df_soft_skills.sort_values(by="Nombre d'offres", ascending=True)

    fig5 = px.bar(df_soft_skills, x="Nombre d'offres", y="Soft Skills", orientation='h', 
                title="", 
                color_discrete_sequence=px.colors.sequential.Purples_r)

    # Mettre à jour l'ordre des catégories sur l'axe Y
    fig5.update_layout(yaxis=dict(categoryorder="total ascending"))

    col5.plotly_chart(fig5, use_container_width=True)


    

#*********************************************************************************************

def afficher_raison_wildfindjob():
    st.title("A propos de Wild Find Job")
    st.text("Wild Find Job est un projet de......")

#*********************************************************************************************

# paramètres barre de navigation et affichage des pages

st.markdown("""
<style>
.nav-bar {
    display: flex;
    align-items: center;  
    justify-content: space-between; 
    /*padding: 20px;*/
    /*border-radius: 20px;*/
}
.nav-link {
    padding: 10px 30px; /* Ajuster le padding pour une meilleure apparence */
    background-color:white;
    color: rgb(148, 73, 189) !important;
    border-radius: 16px;
    border: none;
    cursor: pointer;
    display: inline-block;
    font-weight: bold;
    text-align: center;
    text-decoration: none !important;
    font-size: 25px;
    margin: 4px 2px;
    box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.3);
    transition: background 0.3s;
}
.nav-link:hover {
    background-color:rgb(201, 183, 211);
}
.logo-h1 { 
    margin-right: 0px
}
.logo-text { 
    font-size: 60px;
    font-weight: bold;
    color:black;
    font-family: Arial, sans-serif;
}

</style>
""", unsafe_allow_html=True)

# Barre de navigation (dans un seul conteneur)
st.markdown("""
<div class="nav-bar">
    <div class="logo-h1">
        <h1 class="logo-text">Wild Find Job</h1>
    </div>
    <div class="nav-buttons">  <a href="?page=accueil" class="nav-link">Accueil</a>
        <a href="?page=analyse" class="nav-link">Analyse des tendances</a>
    </div>
</div>
""", unsafe_allow_html=True)


# Gestion des paramètres et affichage des pages (inchangé)
params = st.query_params
current_page = params.get("page", "accueil")

if current_page == "accueil":
    df_offres2 = load_data()
    preprocess_data(df_offres2) 
    accueil(df_offres2)

elif current_page == "analyse":
    analyser_tendances()
# elif current_page == "a_propos":
#     afficher_raison_wildfindjob()
else:
    st.write("Page non trouvée")