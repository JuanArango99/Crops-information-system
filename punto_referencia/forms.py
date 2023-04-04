from django import forms
from municipios.models import Municipio
from punto_referencia.models import Dato, Punto_Referencia

VARIABLES = (    
    ('temperature', ("Temperatura")),
    ('relative_humidity', ("Humedad Relativa")),
    ('irradiance', ("Irradiación")),
    ('precipitation', ("Precipitación"))    
)

class TerritoriesSearchForm(forms.Form):
    date_from = forms.DateField(label=("Fecha Desde"),widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(label=("Fecha Hasta"),widget=forms.DateInput(attrs={'type':'date'}))    
    punto_referencia = forms.ModelChoiceField(queryset=Punto_Referencia.objects.all())

class MunicipiosSearchForm(forms.Form):
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all())

class ChartForm(forms.Form):
    date_from = forms.DateField(label=("Fecha Desde"), widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(label=("Fecha Hasta"),widget=forms.DateInput(attrs={'type':'date'}))    
    variable = forms.ChoiceField(widget=forms.Select(), required=True, choices=VARIABLES)
    
class Punto_ReferenciaForm(forms.ModelForm):
    class Meta:
        model = Punto_Referencia
        fields = ('municipio',)

class DatoForm(forms.ModelForm):
    class Meta:
        model = Dato
        fields = ('punto_referencia',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['punto_referencia'].queryset = Punto_Referencia.objects.none()

 
       
            

