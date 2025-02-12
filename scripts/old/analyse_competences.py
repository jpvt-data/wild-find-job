import pandas as pd
import re
import spacy

# Charger le modèle NLP français
nlp = spacy.load("fr_core_news_sm")

# Définition du chemin des fichiers
df_clean_path = "./data/datasets/brut/df_clean2.csv"
df_output_path = "./data/datasets/propre/df_clean2_nlp.csv"

# Définition des dictionnaires de mots-clés
competences_cles = {
    "programmation": [
        "Python", "SQL", "R", "Scala", "Java", "C++", "Julia", "C#", "JavaScript", "Bash", 
        "TypeScript", "Go", "Rust", "Perl", "Matlab", "Dart"
    ],
    "analyse_donnees": [
        "Statistiques", "Analyse exploratoire", "EDA", "Pré-traitement des données", "Feature engineering", 
        "Nettoyage des données", "Imputation des valeurs manquantes", "Agrégation", "Analyse descriptive", 
        "Analyse prédictive", "Analyse factorielle", "Réduction de dimension", "ACP", "ANOVA"
    ],
    "machine_learning": [
        "Modélisation", "Régression", "Classification", "Clustering", "Deep Learning", "Réseaux de neurones", 
        "Apprentissage supervisé", "Apprentissage non supervisé", "Apprentissage semi-supervisé", 
        "AutoML", "Feature Selection", "Feature Extraction", "Régularisation", "Apprentissage par renforcement",
        "Systèmes de recommandation", "Génération de texte", "Vision par ordinateur", "Traitement du signal"
    ],
    "big_data": [
        "Spark", "Hadoop", "Dask", "Flink", "MapReduce", "Storm", "Kafka Streams", "ElasticSearch",
        "Data Lake", "Delta Lake", "HBase", "Parquet", "Avro", "OLAP", "ETL", "Pipeline de données"
    ],
    "visualisation": [
        "DataViz", "Dashboarding", "Storytelling", "Exploration des données", "Heatmap", "Graphiques interactifs",
        "Infographies", "Rapports interactifs", "KPIs", "Business Intelligence", "Data Journalism"
    ],
    "optimisation": [
        "A/B testing", "Optimisation de modèles", "Hyperparameter tuning", "Fine-tuning", "Cross-validation", 
        "Gradient Boosting", "Feature Scaling", "Grid Search", "Random Search", "Bayesian Optimization"
    ],
    "business_intelligence": [
        "BI", "Reporting", "Analyse métier", "Dataviz", "Exploration visuelle", "Gestion des performances",
        "Tableaux de bord", "Analyse de rentabilité", "Analyse des ventes", "Segmentation client"
    ],
    "gestion_projet": [
        "Agile", "Scrum", "Kanban", "Gestion de projet", "Sprint planning", "JIRA", "Confluence", 
        "Méthodologie Lean", "Product Owner", "Scrum Master", "Cycle en V", "Waterfall", "OKR", "KPI"
    ]
}


soft_skills = {
    "communication": [
        "Présentation", "Vulgarisation", "Synthèse", "Storytelling", "Communication orale", "Rédaction", 
        "Clarté", "Argumentation", "Prise de parole en public", "Pédagogie", "Éloquence", "Persuasion", "Négociation"
    ],
    "collaboration": [
        "Travail en équipe", "Esprit collaboratif", "Relation client", "Gestion de conflits", "Empathie", 
        "Écoute active", "Coordination", "Médiation", "Co-création", "Animation d'atelier", "Travail interdisciplinaire"
    ],
    "résolution_problemes": [
        "Esprit analytique", "Curiosité", "Créativité", "Prise d'initiative", "Pensée critique", 
        "Logique", "Prise de recul", "Gestion des risques", "Approche systémique", "Résilience", 
        "Trouver des solutions alternatives", "Pensée latérale", "Anticipation"
    ],
    "gestion_temps": [
        "Organisation", "Priorisation", "Autonomie", "Gestion du stress", "Planification", "Discipline", 
        "Gestion des deadlines", "Multi-tasking", "Respect des délais", "Rigueur", "Efficacité"
    ],
    "adaptabilité": [
        "Flexibilité", "Ouverture d'esprit", "Capacité d'apprentissage", "Agilité cognitive", "Résilience", 
        "Apprentissage en continu", "Capacité à gérer l'incertitude", "Capacité d’adaptation rapide", "Polyvalence"
    ],
    "leadership": [
        "Prise de décision", "Esprit d'initiative", "Gestion d'équipe", "Influence", "Motivation", 
        "Encadrement", "Coaching", "Capacité à inspirer", "Vision stratégique", "Gestion du changement"
    ]
}


