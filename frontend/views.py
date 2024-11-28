from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from account.models import Shipment, LiveUpdate
from . import emailsend


def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('account:dashboard')    
        else:
            messages.info(request, 'Username or Password is incorrect')
    return render(request, 'frontend/login.html')


def home(request):
    return render(request, 'frontend/index.html')


def track_shipment(request):
    if request.method == 'POST':

        tracking_code = request.POST.get('tracking_code')
        shipments = Shipment.objects.filter(tracking_number=tracking_code)

        if shipments.exists():

            shipment_single = shipments.first()
            live_update = LiveUpdate.objects.filter(shipment=shipment_single)
            live_update_count = live_update.count()
            latest_update = live_update.last()

            return render(request, 'frontend/track_shipment.html', {'shipments':shipments, 'shipment_single':shipment_single,
            'update_count':live_update_count, 'latest_update':latest_update,
            'live_update':live_update}) 
        else:
            messages.error(request, "Invalid tracking code.  Please check the code and try again.")
            return redirect('frontend:track_shipment')
    return render(request, 'frontend/track_shipment.html')


@login_required()
def logoutUser(request):
	logout(request)
	return redirect('frontend:login')


def about_us(request):
    return render(request, 'frontend/about_us.html')

def service(request):
    return render(request, 'frontend/service.html')


def contact_us(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        final_message = render_to_string('frontend/emails/customer_care_email.html', 
        {
            'name': name,
            'email': email,
            'message': message,
            'subject': subject
        })

        try:
            emailsend.email_send(
                'Email From '+name,
                final_message,
                'contact@metroworldexpress.com',
            )
            messages.success(request, 'Email sent successfully, we will get back to you as soon as possible')
        except:
            messages.error(request, 'There was an error while trying to send your email, please try again')

        finally:
            return redirect('frontend:contact_us')
    return render(request, 'frontend/contact.html')
