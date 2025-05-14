from django.shortcuts import render, get_object_or_404
from .models import Store, Tag
#from django.http import HttpResponse


def home(request):
    
    selected_tag = request.GET.get('tag')
    
    if selected_tag:
        stores = Store.objects.filter(tags__name=selected_tag).distinct()
    else:
        stores = Store.objects.all()

    # Agrupamento de tags por setor
    tag_groups = {
        'Comidas': ['Comidas','Pizzas', 'Lanches', 'Açaiterias'],
        'Comércios': ['Bazares', 'PetShops', 'Padarias', 'Auto Peças'],    
        'Serviços': ['Encanador', 'Pintor', 'Pedreiro','Técnico de Informática'],
        'Beleza': ['Beleza', 'Manicure', 'Salão de Beleza', 'Maquiadora'],
        'Saúde' :['Psicólogos', 'Fisioterapeutas', 'Nutricionista', 'Fonoaudiólogo'],
        'Educação': ['Alfabetização','Música', 'Inglês', 'Aulas Particulares'],
        'Outros': ['Aluguéis', 'Vendas', 'Trocas', 'Parcerias']
        # Adicione mais grupos conforme necessário
    }

    context = {
        'stores': stores,
        'tag_groups': tag_groups,
    }

    return render(request, 'home.html', context)
    

def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    return render(request, 'store_detail.html', {'store':store})

def advertise(request):

    return render(request, 'advertise.html')

def about(request):
    
    return render(request, 'about.html')