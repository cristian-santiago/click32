from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('vitrine', '0024_store_qr_uuid_store_slug'),
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE vitrine_store SET slug = 'temp-slug-' || id WHERE slug IS NULL;",
            reverse_sql="UPDATE vitrine_store SET slug = NULL;"
        ),
        migrations.AlterField(
            model_name='store',
            name='slug',
            field=models.CharField(max_length=200, unique=True, null=True),
        ),
    ]
