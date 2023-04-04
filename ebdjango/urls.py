"""ebdjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view,news_view
from .forms import EmailValidationOnForgotPassword, MyAuthenticationForm, MySetPasswordForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('noticias/', news_view, name='news'),    
    path('municipios/', include('municipios.urls', namespace='municipios')),
    path('punto_referencia/', include('punto_referencia.urls', namespace='punto_referencia')),
    path('perfiles/', include('perfiles.urls', namespace='perfiles')),    
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html',authentication_form=MyAuthenticationForm ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),        
    path('password-reset/', auth_views.PasswordResetView.as_view(form_class=EmailValidationOnForgotPassword,template_name="auth/password_reset.html"), name='password_reset'),            
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"), name='password_reset_done'),            
    path('password-reset/confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html", form_class=MySetPasswordForm), name='password_reset_confirm'),            
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"), name='password_reset_complete'),            
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
