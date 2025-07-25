# Generated by Django 5.2 on 2025-06-29 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vitrine', '0018_store_flyer_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clicktrack',
            name='element_type',
            field=models.CharField(choices=[('main_banner', 'Main Banner'), ('whatsapp_link', 'WhatsApp Link'), ('instagram_link', 'Instagram Link'), ('facebook_link', 'Facebook Link'), ('youtube_link', 'YouTube Link'), ('x_link', 'X Link'), ('google_maps_link', 'Google Maps Link'), ('website_link', 'Website Link'), ('home_access', 'Home Access'), ('flyer_pdf', 'flyer PDF')], max_length=50),
        ),
    ]
