# Generated by Django 4.1.1 on 2022-09-22 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('municipios', '0002_auto_20220922_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csv',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='dato',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='municipio',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]