from django.db import models
from datetime import time
# Create your models here.

class Salle(models.Model):
    nom=models.CharField(max_length=100)
    capacite_max=models.IntegerField()
    
    def __str__(self):
        return f"{self.nom} Capacité maximale : {self.capacite_max}"
    
class Entite(models.Model):
    nom=models.CharField(max_length=100)
    filiere=models.CharField(max_length=100)
    anne_etude=models.CharField(max_length=10)
    effectif=models.IntegerField()
    heure_debut = models.TimeField()  # Créneau de début
    heure_fin = models.TimeField()   # Créneau de fin
    priorite = models.IntegerField(default=1) 
    
    def __str__(self):
        return f"{self.nom} Effectif: {self.effectif}"


class Attribution(models.Model):
    entite = models.ForeignKey('Entite', on_delete=models.CASCADE, related_name="attributions")
    salle = models.ForeignKey('Salle', on_delete=models.CASCADE, related_name="attributions")
    heure_debut = models.TimeField()  # Créneau de début
    heure_fin = models.TimeField() 
    date_attribution = models.DateTimeField(auto_now_add=True)  # Date de l'attribution pour suivi historique
    # Facultatif : statut de l'attribution si besoin de plusieurs états
    statut = models.CharField(max_length=50, choices=[('actif', 'Actif'), ('archive', 'Archivé')], default='actif')
    conflit_non_resolu = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('entite', 'salle')  # Une entité doit être assignée à une seule salle par attribution
        ordering = ['date_attribution']

    def __str__(self):
        return f"Attribution de la salle {self.salle.nom} à l'entité {self.entite.nom} de ,{self.entite.heure_debut} à {self.entite.heure_fin}"