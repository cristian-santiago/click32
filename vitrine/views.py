from django.shortcuts import render, get_object_or_404
from .models import Store
#from django.http import HttpResponse


def home(request):
    
    stores = Store.objects.all().order_by('-highlight', 'name') # recupera todas as lojas, ordenadas pelo nome
    return render(request, 'home.html', {'stores':stores})
    #return HttpResponse("Pagina inicial da vitrine.")

def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    return render(request, 'store_detail.html', {'store':store})

def advertise(request):

    return render(request, 'advertise.html')

def about(request):
    
    return render(request, 'about.html')