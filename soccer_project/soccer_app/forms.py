from django import forms

class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='From Date')
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='To Date')
