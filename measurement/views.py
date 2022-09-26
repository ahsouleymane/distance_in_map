from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
from geopy.geocoders import Nominatim
from geopy.distance import geodesic # this fonction calculate distance
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium

# Create your views here.



def calculate_distance_view(request):

    # Initial values

    distance = None
    destination = None

    obj = Measurement.objects.get(id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurement')

    ip_ = get_ip_address(request)
    print(ip_)
    ip = '72.14.207.99'

    country, city, lat, lon = get_geo(ip)

    location = geolocator.geocode(city)

    # Location coordinates
    l_lat = lat
    l_lon = lon

    pointA = (l_lat, l_lon)

    # Initial folium map
    m = folium.Map(width=1600, height=600, location=get_center_coordinates(l_lat, l_lon), zoom_start=8)

    # Location marker
    folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'], 
                    icon=folium.Icon(color='purple')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # Destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude

        pointB = (d_lat, d_lon)

        # Distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # Folium map modification
        m = folium.Map(width=1600, height=600, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), 
            zoom_start=get_zoom(distance))

        # Location marker
        folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'], 
                        icon=folium.Icon(color='purple')).add_to(m)

        # Destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination, 
                        icon=folium.Icon(color='red', icon='cloud')).add_to(m)

        # Draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=2, color='blue')
        m.add_child(line)
        

        instance.location = location
        instance.distance = distance
        instance.save()

    m = m._repr_html_()

    context = {'distance': distance,'destination': destination, 'form': form, 'map': m}
    return render(request, 'measurement/main.html', context) 
