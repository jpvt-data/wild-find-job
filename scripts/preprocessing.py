
import pandas as pd
import re
import ast
import spacy
from spacy.matcher import PhraseMatcher
from spacy.lang.fr.stop_words import STOP_WORDS
import warnings
warnings.simplefilter(action='ignore')
import time


# init check progress
start_time = time.time()

# importation des données
data = pd.read_csv("./base_csv/offres_data.csv")
df = pd.DataFrame(data)


# check progress
end_time = time.time()
execution_time = end_time - start_time
print(f"✅ Importation du fichier 'offres_data.csv' terminée en {execution_time:.{2}f} s ")


#  Filtrer les annonces Data et Données
df_filtered = df[df['OfferTitle'].str.contains(r"(data|donn[eé]e)",
                                               flags=re.IGNORECASE, na=False,
                                               regex=True)]


#  Supprimer duplicate
df_filtered.drop_duplicates(inplace=True)

#  Ajouter OfferLabel pour récupérer le type du poste


def eval(text):
    # liste = []
    ma_liste = ast.literal_eval(text)
    return ma_liste[0]['Label']


df_filtered['OfferLabel'] = df_filtered['Criterions'].apply(eval)

# Garder colonnes intéressantes
df_clean = df_filtered[['Id', 'PublishDate', 'Domaine', 'OfferTitle',
                        'OfferLabel', 'ContractType', 'IsFulltime', 'Telework',
                        'DisplayedSalary', 'Description', 'Profile',
                        'CompanyName', 'CompanyLogo', 'Localisations',
                        'UrlOffre']]

# Supprimer duplicate (part 2)
df_clean.drop_duplicates(inplace=True)

#  Changer format date

# check progress
print("✅ pre-dimmensionnement des données terminée")


def date_format(date):
    regex = re.findall(r"T\d+:\d+:\d+.\d+", date)
    regex = " ".join(regex)
    new_format = date.replace(regex, "")
    return new_format


df_clean['PublishDate'] = df_clean['PublishDate'].apply(date_format)
df_clean['PublishDate'] = df_clean['PublishDate'].apply(lambda x: pd.to_datetime(x))


# check progress
print("✅ traitement de la date terminée")


# Gérer les valeurs manquantes
# On remplace les valeurs vides par NC (non communiqué)...
#  ...sur les colonnes sélectionnées
df_clean['Domaine'].fillna("NC", inplace=True)
df_clean['ContractType'].fillna("NC", inplace=True)
df_clean['Telework'].fillna("NC", inplace=True)
df_clean['DisplayedSalary'].fillna("NC", inplace=True)

# On met une chaine vide à la place des NaN
df_clean['Profile'].fillna("", inplace=True)

# Les entreprises souhaitant rester anonymes
df_clean['CompanyName'].fillna("Anonyme", inplace=True)

# On met un logo par défaut aux annonces qui n'en ont pas
df_clean['CompanyLogo'].fillna("https://cdn-icons-png.flaticon.com/512/1810/1810755.png", inplace=True)

#  Refiltrer les offres sur OfferLabel (data, données)
df_final = df_clean[df_clean['OfferLabel'].str.contains(r"(data|donn[eé]e)",
                                                        flags=re.IGNORECASE,
                                                        na=False, regex=True)]


# check progress
print("✅ Traitement des valeurs manquantes terminée")


# Ajout des colonnes ville, code postal etc

# On crée un df temporaire pour travailler nos données
df_loc = df_final[['Id', 'Localisations']]


# Fonction pour extraire données de localisation


def extract_coordonnees(text):
    def eval_objet():
        ma_liste = []
        if isinstance(text, str):
            ma_liste = ast.literal_eval(text)
            pays = None
            region = []
            departement = []
            ville = []
            codepostal = []

            for dico in ma_liste:
                if dico['Type'] == 'Pays':
                    pays = dico['Label']
                if dico['Type'] == 'Region':
                    region.append(dico['Label'])
                if dico['Type'] == 'Departement':
                    departement.append(dico['Label'])
                if dico['Type'] == 'Commune':
                    ville.append(dico['Label'])
                if dico['Type'] == 'Commune':
                    codepostal.append(dico['ShortUri'])

            return pays, region, departement, ville, codepostal

        return "NC", "NC", "NC", "NC", "NC"

    return eval_objet()


# On ajoute les colonnes souhaitées
df_loc[['Pays', 'Region', 'Departement', 'Ville', 'CodePostal']] = df_loc['Localisations'].apply(lambda x: pd.Series(extract_coordonnees(x)))

# On merge ce df temporaire avec le df_final
df_final2 = df_final.merge(df_loc, left_on="Id", right_on="Id",)

# On drop les colonnes indésirables (Localisation_x, Localisation_y)
df_final2.drop(["Localisations_x", "Localisations_y"], axis=1, inplace=True)


# check progress
end_time2 = time.time()
execution_time2 = end_time2 - end_time
print(f"✅ traitement de la localisation terminée en  {execution_time2:.{2}f} s")


# fonction salaire


