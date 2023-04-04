# Generated by Django 4.1.1 on 2022-09-25 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('municipios', '0003_alter_csv_id_alter_dato_id_alter_municipio_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CSV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=120)),
                ('csv_file', models.FileField(upload_to='csvs')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Punto_Referencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('longitud', models.FloatField()),
                ('latitud', models.FloatField()),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='municipios.municipio')),
            ],
        ),
        migrations.CreateModel(
            name='Dato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.DateField()),
                ('irradiance', models.FloatField(help_text='MJ/m^2/day')),
                ('temperature', models.FloatField(help_text='°C')),
                ('relative_humidity', models.FloatField(help_text='%')),
                ('precipitation', models.FloatField(help_text='mm/day')),
                ('punto_referencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='punto_referencia.punto_referencia')),
            ],
        ),
    ]
