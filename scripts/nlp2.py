import spacy
import pandas as pd
import re
from spacy.matcher import PhraseMatcher
from spacy.lang.fr.stop_words import STOP_WORDS

# Charger le modèle NLP
nlp = spacy.load("fr_core_news_lg")

# Définition des chemins des fichiers
df_clean_path = "./data/datasets/brut/df_final2.csv"
df_output_path = "./data/datasets/propre/df_clean2_nlp.csv"

# Charger df_clean
df_clean = pd.read_csv(df_clean_path, encoding="utf-8")

# Vérifier la présence des colonnes nécessaires
if "Profile" not in df_clean.columns or "Description" not in df_clean.columns:
    raise ValueError("Les colonnes 'Profile' et 'Description' sont requises dans df_clean.")


# Fonction de nettoyage avancé du texte
def nettoyer_texte(texte):
    if pd.isna(texte):
        return ""
    texte = texte.lower()
    texte = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", "", texte)  # Supprimer les caractères spéciaux
    doc = nlp(texte)  # Transformer en objet spaCy
    tokens = [token.lemma_ for token in doc if token.text not in STOP_WORDS and not token.is_punct]
    return " ".join(tokens)


# Appliquer le nettoyage et la lemmatisation
df_clean["Profile"] = df_clean["Profile"].apply(nettoyer_texte)
df_clean["Description"] = df_clean["Description"].apply(nettoyer_texte)


# Fonction pour construire les matchers avec lemmatisation des termes
def construire_matcher(dictionnaire):
    matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")  # Prend en compte les formes de base (lemmatisation)
    for categorie, termes in dictionnaire.items():
        patterns = [nlp(terme.lower()) for terme in termes]  # NLP sur chaque mot-clé
        matcher.add(categorie, patterns)
    return matcher


# Dictionnaires de mots-clés (formes lemmatisées et variantes incluses)
competences_cles = {
    "SQL et bases de données": ["sql", "base de données", "requête", "jointure", "index", "optimisation"],
    "Python": ["python", "pandas", "numpy", "programmation", "data analysis"],
    "Statistiques et probabilités": ["statistique", "probabilité", "analyse statistique", "régression"],
    "Nettoyage et transformation des données": ["etl", "data cleaning", "transformation", "pipelines"],
    "Visualisation et storytelling": ["visualisation", "dashboard", "tableau de bord", "reporting", "graphique"],
    "Cloud et Big Data": ["aws", "gcp", "azure", "hadoop", "big data"],
    "Automatisation et scripting": ["automatisation", "script", "workflow", "shell", "airflow"],
    "Gestion des API et Web Scraping": ["api", "web scraping", "json", "rest"],
    "Modélisation et machine learning": ["machine learning", "modèle prédictif", "classification", "régression"],
    "Déploiement et industrialisation": ["déploiement", "ci/cd", "docker", "fastapi", "flask", "mlops"]
}

soft_skills = {
    "Esprit analytique": ["analyse", "modélisation", "logique"],
    "Curiosité et apprentissage continu": ["curiosité", "formation", "autodidacte"],
    "Communication et vulgarisation": ["communication", "explication", "présentation"],
    "Résolution de problèmes": ["problème", "solution", "optimisation"],
    "Collaboration et travail en équipe": ["équipe", "collaboration", "partage"],
    "Autonomie et prise d’initiative": ["autonomie", "proactivité"],
    "Adaptabilité et agilité": ["adaptabilité", "agile", "scrum"],
    "Gestion du temps et organisation": ["gestion du temps", "priorisation"],
    "Esprit critique": ["sens critique", "remise en question"],
    "Sens du détail et rigueur": ["rigueur", "précision"]
}

outils = {
    "SQL": ["sql", "postgresql", "mysql", "bigquery"],
    "Python": ["python", "pandas", "numpy", "scikit-learn"],
    "Excel & Google Sheets": ["excel", "tableau croisé dynamique", "vba"],
    "Power BI / Tableau / Looker": ["power bi", "tableau", "looker"],
    "Jupyter Notebook & VS Code": ["jupyter", "vs code"],
    "Apache Airflow & dbt": ["airflow", "dbt"],
    "Git & GitHub/GitLab": ["git", "github", "gitlab"],
    "Docker & Kubernetes": ["docker", "kubernetes"],
    "Cloud Computing": ["aws", "gcp", "azure"],
    "Google Colab": ["colab", "google colab"]
}

# Initialiser les matchers avec les dictionnaires optimisés
matcher_competences = construire_matcher(competences_cles)
matcher_soft_skills = construire_matcher(soft_skills)
matcher_outils = construire_matcher(outils)


# 🔹 Fonction de détection des mots-clés avec NLP et lemmatisation
def detecter_mots_cles(texte, matcher):
    doc = nlp(texte)
    mots_cles = set()
    for match_id, start, end in matcher(doc):
        mots_cles.add(nlp.vocab.strings[match_id])  # Récupérer la catégorie correspondante
    return list(mots_cles)


# Appliquer la détection NLP aux colonnes
df_clean["Competences_Clés"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_competences)) + \
                               df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_competences))

df_clean["Soft_Skills"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_soft_skills)) + \
                          df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_soft_skills))

df_clean["Outils"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_outils)) + \
                     df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_outils))

# Supprimer les doublons
df_clean["Competences_Clés"] = df_clean["Competences_Clés"].apply(lambda x: list(set(x)))
df_clean["Soft_Skills"] = df_clean["Soft_Skills"].apply(lambda x: list(set(x)))
df_clean["Outils"] = df_clean["Outils"].apply(lambda x: list(set(x)))

# Sauvegarde du fichier
df_clean.to_csv(df_output_path, index=False, encoding="utf-8")
print(f"Fichier enregistré : {df_output_path}")
