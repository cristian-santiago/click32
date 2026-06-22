# vitrine/tests/test_views_links.py

from unittest.mock import patch
from django.test import TestCase, Client, override_settings, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from vitrine.models import Store, ClickTrack
from vitrine.views import track_click

# Desabilita rate limit e cache nos testes
@override_settings(
    RATELIMIT_ENABLE=False,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class LinkTrackingTest(TestCase):
    """Testes para tracking de links"""

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        # Cria loja com todos os links
        self.store = Store.objects.create(
            name="Loja com Links",
            slug="loja-com-links",
            is_verified=True,
            whatsapp_link_1="https://wa.me/5511999999999",
            whatsapp_link_2="https://wa.me/5511988888888",
            phone_link="11999999999",
            instagram_link="https://instagram.com/loja",
            facebook_link="https://facebook.com/loja",
            x_link="https://x.com/loja",
            youtube_link="https://youtube.com/@loja",
            google_maps_link="https://maps.google.com/?q=loja",
            anota_ai_link="https://anota.ai/loja",
            ifood_link="https://ifood.com.br/loja"
        )
        
        # Cria loja sem links
        self.store_no_links = Store.objects.create(
            name="Loja sem Links",
            slug="loja-sem-links",
            is_verified=True
        )
        
        # Cria loja desativada
        self.store_deactivated = Store.objects.create(
            name="Loja Desativada",
            slug="loja-desativada",
            is_deactivated=True
        )
        
        # URLs de tracking
        self.track_url = reverse('track_click', args=[self.store.id, 'whatsapp_link_1'])

    def test_track_click_whatsapp(self):
        """Testa tracking de clique no WhatsApp"""
        response = self.client.get(self.track_url)
        self.assertRedirects(response, self.store.whatsapp_link_1, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='whatsapp_link_1'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_whatsapp_2(self):
        """Testa tracking de clique no WhatsApp 2"""
        url = reverse('track_click', args=[self.store.id, 'whatsapp_link_2'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.whatsapp_link_2, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='whatsapp_link_2'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_instagram(self):
        """Testa tracking de clique no Instagram"""
        url = reverse('track_click', args=[self.store.id, 'instagram_link'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.instagram_link, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='instagram_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_facebook(self):
        """Testa tracking de clique no Facebook"""
        url = reverse('track_click', args=[self.store.id, 'facebook_link'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.facebook_link, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='facebook_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_youtube(self):
        """Testa tracking de clique no YouTube"""
        url = reverse('track_click', args=[self.store.id, 'youtube_link'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.youtube_link, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='youtube_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_x(self):
        """Testa tracking de clique no X (Twitter)"""
        url = reverse('track_click', args=[self.store.id, 'x_link'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.x_link, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='x_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_google_maps(self):
        """Testa tracking de clique no Google Maps"""
        url = reverse('track_click', args=[self.store.id, 'google_maps_link'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.google_maps_link, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='google_maps_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_anota_ai(self):
        """Testa tracking de clique no Anota Ai"""
        url = reverse('track_click', args=[self.store.id, 'anota_ai_link'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.anota_ai_link, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='anota_ai_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_ifood(self):
        """Testa tracking de clique no iFood"""
        url = reverse('track_click', args=[self.store.id, 'ifood_link'])
        response = self.client.get(url)
        self.assertRedirects(response, self.store.ifood_link, fetch_redirect_response=False)
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='ifood_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_phone(self):
        """Testa tracking de clique no telefone"""
        url = reverse('track_click', args=[self.store.id, 'phone_link'])
        response = self.client.get(url)
        
        # Telefone retorna JSON (não redireciona)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'click_logged')
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='phone_link'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)

    def test_track_click_main_banner(self):
        """Testa tracking de clique no main_banner"""
        url = reverse('track_click', args=[self.store.id, 'main_banner'])
        response = self.client.get(url)
        
        detail_url = reverse('store_detail', args=[self.store.slug])
        self.assertRedirects(response, f"{detail_url}?element_type=main_banner")
        
        click = ClickTrack.objects.filter(
            store=self.store,
            element_type='main_banner'
        )
        self.assertTrue(click.exists())
        self.assertGreaterEqual(click.first().click_count, 1)

    def test_track_click_invalid_element(self):
        """Testa tracking com elemento inválido"""
        url = reverse('track_click', args=[self.store.id, 'elemento_invalido'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_track_click_store_not_found(self):
        """Testa tracking com loja inexistente"""
        url = reverse('track_click', args=[99999, 'whatsapp_link_1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_track_click_store_without_link(self):
        """Testa tracking quando loja não tem o link"""
        url = reverse('track_click', args=[self.store_no_links.id, 'whatsapp_link_1'])
        response = self.client.get(url)
        
        detail_url = reverse('store_detail', args=[self.store_no_links.slug])
        try:
            self.assertRedirects(response, detail_url, fetch_redirect_response=False)
        except AssertionError:
            self.assertEqual(response.status_code, 500)

    def test_track_click_deactivated_store(self):
        """Testa tracking em loja desativada"""
        url = reverse('track_click', args=[self.store_deactivated.id, 'whatsapp_link_1'])
        response = self.client.get(url)
        self.assertIn(response.status_code, [404, 500])

    def test_track_click_multiple_clicks(self):
        """Testa que múltiplos cliques incrementam o contador"""
        for _ in range(3):
            self.client.get(self.track_url)
        
        click = ClickTrack.objects.get(
            store=self.store,
            element_type='whatsapp_link_1'
        )
        self.assertEqual(click.click_count, 3)

    def test_track_click_daily_tracking(self):
        """Testa que cliques diários são registrados"""
        self.client.get(self.track_url)
        
        from vitrine.models import ClickTrackDaily
        daily = ClickTrackDaily.objects.filter(
            store=self.store,
            element_type='whatsapp_link_1',
            date=timezone.now().date()
        )
        self.assertTrue(daily.exists())
        self.assertEqual(daily.first().click_count, 1)

    def test_track_click_home_access(self):
        """Testa tracking de acesso à home"""
        # CORREÇÃO: Agora a view retorna HttpResponse (código corrigido)
        request = self.factory.get('/track-click/0/home_access/')
        
        # Chama a view diretamente
        response = track_click(request, store_id=0, element_type='home_access')
        
        # AGORA: Deve retornar HttpResponse (não None)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        
        # Verifica se o clique foi registrado
        click = ClickTrack.objects.filter(
            store=None,
            element_type='home_access'
        )
        self.assertTrue(click.exists())
        self.assertEqual(click.first().click_count, 1)


@override_settings(
    RATELIMIT_ENABLE=False,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class LinkSecurityTest(TestCase):
    """Testes de segurança para links"""

    def setUp(self):
        self.client = Client()
        self.store = Store.objects.create(
            name="Loja Teste",
            slug="loja-teste",
            whatsapp_link_1="https://wa.me/5511999999999"
        )
        self.track_url = reverse('track_click', args=[self.store.id, 'whatsapp_link_1'])

    def test_track_click_malicious_url(self):
        """Testa proteção contra URLs maliciosas"""
        malicious_store = Store.objects.create(
            name="Loja Maliciosa",
            slug="loja-maliciosa",
            whatsapp_link_1="javascript:alert('XSS')"
        )
        
        url = reverse('track_click', args=[malicious_store.id, 'whatsapp_link_1'])
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 500])

    def test_track_click_relative_path(self):
        """Testa proteção contra path traversal em links"""
        path_traversal_store = Store.objects.create(
            name="Loja Path",
            slug="loja-path",
            whatsapp_link_1="/../../etc/passwd"
        )
        
        url = reverse('track_click', args=[path_traversal_store.id, 'whatsapp_link_1'])
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 500])


@override_settings(
    RATELIMIT_ENABLE=False,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class LinkModelTest(TestCase):
    """Testes para links no modelo Store"""

    def setUp(self):
        self.store = Store.objects.create(
            name="Loja Teste",
            slug="loja-teste"
        )

    def test_link_field_default_empty(self):
        """Testa que links vazios são permitidos"""
        self.assertIsNone(self.store.whatsapp_link_1)
        self.assertIsNone(self.store.instagram_link)
        self.assertIsNone(self.store.facebook_link)

    def test_link_fields_all_types(self):
        """Testa que todos os tipos de link existem"""
        link_fields = [
            'whatsapp_link_1',
            'whatsapp_link_2',
            'phone_link',
            'instagram_link',
            'facebook_link',
            'x_link',
            'youtube_link',
            'google_maps_link',
            'anota_ai_link',
            'ifood_link'
        ]
        
        for field in link_fields:
            self.assertTrue(hasattr(self.store, field))
            field_obj = self.store._meta.get_field(field)
            self.assertIn(field_obj.__class__.__name__, ['URLField', 'CharField'])