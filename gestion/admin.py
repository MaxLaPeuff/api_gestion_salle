from django.contrib import admin
from .models import Salle,Entite,Attribution

# Register your models here.

admin.site.register(Salle)
admin.site.register(Entite)
admin.site.register(Attribution)