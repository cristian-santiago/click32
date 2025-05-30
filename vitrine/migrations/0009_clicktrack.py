# Generated by Django 5.2 on 2025-05-27 06:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vitrine', '0008_alter_store_google_maps_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClickTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element_type', models.CharField(choices=[('main_banner', 'Main Banner'), ('whatsapp_link', 'WhatsApp Link'), ('instagram_link', 'Instagram Link'), ('facebook_link', 'Facebook Link'), ('youtube_link', 'YouTube Link'), ('x_link', 'X Link'), ('google_maps_link', 'Google Maps Link'), ('website_link', 'Website Link')], max_length=50)),
                ('click_count', models.PositiveIntegerField(default=0)),
                ('last_clicked', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='vitrine.store')),
            ],
            options={
                'unique_together': {('store', 'element_type')},
            },
        ),
    ]
