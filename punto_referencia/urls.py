from django.urls import path
from .views import (
    reports_view, 
    chartView,
    csv_upload_view,
    mapView,
    uploadTemplateView,
    load_punto_referencia,
    export
    )

app_name = 'punto_referencia'

urlpatterns = [
    path('reports/', reports_view, name='reports'),
    path('charts/', chartView, name='charts'),
    path('clima/', uploadTemplateView, name='clima'),
    path('upload/', csv_upload_view, name='upload'),
    path('map/', mapView, name='map'),
    path('export/', export, name='export'),
    path('ajax/load-cities/', load_punto_referencia, name='ajax_load_cities'),  # <-- this one here
   
]
