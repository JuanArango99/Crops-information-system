
from django import template
from django.http import HttpResponse
from django.shortcuts import render
import numpy as np
from .forms import ChartForm, DatoForm, MunicipiosSearchForm, TerritoriesSearchForm, Punto_ReferenciaForm
from .models import Dato, CSV
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from punto_referencia.models import Punto_Referencia
from municipios.models import Municipio
from django.http import JsonResponse
from django.http import HttpResponse
import pandas as pd
from django.contrib.auth.decorators import login_required
import folium
from branca.element import Figure
from django.core.paginator import Paginator
from datetime import datetime
import csv
import boto3
from django.conf import settings

register = template.Library()
@register.filter
def get_attr(object, name):
    return getattr(object, name, '')

"""
Vista para reportes del clima
"""
@login_required
def reports_view(request):
    form = TerritoriesSearchForm(request.POST or None)
    no_data = obj = datos=punto_referencia=date_from=date_to=date_max=date_min= None
    objs = []
                
    if request.method == 'POST':
        if form.is_valid():
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')        
            id_punto_referencia = request.POST.get('punto_referencia')
            punto_referencia = Punto_Referencia.objects.get(id=id_punto_referencia)                 
            objs = Dato.objects.filter(
                    punto_referencia=punto_referencia,
                    year__lte=date_to,
                    year__gte = date_from                
                    )
            date_max=objs.last().year.strftime("%Y")
            date_min=objs.first().year.strftime("%Y")
            obj = objs[:10]    
            #Se usan cookies para guardar el punto de referencia y el rango de tiempo para usarlos en la vista de exportar.            
            request.session['punto_referencia'] = id_punto_referencia
            request.session['date_to'] = date_to
            request.session['date_from'] = date_from
            if len(obj) == 0:
                no_data = 'No se encontraron registros en las fechas seleccionadas.'
        #Mostrar los 10 primeros registros encontrados
        p = Paginator(obj,10)        
        page = request.GET.get('page')
        datos = p.get_page(page)

    context = {
        'form': form,
        'obj': obj,  
        'cantidad':len(objs),
        'date_from':date_min,
        'date_to':date_max,
        'punto_referencia':punto_referencia, 
        'datos': datos,
        'no_data': no_data,
    }
    return render(request,'punto_referencia/reports.html', context)

""" 
Función para exportar los datos consultados del clima en la vista de reportes como CSV.
"""
def export(request):
    #Se obtienen el punto de referencia y el rango de tiempo guardadas en la sesión
    id_punto_referencia=request.session['punto_referencia'] 
    punto_referencia = Punto_Referencia.objects.get(id=id_punto_referencia)                        
    date_to=request.session['date_to'] 
    date_from=request.session['date_from'] 
    obj = Dato.objects.filter(
                    punto_referencia=punto_referencia,
                    year__lte=date_to,
                    year__gte = date_from                
                    )    
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Fecha','Radiacion Solar', 'Temperatura','Humedad Relativa','Precipitacion'])
    for dato in obj.values_list('year','irradiance','temperature','relative_humidity', 'precipitation'):
        writer.writerow(dato)

    response['Content-Disposition']='attachment;filename=Reporte '+punto_referencia.name+' ('+date_from+' - '+date_to+') '+'.csv'

    return response

