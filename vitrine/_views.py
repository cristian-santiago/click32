from django.shortcuts import render, get_object_or_404
from .models import Store, Tag, ClickTrack
#from django.http import HttpResponse


def home(request):
    
    tag_name = request.GET.get('filter') # take the URL valur: /?filter=tag.name
    tags = Tag.objects.all()

    if tag_name:
        stores = Store.objects.filter(tags__name=tag_name).distinct()
    else:
        stores = Store.objects.all()

    stores = stores.order_by('-highlight', 'name') # recover all the stores ordered by name
    return render(request, 'home.html', {
        'stores':stores,
        'tags': tags,
        'selected_tag': tag_name
        })
    

def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    return render(request, 'store_detail.html', {'store':store})

def advertise(request):

    return render(request, 'advertise.html')

def about(request):
    
    return render(request, 'about.html')

def clicks_dashboard(request):
    clicks_data = ClickTrack.objects.values('store__name', 'element_type').annotate(
        total_clicks=Sum('click_count')
    ).order_by('-total_clicks')
    
    return render(request, 'admin/clicks_dashboard.html', {
        'clicks_data': clicks_data,
    })