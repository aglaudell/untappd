import pandas as pd
import numpy as np
import os
import json
import folium

from geopy.geocoders import GoogleV3
from time import sleep

import settings

path = os.path.dirname(__file__)

""" USER INPUT HERE"""
# User data file path
userdata = 'userdata.csv'
api_key = settings.API_KEY

""" LOAD AND PREPROCESS """
userdata = os.path.join(path, 'data', userdata)

# Load data
data = pd.read_csv(userdata, index_col = 'created_at')

data.index = pd.to_datetime(data.index)

# create unique beer_id, brewery_id
data['beer_id'] = data['beer_url'].str.rsplit('/', 1).str[-1]
data['brewery_id'] = data['brewery_url'].str.rsplit('/', 1).str[-1]


""" FETCH COORDINATES """
# aggregate brewery data
grouped = data.groupby('brewery_id')
brewery_data = grouped[['brewery_name', 'brewery_url', 
                        'brewery_country', 'brewery_city',
                        'brewery_state']].first()
brewery_data[['count','unique']] = grouped['beer_id'].describe()[['count','unique']]

brewery_data = brewery_data.rename(columns={
        col : col.split('_')[-1] for col in brewery_data.columns
        })
brewery_data['rating_avg'] = grouped['rating_score'].mean()
brewery_data.fillna('', inplace=True)

# create address col
brewery_data['address'] = brewery_data[['name','city','state','country']].apply(
        lambda x: ', '.join([y for y in x if y]), axis=1
        )

# fetch coordinates using Google api
geolocator = GoogleV3(api_key=api_key)
coords_path = os.path.join(path, 'data', 'coords.json')

try:
    with open(coords_path, 'r') as f:
        coords_dict = json.load(f)
except EnvironmentError:
    coords_dict = {}
    
def locate(address, timeout=10):
    """ 
    Uses Google API to locate coordinates based on address with components
    separated by a comma ','. If address is not found, searches one component
    less specific.
    """
    if address not in coords_dict:
        try:
            location = geolocator.geocode(address, timeout=timeout)
            lat = location.latitude
            long = location.longitude
            
            coords_dict[address] = [lat, long]
            return pd.Series([lat, long])
        except:
            sleep(1)
            pass
        try:
            rdx = ', '.join(address.split(',').strip()[1:])
            location = geolocator.geocode(rdx, timeout=timeout)
            lat = location.latitude
            long = location.longitude
            
            coords_dict[address] = [lat, long]
            return pd.Series([lat, long])
        except:
            print('No coords for: ', address)
            return pd.Series([np.nan, np.nan])
        
    else:
        lat = coords_dict[address][0]
        long = coords_dict[address][1]
        return pd.Series([lat, long])
    
brewery_data[['lat','long']] = brewery_data['address'].apply(locate)

# write coords to json
f = open(coords_path, 'w')
f.write(json.dumps(coords_dict))
f.close()

""" CREATE BEER MAP """
LOCAL_COORDS = (34.4208, -119.6982)
m = folium.Map(location=LOCAL_COORDS, zoom_start=4, min_zoom=2)

for each in brewery_data.iterrows():
    location = [each[1]['lat'], each[1]['long']]
    brewery = each[1]['name']
    address = ', '.join([y for y in each[1][['city','state']].values if y])
    if each[1]['country'] != 'United States':
        address = '{}, {}'.format(address, each[1]['country'])
    unique = each[1]['unique']
    count = each[1]['count']
    size = np.sqrt(unique)*5 # 1ct = 1px
    if not np.isnan(location).any():
        text = '{}\n{}\nUnique: {}, Total: {}'.format(brewery, address, unique, count)
        popup = folium.Popup(text, parse_html=True)
        folium.CircleMarker(
            location=location,
            radius=size,
            popup=popup,
            color='#FFD700',
            fill=True,
            fill_color='#FFD700', fill_opacity=0.5, 
            weight=1,
        ).add_to(m)
        
m.save(os.path.join(path, 'checkins_map.html'))