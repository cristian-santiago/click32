from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum, Max, Q
from .models import Store, ClickTrack, Category
import logging
from .click32_admin.functions import get_category_tags, get_site_metrics

logger = logging.getLogger(__name__)


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
    stores = Store.objects.all()

    if selected_tag:
        category = Category.objects.filter(name=selected_tag).first()
        if category:
            stores = stores.filter(tags__in=category.tags.all()).distinct()
        else:
            stores = stores.filter(tags__name=selected_tag).distinct()
    else:
        # Rastrear acesso à home apenas quando não há filtros
        track_click(request, element_type='home_access')

    stores = stores.order_by('-highlight', 'name')
    
    context = {
        'stores': stores,
        'category_tags': get_category_tags(),
        'selected_tag': selected_tag,
    }

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

#--------------------------------
def track_click(request, store_id=None, element_type=None):
    try:
        valid_elements = [
            'main_banner', 'whatsapp_link', 'instagram_link', 'facebook_link',
            'youtube_link', 'x_link', 'google_maps_link', 'website_link', 'home_access'
        ]
        if element_type not in valid_elements:
            return HttpResponse(status=400)

        if element_type == 'home_access':
            # Não associa a uma loja específica para acessos à home
            click_track, created = ClickTrack.objects.get_or_create(
                store=None,  # Nenhum store associado
                element_type='home_access',
                defaults={'click_count': 1}
            )
            if not created:
                click_track.click_count += 1
                click_track.save()
            logger.info(f"Click tracked: Home Access")
            return None  # Retorna None para não interferir na renderização
        else:
            store = get_object_or_404(Store, id=store_id)
            click_track, created = ClickTrack.objects.get_or_create(
                store=store,
                element_type=element_type,
                defaults={'click_count': 1}
            )
            if not created:
                click_track.click_count += 1
                click_track.save()
            logger.info(f"Click tracked: {store.name} - {element_type}")

            if element_type == 'main_banner':
                return render(request, 'store_detail.html', {'store': store})
            else:
                link_field = element_type
                link = getattr(store, link_field, None)
                if link:
                    return HttpResponseRedirect(link)
                return HttpResponse(status=404)
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return HttpResponse(status=500)
    
def teste_print(request):
    print(">>> DEBUG: view teste_print foi chamada <<<")
    return HttpResponse("Teste de print no console OK!")