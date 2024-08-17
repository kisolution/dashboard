from django import forms
from .models import IncomeUpload, ExpenseUpload

class IncomeUploadForm(forms.ModelForm):
    class Meta:
        model = IncomeUpload
        fields = ['file_upload']

class ExpenseUploadForm(forms.ModelForm):
    class Meta:
        model = ExpenseUpload
        fields = ['file_upload'] 