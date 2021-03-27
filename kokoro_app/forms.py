from django import forms

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activity', 'description']
        labels = {'description': ''}
        widgets = {
            'activity': forms.RadioSelect(
                attrs={
                    'class': 'form-control'
                }
            ),

            'description': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }
