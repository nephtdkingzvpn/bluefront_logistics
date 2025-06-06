from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from urllib.parse import urlencode
import json


from .models import Shipment, LiveUpdate, MessageLog
from .forms import ShipmentCreateForm, LiveUpdateCreateForm, SmsShipmentForm
from frontend import emailsend
from .sms import AsyncSMSMixin
from .sms_providers import send_sms_twilio


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


@login_required
def create_new_shipment(request):
    form = ShipmentCreateForm(request.POST or None)

    if form.is_valid():
        shipment = form.save()

        # Build URLs
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'

        query_string = urlencode({'tracking_number': shipment.tracking_number})
        tracking_url = f"{protocol}://{domain}{reverse('frontend:track_shipment')}?{query_string}"
        contact_url = f"{protocol}://{domain}{reverse('frontend:contact_us')}"

        final_message = render_to_string('frontend/emails/shipment_sent_email.html', 
        {
            'receiver_name': shipment.receiver_name,
            'sender_name': shipment.sender_name,
            'tracking_number': shipment.tracking_number,
            'dispatched_from': shipment.origin_office,
            'delivery_date': shipment.delivery_date,
            'tracking_url': tracking_url,
            'contact_url': contact_url
        })

        try:
            emailsend.email_send('Shipment Registered', final_message, shipment.receiver_email)
            messages.success(request, 'A new shippment was created successfully and email was sent to the receiver')
        except:
            messages.success(request, 'A new shippment was created successfully but email sending failed')
        finally:
            return redirect('account:dashboard')

    context = {'form':form}
    return render(request, 'account/create_shipment.html', context)


@login_required
def edit_shipment(request, pk):
    shipment = Shipment.objects.get(pk=pk)
    form = ShipmentCreateForm(request.POST or None, instance=shipment)

    if form.is_valid():
        form.save()
        messages.success(request, 'Shippment was Updated successfully')
        return redirect('account:dashboard')
    
    context = {'form':form}
    return render(request, 'account/edit_shipment.html', context)


@login_required
def delete_shipment(request, pk):
    shipment = Shipment.objects.get(pk=pk)
    shipment.delete()
    messages.success(request, 'Shipment was deleted successfully')
    return redirect('account:dashboard')


@login_required
def shipment_detail(request, pk):
    shipment = Shipment.objects.get(pk=pk)
    live_update = LiveUpdate.objects.filter(shipment=shipment)
    live_update_count = live_update.count()
    latest_update = live_update.last()

    form = LiveUpdateCreateForm(request.POST or None)
    
    if form.is_valid():
        update_live_object = form.save(commit=False)
        update_live_object.shipment = shipment
        update_live_object.save()
        
        request.session['form_submitted'] = True
        messages.success(request, 'Live Update is saved successfully')
        return redirect('account:shipment_detail', pk=pk)
    
    form_submitted = request.session.pop('form_submitted', False)

    # Prepare list of locations with lat/lon for JS
    locations = [
        {
            "lat": update.latitude,
            "lng": update.longitude,
            "location": update.current_location,
            "status": update.status,
            "time": update.created_on.strftime("%Y-%m-%d %H:%M:%S")
        }
        for update in live_update if update.latitude is not None and update.longitude is not None
    ]

    context = {
        'shipment': shipment,
        'live_update': live_update,
        'update_count': live_update_count,
        'latest_update': latest_update,
        'form': form,
        'form_submitted': form_submitted,
        'locations_json': json.dumps(locations)  # Pass JSON to template
    }

    return render(request, 'account/shipment_detail.html', context)



@login_required
def update_live_update(request, pk):
    live_update = LiveUpdate.objects.get(pk=pk)

    form = LiveUpdateCreateForm(request.POST or None, instance=live_update)

    if form.is_valid():
        form.save()

        request.session['form_submitted'] = True

        # Display a success message
        messages.success(request, 'Live Update is saved successfully')
        
        # Redirect to the same shipment detail page
        return redirect('account:shipment_detail', pk=live_update.shipment.pk)
    
    form_submitted = request.session.pop('form_submitted', False)

    context = {'form':form, 'form_submitted': form_submitted}
    return render(request, 'account/update_live_update.html', context)


@login_required
def delete_live_update(request, pk):
    live_update = LiveUpdate.objects.get(pk=pk)
    live_update.delete()
    messages.success(request, 'Live Update is deleted successfully')
    return redirect('account:shipment_detail', pk=live_update.shipment.pk)


def view_receipt(request, pk):
    shipment = Shipment.objects.get(pk=pk)
    live_update = LiveUpdate.objects.filter(shipment=shipment).first()

    context = {'shipment':shipment, 'live_update':live_update}
    return render(request, 'account/receipt.html', context)



# twilio
class AlertHandler(AsyncSMSMixin):
    pass

sms_handler = AlertHandler()


@login_required
def admin_send_sms(request, pk):
    shipment = Shipment.objects.get(pk=pk)
    form = SmsShipmentForm(request.POST or None, instance=shipment)
    sms_log = shipment.sms_logs.all().order_by('-created_at')

    if form.is_valid():
        data = form.save()

        # Build URLs
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'

        query_string = urlencode({'tracking_number': shipment.tracking_number})
        tracking_url = f"{protocol}://{domain}{reverse('frontend:track_shipment')}?{query_string}"

        contexta = {
            'receiver_name': data.receiver_name,
            'sender_name': data.sender_name,
            'tracking_number': data.tracking_number,
            'tracking_url': tracking_url,
        }

        
        # send sms twilo here
        sms_handler.send_sms_async(
            send_function=send_sms_twilio,
            to=data.receiver_phone,
            template='frontend/emails/shipment_sent_sms.txt',
            context=contexta,
            shipment=shipment,
            request=request
        )
        messages.success(request, 'sms message was sent successfully')
        return redirect('account:admin_send_sms', pk=pk)
    context =  {'form':form, 'sms_log':sms_log}
    return render(request, 'account/admin_send_sms.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def sms_status_callback(request):
    # Extract data from POST request
    message_sid = request.POST.get('MessageSid')
    message_status = request.POST.get('MessageStatus')  # e.g. delivered, failed, sent

    logger.info(f"Status callback received: SID={message_sid} status={message_status}")

    if not message_sid or not message_status:
        logger.warning("Missing SID or Status in callback.")
        return HttpResponse("Missing data", status=400)

    try:
        msg_log = MessageLog.objects.get(sid=message_sid)
        # Normalize status for your choices, e.g. uppercase
        msg_log.status = message_status.upper()
        msg_log.save()
        logger.info(f"MessageLog updated for SID {message_sid} with status {message_status}")
    except MessageLog.DoesNotExist:
        logger.warning(f"MessageLog with SID {message_sid} not found")

    return HttpResponse("OK")
