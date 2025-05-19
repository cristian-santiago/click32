from django.shortcuts import render, get_object_or_404
from .models import Store, Tag

def get_tag_groups():
    return {
        'Comidas': ['Comidas', 'Pizzas', 'Lanches', 'Açaiterias'],
        'Comércios': ['Bazares', 'PetShops', 'Padarias', 'Auto Peças'],    
        'Serviços': ['Encanador', 'Pintor', 'Pedreiro', 'Técnico de Informática'],
        'Beleza': ['Beleza', 'Manicure', 'Salão de Beleza', 'Maquiadora'],
        'Saúde': ['Psicólogos', 'Fisioterapeutas', 'Nutricionista', 'Fonoaudiólogo'],
        'Educação': ['Alfabetização', 'Música', 'Inglês', 'Aulas Particulares'],
        'Outros': ['Aluguéis', 'Vendas', 'Trocas', 'Parcerias']
    }

def home(request):
    selected_tag = request.GET.get('tag')
    if selected_tag:
        stores = Store.objects.filter(tags__name=selected_tag).distinct().order_by('-highlight', 'name')
    else:
        stores = Store.objects.all().order_by('-highlight', 'name')
    
    context = {'stores': stores, 'tag_groups': get_tag_groups()}
    return render(request, 'home.html', context)


def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    context = {'store': store, 'tag_groups': get_tag_groups()}
    return render(request, 'store_detail.html', context)

def advertise(request):
    
    context = {'tag_groups': get_tag_groups()}
    return render(request, 'advertise.html', context)

def about(request):
    context = {'tag_groups': get_tag_groups()}
    return render(request, 'about.html', context)    