def salaire(texte):
    dico_s = {}

    if '€ / heure' in texte or '€ / jour' in texte or 'NC' in texte:
        dico_s["salaire_max"] = "NA"
        dico_s["salaire_min"] = "NA"

    else:
        if '-' in texte:
            min_a = texte.split('-')[0].replace('\u202f', '').replace(',', '.').strip()
            max_a = texte.split('-')[1].replace('\u202f', ''""'').replace(',', '.').replace(' € / an', "").strip()
            if '€' in max_a:
                min = 12*float(min_a)
                max = float(max_a.replace('€ / mois', '').strip())*12
            else:
                min = float(min_a)
                max = float(max_a)

        else:
            max_a = texte.split('-')[0].replace('\u202f', '').replace(',', '.').strip().replace(' € / an', "")
            if '€' in max_a:
                max = float(max_a.replace('€ / mois', '').strip())*12
            else:
                max = float(max_a)
            min = max
        dico_s["salaire_max"] = int(max)
        dico_s["salaire_min"] = int(min)

    return dico_s


df_final2['salaire'] = df_final2['DisplayedSalary'].apply(salaire)
df_final2['salaire_min'] = df_final2['salaire'].apply(lambda x: x['salaire_min'])
df_final2['salaire_max'] = df_final2['salaire'].apply(lambda x: x['salaire_max'])

# on supprime la colonne df['salaire'] et on exporte un CSV
df_final2.drop(['salaire'], axis=1, inplace=True)


# check progress
print(f"✅ traitement des salaires terminée")


# normalisation des metiers de la data 


def attribuer_categorie(metier):
    metier = metier.lower()
    
    if re.search(r"(engineer|developer|software|base|bases|center|miner|technicien|ing[ée]nieur|administrateur|administratrice)", metier):

        return 'Ingénierie des données'
    
    elif re.search(r"(scientist|machine|learning|research|model|science)", metier):
    
        return 'Science des données'
    
    elif re.search(r"(analyst|analyste|business|specialist|specialiste|qualit[eé])", metier):
        return 'Analyse des données'
    
    elif re.search(r"(manager|consultant|product|architect|architecte|consultant|responsable|protection)", metier):
    
        return 'Gestion et management'
    else:
        return 'Autre'
    

df_final2['categorie_metier'] = df_final2['OfferLabel'].apply(attribuer_categorie)


# check progress
end_time3 = time.time()
execution_time3 = end_time3 - end_time2
print(f"✅ creation de la catégorie métier terminée en {execution_time3:.{2}f} s")

# df_final2.to_csv('./data/datasets/brut/df_final2.csv')


# ************************************NLP****************************************


# Charger le modèle NLP
nlp = spacy.load("fr_core_news_lg")


# check progress
end_time4 = time.time()
execution_time4 = end_time4 - end_time3
print(f"✅ spacy load terminée en  {execution_time4:.{2}f} s")


# Définition des chemins des fichiers
# df_clean_path = "./data/datasets/brut/df_final2.csv"
df_output_path = "./data/datasets/propre/df_clean3_nlp.csv"

# Charger df_clean
# df_clean = pd.read_csv(df_clean_path, encoding="utf-8")

df_clean = df_final2

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

end_time5 = time.time()
execution_time5 = end_time5 - end_time4
print(f"✅ nettoyage NLP terminée en {execution_time5:.{2}f} s")

# Fonction pour construire les matchers avec lemmatisation des termes
def construire_matcher(dictionnaire):
    matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")  # Prend en compte les formes de base (lemmatisation)
    for categorie, termes in dictionnaire.items():
        patterns = [nlp(terme.lower()) for terme in termes]  # NLP sur chaque mot-clé
        matcher.add(categorie, patterns)
    return matcher


# check progress
end_time6 = time.time()
execution_time6 = end_time6 - end_time5
print(f"✅ matcher NLP terminée en {execution_time6:.{2}f} s")


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


# check progress
end_time7 = time.time()
execution_time7 = end_time7 - end_time6
print(f"✅ detection mot clef NLP terminée en {execution_time7:.{2}f} s")


# Appliquer la détection NLP aux colonnes
df_clean["Competences_Clés"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_competences)) + \
                               df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_competences))

df_clean["Soft_Skills"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_soft_skills)) + \
                          df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_soft_skills))

df_clean["Outils"] = df_clean["Profile"].apply(lambda x: detecter_mots_cles(x, matcher_outils)) + \
                     df_clean["Description"].apply(lambda x: detecter_mots_cles(x, matcher_outils))


# check progress
end_time8 = time.time()
execution_time8 = end_time8 - end_time7
print(f"✅ matcher appliqué aux colonnes NLP terminée en {execution_time8:.{2}f} s")


# Supprimer les doublons
df_clean["Competences_Clés"] = df_clean["Competences_Clés"].apply(lambda x: list(set(x)))
df_clean["Soft_Skills"] = df_clean["Soft_Skills"].apply(lambda x: list(set(x)))
df_clean["Outils"] = df_clean["Outils"].apply(lambda x: list(set(x)))

end_time9 = time.time()
execution_time9 = end_time9 - end_time8
print(f"✅ traitement NLP  terminée en {execution_time9:.{2}f} s")


# Sauvegarde du fichier
df_clean.to_csv(df_output_path, index=False, encoding="utf-8")


# check progress
end_time10 = time.time()
execution_time10 = end_time10 - end_time9
execution_timeT = end_time10 - start_time
print(f"Fichier enregistré : {df_output_path} en {execution_time10:.{2}f} s")
print(f"temps total de traitement : {execution_timeT:.{2}f} s")


# END