from xml.etree.ElementInclude import include
from django.urls import path
from .views import create_municipio_view,csv_upload_view,export,reports_view,chartView,AgroClimateView

app_name = 'municipios'

urlpatterns = [
 path('maiz/', create_municipio_view, name = "maiz"),   
 path('upload/', csv_upload_view, name='upload'),
 path('charts/', chartView, name='charts'),
 path('charts/agroclima/', AgroClimateView, name='agroclimate'),
 path('reports/', reports_view, name='reports'),
 path('export/', export, name='export'),

]
