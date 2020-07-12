from django import forms
from django.forms import Select

from .models import Post


class CustomChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        pass

    def validate(self, value):
        pass

    def run_validators(self, value):
        pass


class PostAdminForm(forms.ModelForm):
    places = CustomChoiceField(widget=Select())

    class Meta:
        model = Post
        fields = "__all__"
