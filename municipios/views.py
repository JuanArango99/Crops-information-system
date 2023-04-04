from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import CSV as myCSV
from .models import Dato, Municipio
from punto_referencia.models import Dato as DatoClima, Punto_Referencia
from .forms import MunicipioOnlyForm, MunicipiosSearchForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.core.paginator import Paginator
import csv
import boto3
from django.conf import settings

""" 
Vista para los gráficos de Cultivos
"""
@login_required
def chartView(request):
    qs=qsTodos=municipio=date_from=date_to=id_municipio=nombreMunicipio=datos=datosTodos=years=municipiosTodos=None
    produccionPromedio=rendimientoPromedio=areaPromedio=añoMaximo=añoMinimo=None
    form = MunicipiosSearchForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():            
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            id_municipio = request.POST.get('municipio')
            municipio = Municipio.objects.get(id=id_municipio)   
            nombreMunicipio=municipio.name
            #Conjunto de datos del municipio seleccionado
            qs = Dato.objects.filter(
                    municipio=municipio,
                    year__lte=date_to,
                    year__gte = date_from                
                    )  
            #Obtener el total de produccion anual
            df = pd.DataFrame(list(qs.values('year', 'produccion','rendimiento','area_sembrada')))
            produccionPromedio = df.produccion.mean() #Aun son datos por periodo
            rendimientoPromedio = df.rendimiento.mean()
            areaPromedio = df.area_sembrada.mean()
            dati=df.groupby(pd.PeriodIndex(df['year'], freq="Y"))['produccion'].sum().reset_index()                                    
            datos = [i for i in dati['produccion'].values]
            years = [i for i in dati['year'].values]    
            añoMinimo= min(years) 
            añoMaximo=max(years)
            #Obtener el total de produccion todos los municipios      
            qsTodos = Dato.objects.filter(year__lte=date_to,year__gte = date_from)            
            dfTodos = pd.DataFrame(list(qsTodos.values('year', 'produccion','municipio')))
            dfTodos.municipio = dfTodos.municipio.apply(lambda x: Municipio.objects.get(id=x).name)
            dfTodosAgrup = dfTodos.groupby('municipio')['produccion'].sum().reset_index()
            dfTodosAgrup = dfTodosAgrup.sort_values(by=['produccion'], ascending=False)
            datosTodos = [i for i in dfTodosAgrup['produccion'].values]            
            municipiosTodos = [i for i in dfTodosAgrup['municipio'].values]            

    context={
        'form':form,
        'qs':qs,
        'years':years,
        'datosProdAnual':datos,
        'municipio':nombreMunicipio,
        'datosTodos':datosTodos,
        'municipiosTodos':municipiosTodos,
        'añoMinimo':añoMinimo,
        'añoMaximo':añoMaximo,
        'produccionPromedio':produccionPromedio,
        'rendimientoPromedio':rendimientoPromedio,
        'areaPromedio':areaPromedio,
    }
    return render(request,'municipios/charts.html', context)