outils = {
    "visualisation": [
        "Power BI", "PBI", "Tableau", "Matplotlib", "Seaborn", "Plotly", "Looker", "Google Data Studio", "GDS", 
        "D3.js", "Bokeh", "Altair", "ggplot2", "Dash", "Excel VBA", "QlikView", "Qlik Sense"
    ],
    "bases_donnees": [
        "PostgreSQL", "Postgres", "MySQL", "MariaDB", "MongoDB", "BigQuery", "Redshift", "Snowflake", "NoSQL", 
        "Cassandra", "CouchDB", "Neo4j", "GraphQL", "Elasticsearch", "Firebase", "Presto", "ClickHouse", "SQL Server"
    ],
    "data_engineering": [
        "Airflow", "ETL", "Pipeline de données", "Kafka", "DataBricks", "Prefect", "Luigi", "Spark Streaming", 
        "Glue", "dbt", "SSIS", "Informatica", "NiFi", "StreamSets", "Talend", "Fivetran"
    ],
    "cloud": [
        "AWS", "Azure", "Google Cloud", "GCP", "S3", "Lambda", "Databricks", "Cloud Computing", "EC2", 
        "Azure Synapse", "Google BigQuery", "Cloud Run", "Athena", "Cloud Functions", "Terraform", "CloudFormation"
    ],
    "machine_learning": [
        "Scikit-learn", "Sklearn", "TensorFlow", "TF", "PyTorch", "Torch", "Keras", "XGBoost", "LightGBM", 
        "CatBoost", "AutoML", "Hugging Face", "BERT", "GPT", "Fast.ai", "OpenCV", "NLTK", "Spacy", "Gensim"
    ],
    "big_data": [
        "Apache Spark", "Spark", "Hadoop", "Hive", "HDFS", "Flink", "Presto", "Delta Lake", "Trino", 
        "Impala", "Storm", "Kylin", "Drill", "Dremio"
    ],
    "devops": [
        "Docker", "Kubernetes", "K8s", "Git", "CI/CD", "Jenkins", "Terraform", "Ansible", "ArgoCD", 
        "Helm", "Travis CI", "CircleCI", "GitLab CI", "Datadog", "Prometheus", "Grafana"
    ]
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
    return texte


# Appliquer le nettoyage aux colonnes concernées
df_clean["Profile"] = df_clean["Profile"].apply(nettoyer_texte)
df_clean["Description"] = df_clean["Description"].apply(nettoyer_texte)


def detecter_mots_cles(texte, dictionnaire):
    tokens = set(nlp(texte).text.split())
    return list(tokens & set(dictionnaire))  # Retourne une liste des mots-clés trouvés


# Ajouter les colonnes contenant la liste des mots-clés trouvés
df_clean["Competences_Clés"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, competences_cles)) + \
                                          df_clean["Description"].apply(lambda x: detecter_mots_cles(x, competences_cles))

df_clean["Soft_Skills"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, soft_skills)) + \
                                    df_clean["Description"].apply(lambda x: detecter_mots_cles(x, soft_skills))

df_clean["Outils"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, outils)) + \
                               df_clean["Description"].apply(lambda x: detecter_mots_cles(x, outils))

# Supprimer les doublons dans les listes
df_clean["Competences_Clés"] = df_clean["Competences_Clés"].apply(lambda x: list(set(x)))
df_clean["Soft_Skills"] = df_clean["Soft_Skills"].apply(lambda x: list(set(x)))
df_clean["Outils"] = df_clean["Outils"].apply(lambda x: list(set(x)))

# Sauvegarde du fichier
df_clean.to_csv(df_output_path, index=False, encoding="utf-8")
print(f"Fichier enregistré : {df_output_path}")

