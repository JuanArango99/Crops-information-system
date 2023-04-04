from django.db import models
from django.forms import DateField

class Municipio(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return str(self.name)

class Dato(models.Model):
    year = models.DateField()
    period = models.CharField(max_length=120)
    area_sembrada=models.FloatField(help_text='Ha')
    area_cosechada=models.FloatField(help_text='Ha')
    produccion=models.FloatField(help_text='T')
    rendimiento=models.FloatField(help_text='T/Ha')
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.municipio.name}: {self.year}"

class CSV(models.Model):
    file_name = models.CharField(max_length=120)
    csv_file = models.FileField(upload_to='csvs')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.file_name)
