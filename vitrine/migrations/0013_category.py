# Generated by Django 5.2 on 2025-06-04 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vitrine', '0012_alter_clicktrack_store'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('tags', models.ManyToManyField(blank=True, related_name='categories', to='vitrine.tag')),
            ],
        ),
    ]
