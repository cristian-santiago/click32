from django.utils.text import slugify
from vitrine.models import Store

for store in Store.objects.all():
    if not store.slug:
        store.slug = slugify(store.name)
        store.save()