""" 
Vista para los gráficos de Agroclima (Clima vs Rendimiento)
"""
@login_required
def AgroClimateView(request):
    qsCultivo=qsClima=qs=df=Temp_Y=Hum_Y=Prec_Y=Rad_Y=municipio=None
    lista_Temp_Y = []
    lista_Prec_Y = []
    lista_Hum_Y = []
    lista_Rad_Y = []
    
    form = MunicipioOnlyForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid(): 
            municipio=form.cleaned_data.get('municipio')  
            qs = Punto_Referencia.objects.filter(municipio=municipio)
            if qs:
                qsCultivo = Dato.objects.filter(
                        municipio=municipio              
                        )   
                #Obtener el primer objeto punto referencia perteneciente al municipio
                punto_referencia =  Punto_Referencia.objects.filter(municipio=municipio)[:1].get()
                qsClima = DatoClima.objects.filter(
                    year__gte = '2006-07-01' ,
                    year__lte= '2018-06-30',##### ARREGLAR!!
                    punto_referencia = punto_referencia
                )
                #Lectura datos de cultivo y rendimiento para ese periodo de tiempo.
                df = pd.DataFrame(list(qsCultivo.values('year','period','rendimiento')))    
                df2 = pd.DataFrame(list(qsClima.values('year','irradiance','temperature','relative_humidity','precipitation')))    
                df2['year'] = pd.to_datetime(df2['year'])
                df2=df2.set_index('year')            
                years = df2.index.year.astype(int)
                semes = (df2.index.month.astype(int) - 1) // 6
                #Los datos de clima se agrupan por semestre
                df2_semestral = df2.groupby([years, semes])['irradiance','relative_humidity','temperature'].mean()
                df2_semestral['precipitation'] = df2.groupby([years, semes])['precipitation'].sum()
                df2_semestral.index.names=['year','period']
                df2_semestral=df2_semestral.reset_index()
                df2_semestral['period'] = df2_semestral.apply(lambda row: "".join([str(int(row['year'])),"A"]) if row['period'] == 0 else "".join([str(int(row['year'])),"B"]),axis=1)             
                #Agregar las columnas 'rendimiento' y 'period' del dataframe de los cultivos 
                #al dataframe con los datos del clima agrupados por semester (df2_semestral)
                df_merged = pd.merge(df[['rendimiento','period']],df2_semestral, on="period", how="left")
                df_merged['irradiance']=df_merged['irradiance'].apply(lambda x: round(x,2))            
                df_merged['relative_humidity']=df_merged['relative_humidity'].apply(lambda x: round(x,2))            
                df_merged['temperature']=df_merged['temperature'].apply(lambda x: round(x,2))            
                df_merged['precipitation']=df_merged['precipitation'].apply(lambda x: round(x,2))            
                df_merged['rendimiento']=df_merged['rendimiento'].apply(lambda x: round(x,2))  
                #Se crean diferentes listas para el conjunto x,y con los datos de la variable climática vs rendimiento
                for h, w in zip(df_merged['temperature'], df_merged['rendimiento']):
                    lista_Temp_Y.append({'x': h, 'y': w})
                for h, w in zip(df_merged['precipitation'], df_merged['rendimiento']):
                    lista_Prec_Y.append({'x': h, 'y': w})
                for h, w in zip(df_merged['relative_humidity'], df_merged['rendimiento']):
                    lista_Hum_Y.append({'x': h, 'y': w})
                for h, w in zip(df_merged['irradiance'], df_merged['rendimiento']):
                    lista_Rad_Y.append({'x': h, 'y': w})
                Temp_Y = str(lista_Temp_Y).replace('\'', '')
                Prec_Y = str(lista_Prec_Y).replace('\'', '')
                Hum_Y = str(lista_Hum_Y).replace('\'', '')
                Rad_Y = str(lista_Rad_Y).replace('\'', '')
            
    context = {
        'form':form,
        'qs':qs,
        'df':df,
        'Temp_Y':Temp_Y,
        'Prec_Y':Prec_Y,
        'Hum_Y':Hum_Y,
        'Rad_Y':Rad_Y,
        'municipio':municipio,
    }
    return render(request,'municipios/agroclimate.html', context)

""" 
Vista reportes de cultivos
"""
@login_required
def reports_view(request):
    form = MunicipiosSearchForm(request.POST or None)
    no_data = obj = datos=municipio=date_from=date_to=date_min=date_max=None
    objs = []

    if request.method == 'POST':
        if form.is_valid():
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            id_municipio = request.POST.get('municipio')
            municipio = Municipio.objects.get(id=id_municipio)   
            objs = Dato.objects.filter(
                    municipio=municipio,
                    year__lte=date_to,
                    year__gte = date_from                
                    )  
            date_max=objs.last().year.strftime("%Y")
            date_min=objs.first().year.strftime("%Y")
            obj = objs[:5]    
            #Se usan cookies para guardar el municipio y el rango de tiempo para usarlos en la vista de exportar.
            request.session['municipio'] = id_municipio
            request.session['date_to'] = date_to
            request.session['date_from'] = date_from
            if len(obj) == 0:
                no_data = 'No se encontraron registros en las fechas seleccionadas.'
        #Mostrar los 5 primeros registros encontrados
        p = Paginator(obj,5)        
        page = request.GET.get('page')
        datos = p.get_page(page) 

    context={
        'form': form,
        'obj': obj,  
        'cantidad':len(objs),
        'date_from':date_min,
        'date_to':date_max,
        'municipio':municipio, 
        'datos': datos,
        'no_data': no_data,
    }
    return render(request,'municipios/reports.html', context)

""" 
Función para exportar los datos del cultivo consultados en la vista de reportes como CSV.
"""
def export(request):
    #Se obtienen el municipio y el rango de tiempo guardadas en la sesión
    id_municipio=request.session['municipio'] 
    municipio = Municipio.objects.get(id=id_municipio)                        
    date_to=request.session['date_to'] 
    date_from=request.session['date_from'] 
    obj = Dato.objects.filter(
                    municipio=municipio,
                    year__lte=date_to,
                    year__gte = date_from                
                    )  
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Año','Periodo', 'Area Sembrada','Area Cosechada','Produccion','Rendimiento'])
    for dato in obj.values_list('year','period','area_sembrada','area_cosechada','produccion','rendimiento'):
        writer.writerow(dato)

    response['Content-Disposition']='attachment;filename=Reporte '+municipio.name+' ('+date_from+' - '+date_to+') '+'.csv'
    return response

""" 
Vista para la página de carga de datos del cultivo
"""
@login_required
def create_municipio_view(request):
    context = {}
    return render(request,'municipios/home.html', context)

