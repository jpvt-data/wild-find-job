import pandas as pd
import streamlit as st
from streamlit_elements import elements, mui, nivo

dataviz = pd.read_csv("./data/datasets/brut/table_fictive_dataviz_jp.csv")

# Calcul des indicateurs
salaire_moyen = pd.to_numeric(dataviz["salaire"].str.extract("(\d+)")[0], errors="coerce").mean()
nb_offres = len(dataviz)
nb_entreprises = dataviz["entreprise"].nunique()

st.title("Streamlit Elements - KPI - DF - Visuels")

with elements("dashboard"):
    mui.Grid(container=True, spacing=2)(
        mui.Grid(item=True, xs=4)(
            mui.Card(
                mui.CardContent(
                    mui.Typography(f"{nb_offres} offres", variant="h5")
                )
            )
        ),
        mui.Grid(item=True, xs=4)(
            mui.Card(
                mui.CardContent(
                    mui.Typography(f"{nb_entreprises} entreprises", variant="h5")
                )
            )
        ),
        mui.Grid(item=True, xs=4)(
            mui.Card(
                mui.CardContent(
                    mui.Typography(f"Salaire moyen {salaire_moyen:.0f}k", variant="h5")
                )
            )
        ),
    )

# Tableau
df_table = dataviz[["entreprise", "type_contrat"]].drop_duplicates().head(10)

with elements("table"):
    mui.TableContainer(
        mui.Table(
            mui.TableHead(
                mui.TableRow(
                    mui.TableCell("Entreprise"),
                    mui.TableCell("Type de Contrat"),
                )
            ),
            mui.TableBody(
                [
                    mui.TableRow(
                        mui.TableCell(row["entreprise"]),
                        mui.TableCell(row["type_contrat"]),
                    )
                    for _, row in df_table.iterrows()
                ]
            ),
        )
    )

# Graphique dynamique
df_secteurs = dataviz["secteur_activité"].value_counts().reset_index()
df_secteurs.columns = ["secteur", "nombre"]

st.title("Graphique dynamique des offres par secteur")

# Vérifier si les données sont bien formatées
if df_secteurs.empty:
    st.error("Aucune donnée disponible pour afficher le graphique.")
else:
    with elements("bar_chart"):
        try:
            nivo.Bar(
                data=df_secteurs.to_dict(orient="records"),
                keys=["nombre"],
                indexBy="secteur",
                margin={"top": 40, "right": 30, "bottom": 80, "left": 60},
                padding=0.3,
                colors={"scheme": "category10"},
                axisBottom={"tickRotation": -45},
                enableLabel=True,
            )
        except Exception as e:
            st.error(f"Erreur lors du rendu avec Streamlit Elements : {e}")


