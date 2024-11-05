from django.urls import path
from .views import FiliereCreateAPI,FiliereReadAPI,SalleReadAPI,LancerAlgoAPI,AfficherAttribAPI,ConflitsAPIView,ResoudreConflitAPIView,ListerNonResoluAPIView

urlpatterns = [
    path('list-salle',SalleReadAPI.as_view()), #endpoint=http://127.0.0.1:8000/gestion/list-salle
    
    path('add-filiere',FiliereCreateAPI.as_view()),#endpoint=http://127.0.0.1:8000/gestion/add-filiere
    path('list-filiere',FiliereReadAPI.as_view()),#endpoint=http://127.0.0.1:8000/gestion/list-filiere
    
    path('lancer-algo/', LancerAlgoAPI.as_view(), name='lancer_algo'),#endpoint=http://127.0.0.1:8000/gestion/lancer-algo
    
    path('attribution',AfficherAttribAPI.as_view()),#endpoint=http://127.0.0.1:8000/gestion/attribution
    
    path('conflits',ConflitsAPIView.as_view()),#endpoint=http://127.0.0.1:8000/gestion/conflits
    
    path('gerer-conflit',ResoudreConflitAPIView.as_view()),#endpoint=http://127.0.0.1:8000/gestion/gerer-conflit
    path('non-resolu',ListerNonResoluAPIView.as_view()),
]