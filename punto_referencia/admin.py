from django.contrib import admin
from .models import Punto_Referencia, Dato, CSV
# Register your models here.
admin.site.register(Punto_Referencia)
admin.site.register(Dato)
admin.site.register(CSV)