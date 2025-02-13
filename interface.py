import streamlit as st
import pandas as pd
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

# chargement des données en cache afin d'alléger le chargement des données sur la plateforme
@st.cache_data
def load_data():
    return pd.read_csv("./data/datasets/propre/df_clean2_nlp.csv", sep=',', nrows=200)

df_offres2 = load_data() 

#***********************************************************************************

# code de transformation de certaines colonnes nécessaires pour l'affichage
# extraire les départements uniques
def transfo_departements(dept):
    if isinstance(dept, str):
        return ast.literal_eval(dept)
    else:
        return dept

df_offres2["Departement"] = df_offres2["Departement"].apply(transfo_departements)
df_offres2["Departement_affichage"] = df_offres2["Departement"].apply(lambda x: " - ".join(x))
df_offres2["Telework"] = df_offres2["Telework"].str.replace("Télétravail ", "").str.capitalize()

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

#***********************************************************************************

# fonction permettant de filtrer les données selon les choix de l'utilisateur
def filtrer_offres(df, OfferTitle, Departement, Domaine, ContractType, Salaire_Affiche, Salaire_Min, Telework):
    masque = pd.Series([True] * len(df))

    if OfferTitle:
        masque &= df["OfferLabel"].str.contains(OfferTitle, case=False, na=False)
    if Departement:
        masque &= df["Departement"].isin(localisations_uniques)

    if Domaine:
        masque &= df["Domaine"].isin(Domaine)
    if ContractType:
        masque &= df["ContractType"].isin(ContractType)

    if Salaire_Affiche: 
        masque &= df["DisplayedSalary"].notna() 
        masque &= df["DisplayedSalary"] != "NC"

    if Salaire_Min is not None:  # Filtrer par salaire minimum
        # Convertir la colonne "salaire_min" en numérique si ce n'est pas déjà le cas
        if Salaire_Min is not None and Salaire_Min > 0:
            if df["salaire_min"].dtype != "float64":
                df["salaire_min"] = pd.to_numeric(df["salaire_min"].astype(str).str.replace(" ", ""), errors='coerce')
            masque &= df["salaire_min"] >= Salaire_Min

    if Telework:
        if Telework:
            masque &= df["Telework"].isin(Telework)
    return df[masque]

#***********************************************************************************

# fonction définissant les fonctionnalités de la page d'acceuil
def accueil():

    st.markdown(
            """
            <h1 style="font-size: 2em;">  Devenez l'expert DATA <br> que vous souhaitez être.</h1>
            """,
            unsafe_allow_html=True,)

    # formulaire de recherche
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            intitule_poste = st.selectbox("Intitulé du poste", sorted(df_offres2["OfferLabel"].unique()), index=None, placeholder="Choisissez un métier")
        
        with col2:
            localisation = st.multiselect("Département", localisations_uniques, placeholder="Choisissez un département")
        
        with col3:
            with st.popover("Filtres avancés"): # affichage des filtres sous forme de pop up à proximité de l'élément
                
                type_de_contrat = st.multiselect("Type de contrat", sorted(df_offres2["ContractType"].unique()))

                st.write("Salaire minimum")
                if "salaire_filtre_active" not in st.session_state:
                    st.session_state["salaire_filtre_active"] = False

                afficher_salaire = st.checkbox("Afficher uniquement les offres avec salaire déclaré", value=st.session_state["salaire_filtre_active"])
                
                if "salaire_min" in df_offres2.columns:
        
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
                    col4, col5, col6 = st.columns(3)
                    with col4:
                        st.write("Annuel")
                        st.write(f"{salary_value} €")
                        with col5:
                            st.write("Moyen")
                            st.write(f"{round(average_salary, 1)} €")
                        with col6:
                            st.write("Mensuel")
                            st.write(f"{round(monthly_salary, 1)} €")

                    st.write("*Estimation salaire brut 35h/sem.*")


                secteur_d_activite = st.multiselect("Secteur d'activité", sorted(df_offres2["Domaine"].unique()))

                df_offres2["Telework"] = df_offres2["Telework"].str.replace("Télétravail ", "").str.capitalize()
                teletravail_options = sorted(set(df_offres2["Telework"].dropna().unique()) - {"NC"})
                teletravail = st.multiselect("Télétravail", teletravail_options, key="teletravail_filter")

    # initialisation de la base contenant uniquement les résultats de recherche de l'utilisateur

    resultats = None 
            
    results = filtrer_offres(df_offres2, OfferTitle=intitule_poste, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire_Affiche=afficher_salaire, Salaire_Min=salary_value if "salaire_min" in df_offres2.columns else None, Telework=teletravail)
    if teletravail != "NC":
        results = filtrer_offres(df_offres2, OfferTitle=intitule_poste, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire_Affiche=afficher_salaire, Salaire_Min=salary_value if "salaire_min" in df_offres2.columns else None, Telework=teletravail) 
    else:
        results = filtrer_offres(df_offres2, OfferTitle=intitule_poste, Departement=localisation, Domaine=secteur_d_activite, ContractType=type_de_contrat, Salaire_Affiche=afficher_salaire, Salaire_Min=salary_value if "salaire_min" in df_offres2.columns else None, Telework=None) 
    
    # ajouter les colonnes description, profil et lien à la table filtrée utilisée pour les résultats de recherche

    resultats = pd.DataFrame(results)
    new = df_offres2[['Description', 'Profile', 'UrlOffre']] # definition d'un df n'utilisant que les colonnes à ajouter
    resultats = pd.merge(resultats, new, left_index=True, right_index=True, how='inner').reset_index() # merge des colonnes des 2 df
        
    resultats.drop(columns='Unnamed: 0', inplace=True) # suppression des colonnes inutiles
        
    # initialisation des valeurs des kpis à afficher

    nombre_annonces = len(resultats)
    nombre_entreprises = resultats["CompanyName"].nunique()
    nombre_cdi = len(resultats[resultats["ContractType"] == "CDI"])
    nombre_teletravail = len(resultats[resultats["Telework"] != "NC"])


    # code d'affichage des kpis sur l'ensemble des annonces
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📢 Annonces<br><b>{nombre_annonces}</b></div>""", unsafe_allow_html=True)
        with col2:
            col2.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>💼 CDI<br><b>{nombre_cdi}</b></div>""", unsafe_allow_html=True)
        with col3:
            col3.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🏢 Entreprises<br><b>{nombre_entreprises}</b></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🖥️ Télétravail<br><b>{nombre_teletravail}</b></div>""", unsafe_allow_html=True)
    
        
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
                        st.markdown(f"**{resultats.iloc[i]['OfferTitle']}**")
                        st.write(f"{resultats.iloc[i]['CompanyName']}")
                    
                        col8, col9, col10, col11 = st.columns(4)
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
                        with col11:
                            if st.button(f"Voir l'offre", key=f"btn_{i}"):
                                st.session_state.offre_selectionnee = i
                                modal.open()
                    st.markdown("---")  # séparateur entre les offres
    
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

#***********************************************************************************

def analyser_tendances():
    import pandas as pd

    # --- Configuration de la page ---

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

    st.markdown("""
    <div style='font-size:22px;'>
    <br>Cette page vous permet d'analyser <b>les tendances actuelles du marché de l'emploi</b> dans les métiers de la Data.<br>
    Cette analyse est réalisée à partir des offres d'emploi récupérées sur divers sites spécialisés,
    assurant ainsi des tendances constamment mises à jour pour refléter le marché en temps réel.<br>
    <br>
    Vous trouverez ici <b>des indicateurs clés et des visualisations interactives</b> pour mieux comprendre
    l'évolution des offres, des salaires et des types de contrats tout en choisissant vos critères à l'aide des filtres ci-dessous.<br>
    </div>
    """, unsafe_allow_html=True)

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
    col1, col2, col3, col4 = st.columns(4)

    domaine = col1.selectbox("Métier", ["Tous"] + sorted(df_offres2["OfferLabel"].unique()))
    contrat = col2.selectbox("Type de contrat", ["Tous"] + sorted(df_offres2["ContractType"].unique()))
    entreprise = col3.selectbox("Entreprise", ["Tous"] + sorted(df_offres2["CompanyName"].unique()))
    teletravail = col4.selectbox("Télétravail", ["Tous"] + sorted(df_offres2["Telework"].unique()))

    st.markdown("<br>", unsafe_allow_html=True)
    # --- Filtrage des données ---
    filtered_df = df_offres2.copy()
    if domaine != "Tous":
        filtered_df = filtered_df[filtered_df["OfferLabel"] == domaine]
    if contrat != "Tous":
        filtered_df = filtered_df[filtered_df["ContractType"] == contrat]
    if entreprise != "Tous":
        filtered_df = filtered_df[filtered_df["CompanyName"] == entreprise]
    if teletravail != "Tous":
        filtered_df = filtered_df[filtered_df["Telework"] == teletravail]
    
    # --- Section 1 : Répartition du Marché ---
    st.markdown("## 🔹 Répartition du marché de l'emploi")

    # --- KPIs Dynamiques ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📢 Nombre d'offres<br><b>{len(filtered_df)}</b></div>""", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🏢 Entreprises<br><b>{filtered_df['CompanyName'].nunique()}</b></div>""", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📆 Offres récentes<br><b>{filtered_df[filtered_df['PublishDate'] >= pd.Timestamp.today() - pd.DateOffset(days=30)].shape[0]}</b></div>""", unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🖥️ Télétravail<br><b>{filtered_df[filtered_df["Telework"] == "Oui"].shape[0]}</b></div>""", unsafe_allow_html=True)

    # --- Graphiques Secteurs & Contrats ---

    col1, col2 = st.columns(2)

    df_contrats = filtered_df["ContractType"].value_counts().reset_index()
    df_contrats.columns = ["Type de contrat", "Nombre"]

    ###################################################################

    # Répartition Contrats
    # Graphique en Anneau
    import plotly.express as px
    fig1 = px.pie(df_contrats, names="Type de contrat", values="Nombre", title="Répartition des types de contrats", color_discrete_sequence=px.colors.sequential.Purples_r, hole=0.4)
    col1.plotly_chart(fig1, use_container_width=True)

    ###################################################################

    # Graphique en barres horizontales
    fig_contrats_bar = px.bar(
        df_contrats,
        x="Nombre",
        y="Type de contrat",
        orientation='h',
        title="Répartition des types de contrats",
        color="Type de contrat",
        color_discrete_sequence=px.colors.sequential.Purples_r
    )
    col2.plotly_chart(fig_contrats_bar, use_container_width=True)

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
################################################################### 

    # Jauges Contrat
    col1, col2 = st.columns(2)

    # Jauges Contrat
    import plotly.graph_objects as go

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
            title={'text': contrat, 'font': {'size': 12}},  # Taille du titre ajustée
            gauge={
                'axis': {'range': [0, max_offres]},
                'bar': {'color': couleurs[contrat]},
                'steps': [{'range': [0, max_offres], 'color': "#f2e6ff"}]  # Couleur de fond plus claire
            },
            domain=positions[contrat]
        ))

    # Ajouter un titre avec une **marge plus grande**
    fig_contrats_jauge.add_annotation(
        x=0, y=1.25,  # Plus d'espace au-dessus des jauges
        text="Nombre d'offres par Types de Contrat",
        showarrow=False,
        font=dict(size=16, color="black", weight="bold"),
        xanchor="left"
    )

    # Ajustement de la mise en page pour éviter le chevauchement
    fig_contrats_jauge.update_layout(margin=dict(t=80, b=40))  # t = top, b = bottom

    # Affichage dans col1
    col1.plotly_chart(fig_contrats_jauge, use_container_width=True)

###################################################################

    # TELETRAVAIL 
    import plotly.graph_objects as go

    # Filtrer uniquement les valeurs valides (exclure "NC")
    df_telework = df_offres2[df_offres2["Telework"] != "NC"]["Telework"].value_counts().reset_index()
    df_telework.columns = ["Type de Télétravail", "Nombre"]

    # Définir les couleurs
    colors = ["#6a0dad", "#c084fc"]  # Violet foncé et violet clair

    # Création de la figure en "demi-donut"
    fig_telework = go.Figure()

    fig_telework.add_trace(go.Pie(
        labels=df_telework["Type de Télétravail"],
        values=df_telework["Nombre"],
        hole=0.6,  # Centre du donut
        marker=dict(colors=colors),
        textinfo="label+percent",
        direction="clockwise",
        sort=False,
        domain={'x': [0, 1], 'y': [0, 0.5]}  # Ajuste pour afficher uniquement la moitié haute
    ))

    # Ajustement de l'affichage pour un demi-donut
    fig_telework.update_layout(
        title=dict(
            text="📡 Répartition du Télétravail",
            x=0.5,  # Centrage du titre
            font=dict(size=14, color="black")
        ),
        showlegend=False,  # Supprime la légende pour ne pas encombrer
        margin=dict(t=50, b=0, l=0, r=0),  # Ajustement des marges
    )

    # Affichage dans Streamlit
    col2.plotly_chart(fig_telework, use_container_width=True)

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
###################################################################

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
            ### 🏢 Répartition des offres par secteur 
            <br>
            Ce graphique permet d’identifier les secteurs d'activité les plus 
            dynamiques en termes de recrutement. 
            
            En un coup d'œil, il est possible de repérer les domaines où la demande 
            est la plus forte, offrant ainsi des insights précieux sur les tendances 
            actuelles du marché.
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
###################################################################

    # Entreprises
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 📊 Répartition des entreprises recrutant le plus
            <br>
            Ce graphique met en avant les entreprises qui proposent le plus d'offres 
            en fonction des critères de filtrage appliqués. Plus un nom est grand, 
            plus l'entreprise est présente dans les offres disponibles.
            
            Cela permet d’identifier rapidement les principaux employeurs du marché, 
            offrant ainsi une vision des acteurs majeurs du recrutement.
            """,
            unsafe_allow_html=True
        )


    # WordCloud présence Entreprises
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    entreprises_freq = df_offres2["CompanyName"].value_counts().to_dict()

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

    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)
