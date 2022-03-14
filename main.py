import streamlit as st
from pandas.io.json import json_normalize
import folium
from geopy.geocoders import Nominatim
import requests

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt 
from sklearn.cluster import KMeans
import folium
from IPython.display import display

from IPython.display import HTML

#---------
import streamlit as st
from streamlit_folium import folium_static
import folium

import geopy


#--------------------------
from PIL import Image
image = Image.open('EXPLORER-logo.jpg')
st.image(image, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
st.title("Explorer")

city_name = st.selectbox("City", ("Ghaziabad", "New Delhi", "Gurugram", "Noida","Meerut", "Dehradun","Chandigarh","Punjab"))
#city = "Hyderabad"
## get location
locator = geopy.geocoders.Nominatim(user_agent="MyCoder")
location = locator.geocode(city_name)
lattt = location.latitude
longgg = location.longitude

#---------------

CLIENT_ID = '4T5ETI3BWAGID53KGFGLU2CFZ44AFNXTL1XO5C3A31NJAFMO'
CLIENT_SECRET = 'WXJSXNGCORCJGM4VKYOCZPN22DBKT0BDRWXOBUIWLQQ4ELA4'
VERSION = '20200226'
LIMIT = 10000

url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    lattt,longgg,
    #28.6692, 77.4538,
    10000, 
    LIMIT)

results = requests.get(url).json()

venues = results['response']['groups'][0]['items']
nearby_venues = json_normalize(venues)

restrau = []
oth = []
for lat,lng in zip(nearby_venues['venue.location.lat'], nearby_venues['venue.location.lng']):
    url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(CLIENT_ID,
    CLIENT_SECRET, VERSION, lat,lng,1000, 100)
    res = requests.get(url).json()
    venue= res['response']['groups'][0]['items']
    nearby_venue = json_normalize(venue)
    df1 = nearby_venue['venue.categories']

    g=[]
    for i in range(0,df1.size):
        g.append(df1[i][0]['icon']['prefix'].find('food'))
    co=0
    for i in g:
          if i>1:
              co+=1
    restrau.append(co)
    oth.append(len(g) - co)


nearby_venues['restaurent'] = restrau
nearby_venues['others'] = oth

lat=nearby_venues['venue.location.lat']
long=nearby_venues['venue.location.lng']

f=['venue.location.lat','venue.location.lng']
kmeans_parameters = nearby_venues[f]

error=[]
for i in range(1,11):
    kmeans=KMeans(n_clusters=i, max_iter=300)
    kmeans.fit(kmeans_parameters)
    ##kmeans.fit(nearby_venues['venue.location.lat', 'venue.location.lat'])
    error.append(kmeans.inertia_)

k = [i*100 for i in np.diff(error,2)].index(min([i*100 for i 
     in np.diff(error,2)]))

df=nearby_venues.drop(['referralId', 'reasons.count', 'reasons.items', 'venue.id',
       'venue.name', 
       'venue.location.labeledLatLngs', 'venue.location.distance',
       'venue.location.cc', 
       'venue.categories', 'venue.photos.count', 'venue.photos.groups',
       'venue.location.crossStreet', 'venue.location.address','venue.location.city',
       'venue.location.state', 'venue.location.crossStreet',
       #'venue.location.neighborhood',#'venue.venuePage.id',
       'venue.location.postalCode','venue.location.country'],axis=1)

df=df.rename(columns={'venue.location.lat': 'lat' , 'venue.location.lng': 'long', 'venue.location.formattedAddress': 'address'})

kmeans = KMeans(n_clusters=k)
kmeans.fit(kmeans_parameters)

labels = kmeans.predict(kmeans_parameters)
df['cluster'] = labels

chars = ["[","]"]
for char in chars:
    df['address'] = df['address'].astype(str).str.replace(char, ' ')

df1 = df[df.cluster == 0]
df2 = df[df.cluster == 1]
df3 = df[df.cluster == 2]


#---------------------
m = folium.Map(location=[lattt, longgg], zoom_start=10)
#m = folium.Map(location=[28.685151275979585, 77.21357111294833], zoom_start=10)

for i in df1.itertuples():
    folium.Marker(location=[i.lat, i.long],
                  popup=i.address,
                  icon=folium.Icon(color='red')).add_to(m)
i=0
for i in df2.itertuples():
    folium.Marker(location=[i.lat, i.long],
                  popup=i.address,
                  icon=folium.Icon(color='blue')).add_to(m)

i=0
for i in df3.itertuples():
    folium.Marker(location=[i.lat, i.long],
                  popup=i.address,
                  icon=folium.Icon(color='purple')).add_to(m)


#HTML('<iframe src=map.html width=700 height=450></iframe>')
#m.save('map.html')
folium_static(m)
#st.markdown(m._repr_html_(), unsafe_allow_html=True)
#st.write(m)