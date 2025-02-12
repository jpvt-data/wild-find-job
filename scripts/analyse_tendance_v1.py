import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
import altair as alt
import bokeh.plotting as bp
from bokeh.models import ColumnDataSource
from bokeh.palettes import Purples8
from bokeh.transform import factor_cmap
import time

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
#st.markdown("<br>", unsafe_allow_html=True)
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
st.markdown("<br>", unsafe_allow_html=True)

# --- Chargement des données ---
df = pd.read_csv("./data/datasets/brut/table_fictive_dataviz_jp.csv")
df["date_publication"] = pd.to_datetime(df["date_publication"])

# --- Filtres interactifs ---
col1, col2, col3, col4 = st.columns(4)

metier = col1.selectbox("Sélectionner un métier", ["Tous"] + sorted(df["titre_poste"].unique()))
contrat = col2.selectbox("Sélectionner un type de contrat", ["Tous"] + sorted(df["type_contrat"].unique()))
lieu = col3.selectbox("Sélectionner un lieu", ["Tous"] + sorted(df["lieu"].unique()))
entreprise = col4.selectbox("Sélectionner une entreprise", ["Tous"] + sorted(df["entreprise"].unique()))

# --- Filtrage des données ---
filtered_df = df.copy()
if metier != "Tous":
    filtered_df = filtered_df[filtered_df["titre_poste"] == metier]
if contrat != "Tous":
    filtered_df = filtered_df[filtered_df["type_contrat"] == contrat]
if lieu != "Tous":
    filtered_df = filtered_df[filtered_df["lieu"] == lieu]



# --- Section 1 : Répartition du Marché ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## 🔹 Répartition du marché de l'emploi")

# --- KPIs Dynamiques ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown("""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>📌 Nombre d'offres<br><b>{}</b></div>""".format(len(filtered_df)), unsafe_allow_html=True)
with kpi2:
    st.markdown("""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>💰 Salaire moyen<br><b>{}k</b></div>""".format(int(filtered_df['salaire'].str.extract('(\d+)')[0].astype(float).mean())), unsafe_allow_html=True)
with kpi3:
    st.markdown("""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🏢 Entreprises<br><b>{}</b></div>""".format(filtered_df["entreprise"].nunique()), unsafe_allow_html=True)
with kpi4:
    st.markdown("""<div style='border: 2px solid #D8BFD8; border-radius: 10px; padding: 5px; font-size: 26px; text-align: center;'>🖥️ Télétravail<br><b>{}</b></div>""".format(filtered_df[filtered_df["télétravail"] == "Oui"].shape[0]), unsafe_allow_html=True)

# Colonnes pour visuels
col1, col2 = st.columns(2)
# Définir une hauteur commune
common_height = 600 

# Pie chart streamlit type de contrat
df_contrats = filtered_df["type_contrat"].value_counts().reset_index()
df_contrats.columns = ["contrat", "nombre"]
fig1 = px.pie(
    df_contrats, 
    names="contrat", 
    values="nombre", 
    title="Répartition des types de contrats (Streamlit)", 
    color_discrete_sequence=px.colors.sequential.Purples_r,
    hole=0.4  # Ajoute un trou pour créer l'effet "anneau"
)

# Afficher "X offres" au lieu des pourcentages
fig1.update_traces(
    textinfo='text', 
    text=df_contrats['nombre'].astype(str) + ' offres'
)
fig1.update_layout(height=common_height)
col1.plotly_chart(fig1, use_container_width=True)


# Altair Bar Chart des types de contrats
df_secteurs = filtered_df["secteur_activité"].value_counts().reset_index()
df_secteurs.columns = ["secteur", "nombre"]
fig4 = alt.Chart(df_secteurs).mark_bar().properties(height=common_height).encode(
    x='nombre:Q',
    y=alt.Y('secteur:N', sort='-x'),
    color=alt.Color('secteur:N', scale=alt.Scale(scheme='purples'))
).properties(title="Répartition des offres par secteur (Altair)")
col2.altair_chart(fig4, use_container_width=True)

# Bar chart Streamlit du nombre d'offres par secteur d'activité
fig6 = px.bar(df_secteurs, x="secteur", y="nombre", title="Répartition des offres par secteur", color="secteur", color_discrete_sequence=px.colors.sequential.Purples)
fig6.update_layout(height=common_height)
col1.plotly_chart(fig6, use_container_width=True)


# Radar chart du nombre d'offres par métier
df_metier_offres = filtered_df["titre_poste"].value_counts().reset_index()
df_metier_offres.columns = ["titre_poste", "nombre_offres"]
fig3 = px.line_polar(df_metier_offres, r="nombre_offres", theta="titre_poste", line_close=True, 
                          title="Répartition du nombre d'offres par métier", 
                          color_discrete_sequence=px.colors.sequential.Purples_r)
fig3.update_layout(height=common_height)
col2.plotly_chart(fig3, use_container_width=True)

# --- Section 2 : Analyse des Salaires ---
st.markdown("## 🔹 Analyse des salaires")
if st.button("🔝 Retour aux filtres"):
    st.rerun()

col3, col4 = st.columns(2)

fig3 = px.histogram(filtered_df, x="salaire", title="Répartition des salaires", nbins=4, color_discrete_sequence=px.colors.sequential.Purples_r)
col3.plotly_chart(fig3, use_container_width=True)

df_salaire_metier = filtered_df.groupby("titre_poste")["salaire"].apply(lambda x: x.str.extract('(\d+)')[0].astype(float).mean()).reset_index()
df_salaire_metier.columns = ["Métier", "Salaire Moyen (K€)"]

fig4 = px.bar(df_salaire_metier, x="Salaire Moyen (K€)", y="Métier", orientation='h', 
                            title="Salaire moyen des offres par métier", 
                            color="Salaire Moyen (K€)", color_continuous_scale=px.colors.sequential.Purples_r)

col4.plotly_chart(fig4, use_container_width=True)

# --- Section 3 : Répartition Géographique avec Géocodage ---
st.markdown("## 🔹 Répartition géographique des offres")

geolocator = Nominatim(user_agent="streamlit-geocoder")
location_cache = {}

def get_lat_lon(city):
    if city in location_cache:
        return location_cache[city]
    try:
        location = geolocator.geocode(city, timeout=10)
        if location:
            location_cache[city] = (location.latitude, location.longitude)
            return location.latitude, location.longitude
    except:
        return None, None

m = folium.Map(location=[46.603354, 1.888334], zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

for _, row in filtered_df.iterrows():
    lat, lon = get_lat_lon(row["lieu"])
    if lat and lon:
        folium.Marker(
            location=[lat, lon],
            popup=f"{row['lieu']} - {row['salaire']}€",
            icon=folium.Icon(color='purple')
        ).add_to(marker_cluster)
folium_static(m)