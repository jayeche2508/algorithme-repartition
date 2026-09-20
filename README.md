# Algorithme de répartition

Algorithme de répartition en Python inspiré du Choixpeau magique (Harry Potter).

## Description

Projet réalisé en binôme dans le cadre de ma formation en BUT Informatique. L'objectif était de répartir des élèves dans quatre maisons (Gryffondor, Serdaigle, Poufsouffle, Serpentard) à partir de leurs réponses à un questionnaire, en développant et en comparant plusieurs méthodes de complexité croissante.

## Méthodes implémentées

1. **Score maximal** — l'élève est affecté à la maison correspondant à sa réponse la mieux notée (questionnaire à 4 questions).
2. **Distance euclidienne** — l'élève est comparé à des profils de référence (les fondateurs des maisons) via un questionnaire à 10 questions, et affecté à la maison du profil le plus proche.
3. **k plus proches voisins (k-NN)** — la méthode la plus aboutie : l'élève est comparé à 40 profils de référence, et affecté à la maison majoritaire parmi ses k plus proches voisins.

## Résultats

Taux d'erreur de chaque méthode, mesuré par rapport à la répartition de référence :

| Méthode                          | Taux d'erreur |
|-----------------------------------|---------------|
| Répartition aléatoire (référence) | ~75 %         |
| Score maximal                     | 57,3 %        |
| Distance euclidienne               | 20,2 %        |
| k plus proches voisins (k = 1)     | 16,1 %        |
| k plus proches voisins (k = 3)     | **2,4 %**     |

La méthode des k plus proches voisins avec k = 3 est la plus précise, avec un taux d'erreur de seulement 2,4 %.

## Technologies utilisées

- Python
- JSON

## Fichiers nécessaires

Le script attend les fichiers de données suivants dans le même dossier :
- `questionnaire_premiere_annee.txt` (questionnaire à 4 questions)
- `affectation_premiere_annee.json` (répartition de référence)
- `questionnaire_premiere_annee_10q.txt` (questionnaire à 10 questions)
- `houses_ref.json` (4 profils de référence : les fondateurs)
- `houses_multiple_refs.json` (40 profils de référence)

## Lancer le projet

```bash
python algorithme_repartition.py
```

Le script exécute d'abord une série de tests unitaires, puis calcule et affiche le taux d'erreur de chaque méthode.

## Auteurs

- Jayeche CAROUNAGARANE
- Shayan ISSAC
