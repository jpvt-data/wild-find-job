import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
df = pd.read_csv("./data/datasets/brut/table_fictive_dataviz_jp.csv")
df["date_publication"] = pd.to_datetime(df["date_publication"])

# Mise en page de la page Streamlit
st.set_page_config(page_title="Dashboard Streamlit", layout="wide")
st.title("Dashboard Streamlit")

# --- Filtres interactifs ---
col1, col2, col3, col4 = st.columns(4)

metier = col1.selectbox("Sélectionner un métier", ["Tous"] + sorted(df["titre_poste"].unique()))
contrat = col2.selectbox("Sélectionner un type de contrat", ["Tous"] + sorted(df["type_contrat"].unique()))
lieu = col3.selectbox("Sélectionner un lieu", ["Tous"] + sorted(df["lieu"].unique()))
entreprise = col4.selectbox("Sélectionner une entreprise", ["Tous"] + sorted(df["entreprise"].unique()))

# Filtrage des données
filtered_df = df.copy()
if metier != "Tous":
    filtered_df = filtered_df[filtered_df["titre_poste"] == metier]
if contrat != "Tous":
    filtered_df = filtered_df[filtered_df["type_contrat"] == contrat]
if lieu != "Tous":
    filtered_df = filtered_df[filtered_df["lieu"] == lieu]

# --- KPIs dynamiques ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("📌 Nombre d'offres", len(filtered_df))
kpi2.metric("💰 Salaire moyen", f"{filtered_df['salaire'].str.extract('(\\d+)')[0].astype(float).mean():.0f}k")
kpi3.metric("🏢 Entreprises", filtered_df["entreprise"].nunique())
kpi4.metric("🖥️ Télétravail", filtered_df[filtered_df["télétravail"] == "Oui"].shape[0])

# --- Visualisations ---
st.markdown("---")

col5, col6 = st.columns(2)

# Histogramme des offres par secteur
df_secteurs = filtered_df["secteur_activité"].value_counts().reset_index()
df_secteurs.columns = ["secteur", "nombre"]
fig1 = px.bar(df_secteurs, x="secteur", y="nombre", title="Répartition des offres par secteur", color="secteur", color_discrete_sequence=px.colors.sequential.Purp)
col5.plotly_chart(fig1, use_container_width=True)

# Pie Chart des types de contrats
df_contrats = filtered_df["type_contrat"].value_counts().reset_index()
df_contrats.columns = ["contrat", "nombre"]
fig2 = px.pie(df_contrats, names="contrat", values="nombre", title="Répartition des types de contrats", color_discrete_sequence=px.colors.sequential.Blues)
col6.plotly_chart(fig2, use_container_width=True)

# Courbe d'évolution des offres
fig3 = px.line(filtered_df.groupby("date_publication").size().reset_index(name="Nombre d'offres"), x="date_publication", y="Nombre d'offres", title="Évolution du nombre d'offres", color_discrete_sequence=px.colors.sequential.Magma)
st.plotly_chart(fig3, use_container_width=True)

# --- Tableau dynamique ---
st.markdown("---")
st.subheader("Liste des offres d'emploi")
st.dataframe(filtered_df[["titre_poste", "entreprise", "lieu", "salaire", "type_contrat", "date_publication"]])