""" 
Función para leer y almacenar los datos dentro del archivo CSV subido.
"""
@login_required
def csv_upload_view(request):
    if request.method == 'POST':
        csv_file_name = request.FILES.get('file').name
        csv_file = request.FILES.get('file')
        obj, created = myCSV.objects.get_or_create(file_name = csv_file_name)
        if created:
            obj.csv_file = csv_file
            obj.save()
            # #Leer dataset     
            # df = pd.read_csv(obj.csv_file.path, parse_dates=['AÑO'])
            # data = df.iloc[:,[3,8,9,10,11,12,13]]
            # nombres = ['Municipio','Year','Periodo','Area_Sembrada', 'Area_Cosechada', 'Produccion','Rendimiento']
            # for i in range(len(nombres)):
            #     data.columns.values[i] = nombres[i]
            # # Filtrar por los municipios seleccionados en el proyecto pertenecientes a las zonas productoras en Cesar. 
            # # A futuro se puede permitir que lea todos los municipios.
            # Munis = ["Aguachica","Agustin Codazzi","Bosconia","La Paz","Rio De Oro","San Alberto","San Diego","San Martin","Valledupar"]
            # Munis = [x.upper() for x in Munis]
            # data = data[data['Municipio'].isin(Munis)]
            # data=data.groupby(['Municipio','Year','Periodo']).sum().reset_index()
            # data=data.sort_values(by=['Municipio','Year'])            
            # data['Rendimiento'] = data.apply(lambda row: row.Produccion / row.Area_Cosechada if row.Area_Cosechada > 0 else 0 , axis=1)
            # data = data.reset_index(drop=True)            
            # #Crear obj municipio
            # for muni in Munis:
            #     municipio_obj, createdd = Municipio.objects.get_or_create(name=muni)
            #     if createdd:
            #         municipio_obj.save()       
            # #Crear obj dato
            # for i in range(data.shape[0]):
            #     year = data['Year'][i]
            #     period = data['Periodo'][i]
            #     area_sembrada = data['Area_Sembrada'][i]
            #     area_cosechada = data['Area_Cosechada'][i]
            #     produccion = data['Produccion'][i]
            #     rendimiento = data['Rendimiento'][i]
            #     municipio = Municipio.objects.get(name=data['Municipio'][i])

            #     data_obj = Dato.objects.create(
            #         year=year,
            #         period=period,
            #         area_sembrada=area_sembrada,
            #         area_cosechada=area_cosechada,
            #         produccion=produccion,
            #         rendimiento=rendimiento,
            #         municipio=municipio
            #         )
            #     data_obj.save()
            # return JsonResponse({'created':True})  
            
            # Conexión a S3 con las credenciales de AWS y obtención del objeto CSV recién creado.
            s3 = boto3.client('s3',
                        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
                        ) 
            response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(obj.csv_file))
            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if status == 200:
                print(f"Successful S3 get_object response. Status - {status}")
                #Leer dataset
                df = pd.read_csv(response.get("Body"),parse_dates=['AÑO'])
                data = df.iloc[:,[3,8,9,10,11,12,13]]
                # Filtrar por los municipios seleccionados en el proyecto pertenecientes a las zonas productoras en Cesar. 
                # A futuro se puede permitir que lea todos los municipios.
                nombres = ['Municipio','Year','Periodo','Area_Sembrada', 'Area_Cosechada', 'Produccion','Rendimiento']
                for i in range(len(nombres)):
                    data.columns.values[i] = nombres[i]
                Munis = ["Aguachica","Agustin Codazzi","Bosconia","La Paz","Rio De Oro","San Alberto","San Diego","San Martin","Valledupar"]
                Munis = [x.upper() for x in Munis]
                data = data[data['Municipio'].isin(Munis)]
                data=data.groupby(['Municipio','Year','Periodo']).sum().reset_index()
                data=data.sort_values(by=['Municipio','Year'])            
                data['Rendimiento'] = data.apply(lambda row: row.Produccion / row.Area_Cosechada if row.Area_Cosechada > 0 else 0 , axis=1)
                data = data.reset_index(drop=True)            
                #Crear obj municipio
                for muni in Munis:
                    municipio_obj, createdd = Municipio.objects.get_or_create(name=muni)
                    if createdd:
                        municipio_obj.save()       
                #Crear obj dato cultivo
                for i in range(data.shape[0]):
                    year = data['Year'][i]
                    period = data['Periodo'][i]
                    area_sembrada = data['Area_Sembrada'][i]
                    area_cosechada = data['Area_Cosechada'][i]
                    produccion = data['Produccion'][i]
                    rendimiento = data['Rendimiento'][i]
                    municipio = Municipio.objects.get(name=data['Municipio'][i])
                    data_obj = Dato.objects.create(
                        year=year,
                        period=period,
                        area_sembrada=area_sembrada,
                        area_cosechada=area_cosechada,
                        produccion=produccion,
                        rendimiento=rendimiento,
                        municipio=municipio
                        )
                    data_obj.save()
                return JsonResponse({'created':True})
            else:
                print(f"Unsuccessful S3 get_object response. Status - {status}")
        return JsonResponse({'created':False,'fileName':csv_file_name})
    return HttpResponse()
