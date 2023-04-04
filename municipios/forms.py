from django import forms

from municipios.models import Municipio

class CreateMunicipio(forms.Form):
    name = forms.CharField(max_length=20)

class MunicipiosSearchForm(forms.Form):
    date_from = forms.DateField(label=("Fecha Desde"),widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(label=("Fecha Hasta"),widget=forms.DateInput(attrs={'type':'date'}))    
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all())

class MunicipioOnlyForm(forms.Form):
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all())
        