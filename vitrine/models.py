from django.db import models

# Create your models here.

class Store(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image  = models.ImageField(upload_to='stores/', blank=True, null=True)
    external_link = models.URLField(help_text="Link para WPP, iFood")
    highlight = models.BooleanField(default=False)

    def __str__(self):
        return self.name