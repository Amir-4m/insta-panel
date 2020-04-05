from django.forms import ModelForm, PasswordInput

from apps.page.models import Page


class PageForm(ModelForm):
    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'password': PasswordInput(),
        }