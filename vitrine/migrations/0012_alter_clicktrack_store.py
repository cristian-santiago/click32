# Generated by Django 5.2 on 2025-05-29 05:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vitrine', '0011_alter_clicktrack_element_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clicktrack',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicktrack', to='vitrine.store'),
        ),
    ]
