# Generated by Django 3.1.2 on 2022-09-22 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('municipios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csv',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='dato',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='municipio',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
