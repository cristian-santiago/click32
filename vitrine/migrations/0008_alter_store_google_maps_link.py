# Generated by Django 5.2 on 2025-05-18 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vitrine', '0007_store_google_maps_link_store_x_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='google_maps_link',
            field=models.URLField(blank=True, max_length=300, null=True, verbose_name='Google Maps'),
        ),
    ]
