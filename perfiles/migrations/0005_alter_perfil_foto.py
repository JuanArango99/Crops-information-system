# Generated by Django 4.1.1 on 2022-09-23 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0004_alter_perfil_foto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfil',
            name='foto',
            field=models.ImageField(default='no_picture.jpg', upload_to='fotos/'),
        ),
    ]
