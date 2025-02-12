# Recherche de Bibliothèques de Visualisation pour Streamlit

## Objectif
L'objectif est d'identifier des bibliothèques de visualisation dynamiques, esthétiques et faciles à intégrer dans Streamlit, en évitant les options classiques comme Matplotlib et Seaborn, dont le rendu peut être limité.

## Critères de sélection
- Visuels modernes et professionnels
- Interactivité avec les graphiques
- Facilité d'intégration avec Streamlit
- Open-source ou accessibles librement

---

## Sélection des Bibliothèques

### Plotly

**Présentation :** 
Plotly est une bibliothèque interactive qui permet de générer des graphiques dynamiques et personnalisables. Elle s'intègre parfaitement avec Streamlit grâce à `st.plotly_chart()`.

**Avantages :**
- Graphiques interactifs (zoom, hover, sélection)
- Facile à intégrer dans Streamlit
- Large choix de graphiques (courbes, barres, scatter, cartes, etc.)

**Exemples de rendus :**
![Plotly example](https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Plotly-logo.png/200px-Plotly-logo.png)

**Lien vers la documentation :**
[https://plotly.com/python/](https://plotly.com/python/)

---

### Altair

**Présentation :** 
Altair est une bibliothèque déclarative qui permet de construire des visualisations élégantes avec peu de code.

**Avantages :**
- Syntaxe simple et efficace
- Interactions avancées possibles (sélection de données, filtres dynamiques)
- Bonne intégration avec Pandas et Streamlit

**Exemples de rendus :**
![Altair example](https://altair-viz.github.io/_static/altair-logo.png)

**Lien vers la documentation :**
[https://altair-viz.github.io/](https://altair-viz.github.io/)

---

### PyDeck

**Présentation :**
PyDeck est une bibliothèque spécialisée dans la visualisation cartographique interactive. Idéal pour représenter des données géospatiales.

**Avantages :**
- Intégration fluide avec Streamlit (`st.pydeck_chart()`)
- Visualisations en 3D possibles
- Fonctionne bien avec des jeux de données géographiques (lat/lon)

**Exemples de rendus :**
![PyDeck example](https://pydeck.gl/static/images/hero.png)

**Lien vers la documentation :**
[https://deck.gl/docs/api-reference/pydeck-layer](https://deck.gl/docs/api-reference/pydeck-layer)

---

### Bokeh

**Présentation :**
Bokeh permet de créer des graphiques interactifs et dynamiques avec un rendu esthétique très soigné.

**Avantages :**
- Haut niveau d'interactivité
- Adapté aux dashboards analytiques
- Possibilité d'exporter en HTML

**Exemples de rendus :**
![Bokeh example](https://docs.bokeh.org/en/latest/_images/examples_scatter.png)

**Lien vers la documentation :**
[https://docs.bokeh.org/en/latest/](https://docs.bokeh.org/en/latest/)

---

### Streamlit Elements

**Présentation :**
Streamlit Elements est un package permettant d'intégrer des composants interactifs comme des graphiques avancés, des tableaux et des éditeurs de code dans un dashboard Streamlit.

**Avantages :**
- Permet d'ajouter des visualisations modernes et fluides
- Basé sur React.js et d'autres technologies avancées
- Très bien intégré à Streamlit

**Exemples de rendus :**
![Streamlit Elements example](https://raw.githubusercontent.com/okld/streamlit-elements/main/docs/assets/tour-2.gif)

**Lien vers la documentation :**
[https://github.com/okld/streamlit-elements](https://github.com/okld/streamlit-elements)

---

### PieCharts

**Présentation :**
PieCharts est une bibliothèque spécialisée dans la visualisation de diagrammes circulaires. Parfait pour représenter des répartitions de données de manière visuelle et intuitive.

**Avantages :**
- Très simple à utiliser
- Rendu esthétique moderne
- Intégration facile avec Streamlit

**Exemples de rendus :**
![PieCharts example](https://upload.wikimedia.org/wikipedia/commons/3/3a/Pie_chart_example.png)

**Lien vers la documentation :**
[https://github.com/xx/PieCharts](https://github.com/xx/PieCharts) *(Remplacer par un lien valide)*

---

## Inspiration : Data Emploi
L'organisation de la page Analyse des tendances métiers s'inspire fortement du dashboard de Data Emploi. Les éléments clés à intégrer :
- Courbes d'évolution des offres d'emploi
- Répartition géographique
- Taux de recrutement par secteur
- Comparaison des salaires

**Référence :** [Data Emploi](https://dataemploi.francetravail.fr/emploi/metier/chiffres-cles/NAT/FR/M1403)

**Prochaine étape** : Tester ces bibliothèques sur Streamlit pour choisir les meilleures pour notre dashboard d'analyse des tendances.

