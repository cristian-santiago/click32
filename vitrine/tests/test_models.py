import uuid
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from vitrine.models import Store, Tag, Category, StoreOpeningHour, ClickTrack

class StoreModelTest(TestCase):
    """Testes para o modelo Store"""

    def setUp(self):
        self.store = Store.objects.create(
            name="Loja Teste",
            description="Descrição da loja teste",
            address="Rua Teste, 123",
            highlight=True,
            is_vip=True,
            is_verified=True,
            verified_at=timezone.now()
        )

    def test_store_creation(self):
        self.assertEqual(self.store.name, "Loja Teste")
        self.assertTrue(self.store.highlight)
        self.assertTrue(self.store.is_vip)
        self.assertTrue(self.store.is_verified)
        self.assertIsNotNone(self.store.verified_at)

    def test_slug_generation(self):
        self.assertEqual(self.store.slug, "loja-teste")
        
        store2 = Store.objects.create(name="Loja Teste 2")
        self.assertEqual(store2.slug, "loja-teste-2")
        
        store3 = Store.objects.create(name="Loja Teste 3")
        self.assertEqual(store3.slug, "loja-teste-3")

    def test_slug_update_on_name_change(self):
        self.store.name = "Nova Loja Teste"
        self.store.save()
        self.assertEqual(self.store.slug, "nova-loja-teste")

    def test_qr_code_properties(self):
        self.assertIsInstance(self.store.qr_uuid, uuid.UUID)
        self.assertIn('/generate-qr-code/', self.store.qr_code_url)
        self.assertIn(str(self.store.qr_uuid), self.store.qr_code_url)
        self.assertIn('/qr_codes/', self.store.qr_code_image_url)
        self.assertIn(str(self.store.qr_uuid), self.store.qr_code_image_url)

    def test_is_open_property_no_hours(self):
        self.assertFalse(self.store.is_open)

    def test_is_open_property_with_hours(self):
        opening_hour = StoreOpeningHour.objects.create(
            store=self.store,
            day_range="Todos os dias",
            time_open="00:00",
            time_close="23:59"
        )
        self.assertTrue(self.store.is_open)

    def test_store_str_method(self):
        self.assertEqual(str(self.store), "Loja Teste")

    def test_store_deactivated_excluded_from_queries(self):
        store_deactivated = Store.objects.create(
            name="Loja Desativada",
            is_deactivated=True
        )
        
        active_stores = Store.objects.filter(is_deactivated=False)
        self.assertIn(self.store, active_stores)
        self.assertNotIn(store_deactivated, active_stores)


class TagModelTest(TestCase):
    def test_tag_creation(self):
        tag = Tag.objects.create(name="Pizza")
        self.assertEqual(tag.name, "Pizza")
        self.assertEqual(str(tag), "Pizza")


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Comidas", icon="fa-utensils")
        self.assertEqual(category.name, "Comidas")
        self.assertEqual(category.icon, "fa-utensils")
        self.assertEqual(str(category), "Comidas")

    def test_category_with_tags(self):
        category = Category.objects.create(name="Comidas")
        tag1 = Tag.objects.create(name="Pizza")
        tag2 = Tag.objects.create(name="Hamburger")
        category.tags.add(tag1, tag2)
        
        self.assertEqual(category.tags.count(), 2)
        self.assertIn(tag1, category.tags.all())
        self.assertIn(tag2, category.tags.all())


class StoreOpeningHourTest(TestCase):
    """Testes para o modelo StoreOpeningHour"""

    def setUp(self):
        self.store = Store.objects.create(name="Loja Teste")
        self.hour = StoreOpeningHour.objects.create(
            store=self.store,
            day_range="Seg-Sex",
            time_open="09:00",
            time_close="18:00"
        )

    def test_opening_hour_creation(self):
        """Testa criação de horário de funcionamento"""
        self.assertEqual(self.hour.day_range, "Seg-Sex")
        self.assertEqual(str(self.hour.time_open), "09:00")
        self.assertEqual(str(self.hour.time_close), "18:00")

    def test_is_active_now_24h(self):
        """Testa is_active_now para horário 24h (sem fechamento)"""
        hour_24h = StoreOpeningHour.objects.create(
            store=self.store,
            day_range="24h",
            time_open="00:00",
            time_close=None
        )
        self.assertTrue(hour_24h.is_active_now)

    def test_is_active_now_full_day(self):
        """Testa is_active_now para dia inteiro (00:00-23:59)"""
        hour_full = StoreOpeningHour.objects.create(
            store=self.store,
            day_range="Dia inteiro",
            time_open="00:00",
            time_close="23:59"
        )
        self.assertTrue(hour_full.is_active_now)

    def test_str_method(self):
        """Testa representação string do horário"""
        self.assertEqual(str(self.hour), "Seg-Sex 09:00–18:00")
        
        hour_24h = StoreOpeningHour.objects.create(
            store=self.store,
            day_range="Sáb",
            time_open="10:00",
            time_close=None
        )
        self.assertEqual(str(hour_24h), "Sáb 10:00–24h")


class ClickTrackModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Loja Teste")

    def test_click_track_creation(self):
        click = ClickTrack.objects.create(
            store=self.store,
            element_type='whatsapp_link_1',
            click_count=5
        )
        self.assertEqual(click.click_count, 5)
        self.assertEqual(click.element_type, 'whatsapp_link_1')
        self.assertIsNotNone(click.last_clicked)

    def test_click_track_str_method(self):
        click = ClickTrack.objects.create(
            store=self.store,
            element_type='instagram_link',
            click_count=3
        )
        self.assertIn("Loja Teste", str(click))
        self.assertIn("instagram_link", str(click))
        self.assertIn("3 clicks", str(click))

    def test_click_track_no_store(self):
        click = ClickTrack.objects.create(
            store=None,
            element_type='home_access',
            click_count=10
        )
        self.assertEqual(click.click_count, 10)
        self.assertIn("No Store", str(click))