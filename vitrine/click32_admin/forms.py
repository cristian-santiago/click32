from django import forms
from django.contrib.auth.models import Group
from django.core.validators import FileExtensionValidator, URLValidator
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.html import strip_tags
from django.template.defaultfilters import filesizeformat
from vitrine.models import Store, Tag, Category, StoreOpeningHour

class MaxFileSizeValidator:
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, value):
        if value and value.size > self.max_size:
            raise ValidationError(
                f'Arquivo muito grande. Tamanho máximo: {filesizeformat(self.max_size)}'
            )

def safe_url_validator(value):
    if value:
        if value.startswith(('javascript:', 'data:', 'vbscript:')):
            raise ValidationError('Tipo de URL não permitido')
        URLValidator()(value)

class StoreForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 10, 'id': 'selected-tags'})
    )
    
    flyer_pdf = forms.FileField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            MaxFileSizeValidator(max_size=5*1024*1024)  # 5MB 
        ],
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
    )

    class Meta:
        model = Store
        fields = [
            'name', 'description','address', 'main_banner', 'carousel_2', 'carousel_3', 'carousel_4',
            'highlight', 'is_vip', "is_deactivated", 'tags', 'whatsapp_link_1','whatsapp_link_2','phone_link', 
            'instagram_link', 'facebook_link', 'x_link', 'google_maps_link', 'youtube_link', 
            'anota_ai_link', 'ifood_link', 'flyer_pdf'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica validação de URL segura
        url_fields = ['whatsapp_link_1', 'whatsapp_link_2', 'phone_link', 
                     'instagram_link', 'facebook_link', 'x_link', 
                     'google_maps_link', 'youtube_link', 'anota_ai_link', 'ifood_link']
        
        for field_name in url_fields:
            self.fields[field_name].validators.append(safe_url_validator)

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        return strip_tags(description)  # Remove HTML para prevenir XSS

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class CategoryForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Category
        fields = ['name', 'icon', 'tags']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']


StoreOpeningHourFormSet = inlineformset_factory(
    Store,
    StoreOpeningHour,
    fields=('day_range', 'time_range'),
    extra=1,
    max_num=3,
    can_delete=True
)