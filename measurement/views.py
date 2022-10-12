from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
from geopy.geocoders import Nominatim
from geopy.distance import geodesic # this fonction calculate distance
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium
import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from ipware import get_client_ip
import json, urllib
# Create your views here.

""" class locationAPI(APIView):

    def get(self, request, format=None):
        client_ip, ip_routable = get_client_ip(request)

        if client_ip is None:
            client_ip = "0.0.0.0"
        else:
            if ip_routable:
                ip_type = "public"
            else:
                ip_type = "private"

        print(client_ip, ip_type)

        ip_address = '154.127.94.179'
        url='https://api.ipfind.com/?ip=' + ip_address
        respon = urllib.request.urlopen(url)
        data1 = json.loads(respon.read())
        data1['client_ip'] = client_ip
        data1['ip_type'] = ip_type
        return Response(data1) """


def calculate_distance_view(request):

    # Initial values

    distance = None
    destination = None

    obj = Measurement.objects.get(id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurement')

    ## Methode 1

    ip_ = get_ip_address(request)
    #print(ip_)
    ip = '154.127.94.179'

    country, city, lat, lon = get_geo(ip)

    location = geolocator.geocode(city)

    # Location coordinates
    l_lat = lat
    l_lon = lon

    #print(l_lat, l_lon)


    ## Methode 2


    # Location coordinates using json
    r = requests.get('https://get.geojs.io/')
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    ip_add = ip_request.json()['ip']
    print(ip_add)

    url = 'https://get.geojs.io/v1/ip/geo/'+ip_add+'.json'
    geo_request = requests.get(url)
    geo_data = geo_request.json()
    #print(geo_data)

    # Location coordinates
    x_lat = float(geo_data['latitude'])
    x_lon = float(geo_data['longitude'])

    print(x_lat, x_lon)

    pointA = (x_lat, x_lon)

    # Initial folium map
    m = folium.Map(width=1600, height=600, location=get_center_coordinates(x_lat, x_lon), zoom_start=12)

    # Location marker
    folium.Marker([x_lat, x_lon], tooltip='click here for more', popup=city['city'], 
                    icon=folium.Icon(color='purple')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        print(destination)

        # Destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude

        pointB = (d_lat, d_lon)

        # Distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        print(str(distance) + 'km')

        # Folium map modification
        m = folium.Map(width=1600, height=600, location=get_center_coordinates(x_lat, x_lon, d_lat, d_lon), 
            zoom_start=get_zoom(distance))

        # Location marker
        folium.Marker([x_lat, x_lon], tooltip='click here for more', popup=city['city'], 
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
