# from .models import LiveUpdate, CountryLocation
from django.db import connection
import threading
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="your_app_name")

def extract_country_from_location(location_str):
    if not location_str:
        return None
    parts = location_str.split(',')
    if len(parts) > 1:
        return parts[-1].strip().title()  # Normalize country here too
    return location_str.strip().title()

def geocode_and_update(live_update_id):
    from .models import LiveUpdate, CountryLocation
    connection.close()  # Close DB connection in thread

    try:
        instance = LiveUpdate.objects.get(id=live_update_id)

        if instance.latitude and instance.longitude:
            return

        country = extract_country_from_location(instance.current_location)
        cached = CountryLocation.objects.filter(country_name__iexact=country).first()

        if cached:
            instance.latitude = cached.latitude
            instance.longitude = cached.longitude
            instance.save()
            return

        location = geolocator.geocode(instance.current_location)
        if location:
            instance.latitude = location.latitude
            instance.longitude = location.longitude
            instance.save()

            if country:
                CountryLocation.objects.get_or_create(
                    country_name=country,
                    defaults={'latitude': location.latitude, 'longitude': location.longitude}
                )
    except Exception as e:
        print(f"Geocoding error: {e}")

def start_geocoding_thread(instance_id):
    thread = threading.Thread(target=geocode_and_update, args=(instance_id,))
    thread.daemon = True
    thread.start()
