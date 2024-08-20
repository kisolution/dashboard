from django import forms
class LeasingInput(forms.Form):
    first_month_rent_value = forms.FloatField(min_value=1)
    start_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))