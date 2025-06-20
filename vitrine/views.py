from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum, Max, Q
from .models import Store, ClickTrack, Category
from django.core.mail import send_mail
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
    stores_vip = None  # Inicializa como None para evitar exibição com filtros

    if selected_tag:
        category = Category.objects.filter(name=selected_tag).first()
        if category:
            stores = stores.filter(tags__in=category.tags.all()).distinct()
        else:
            stores = stores.filter(tags__name=selected_tag).distinct()
    else:
        # Rastrear acesso à home e carregar lojas VIP apenas sem filtros
        track_click(request, element_type='home_access')
        stores_vip = Store.objects.filter(is_vip=True)[:10]  # Limita a 10 lojas VIP

    stores = stores.order_by('-highlight', 'name')
    
    context = {
        'stores': stores,
        'stores_vip': stores_vip,  # Será None se houver filtro
        'category_tags': get_category_tags(),
        'selected_tag': selected_tag,
    }

    return render(request, 'home.html', context)

def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    context = {
        'store': store,
        'category_tags': get_category_tags()
    }
    return render(request, 'store_detail.html', context)

def advertise(request):
    context = {'category_tags': get_category_tags()}
    return render(request, 'advertise.html', context)

def about(request):
    context = {'category_tags': get_category_tags()}
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
    





# view inactivated #
def submit_advertise(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        business = request.POST.get('business')
        message = request.POST.get('message')
        # Exemplo: salvar ou enviar e-mail
        send_mail(
            f'Novo Anunciante: {business}',
            f'Nome: {name}\nE-mail: {email}\nNegócio: {business}\nMensagem: {message}',
            'no-reply@click32.com',
            ['contato@click32.com'],
            fail_silently=True,
        )
        return redirect('advertise_success')  
    return render(request, 'advertise.html')

# view inactivated #
def advertise_success(request):
    return render(request, 'advertise_success.html')


def teste_print(request):
    print(">>> DEBUG: view teste_print foi chamada <<<")
    return HttpResponse("Teste de print no console OK!")