from django import forms

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName, ProfileQuote,\
                    ProfileImage, ProfileTimezone, ContactInfo, ProfilePost, SupportReport

from cloudinary.forms import CloudinaryFileField

# Create forms based on defined models


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activity', 'description']
        labels = {'description': ''}


class PerfectBalanceForm(forms.ModelForm):
    class Meta:
        model = PerfectBalance
        fields = ['perfect_mind', 'perfect_body', 'perfect_soul']


class ProfileBioForm(forms.ModelForm):
    class Meta:
        model = ProfileBio
        fields = ['biography']


class ProfileDisplayNameForm(forms.ModelForm):
    class Meta:
        model = ProfileDisplayName
        fields = ['display_name']


class ProfileQuoteForm(forms.ModelForm):
    class Meta:
        model = ProfileQuote
        fields = ['quote', 'quote_author']


class ProfileImageForm(forms.ModelForm):
    image = CloudinaryFileField(
        options={
            # change upload settings when needed
            'crop': 'thumb',
            'gravity': 'face',
            'width': 200,
            'height': 200,
            'folder': 'kokoro_images',
        }
    )

    class Meta:
        model = ProfileImage
        fields = ['image']


class ProfileTimezoneForm(forms.ModelForm):
    class Meta:
        model = ProfileTimezone
        fields = ['user_timezone']


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = ['user_email']


class ProfilePostForm(forms.ModelForm):
    class Meta:
        model = ProfilePost
        fields = ['headline', 'content']


class SupportReportForm(forms.ModelForm):
    """
    Form for sending a support/help report to kokoro
    """

    class Meta:
        model = SupportReport
        fields = ['subject', 'body', 'contact_email', 'username']
