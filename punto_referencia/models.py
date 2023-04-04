from django.db import models
from municipios.models import Municipio

class Punto_Referencia(models.Model):
    name = models.CharField(max_length=120)
    longitud = models.FloatField()
    latitud = models.FloatField()
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Dato(models.Model):
    year = models.DateField()
    irradiance = models.FloatField(help_text='MJ/m^2/day')
    temperature = models.FloatField(help_text='°C')
    relative_humidity = models.FloatField(help_text='%')
    precipitation = models.FloatField(help_text='mm/day')
    punto_referencia = models.ForeignKey(Punto_Referencia, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.punto_referencia.name}: {self.year}"

class CSV(models.Model):
    file_name = models.CharField(max_length=120)
    csv_file = models.FileField(upload_to='csvs')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.file_name)
    