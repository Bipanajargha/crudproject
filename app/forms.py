from django import forms
from .models import Registartion

class RegistrationForm(forms.ModelForm):
    class Meta:
      model = Registartion
      fields = ['name','email','course','message']