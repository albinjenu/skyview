from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from .models import Billboard

def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    billboards = Billboard.objects.all()
    return render(request, 'billboards/index.html', {'billboards': billboards})

def billboard_detail(request, pk):
    billboard = get_object_or_404(Billboard, pk=pk)
    return render(request, 'billboards/detail.html', {'billboard': billboard})
