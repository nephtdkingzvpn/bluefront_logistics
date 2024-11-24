from django import forms

from .models import Shipment

class ShipmentCreateForm(forms.ModelForm):

    class Meta:
        model = Shipment
        fields = '__all__'
        exclude = ['date_created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['content'].widget = forms.Textarea(attrs={'rows':1, 'cols':15})

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})