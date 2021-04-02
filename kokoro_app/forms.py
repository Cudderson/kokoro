from django import forms

from .models import Activity, PerfectBalance


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


class PerfectBalanceForm(forms.ModelForm):
    class Meta:
        model = PerfectBalance
        fields = ['perfect_mind', 'perfect_body', 'perfect_soul']

        # turn off labels when ready:
        # labels = {
        #     'perfect_mind': '',
        #     'perfect_body': '',
        #     'perfect_soul': '',
        # }

        # example of bootstrap text-input field
        widgets = {
            'perfect_mind': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }
