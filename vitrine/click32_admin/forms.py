from django import forms
from django.contrib.auth.models import Group
from django.core.validators import FileExtensionValidator
from vitrine.models import Store, Tag, Category

class StoreForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 10, 'id': 'selected-tags'})
    )
    flyer_pdf = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
    )

    class Meta:
        model = Store
        fields = [
            'name', 'description', 'main_banner', 'carousel_2', 'carousel_3', 'carousel_4',
            'highlight', 'is_vip', 'tags', 'whatsapp_link', 'instagram_link', 'facebook_link',
            'x_link', 'google_maps_link', 'youtube_link', 'website_link', 'flyer_pdf'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

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