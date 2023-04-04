from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    bio = models.TextField(default="no bio...")
    foto = models.ImageField(upload_to='fotos/', default='no_picture.jpg')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
class ManualUsuario(models.Model):
    file_name = models.CharField(max_length=120)
    pdf_file = models.FileField(upload_to='manuales')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.file_name)

