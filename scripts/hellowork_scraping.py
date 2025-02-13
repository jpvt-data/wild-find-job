import requests
import pandas as pd
import json
import warnings
import time
warnings.simplefilter(action='ignore')


# init check progress
start_time = time.time()

# liste des pages par type de metier à scrapper 
mots_cles = ['Ingénieur big data', 'Data scientist', 'Data analyst',
                'Data analyste', 'Data manager', 'Data specialist',
                'Chef de projet data', 'Master data', 'Consultant en big data',
                'Consultant big data']

# - Définir l'endpoint principal de l'API Hellowork et de l'user agent pour "contourner la protection"
endpoint = "https://www.hellowork.com/searchoffers/getsearchfacets"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

# initialisation de la liste des offres
all_offres = []

# Boucle sur les mots-clés
for mot_cle in mots_cles:
    page = 1            # Réinitialisation de la page pour chaque mot-clé
    params = {
        "k": mot_cle,   # Mot-clé pour le poste
        "l": "france",  # Localisation : France
        "d": "all",     # Toutes les annonces disponibles
        "p": page
    }
    # Boucle pour récupérer toutes les pages pour le mot-clé en cours
    while True:
        response = requests.get(endpoint, params=params, headers={"User-Agent": user_agent})

        if response.status_code == 200:
            data = response.json()
            if 'Results' in data and data['Results']:
                all_offres.extend(data['Results'])                                       # Ajoute les offres récupérées à la liste
                print(f"Page {page} récupérée avec succès pour le mot-clé {mot_cle}.")
                page += 1                                                                # Passe à la page suivante
                params["p"] = page                                                       # Met à jour le # de page
            else:
                print(f"Aucune offre supplémentaire trouvée pour le mot-clé {mot_cle}.")
                break
        else:
            print(f"Erreur lors de la requête à la page {page} pour le mot-clé {mot_cle} : {response.status_code}")
            break

    # check progress
    end_time_i = time.time()
    execution_time_i = end_time_i - start_time
    print(f"✅ scrap {mot_cle} terminée en {execution_time_i:.{2}f} s ")

# Affichage du nombre total d'offres collectées
end_time = time.time()
execution_time = end_time - start_time
print(f"Nombre total d'offres collectées : {len(all_offres)} en {execution_time:.{2}f} s")

# Transformation des données en dataframe
df_offres = pd.DataFrame(all_offres)

# Exportation des données nettoyées au format CSV.
df_offres.to_csv('./base_csv/offres_data.csv', index=False)
