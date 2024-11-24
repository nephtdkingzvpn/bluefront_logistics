from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Shipment
from .forms import ShipmentCreateForm

class DashboardView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = 'account/dashboard.html'
    context_object_name = 'shipments'
    paginate_by = 15

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_staff:
    #         return HttpResponseRedirect(reverse_lazy('shipment:n_dashboard'))        
    #     return super().dispatch(request, *args, **kwargs)

    # def get_queryset(self, *args, **kwargs):
    #     qs = super(DashboardView, self).get_queryset(*args, **kwargs)
    #     qs = qs.order_by("-created")
    #     return qs


def create_new_shipment(request):
    form = ShipmentCreateForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, 'A new shippment was created successfully')
        return redirect('account:dashboard')

    context = {'form':form}
    return render(request, 'account/create_shipment.html', context)


def delete_shipment(request, id):
    shipment = Shipment.objects.get(id=id)
    shipment.delete()
    messages.success(request, 'Shipment was deleted successfully')
    return redirect('account:dashboard')
