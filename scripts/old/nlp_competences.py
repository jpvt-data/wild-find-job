import pandas as pd
import re
import spacy
from spacy.matcher import PhraseMatcher
from spacy.lang.fr.stop_words import STOP_WORDS

# Charger un modèle NLP plus puissant
nlp = spacy.load("fr_core_news_lg")

# Définition du chemin des fichiers
df_clean_path = "./data/datasets/brut/df_clean2.csv"
df_output_path = "./data/datasets/propre/df_clean2_nlp.csv"

# Fusionner les dictionnaires en un seul pour un traitement plus efficace
competences_cles = {
    "Programmation": ["Python", "SQL", "R", "Scala", "Java", "C++", "Julia", "C#", "JavaScript", "Bash", 
                      "TypeScript", "Go", "Rust", "Perl", "Matlab", "Dart"],
    "Analyse de données": ["Statistique", "Analyse exploratoire", "EDA", "Prétraitement", "Feature engineering", 
                         "Nettoyage", "Agrégation", "Descriptive", "Prédictive", "Réduction de dimension"],
    "Machine Learning": ["Modélisation", "Régression", "Classification", "Clustering", "Deep Learning", 
                         "Réseaux de neurones", "Apprentissage supervisé", "AutoML", "Feature Selection", 
                         "Recommandation", "Traitement du signal"],
    "Big Data": ["Spark", "Hadoop", "Dask", "Flink", "MapReduce", "Kafka", "ElasticSearch", "Data Lake", 
                 "Delta Lake", "HBase", "Parquet", "Avro", "ETL", "Pipeline"],
    "Visualisation": ["DataViz", "Dashboarding", "Storytelling", "Exploration", "Heatmap", "Graphiques", 
                      "Rapports", "KPIs", "Business Intelligence"],
    "Optimisation": ["A/B testing", "Hyperparameter tuning", "Fine-tuning", "Gradient Boosting", "Cross-validation"],
    "Business Intelligence": ["BI", "Reporting", "Analyse métier", "Tableaux de bord", "Analyse de rentabilité"],
    "Gestion Projet": ["Agile", "Scrum", "Kanban", "JIRA", "Lean", "Product Owner", "Scrum Master", "Cycle en V"]
}

soft_skills = {
    "Communication": ["Présentation", "Vulgarisation", "Synthèse", "Storytelling", "Argumentation", "Éloquence"],
    "Collaboration": ["Travail en équipe", "Esprit collaboratif", "Relation client", "Médiation", "Écoute active"],
    "Résolution de problèmes": ["Esprit analytique", "Curiosité", "Créativité", "Pensée critique", "Logique"],
    "Gestion du Temps": ["Organisation", "Priorisation", "Autonomie", "Gestion du stress", "Planification"],
    "Adaptabilité": ["Flexibilité", "Ouverture d'esprit", "Capacité d'apprentissage", "Résilience"],
    "Leadership": ["Prise de décision", "Esprit d'initiative", "Gestion d'équipe", "Motivation"]
}

outils = {
    "Visualisation": ["Power BI", "PBI", "Tableau", "Matplotlib", "Seaborn", "Plotly", "Looker", "GDS", "D3.js"],
    "Base de données": ["PostgreSQL", "MySQL", "MariaDB", "MongoDB", "BigQuery", "Snowflake", "NoSQL"],
    "Data Engineering": ["Airflow", "ETL", "Kafka", "DataBricks", "Prefect", "Spark Streaming"],
    "Cloud": ["AWS", "Azure", "Google Cloud", "GCP", "S3", "Lambda", "Databricks"],
    "Machine Learning": ["Scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "AutoML", "Hugging Face"],
    "Big Data": ["Apache Spark", "Hadoop", "Hive", "HDFS", "Flink", "Presto", "Delta Lake"],
    "Devops": ["Docker", "Kubernetes", "Git", "CI/CD", "Jenkins", "Terraform", "Ansible"]
}

# Charger df_clean
df_clean = pd.read_csv(df_clean_path, encoding="utf-8")

# Vérifier que les colonnes nécessaires existent
if "Profile" not in df_clean.columns or "Description" not in df_clean.columns:
    raise ValueError("Les colonnes 'Profile' et 'Description' sont requises dans df_clean.")

# Fonction de nettoyage du texte
def nettoyer_texte(texte):
    if pd.isna(texte):
        return ""
    texte = texte.lower()
    texte = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", "", texte)  # Supprimer les caractères spéciaux
    tokens = texte.split()
    tokens = [mot for mot in tokens if mot not in STOP_WORDS]  # Supprimer les stopwords
    return " ".join(tokens)

# Appliquer le nettoyage
df_clean["Profile"] = df_clean["Profile"].apply(nettoyer_texte)
df_clean["Description"] = df_clean["Description"].apply(nettoyer_texte)

# Initialiser les matchers de spaCy
def construire_matcher(dictionnaire):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for categorie, termes in dictionnaire.items():
        patterns = [nlp(terme.lower()) for terme in termes]
        matcher.add(categorie, patterns)
    return matcher

matcher_competences = construire_matcher(competences_cles)
matcher_soft_skills = construire_matcher(soft_skills)
matcher_outils = construire_matcher(outils)

# Fonction de détection des mots-clés en utilisant spaCy Matcher
def detecter_mots_cles(texte, matcher):
    doc = nlp(texte)
    mots_cles = set()
    for match_id, start, end in matcher(doc):
        mots_cles.add(nlp.vocab.strings[match_id])  # Récupérer la catégorie associée
    return list(mots_cles)

# Appliquer la détection sur les colonnes
df_clean["Competences_Clés"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_competences)) + \
                               df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_competences))

df_clean["Soft_Skills"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_soft_skills)) + \
                          df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_soft_skills))

df_clean["Outils"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_outils)) + \
                     df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_outils))

# Supprimer les doublons dans les listes
df_clean["Competences_Clés"] = df_clean["Competences_Clés"].apply(lambda x: list(set(x)))
df_clean["Soft_Skills"] = df_clean["Soft_Skills"].apply(lambda x: list(set(x)))
df_clean["Outils"] = df_clean["Outils"].apply(lambda x: list(set(x)))

# Sauvegarde du fichier
df_clean.to_csv(df_output_path, index=False, encoding="utf-8")
print(f"Fichier enregistré : {df_output_path}")
