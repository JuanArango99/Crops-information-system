from django.shortcuts import render
from .models import ManualUsuario, Perfil
from .forms import ProfileUpdateForm,MyUserCreationForm, UserUpdateForm
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.decorators import login_required
from django.conf import settings
import boto3
from django.http import HttpResponseRedirect

@login_required
def my_profile_view(request):
    perfil = Perfil.objects.get(user=request.user)
    confirm = False
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=perfil)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            confirm = True           
            
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=perfil)
    
    context = {
        'perfil':perfil,
        'u_form':u_form,
        'p_form':p_form,
        'confirm':confirm,
    }
    return render(request, 'perfiles/my_profile.html', context)

class MyPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('perfiles:password-change-done')
    template_name = 'perfiles/password_change.html'   

class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name= 'perfiles/password_change_done.html'    

@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('home'))
def show_user_view(request,user_id):
    user = User.objects.get(pk=user_id)
    context = {        
            'user':user,
        }
    return render(request, 'perfiles/show_user.html', context)

@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('home'))
def user_list_view(request):
    user_list = User.objects.all().exclude(is_superuser=True)
    context = {        
        'user_list':user_list,
    }
    return render(request, 'perfiles/list_users.html', context)

@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('home'))
def create_user_view(request):
    users = User.objects.all()
    form = MyUserCreationForm(request.POST or None)    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('perfiles:list-user')
            
    context={
        'form':form,
        'users':users,
    }
    return render(request, 'perfiles/create_user.html', context)

@login_required
def delete_user_view(request,user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect('perfiles:list-user')

@login_required
def descargar_manual_view(request):
    file = ManualUsuario.objects.order_by('-created').first().pdf_file
    s3 = boto3.client('s3',
                        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
                        )
    url = s3.generate_presigned_url('get_object', 
                                    Params = { 
                                                'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 
                                                'Key': str(file), }, 
                                    ExpiresIn = 600,)
    return HttpResponseRedirect(url)
    

    