from django.contrib import admin
from .models import Municipio, Dato, CSV

admin.site.register(Municipio)
admin.site.register(CSV)
admin.site.register(Dato)
