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
col1, col2, col3, col4 = st.columns(4)

domaine = col1.selectbox("Métier", ["Tous"] + sorted(df["OfferLabel"].unique()))
contrat = col2.selectbox("Type de contrat", ["Tous"] + sorted(df["ContractType"].unique()))
entreprise = col3.selectbox("Entreprise", ["Tous"] + sorted(df["CompanyName"].unique()))
teletravail = col4.selectbox("Télétravail", ["Tous"] + sorted(df["Telework"].unique()))

st.markdown("<br>", unsafe_allow_html=True)


# --- Filtrage des données ---
filtered_df = df.copy()
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
    st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📌 Nombre d'offres<br><b>{len(filtered_df)}</b></div>""", unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🏢 Entreprises<br><b>{filtered_df['CompanyName'].nunique()}</b></div>""", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📆 Offres récentes<br><b>{filtered_df[filtered_df['PublishDate'] >= pd.Timestamp.today() - pd.DateOffset(days=30)].shape[0]}</b></div>""", unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🖥️ Télétravail<br><b>{filtered_df[filtered_df["Telework"] == "Oui"].shape[0]}</b></div>""", unsafe_allow_html=True)

# st.markdown("<br>", unsafe_allow_html=True)

# --- Graphiques Secteurs & Contrats ---

col1, col2 = st.columns(2)

df_contrats = filtered_df["ContractType"].value_counts().reset_index()
df_contrats.columns = ["Type de contrat", "Nombre"]

###################################################################

# Répartition Contrats
# Graphique en Anneau
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
df_telework = df[df["Telework"] != "NC"]["Telework"].value_counts().reset_index()
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

st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)
###################################################################
# DATES#

import pandas as pd
import plotly.express as px

# Conversion de la colonne PublishDate en format datetime
df["PublishDate"] = pd.to_datetime(df["PublishDate"])

# Extraction des informations temporelles
df["Année"] = df["PublishDate"].dt.year
df["Mois"] = df["PublishDate"].dt.strftime('%Y-%m')  # Format Année-Mois
df["Jour"] = df["PublishDate"].dt.weekday  # Lundi=0, Dimanche=6
df["Jour_Nom"] = df["PublishDate"].dt.strftime('%A')  # Jour en texte

# **1️⃣ HEATMAP - Répartition des offres par Année, Mois et Jour de la semaine**
df_heatmap = df.groupby(["Année", "Mois", "Jour_Nom"]).size().reset_index(name="Nombre d'offres")

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
df_trend_daily = df.groupby(df["PublishDate"].dt.strftime('%Y-%m-%d')).size().reset_index(name="Nombre d'offres")

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




