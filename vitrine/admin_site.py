from django.contrib.admin import AdminSite
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum, Max, Q
from .models import Store



class Click32AdminSite(AdminSite):
    site_header = "Click32 Admin"
    site_title = "Click32 Painel"
    index_title = "Bem-vindo ao Painel Administrativo"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'clicks-dashboard/',
                self.admin_view(self.clicks_dashboard_view),
                name='clicks-dashboard',
            ),
        ]
        return custom_urls + urls

    def clicks_dashboard_view(self, request):
        stores_data = (
            Store.objects
            .annotate(
                clicks_main_banner=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='main_banner')),
                clicks_whatsapp=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='whatsapp_link')),
                clicks_instagram=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='instagram_link')),
                clicks_facebook=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='facebook_link')),
                clicks_youtube=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='youtube_link')),
                clicks_x=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='x_link')),
                clicks_google_maps=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='google_maps_link')),
                clicks_website=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='website_link')),
                last_clicked=Max('clicktrack__last_clicked')
            )
        )

        clicks_data = []
        for store in stores_data:
            clicks_data.append({
                'store_name': store.name,
                'main_banner': store.clicks_main_banner or 0,
                'whatsapp': store.clicks_whatsapp or 0,
                'instagram': store.clicks_instagram or 0,
                'facebook': store.clicks_facebook or 0,
                'youtube': store.clicks_youtube or 0,
                'x_link': store.clicks_x or 0,
                'google_maps': store.clicks_google_maps or 0,
                'website': store.clicks_website or 0,
                'total_clicks': sum([
                    store.clicks_main_banner or 0,
                    store.clicks_whatsapp or 0,
                    store.clicks_instagram or 0,
                    store.clicks_facebook or 0,
                    store.clicks_youtube or 0,
                    store.clicks_x or 0,
                    store.clicks_google_maps or 0,
                    store.clicks_website or 0,
                ]),
                'last_clicked': store.last_clicked
            })

        context = dict(
            self.each_context(request),
            clicks_data=clicks_data,
            title="Clicks Dashboard",
        )

        return TemplateResponse(request, "admin/clicks_dashboard.html", context)


click32_admin_site = Click32AdminSite(name='click32_admin')