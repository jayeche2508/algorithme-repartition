"""
Algorithme de répartition — inspiré du Choixpeau magique (Harry Potter)

Ce programme répartit des élèves dans quatre maisons (Gryffondor, Serdaigle,
Poufsouffle, Serpentard) à partir de leurs réponses à un questionnaire, selon
trois méthodes de complexité croissante, comparées à une répartition de
référence :

    1. Méthode du score maximal (question à réponse la mieux notée)
    2. Méthode de la distance euclidienne (comparaison à des profils de référence)
    3. Méthode des k plus proches voisins (k-NN), la plus précise des trois

Auteurs : Carounagarane Jayeche, Shayan Issac
"""

import json
from random import randint

MAISONS = ["Gryffondor", "Serdaigle", "Poufsouffle", "Serpentard"]


# ---------------------------------------------------------------------------
# Lecture et structuration des données
# ---------------------------------------------------------------------------

def lecture_reponses(fichier):
    """Lit un fichier au format 'nom:R1/R2/R3/R4' (une ligne par élève) et
    retourne un tableau à plat : [nom, r1, r2, r3, r4, nom, r1, ...].
    Utilisé par la méthode du score maximal.
    """
    tab = []
    with open(fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne == "":
                continue
            nom, notes = ligne.split(":")
            tab.append(nom)
            tab.extend(int(note) for note in notes.split("/"))
    return tab


def create_answers_from_text_file(fichier):
    """Lit un fichier au format 'nom:R1/R2/.../Rn' et retourne un dictionnaire
    {nom: [notes]}. Utilisé par les méthodes de distance euclidienne et k-NN,
    compatible avec un nombre de questions quelconque (4 ou 10 par exemple).
    """
    reponses = {}
    with open(fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne == "":
                continue
            nom, notes = ligne.split(":")
            reponses[nom] = [int(note) for note in notes.split("/")]
    return reponses


def nombre_eleves(tab):
    """Retourne le nombre d'élèves présents dans un tableau à plat de réponses."""
    return len(tab) // 5


def eleves(tab):
    """Retourne la liste des noms d'élèves présents dans un tableau à plat de réponses."""
    return [tab[i] for i in range(0, len(tab), 5)]


# ---------------------------------------------------------------------------
# Méthode 1 — Score maximal (première version, 4 questions)
# ---------------------------------------------------------------------------

def maison_eleve(tab, indice):
    """Retourne la maison attribuée à l'élève dont le nom est à `indice`,
    en fonction de son score le plus élevé parmi les 4 questions."""
    scores = tab[indice + 1: indice + 5]
    index_max = scores.index(max(scores))
    return MAISONS[index_max]


def repartition_score_max(tab):
    """Répartit tous les élèves selon la méthode du score maximal."""
    return {tab[i]: maison_eleve(tab, i) for i in range(0, len(tab), 5)}


# ---------------------------------------------------------------------------
# Méthode 2 — Distance euclidienne à des profils de référence
# ---------------------------------------------------------------------------

def distance_euclidienne(tab1, tab2):
    """Calcule la distance euclidienne entre deux tableaux de notes de même longueur."""
    somme = sum((a - b) ** 2 for a, b in zip(tab1, tab2))
    return somme ** 0.5


def maison_euclidienne(reponse, refs):
    """Retourne la maison du profil de référence (`refs`) le plus proche
    de `reponse` au sens de la distance euclidienne."""
    d_min = float("inf")
    maison = ""
    for ref in refs:
        d = distance_euclidienne(reponse, ref["answer"])
        if d < d_min:
            d_min = d
            maison = ref["house"]
    return maison


def repartition_euclidienne(dict_reponses, refs):
    """Répartit tous les élèves selon la méthode de la distance euclidienne
    à des profils de référence."""
    return {nom: maison_euclidienne(notes, refs) for nom, notes in dict_reponses.items()}


# ---------------------------------------------------------------------------
# Méthode 3 — k plus proches voisins (k-NN)
# ---------------------------------------------------------------------------

def position_insertion_voisin(reponse, ref, voisins):
    """Retourne l'indice où insérer `ref` dans une liste de voisins déjà
    triée par distance croissante à `reponse`."""
    d_ref = distance_euclidienne(reponse, ref["answer"])
    for i, voisin in enumerate(voisins):
        if d_ref < distance_euclidienne(reponse, voisin["answer"]):
            return i
    return len(voisins)


def inserer_voisin(reponse, ref, voisins, k):
    """Insère `ref` dans la liste des k plus proches voisins si sa distance
    le justifie, en maintenant une taille maximale de k."""
    index = position_insertion_voisin(reponse, ref, voisins)
    if len(voisins) < k or index < k:
        voisins.insert(index, ref)
        if len(voisins) > k:
            voisins.pop()
    return voisins


def k_plus_proches_voisins(reponse, refs, k):
    """Retourne les k profils de référence les plus proches de `reponse`."""
    voisins = []
    for ref in refs:
        inserer_voisin(reponse, ref, voisins, k)
    return voisins


def maison_majoritaire(voisins):
    """Détermine la maison majoritaire parmi une liste de voisins.
    En cas d'égalité, le voisin le plus proche (indice 0) tranche."""
    votes = {}
    for voisin in voisins:
        m = voisin["house"]
        votes[m] = votes.get(m, 0) + 1

    max_votes = max(votes.values())
    for voisin in voisins:
        if votes[voisin["house"]] == max_votes:
            return voisin["house"]
    return ""


def repartition_knn(dict_reponses, refs, k):
    """Répartit tous les élèves selon la méthode des k plus proches voisins."""
    resultat = {}
    for nom, notes in dict_reponses.items():
        voisins = k_plus_proches_voisins(notes, refs, k)
        resultat[nom] = maison_majoritaire(voisins)
    return resultat


# ---------------------------------------------------------------------------
# Évaluation des méthodes
# ---------------------------------------------------------------------------

def nb_erreurs(repartition_a, repartition_b):
    """Compte le nombre d'élèves affectés différemment entre deux répartitions."""
    return sum(1 for eleve in repartition_a if repartition_a[eleve] != repartition_b[eleve])


def taux_erreur(repartition_estimee, reference):
    """Retourne le taux d'erreur (%) d'une répartition par rapport à la référence."""
    return nb_erreurs(repartition_estimee, reference) / len(reference) * 100


def repartition_aleatoire(liste_eleves):
    """Retourne une répartition aléatoire des élèves dans les 4 maisons."""
    return {nom: MAISONS[randint(0, 3)] for nom in liste_eleves}


def taux_erreur_aleatoire(reference, n_essais=100):
    """Moyenne le taux d'erreur d'une répartition aléatoire sur `n_essais` tirages."""
    noms = list(reference.keys())
    total = sum(nb_erreurs(repartition_aleatoire(noms), reference) for _ in range(n_essais))
    return (total / n_essais) / len(reference) * 100


# ---------------------------------------------------------------------------
# Tests unitaires
# ---------------------------------------------------------------------------

def executer_tests():
    # Méthode du score maximal
    tab = ["Harry Potter", 10, 5, 8, 1, "Cedric Diggory", 6, 7, 9, 4, "Drago Malefoy", 1, 3, 2, 10]
    assert nombre_eleves(tab) == 3
    assert eleves(tab) == ["Harry Potter", "Cedric Diggory", "Drago Malefoy"]
    assert maison_eleve(tab, 0) == "Gryffondor"
    assert repartition_score_max(tab) == {
        "Harry Potter": "Gryffondor", "Cedric Diggory": "Poufsouffle", "Drago Malefoy": "Serpentard"
    }
    print("Tests méthode 'score maximal' : ok")

    # Méthode de la distance euclidienne
    lisa, donna = [7, 4, 8, 5, 7, 10, 3, 7, 8, 5], [4, 6, 2, 10, 2, 10, 4, 8, 7, 9]
    assert round(distance_euclidienne(lisa, donna), 6) == round(10.862780491200215, 6)
    refs = [
        {"house": "Serpentard", "answer": [4, 6, 5, 9, 1, 7, 3, 10, 9, 8]},
        {"house": "Gryffondor", "answer": [9, 3, 6, 2, 10, 2, 5, 1, 8, 2]},
    ]
    assert maison_euclidienne([9, 4, 5, 3, 9, 2, 5, 1, 8, 2], refs) == "Gryffondor"
    print("Tests méthode 'distance euclidienne' : ok")

    # Méthode k-NN
    ref_basse = {"house": "Maison_0", "answer": [0] * 10}
    ref_haute = {"house": "Maison_10", "answer": [10] * 10}
    resultat = repartition_knn(
        {"Eleve_A": [0] * 10, "Eleve_B": [10] * 10}, [ref_basse, ref_haute], 1
    )
    assert resultat == {"Eleve_A": "Maison_0", "Eleve_B": "Maison_10"}
    print("Tests méthode 'k plus proches voisins' : ok")


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------

def main():
    executer_tests()
    print()

    # --- Méthode 1 : score maximal (questionnaire à 4 questions) ---
    reponses_plates = lecture_reponses("questionnaire_premiere_annee.txt")
    repartition_ref = json.load(open("affectation_premiere_annee.json", encoding="utf-8"))

    r1 = repartition_score_max(reponses_plates)
    print(f"Méthode 1 (score maximal)         : {taux_erreur(r1, repartition_ref):.2f} % d'erreur")

    # --- Méthode 2 : distance euclidienne (questionnaire à 10 questions) ---
    reponses_dict = create_answers_from_text_file("questionnaire_premiere_annee_10q.txt")
    refs_fondateurs = json.load(open("houses_ref.json", encoding="utf-8"))

    r2 = repartition_euclidienne(reponses_dict, refs_fondateurs)
    print(f"Méthode 2 (distance euclidienne)  : {taux_erreur(r2, repartition_ref):.2f} % d'erreur")

    # --- Méthode 3 : k plus proches voisins (40 profils de référence) ---
    refs_40 = json.load(open("houses_multiple_refs.json", encoding="utf-8"))

    for k in range(1, 6):
        r3 = repartition_knn(reponses_dict, refs_40, k)
        print(f"Méthode 3 (k-NN, k={k})            : {taux_erreur(r3, repartition_ref):.2f} % d'erreur")

    # --- Référence : répartition aléatoire ---
    print(f"Répartition aléatoire (référence) : {taux_erreur_aleatoire(repartition_ref):.2f} % d'erreur")


if __name__ == "__main__":
    main()
