import pulp
from .models import Entite, Salle,Attribution
from datetime import time

def lancer_algo_affectation():
    Attribution.objects.all().delete()
    # Récupération des données de la BDD
    demandes = Entite.objects.all()
    salles = Salle.objects.all()
    
    # Définition du modèle de PL
    model = pulp.LpProblem("Affectation_Salles", pulp.LpMinimize)
    
    # Variables de décision : Xij = 1 si la salle j est assignée à l’entité i, sinon 0
    x = pulp.LpVariable.dicts("x", 
                              ((demande.id, salle.id) for demande in demandes for salle in salles), 
                              cat="Binary")
    
    # Fonction objectif : minimiser les espaces non utilisés tout en maximisant les priorités
    model += pulp.lpSum(((salle.capacite_max - demande.effectif) - demande.priorite) * x[(demande.id, salle.id)]
                        for demande in demandes for salle in salles if salle.capacite_max >= demande.effectif)

    # Contrainte 1 : chaque entité doit être assignée à une seule salle
    for demande in demandes:
        model += pulp.lpSum(x[(demande.id, salle.id)] for salle in salles) == 1
     
    # Contrainte 2 : une salle ne peut être attribuée qu’à une seule entité pour un créneau donné
    for salle in salles:
        for demande1 in demandes:
            for demande2 in demandes:
                if demande1 != demande2:
                    # Vérification des chevauchements de créneaux
                    if (demande1.heure_debut < demande2.heure_fin and demande1.heure_fin > demande2.heure_debut):
                        model += x[(demande1.id, salle.id)] + x[(demande2.id, salle.id)] <= 1

    # Contrainte 3 : la salle assignée doit avoir une capacité suffisante
    for demande in demandes:
        for salle in salles:
            model += x[(demande.id, salle.id)] <= (salle.capacite_max >= demande.effectif)

    # Résolution du modèle
    model.solve()

    # Vérification et stockage des résultats
    attribution_result = {}
    conflits = []

    for demande in demandes:
        salle_attribuee = None
        for salle in salles:
            if pulp.value(x[(demande.id, salle.id)]) == 1:
                salle_attribuee = salle
                break

        if salle_attribuee:
            attribution_result[demande] = salle_attribuee
        else:
            conflits.append(demande)  # Ajouter à la liste des conflits si aucune salle n'est attribuée

    # Retourne les résultats et les conflits
    return attribution_result, conflits
