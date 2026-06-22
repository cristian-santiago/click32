import random
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from vitrine.models import Store, Tag, Category, ClickTrack

class HomeViewTest(TestCase):
    """Testes para a view home"""

    def setUp(self):
        """Configuração inicial para testes da home"""
        self.client = Client()
        self.home_url = reverse('home')
        
        # Cria categorias e tags
        self.category = Category.objects.create(name="Comidas")
        self.tag1 = Tag.objects.create(name="Pizza")
        self.tag2 = Tag.objects.create(name="Hamburger")
        self.category.tags.add(self.tag1, self.tag2)
        
        # Cria lojas com diferentes configurações
        self.store1 = Store.objects.create(
            name="Loja VIP",
            is_vip=True,
            highlight=True,
            is_verified=True
        )
        self.store1.tags.add(self.tag1)
        
        self.store2 = Store.objects.create(
            name="Loja Normal",
            is_vip=False,
            highlight=False,
            is_verified=True
        )
        self.store2.tags.add(self.tag2)
        
        self.store3 = Store.objects.create(
            name="Loja Desativada",
            is_deactivated=True
        )

    def test_home_page_status_code(self):
        """Testa se a home retorna 200"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_context(self):
        """Testa se o contexto da home contém os dados esperados"""
        response = self.client.get(self.home_url)
        
        # Verifica chaves do contexto
        self.assertIn('stores', response.context)
        self.assertIn('stores_vip', response.context)
        self.assertIn('stores_deactivated', response.context)
        self.assertIn('category_tags', response.context)
        self.assertIn('selected_tag', response.context)
        self.assertIn('active_category', response.context)
        
        # Verifica se lojas desativadas não estão na lista principal
        stores = response.context['stores']
        store_names = [s.name for s in stores]
        self.assertNotIn("Loja Desativada", store_names)
        
        # Verifica se lojas desativadas estão na lista separada
        deactivated = response.context['stores_deactivated']
        self.assertEqual(len(deactivated), 1)
        self.assertEqual(deactivated[0].name, "Loja Desativada")

    def test_home_page_vip_stores(self):
        """Testa se lojas VIP aparecem na lista separada"""
        response = self.client.get(self.home_url)
        vip_stores = response.context['stores_vip']
        
        # Deve ter pelo menos a loja VIP
        self.assertIsNotNone(vip_stores)
        vip_names = [s.name for s in vip_stores] if vip_stores else []
        self.assertIn("Loja VIP", vip_names)

    def test_home_page_filter_by_category(self):
        """Testa filtro por categoria"""
        response = self.client.get(self.home_url, {'tag': 'Comidas'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_category'], 'Comidas')
        self.assertEqual(response.context['selected_tag'], 'Comidas')
        
        # Deve mostrar apenas lojas com tags da categoria
        stores = response.context['stores']
        store_names = [s.name for s in stores]
        self.assertIn("Loja VIP", store_names)
        self.assertIn("Loja Normal", store_names)
        self.assertNotIn("Loja Desativada", store_names)

    def test_home_page_filter_by_tag(self):
        """Testa filtro por tag específica"""
        response = self.client.get(self.home_url, {'tag': 'Pizza'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tag'], 'Pizza')
        
        # Deve mostrar apenas lojas com a tag Pizza
        stores = response.context['stores']
        store_names = [s.name for s in stores]
        self.assertIn("Loja VIP", store_names)
        self.assertNotIn("Loja Normal", store_names)

    def test_home_page_filter_invalid_tag(self):
        """Testa filtro com tag inexistente"""
        response = self.client.get(self.home_url, {'tag': 'TagInexistente'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tag'], 'TagInexistente')
        self.assertEqual(response.context['active_category'], None)
        
        # Não deve mostrar lojas
        stores = response.context['stores']
        self.assertEqual(len(stores), 0)

    def test_home_page_track_click(self):
        """Testa se o clique na home é registrado"""
        # Faz request sem tag
        self.client.get(self.home_url)
        
        # Verifica se o clique foi registrado
        click_track = ClickTrack.objects.filter(
            store=None,
            element_type='home_access'
        )
        self.assertTrue(click_track.exists())
        self.assertEqual(click_track.first().click_count, 1)

    def test_home_page_no_track_when_filtered(self):
        """Testa que não registra clique quando há filtro"""
        # Faz request com tag
        self.client.get(self.home_url, {'tag': 'Comidas'})
        
        # Não deve registrar home_access
        click_track = ClickTrack.objects.filter(
            store=None,
            element_type='home_access'
        )
        self.assertFalse(click_track.exists())

    def test_home_page_exception_handling(self):
        """Testa se a home trata exceções corretamente"""
        # CORREÇÃO: Usa mock para simular erro
        with patch('vitrine.views.Store.objects.filter') as mock_filter:
            # Força uma exceção ao chamar filter
            mock_filter.side_effect = Exception("Erro simulado no banco")
            
            response = self.client.get(self.home_url)
            
            # Verifica se retorna 200 mesmo com erro
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'home.html')
            
            # Verifica se as listas estão vazias (fallback seguro)
            self.assertEqual(response.context['stores'], [])
            self.assertEqual(response.context['stores_vip'], [])
            self.assertEqual(response.context['stores_deactivated'], [])

    def test_home_page_caching_headers(self):
        """Testa se os headers de cache estão configurados"""
        # Quando ativar cache_page, descomente
        # response = self.client.get(self.home_url)
        # self.assertIn('Cache-Control', response.headers)
        pass