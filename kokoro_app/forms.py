from django import forms

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activity', 'description']
        labels = {'description': ''}


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


class ProfileBioForm(forms.ModelForm):
    class Meta:
        model = ProfileBio
        fields = ['biography']


class ProfileDisplayNameForm(forms.ModelForm):
    class Meta:
        model = ProfileDisplayName
        fields = ['display_name']