###################################################################

    # DATES#

    import pandas as pd
    import plotly.express as px

    # Conversion de la colonne PublishDate en format datetime
    df_offres2["PublishDate"] = pd.to_datetime(df_offres2["PublishDate"])

    # Extraction des informations temporelles
    df_offres2["Année"] = df_offres2["PublishDate"].dt.year
    df_offres2["Mois"] = df_offres2["PublishDate"].dt.strftime('%Y-%m')  # Format Année-Mois
    df_offres2["Jour"] = df_offres2["PublishDate"].dt.weekday  # Lundi=0, Dimanche=6
    df_offres2["Jour_Nom"] = df_offres2["PublishDate"].dt.strftime('%A')  # Jour en texte

    # **1️⃣ HEATMAP - Répartition des offres par Année, Mois et Jour de la semaine**
    df_heatmap = df_offres2.groupby(["Année", "Mois", "Jour_Nom"]).size().reset_index(name="Nombre d'offres")

    # Pivot pour structurer la heatmap
    heatmap_pivot = df_heatmap.pivot(index="Jour_Nom", columns="Mois", values="Nombre d'offres")

    # Création de la heatmap avec Plotly
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Mois", y="Jour de la semaine", color="Nombre d'offres"),
        color_continuous_scale="Purples",
        title="📅 Répartition des offres par jour de la semaine et par mois",
    )

    # Ajustements esthétiques pour lisibilité
    fig_heatmap.update_layout(
        xaxis_title="Mois",
        yaxis_title="Jour de la semaine",
        xaxis=dict(type="category", tickangle=-45),
        yaxis=dict(categoryorder="array", categoryarray=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]),
        margin=dict(l=50, r=50, t=50, b=50),
        plot_bgcolor="white",
    )

    # Affichage dans Streamlit
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # **2️⃣ COURBE EN AIRES - Évolution journalière des offres**
    df_trend_daily = df_offres2.groupby(df_offres2["PublishDate"].dt.strftime('%Y-%m-%d')).size().reset_index(name="Nombre d'offres")

    # Création d'un graphique en aires avec granularité journalière
    fig_area = px.area(
        df_trend_daily,
        x="PublishDate",
        y="Nombre d'offres",
        title="📈 Évolution quotidienne des offres d'emploi",
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

###################################################################

    # --- Section 2 : Analyse des Compétences, Outils et Soft Skills ---
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
        import matplotlib.pyplot as plt
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

    return

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
    justify-content: left; 
    gap: 20px;
    padding: 20px;
    border-radius: 20px;
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
.logo-container { 
    margin-right: 140px
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
    <div class="logo-container">
        <h1 class="logo-text">Wild Find Job</h1>
    </div>
    <div class="nav-buttons">  <a href="?page=accueil" class="nav-link">Accueil</a>
        <a href="?page=analyse" class="nav-link">Analyse des tendances</a>
        <a href="?page=a_propos" class="nav-link"> À propos</a>
    </div>
</div>
""", unsafe_allow_html=True)


# Gestion des paramètres et affichage des pages (inchangé)
params = st.query_params
current_page = params.get("page", "accueil")

if current_page == "accueil":
    accueil()
elif current_page == "analyse":
    analyser_tendances()
elif current_page == "a_propos":
    afficher_raison_wildfindjob()
else:
    st.write("Page non trouvée")