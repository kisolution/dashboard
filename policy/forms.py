from django import forms
from .models import IncomePolicyUpload
class IncomePolicyUploadForm(forms.ModelForm):
    class Meta:
        model = IncomePolicyUpload
        fields = ['file_upload']