"""
Vista del mapa con los puntos de referencia y los municipios a los que hacen parte
"""
def mapView(request):
    #Son 19 colores disponibles por folium para el color de icono.
    colors = ['red', 'orange', 'green', 'darkblue', 'darkgreen', 'black', 'darkred', 'cadetblue', 'pink', 'lightblue', 'purple', 'beige', 'gray', 'lightgray', 'blue', 'darkpurple', 'lightred', 'lightgreen', 'white']
    #Coordenadas para centrar el mapa en cesar
    lon = 9.129754392830863
    lat = -73.53600433475354
    punto_referencia = Punto_Referencia.objects.all()   
    municipios = Municipio.objects.all()
    municipiosPk = [] # Lista de las PK de los municipios
    municipiosName= [] # Lista de los nombres de los municipios
    for municipio in municipios:
        municipiosPk.append(municipio.pk)
        municipiosName.append(municipio.name)    
    municipiosColorName = {}
    municipiosColor = {} # Diccionario con los colores de cada municipio. 
                        #La PK del Municipio es la key y el value es un color de la lista de colores 'colors'
    for i in range(len(municipiosPk)):
        municipiosColorName[municipiosName[i]] = colors[i]
        municipiosColor[municipiosPk[i]] = colors[i]   # Ej: diccionario<key=municipioPk, value=color
                                                      #  {'1':'red; '2':orange'  ....}
    fig = Figure(width="100%", height="550px")
    m = folium.Map(
        location=[lon,lat],
        tiles="OpenStreetMap",        
        width="100",
        height="100",
        zoom_start=8)    
    
    # Capas de visualización (OpenStreetMap, Relieve y Satelital)
    folium.TileLayer(name="Relieve",
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', 
    attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)').add_to(m)        
    folium.TileLayer(name="Satelital",
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
    attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community').add_to(m)    
    folium.LayerControl().add_to(m)
    fig.add_child(m)
    folium.LatLngPopup().add_to(m)

    #Ubicación de cada punto de referencia a partir de su geoubicación y un color de marcador según el municipio al que pertenece 
    for item in punto_referencia:
        folium.CircleMarker(location=(item.longitud,item.latitud),radius=10, fill_color='green').add_to(m)
        folium.Marker(
            location=(item.longitud,item.latitud),popup=item.name,tooltip=item.name, 
            icon=folium.Icon(color=municipiosColor[item.municipio.pk], icon_color='#ffffff')).add_to(m)
        folium.map.Layer()

    m = m._repr_html_()
    context={
        'map':m,
        'municipios': municipiosColorName, 
    }
    return render(request,'punto_referencia/mapa.html',context)

""" 
Vista para los gráficos de las variables del clima
"""
@login_required
def chartView(request):
    unidadesDict = {'temperature': '°C', 'relative_humidity': "%", 'irradiance': "MJ/m^2", 'precipitation': "mm"}
    punto_referenciaForm = Punto_ReferenciaForm()
    datoForm = DatoForm(request.POST or None)
    form = ChartForm(request.POST or None)
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')   
    date_max=date_min=qs = variable = punto_referencia = punto_referenciaObj = unidades=df=dati=datos=fechas=variableName=yDataPrec=yDatosPrec=None    
    periodoLargo=False
    data = []
    fechas=[]
    yDatosFechas=[]
    promedio = minimo = maximo = 0  
    
    if request.method == 'POST':
        if form.is_valid():
            desde = request.POST.get('date_from')
            desde = datetime.strptime(desde,'%Y-%m-%d').strftime("%d/%m/%Y")
            hasta = request.POST.get('date_to')
            hasta = datetime.strptime(hasta,'%Y-%m-%d').strftime("%d/%m/%Y")
            punto_referencia = request.POST.get('punto_referencia')
            variable = str(request.POST.get('variable'))
            variableName = form.cleaned_data['variable']
            variableName = dict(form.fields['variable'].choices)[variableName]            
            punto_referenciaObj = Punto_Referencia.objects.get(id=punto_referencia)                 
            #Conjunto de datos del punto de referencia seleccionado
            qs = Dato.objects.filter(
                punto_referencia = punto_referencia,
                year__lte=date_to,
                year__gte = date_from  
            )
            #Se obtiene la fecha mínima y la fecha máxima en que se encontraron los datos
            date_min=qs.first().year.strftime("%d/%m/%Y")
            date_max=qs.last().year.strftime("%d/%m/%Y")
            #El periodo de tiempo es 'largo' si el periodo es mayor a 5 años
            periodoLargo = True if len(qs)>1825 else False #Periodo largo son periodos mayores a 5 años            
            df = pd.DataFrame(list(qs.values('year', variable)))
            #Para precipitación se suma el total de precipitación que hubo en un periodo de tiempo establecido
            if variableName == "Precipitación":
                # 'dati' agrupa los datos en periodos mensuales
                dati=df.groupby(pd.PeriodIndex(df['year'], freq="M"))[variable].sum().reset_index()
                datos = [i for i in dati[variable].values]
                minimo = min(datos)
                maximo = max(datos)
                promedio = np.average(datos)
                #Si se analiza un periodo de tiempo mayor a un año, se agrega la gráfica de precipitación anual
                if len(qs)>365:
                    yDataPrec = df.groupby(pd.PeriodIndex(df['year'], freq="Y"))[variable].sum().reset_index()
                    yDatosPrec = [i for i in yDataPrec[variable].values]
                    yDatosFechas = yDataPrec['year']
            #Para las otras variables se haya el promedio que hubo en un periodo de tiempo establecido                    
            else:
                # 'dati' agrupa los datos en periodos mensuales
                dati=df.groupby(pd.PeriodIndex(df['year'], freq="M"))[variable].mean().reset_index()
                datos = [i for i in dati[variable].values]
                #Si el periodo de observación es mayor a 5 años
                if periodoLargo:
                    minimo = min(datos)
                    maximo = max(datos)
                    promedio = np.average(datos)
                #Si el periodo de observación es menor a 5 años
                else:
                    minimo = min(df[variable].values)
                    maximo = max(df[variable].values)
                    promedio = np.average(df[variable].values)

            fechas = dati['year']    
            for item in qs:
                data.append(getattr(item, variable))
            unidades = unidadesDict[variable]            
        
    context = {
        'qs': qs,
        'periodoLargo':periodoLargo,
        'punto_referenciaObj': punto_referenciaObj,
        'punto_referenciaForm':punto_referenciaForm,
        'datoForm':datoForm,
        'form':form,
        'variable':variable,
        'variableName':variableName,
        'data':data,   
        'yDatosPrec': yDatosPrec,
        'yDatosFechas':yDatosFechas,
        'fechas':fechas,
        'datos':datos,
        'promedio': round(promedio,2),
        'minimo':round(minimo,2),
        'maximo':round(maximo,2),
        'unidades':unidades,
        'desde': date_min,
        'hasta':date_max
    }
    return render(request, 'punto_referencia/charts.html', context)

"""
En esta función se obtienen los puntos de referencia pertenecientes al municipio seleccionado
en la lista "dropdown" con el fin de simplificar la búsqueda del punto de referencia deseado
"""
def load_punto_referencia(request):
    municipio_id = request.GET.get('municipio')
    if municipio_id != '':        
        punto_referencia = Punto_Referencia.objects.filter(municipio=municipio_id).order_by('name')    
    else:
        punto_referencia = Punto_Referencia.objects.none()
        
    return render(request, 'punto_referencia/prueba.html', {'punto_referencia': punto_referencia}) 

""" 
Vista para la página de carga de datos del clima
"""
@login_required
def uploadTemplateView(request):
    form = MunicipiosSearchForm(request.POST or None)
    if request.method == 'POST':
        municipio = request.POST.get('municipio')      
    context = {
        'form': form,
    }

    return render(request,'punto_referencia/from_file.html', context)

""" 
Función para leer y almacenar los datos dentro del archivo CSV subido.
"""
@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('home'))
def csv_upload_view(request):
    if request.method == 'POST':
        id_municipio = request.POST.get('municipio')        
        csv_file_name = request.FILES.get('file').name
        csv_file = request.FILES.get('file')
        obj, created = CSV.objects.get_or_create(file_name = csv_file_name)
        if created:
            obj.csv_file = csv_file
            obj.save() 
            # #Leer dataset
            # data = pd.read_csv(obj.csv_file.path,skiprows=12, dtype={'DOY': object,'YEAR': object})
            # data = data.replace(-999.0, np.NaN)
            # data = data.fillna(method='bfill')
            # data['DATE'] = pd.to_datetime(data['YEAR']+"-"+data['DOY'], format='%Y-%j').dt.strftime('%d-%m-%Y')
            # data['DATE'] = pd.to_datetime(data['DATE'],format='%d-%m-%Y')
            # #Obtener Longitud y Latitud apartir del csv
            # data_position = pd.read_csv(obj.csv_file.path,skiprows = 3, nrows=0)
            # nombre_territorio = csv_file_name.split(".")[0]
            # nombre_territorio = nombre_territorio.replace("_"," ")       
            # for i in data_position.columns:
            #     a = i
            # longitud = float(a.split()[2])
            # latitud = float(a.split()[4])            
            # #Crear objeto territorio
            # municipio = Municipio.objects.get(id=id_municipio)
            # territorio_obj = Punto_Referencia.objects.create(
            #     name = nombre_territorio,
            #     longitud = longitud,
            #     latitud = latitud,
            #     municipio = municipio)
            # territorio_obj.save()
            # territorio = Punto_Referencia.objects.get(id=territorio_obj.pk)                            
            
            # for i in range(data.shape[0]):
            #     year = data['DATE'][i]
            #     irradiance = data['ALLSKY_SFC_SW_DWN'][i]
            #     temperature = data['T2M'][i]
            #     relative_humidity=data['RH2M'][i]
            #     precipitation = data['PRECTOTCORR'][i]                

            #     data_obj = Dato.objects.create(
            #         year=year,
            #         irradiance=irradiance,
            #         temperature=temperature,
            #         relative_humidity=relative_humidity,
            #         precipitation=precipitation,
            #         punto_referencia=territorio                    
            #         )
            #     data_obj.save()
            # return JsonResponse({'created': True})

            # Conexión a S3 con las credenciales de AWS y obtención del objeto CSV recién creado.
            s3 = boto3.client('s3',
                        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
                        ) 
            response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(obj.csv_file))
            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if status == 200:
                print(f"Successful S3 get_object response 1. Status - {status}")
                data = pd.read_csv(response.get("Body"),skiprows=12, dtype={'DOY': object,'YEAR': object})
                data = data.replace(-999.0, np.NaN)
                data = data.fillna(method='bfill')
                data['DATE'] = pd.to_datetime(data['YEAR']+"-"+data['DOY'], format='%Y-%j').dt.strftime('%d-%m-%Y')
                data['DATE'] = pd.to_datetime(data['DATE'],format='%d-%m-%Y')
                #Obtener Longitud y Latitud apartir del csv
                response2 = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(obj.csv_file))
                status2 = response2.get("ResponseMetadata", {}).get("HTTPStatusCode")
                print(f"Successful S3 get_object response 1. Status - {status2}")
                data_position = pd.read_csv(response2.get("Body"),skiprows = 3, nrows=0)
                nombre_punto_referencia = csv_file_name.split(".")[0]
                nombre_punto_referencia = nombre_punto_referencia.replace("_"," ")       
                for i in data_position.columns:
                    a = i
                longitud = float(a.split()[2])
                latitud = float(a.split()[4])            
                #Crear objeto punto_referencia
                municipio = Municipio.objects.get(id=id_municipio)
                punto_referencia_obj = Punto_Referencia.objects.create(
                    name = nombre_punto_referencia,
                    longitud = longitud,
                    latitud = latitud,
                    municipio = municipio)
                punto_referencia_obj.save()
                punto_referencia = Punto_Referencia.objects.get(id=punto_referencia_obj.pk)                            
                
                for i in range(data.shape[0]):
                    year = data['DATE'][i]
                    irradiance = data['ALLSKY_SFC_SW_DWN'][i]
                    temperature = data['T2M'][i]
                    relative_humidity=data['RH2M'][i]
                    precipitation = data['PRECTOTCORR'][i]                
                    #Crear obj dato clima
                    data_obj = Dato.objects.create(
                        year=year,
                        irradiance=irradiance,
                        temperature=temperature,
                        relative_humidity=relative_humidity,
                        precipitation=precipitation,
                        punto_referencia=punto_referencia                    
                        )
                    data_obj.save()
                return JsonResponse({'created': True})
            else:
                print(f"Unsuccessful S3 get_object response. Status - {status}")
        return JsonResponse({'created': False})
    return HttpResponse()

def export_csv(request):

    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment;filename=Reportes'+ \
        datetime.datetime.now()+'.csv'

    writer=csv.writer(response)
    writer.writerow(['Fecha','Radiacion Solar', 'Temperatura','Precipitación','Humedad Relativa'])