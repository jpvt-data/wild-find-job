# Documentation des paramètres pour requêter l'API Hellowork

L'API Hellowork permet de récupérer des offres d'emploi en France et propose plusieurs paramètres pour personnaliser les requêtes. Voici les détails des paramètres principaux :

---

## **1. Endpoint principal**

```
https://www.hellowork.com/searchoffers/getsearchfacets
```

Cet endpoint est utilisé pour envoyer des requêtes à l'API.

---

## **2. Paramètres de requête**

### **a. Mot-clé : `k`**
- Description : Spécifie le mot-clé pour rechercher un poste ou un domaine d'activité.
- Exemple :
  - `k=Data+analyst` : Recherche les postes de "Data Analyst".
  - `k=Data+engineer` : Recherche les postes de "Data Engineer".

---

### **b. Localisation : `l`**
- Description : Filtre les offres par localisation.
- Valeurs possibles :
  - `l=france` : Offres sur toute la France.
  - `l=paris` : Offres à Paris.
  - `l=lyon` : Offres à Lyon.

---

### **c. Date de publication : `d`**
- Description : Spécifie l'étendue des offres en fonction de leur date de publication.
- Valeurs possibles :
  - `d=all` : Toutes les annonces disponibles.
  - `d=h` : Annonces publiées au cours des dernières 24 heures.
  - `d=w` : Annonces publiées au cours des 7 derniers jours.

---

### **d. Pagination : `p`**
- Description : Définit le numéro de la page pour la navigation dans les résultats.
- Exemple :
  - `p=1` : Page 1 des résultats.
  - `p=2` : Page 2 des résultats.

---

## **3. Utilisation des filtres supplémentaires**

Hellowork permet d'ajouter d'autres filtres directement depuis le site pour affiner les résultats. Voici quelques suggestions :

- **Secteur d'activité :** Utilisez les options du site pour découvrir les secteurs précédents tels que Retail, Finance, ou éducation.
- **Type de contrat :** CDI, CDD, Freelance, etc.
- **Salaire :** Étendue des salaires, si disponible.

## **4. Notes**
- L'API ne requiert pas de clé d'authentification pour les requêtes de base.
- Veillez à respecter les termes d'utilisation du site Hellowork lors de l'extraction des données.

