import os
import random
import uuid
from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify
from vitrine.models import Store, StoreOpeningHour, Tag, Category


# Caminho do diretório do seed.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Sobe dois níveis para chegar em 'vitrine'
APP_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# Pastas de mídia de teste
BANNERS_DIR = os.path.join(APP_DIR, "media_test", "banner")
CAROUSELS_DIR = os.path.join(APP_DIR, "media_test", "carousel")
PDFS_DIR = os.path.join(APP_DIR, "media_test", "pdf")

CATEGORIES = {
    "Beleza": ["Cabeleireiro", "Barbearia", "Manicure", "Estética"],
    "Saúde": ["Clínica", "Odontologia", "Fisioterapia"],
    "Alimentação": ["Restaurante", "Lanchonete", "Pizzaria"],
    "Serviços": ["Oficina", "Chaveiro", "Eletricista"],
    "Moda": ["Roupas", "Calçados", "Acessórios"]
}

class Command(BaseCommand):
    help = "Popula o banco com dados de teste"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Criando categorias e tags..."))
        self.create_categories_and_tags()

        self.stdout.write(self.style.SUCCESS("Criando lojas de teste..."))
        for i in range(50):
            self.create_store(i)

        self.stdout.write(self.style.SUCCESS("Seeding finalizado!"))

    def create_categories_and_tags(self):
        for cat_name, tags in CATEGORIES.items():
            category, _ = Category.objects.get_or_create(name=cat_name)
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                category.tags.add(tag)

    def create_store(self, idx):
        store_name = f"Loja Teste {idx+1}"

        store = Store(
            name=store_name,
            description=f"Descrição da {store_name}, oferecendo ótimos serviços.",
            address=f"Rua Exemplo {idx+1}, Bairro Teste",
            highlight=random.choice([True, False]),
            is_vip=random.choice([True, False]),
        )

        # Banner principal
        banner_file = random.choice(os.listdir(BANNERS_DIR))
        with open(os.path.join(BANNERS_DIR, banner_file), "rb") as f:
            store.main_banner.save(banner_file, File(f), save=False)

        # Carrosseis
        carousel_files = random.sample(os.listdir(CAROUSELS_DIR), 3)
        with open(os.path.join(CAROUSELS_DIR, carousel_files[0]), "rb") as f:
            store.carousel_2.save(carousel_files[0], File(f), save=False)
        with open(os.path.join(CAROUSELS_DIR, carousel_files[1]), "rb") as f:
            store.carousel_3.save(carousel_files[1], File(f), save=False)
        with open(os.path.join(CAROUSELS_DIR, carousel_files[2]), "rb") as f:
            store.carousel_4.save(carousel_files[2], File(f), save=False)

        # Flyer PDF (opcional, nem todas terão)
        if random.choice([True, False]) and os.path.exists(PDFS_DIR):
            pdfs = [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]
            if pdfs:
                pdf_file = random.choice(pdfs)
                with open(os.path.join(PDFS_DIR, pdf_file), "rb") as f:
                    store.flyer_pdf.save(pdf_file, File(f), save=False)

        store.save()

        # Tags (aleatórias)
        all_tags = list(Tag.objects.all())
        store.tags.set(random.sample(all_tags, random.randint(1, 3)))

        # Links simulados
        store.whatsapp_link_1 = f"https://wa.me/55{random.randint(1000000000, 9999999999)}"
        store.instagram_link = f"https://instagram.com/{slugify(store.name)}"
        store.facebook_link = f"https://facebook.com/{slugify(store.name)}"
        store.google_maps_link = f"https://maps.google.com/?q={slugify(store.name)}"
        store.save()

        # Horários de funcionamento
        days = [("Seg–Sex", "09h–19h"), ("Sáb", "09h–14h"), ("Dom", "Fechado")]
        for day, time in days:
            StoreOpeningHour.objects.create(
                store=store, day_range=day, time_range=time
            )
