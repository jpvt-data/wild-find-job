import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from wordcloud import WordCloud  # WordCloud
import matplotlib.pyplot as plt  # WordCloud
import ast

# --- Configuration de la page ---
st.set_page_config(page_title="Analyse des Tendances", layout="wide")
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

st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

# --- Chargement des données ---
df = pd.read_csv("./data/datasets/propre/df_clean2_nlp.csv")

# Conversion des dates
df["PublishDate"] = pd.to_datetime(df["PublishDate"])


# 🔹 **Correction des colonnes contenant des listes**
def convertir_listes(colonne):
    return colonne.apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else [])


df["Competences_Clés"] = convertir_listes(df["Competences_Clés"])
df["Outils"] = convertir_listes(df["Outils"])
df["Soft_Skills"] = convertir_listes(df["Soft_Skills"])

# --- Filtres interactifs ---
st.markdown("## 🔹 Critères d'analyse")
col1, col2, col3 = st.columns([0.3, 0.2, 0.5])

with col1:
    Métier = col1.selectbox("Métier", ["Tous"] + sorted(df["OfferLabel"].unique()))
    Domaine = col1.selectbox("Domaine", ["Tous"] + sorted(df["Domaine"].unique()))

with col3:
    # st.markdown("### 🔹 Filtres disponibles")
    st.markdown("""
                <div style='font-size:22px;'>
                <br>🔹 Sélectionnez un métier et un domaine pour affiner votre recherche.
                <br><br>
                🔹 Les résultats seront mis à jour dynamiquement en fonction de vos choix.<br>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)


# --- Filtrage des données ---
filtered_df = df.copy()
if Métier != "Tous":
    filtered_df = filtered_df[filtered_df["OfferLabel"] == Métier]
if Domaine != "Tous":
    filtered_df = filtered_df[filtered_df["Domaine"] == Domaine]


#####################################################################


#####################################################################



# --- Section 1 : Répartition du Marché ---
st.markdown("## 🔹 Répartition du marché de l'emploi")

# --- KPIs Dynamiques ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📌 Nombre d'offres<br><b>{len(filtered_df)}</b></div>""", unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🏢 Entreprises<br><b>{filtered_df['CompanyName'].nunique()}</b></div>""", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📆 Offres récentes<br><b>{filtered_df[filtered_df['PublishDate'] >= pd.Timestamp.today() - pd.DateOffset(days=30)].shape[0]}</b></div>""", unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""<div style='background-color: #F8F0FC; border: 2px solid #C49BDA; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🖥️ Télétravail<br><b>{filtered_df[filtered_df["Telework"] == "Oui"].shape[0]}</b></div>""", unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

##################################################################


# --- Section Contrats & Télétravail ---

col1, col2 = st.columns(2)

###################################################################

col1.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Offres par Type de Contrat<b></div>""", unsafe_allow_html=True)

# Jauges Contrat
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
#2
#Télétravail#

col2.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Répartition du Télétravail<b><br><br></div>""", unsafe_allow_html=True)

# Filtrer uniquement les valeurs valides (exclure "NC")
df_telework = df[df["Telework"] != "NC"]["Telework"].value_counts().reset_index()
df_telework.columns = ["Type de Télétravail", "Nombre"]

# Définir les couleurs
colors = ["#6a0dad", "#c084fc"]  # Violet foncé et violet clair

# Graphique en Anneau avec annotations et sans légende
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

#SALAIRES#

col1, col2, col3 = st.columns([0.45, 0.1, 0.45])

col1.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Répartition des Salaires<b></div>""", unsafe_allow_html=True)

import plotly.express as px

# ---- Nettoyage des données ----
df.rename(columns={"salaire_min": "Salaire Minimum", "salaire_max": "Salaire Maximum"}, inplace=True)
df_salaire = df[["Salaire Minimum", "Salaire Maximum"]].dropna()  # Supprime les NaN
df_salaire = df_salaire.melt(var_name="Type de Salaire", value_name="Montant")  # Transformation pour boxplot

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

# ---- Création de l'histogramme + KDE ----

col1.markdown("""
                <div style='font-size:22px;'>
                <br><br><br><br><br>Texte à modifier !
                </div>
                """, unsafe_allow_html=True)

col1.markdown("<br>", unsafe_allow_html=True)

col3.markdown(f"""<div style='font-size: 26px; text-align: center;'><b>🔹 Distribution des Salaires Moyens<b></div>""", unsafe_allow_html=True)

import plotly.figure_factory as ff

df_salaire = df[["Salaire Minimum", "Salaire Maximum"]].dropna()  # Suppression des NaN
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

col1, col2, col3 = st.columns([0.5, 0.1, 0.4])

#CARTES#
with col1:
    import pandas as pd
    import folium
    
    # ---- Interface utilisateur ----
    st.markdown(f"""<div style='font-size: 26px; margin-left: 100px;'><b>🗺️ Offres d'Emploi par Région<b></div>""", unsafe_allow_html=True)

    # ---- Étape 1 : Transformer les chaînes en listes et éclater les valeurs ----
    df["Region"] = df["Region"].astype(str).apply(lambda x: x.replace("[", "").replace("]", "").replace("'", "").split(", "))  # Nettoyage et conversion en liste
    df_exploded = df.explode("Region").reset_index(drop=True)  # Éclater les valeurs

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

st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)

###################################################################

st.markdown(f"""<div style='font-size: 26px; margin-left: 100px;'><b>📈 Évolution quotidienne des offres d'emploi<b></div>""", unsafe_allow_html=True)

# Évolution journalière des offres
df_trend_daily = df.groupby(df["PublishDate"].dt.strftime('%Y-%m-%d')).size().reset_index(name="Nombre d'offres")

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
        <br><div style='font-size:22px;'>
        Ce graphique permet d’identifier les secteurs d'activité les plus 
        dynamiques en termes de recrutement. 
        
        En un coup d'œil, il est possible de repérer les domaines où la demande 
        est la plus forte, offrant ainsi des insights précieux sur les tendances 
        actuelles du marché.</div>
        """,
        unsafe_allow_html=True
    )

# st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #C49BDA;'>", unsafe_allow_html=True)


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
entreprises_freq = df["CompanyName"].value_counts().to_dict()

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




