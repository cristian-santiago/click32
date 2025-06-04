from django import forms
from .models import Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'name', 'description', 'highlight', 'tags',
            'whatsapp_link', 'instagram_link', 'facebook_link',
            'youtube_link', 'x_link', 'google_maps_link', 'website_link',
            'main_banner', 'carousel_2', 'carousel_3', 'carousel_4',
        ]
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }
