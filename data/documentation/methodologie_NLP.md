## 🔍 Méthodologie de Détection des Compétences dans les Offres d'Emploi

Ce document décrit la méthodologie utilisée pour identifier les **compétences clés**, **soft skills** et **outils** dans les descriptions d'offres d'emploi. L'objectif est de permettre une **sélection précise** des offres en fonction de critères définis par l'utilisateur.

---

### 🛠 Étape 1 : Création des Dictionnaires de Mots-Clés

Trois listes de mots-clés sont définies pour capturer les éléments essentiels des annonces :

- **Compétences clés** : *(Ex : SQL, Python, Machine Learning…)*  
- **Soft Skills** : *(Ex : Communication, Esprit d’équipe, Résolution de problèmes…)*  
- **Outils** : *(Ex : Power BI, Tableau, Pandas…)*  

---

### 🤖 Étape 2 : Recherche NLP des Mots-Clés dans `Profile` et `Description`

Un traitement **NLP** est appliqué aux colonnes `Profile` et `Description` afin d’identifier la présence des mots-clés.

**Techniques utilisées** :
1. **Nettoyage des textes** :  
   - Conversion en minuscules  
   - Suppression des caractères spéciaux et ponctuations  
   - Tokenisation des mots-clés

2. **Recherche et détection NLP** :  
   - Utilisation de **spaCy** pour l’analyse linguistique et la reconnaissance des entités.  
   - Intersection entre les mots-clés des dictionnaires et le texte des annonces.  
   - Extraction de **toutes les compétences**, **soft skills** et **outils** détectés.

**Ajout de nouvelles colonnes dans le DataFrame (`df_clean`)** :
- `Competences_Clés_Détectées` → Liste des compétences clés trouvées dans `Profile` et `Description`.  
- `Soft_Skills_Détectés` → Liste des soft skills trouvés.  
- `Outils_Détectés` → Liste des outils trouvés.  

Si une offre contient `"Python", "SQL", "Machine Learning"`, la colonne `Competences_Clés_Détectées` affichera :  
```json
["Python", "SQL", "Machine Learning"]
```
Si aucun mot-clé n'est détecté, la valeur sera une liste vide `[]`.

---

### 📊 Étape 3 : Filtrage des Offres dans l’Interface Streamlit

L’utilisateur peut sélectionner **un ou plusieurs critères** parmi les **compétences clés**, **soft skills** et **outils**.

**Mode de sélection** :
- **Mode stricte** → L’offre doit contenir **tous** les critères sélectionnés.  
- **Mode flexible** → L’offre doit contenir **au moins un** des critères sélectionnés.  

**Classement des offres** :
- Un **système de pondération** peut être ajouté (+1 point par mot-clé détecté) afin de classer les offres par **pertinence**.