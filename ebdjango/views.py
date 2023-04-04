from django.shortcuts import render, redirect
from django.contrib.auth import logout


def home_view(request):
    return render(request,'home.html')

def news_view(request):
    return render(request,'news.html')

def logout_view(request):
    logout(request)
    return redirect('login')
