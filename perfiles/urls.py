from django.urls import path
from .views import my_profile_view,create_user_view,delete_user_view,user_list_view,show_user_view,MyPasswordChangeView,MyPasswordChangeDoneView,descargar_manual_view
from .forms import MyChangePasswordForm

app_name = 'perfiles'

urlpatterns = [
    path('mi_perfil/', my_profile_view, name='mi-perfil'),
    path('create_user/', create_user_view, name='create-user'),
    path('list_users/', user_list_view, name='list-user'),
    path('delete_user/<user_id>/', delete_user_view, name='delete-user'),
    path('show_user/<user_id>/',  show_user_view, name='show-user'),
    path('change_password/', MyPasswordChangeView.as_view(form_class=MyChangePasswordForm), name='password-change'),
    path('change_password/done/', MyPasswordChangeDoneView.as_view(), name='password-change-done'),
    path('manual_usuario/', descargar_manual_view, name='ver-manual'),
]
