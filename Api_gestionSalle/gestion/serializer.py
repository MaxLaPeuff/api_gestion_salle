from rest_framework import serializers
from .models import Salle, Entite, Attribution

class SalleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Salle
        fields=('nom','capacite_max')
        

class FiliereSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Entite
        fields=['nom','effectif','anne_etude','filiere','heure_debut','heure_fin','priorite']
        
        def create(self, validated_data):
            request=self.context.get ('request') #récupère la requête actuelle depuis le contexte fourni par la vue.
       
            return super().create(validated_data)
        
        
class AttributionSerializer(serializers.ModelSerializer):
    salle_nom = serializers.CharField(source='salle.nom', read_only=True)
    filiere_nom = serializers.CharField(source='entite.filiere', read_only=True)
    entite_nom = serializers.CharField(source='entite.nom', read_only=True)
    heure_debut=serializers.CharField(source='entite.heure_debut',read_only=True)
    heure_fin=serializers.CharField(source='entite.heure_fin',read_only=True)
    
    class Meta:
        model=Attribution
        fields = ['salle_nom','entite_nom', 'filiere_nom','heure_debut','heure_fin','date_attribution']