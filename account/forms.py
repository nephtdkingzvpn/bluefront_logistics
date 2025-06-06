from django import forms

from .models import Shipment, LiveUpdate


class DateInput(forms.DateInput):
	input_type = 'date'


class ShipmentCreateForm(forms.ModelForm):

    class Meta:
        model = Shipment
        fields = '__all__'
        exclude = ['date_created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['content'].widget = forms.Textarea(attrs={'rows':1, 'cols':15})
        self.fields['shipping_date'].widget = DateInput()
        self.fields['delivery_date'].widget = DateInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class LiveUpdateCreateForm(forms.ModelForm):

    class Meta:
        model = LiveUpdate
        fields = '__all__'
        exclude = ['created_on', 'shipment']
        # exclude = ['created_on', 'shipment', 'latitude', 'longitude']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['content'].widget = forms.Textarea(attrs={'rows':1, 'cols':15})
        # self.fields['shipping_date'].widget = DateInput()
        # self.fields['delivery_date'].widget = DateInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

            # Change label for current_location field
        if 'current_location' in self.fields:
            self.fields['current_location'].label = "Current Country"


class SmsShipmentForm(forms.ModelForm):

    class Meta:
        model = Shipment
        fields = ['receiver_name', 'receiver_phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        