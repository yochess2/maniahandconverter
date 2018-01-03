from django import forms
from .models import HH

class HHForm(forms.ModelForm):
    class Meta:
        model = HH
        fields = ('file',)
