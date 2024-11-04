from .serializer import SalleSerializer,FiliereSerializer,AttributionSerializer
from .models import Salle,Entite,Attribution
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .util import lancer_algo_affectation
from django.db.models import F
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

"""CLASS GENERIQUE POUR LISTER LES SALLES """

class SalleReadAPI(generics.ListAPIView):
    queryset=Salle.objects.all()
    serializer_class=SalleSerializer
    
"""CLASS GENERIQUE POUR CRUD LES FILIERES""" 

class FiliereReadAPI(generics.ListAPIView):
    queryset=Entite.objects.all()
    serializer_class=FiliereSerializer
    
class FiliereCreateAPI(generics.CreateAPIView):
    queryset=Entite.objects.all()
    serializer_class=FiliereSerializer
    
    def get_serializer_context(self):
        # Ajouter la requête actuelle au contexte pour que le sérialiseur puisse y accéder
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
"""CLASS POUR LANCER L'ALGORITHME"""

class LancerAlgoAPI(APIView):
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(
    operation_description="Lancer l'algorithme pour assigner les salles",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'entite_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de l’entité'),
            'salle_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la salle'),
            'heure_debut': openapi.Schema(type=openapi.TYPE_STRING, format='time', description='Heure de début'),
            'heure_fin': openapi.Schema(type=openapi.TYPE_STRING, format='time', description='Heure de fin'),
            'date_debut': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date de début'),
            'date_fin': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date de fin'),
        }
    ),
    responses={
        201: openapi.Response(description="Attribution créée avec succès"),
        400: openapi.Response(description="Conflits détectés avec les attributions existantes"),
    },
)    
    def post(self, request):
        try:
            # Lancer l'algorithme et obtenir les attributions optimales
            attributions, conflits = lancer_algo_affectation()  # Fonction qui retourne les résultats de l'affectation

            # Sauvegarder les attributions dans la base de données
            for entite, salle in attributions.items():
                Attribution.objects.create(entite=entite, salle=salle,heure_debut=entite.heure_debut,
                heure_fin=entite.heure_fin,)

            # Afficher les entités en conflit
            conflit_messages = [f"{entite.nom} : sans salle" for entite in conflits]

            return Response(
                {
                    "message": "L'algorithme a été exécuté avec succès et les salles ont été attribuées.",
                    "conflits": conflit_messages
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            
class AfficherAttribAPI(generics.ListAPIView):
    permission_classes=[IsAuthenticated]

    queryset=Attribution.objects.all()
    serializer_class=AttributionSerializer
    

class ConflitsAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        # Récupérer toutes les attributions
        attributions = Attribution.objects.all()
        
        # Dictionnaire pour stocker les conflits
        conflits = {}
        
        # Identifier les conflits
        for attrib in attributions:
            salle_id = attrib.salle.id
            
            # Vérifier si la salle est déjà dans le dictionnaire
            if salle_id not in conflits:
                conflits[salle_id] = {
                    "salle_nom": attrib.salle.nom,
                    "conflits_entites": []
                }
                
            # Ajouter l'attribution à la liste des conflits pour cette salle
            conflits[salle_id]["conflits_entites"].append({
                "entite_nom": attrib.entite.nom,
                "heure_debut": attrib.heure_debut,
                "heure_fin": attrib.heure_fin
            })

        # Filtrer les conflits
        conflits_result = []
        for salle_info in conflits.values():
            entites = salle_info["conflits_entites"]
            # Vérifier les conflits pour cette salle
            for i in range(len(entites)):
                for j in range(i + 1, len(entites)):
                    entite_a = entites[i]
                    entite_b = entites[j]
                    # Vérification si les heures se chevauchent
                    print(f"Comparing {entite_a} with {entite_b}")  # Debug
                    if (entite_a["heure_debut"] < entite_b["heure_fin"] and entite_a["heure_fin"] > entite_b["heure_debut"]):
                        # Si il y a un conflit, l'ajouter à la liste des résultats
                        conflits_result.append({
                            "salle_nom": salle_info["salle_nom"],
                            "entites": [entite_a["entite_nom"], entite_b["entite_nom"]]
                        })
                        print(f"Conflict found: {entite_a['entite_nom']} and {entite_b['entite_nom']} in {salle_info['salle_nom']}")  # Debug

        # Filtrer les résultats pour ne pas avoir de doublons
        uniques_result = []
        for conflit in conflits_result:
            if not any(c["salle_nom"] == conflit["salle_nom"] and sorted(c["entites"]) == sorted(conflit["entites"]) for c in uniques_result):
                uniques_result.append(conflit)

        print(f"Final conflicts: {uniques_result}")  # Debug

        return Response(uniques_result)



class ResoudreConflitAPIView(APIView):
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Résout les conflits en supprimant certaines attributions et en gardant une attribution spécifique.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'attribution_nom': openapi.Schema(type=openapi.TYPE_STRING, description="Nom de l'attribution à garder"),
                'entites_a_supprimer': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description="Liste des noms des entités à supprimer en cas de conflit"),
            }
        ),
        responses={
            200: openapi.Response("Conflit résolu avec succès"),
            404: openapi.Response("Attribution non trouvée")
        }
    )
    def post(self, request):
        nom_a_garder = request.data.get("nom_a_garder")  # Nom de l'entité à garder
        noms_a_supprimer = request.data.get("noms_a_supprimer")  # Liste des noms des entités à supprimer

        # Vérification des données reçues
        if not nom_a_garder or not noms_a_supprimer:
            return Response({"error": "Le nom de l'entité à garder et la liste des noms à supprimer sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(noms_a_supprimer, list):
            return Response({"error": "La liste des noms à supprimer doit être une liste."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérification que l'entité à garder existe
        try:
            entite_a_garder = Attribution.objects.get(entite__nom=nom_a_garder)
        except Attribution.DoesNotExist:
            return Response({"error": f"Aucune attribution trouvée pour l'entité à garder : {nom_a_garder}"}, status=status.HTTP_404_NOT_FOUND)

        # Supprimer les attributions correspondant aux noms fournis
        try:
            # Supprimer les attributions des entités à supprimer
            attributions_a_supprimer = Attribution.objects.filter(entite__nom__in=noms_a_supprimer).exclude(entite__nom=nom_a_garder)

            deleted_count, _ = attributions_a_supprimer.delete()

            return Response({"message": f"{deleted_count} conflits résolus avec succès."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListerNonResoluAPIView(APIView):
    def get(self, request):
        non_resolus = Attribution.objects.filter(conflit_non_resolu=True).values("entite__nom", "salle__nom")
        return Response(list(non_resolus), status=status.HTTP_200_OK)
