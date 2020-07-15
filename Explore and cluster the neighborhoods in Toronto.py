#!/usr/bin/env python
# coding: utf-8

# # Explore and cluster the neighborhoods in Toronto:

# In[3]:


# Import necessary Libraries
import pandas
import numpy as np
import requests
from bs4 import BeautifulSoup
print('libraries imported')


# In[ ]:


pip install bs4


# In[2]:


# import data 
website_text = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup = BeautifulSoup(website_text,'xml')

table = soup.find('table',{'class':'wikitable sortable'})
table_rows = table.find_all('tr')

data = []
for row in table_rows:
    data.append([t.text.strip() for t in row.find_all('td')])

df = pandas.DataFrame(data, columns=['PostalCode', 'Borough', 'Neighbourhood'])

# to filter out bad rows
df = df[~df['PostalCode'].isnull()]  

df.head(11)


# In[3]:


# replace "Not assigned" to NaN
df.replace("Not assigned", np.nan, inplace = True)

# drop whole row with NaN
df.dropna(subset=["Borough", "Neighbourhood"], axis=0, inplace=True)

# reset index
df.reset_index(drop=True, inplace=True)

df.head()


# In[4]:


# combined similar PostalCode 
df= df.groupby('PostalCode').agg(lambda x: ','.join(x))

#combined similar Borough
df.loc[df['Neighbourhood']=="Not assigned",'Neighbourhood']=df.loc[df['Neighbourhood']=="Not assigned",'Borough']

# remove duplicate Borough
df['Borough']= df['Borough'].str.replace('nan|[{}\s]','').str.split(',').apply(set).str.join(',').str.strip(',').str.replace(",{2,}",",")

# reset index
df = df.reset_index()

df.head()


# ###  Get the latitude and the longitude coordinates of each neighborhood. 

# In[5]:


import pandas as pd
df1 = pd.read_csv('Geospatial_Coordinates.csv')
df1.head()


# In[9]:


# drop Postal Code cloumn in df1
df1.drop(['Postal Code'], axis=1, inplace= True)
df1.head()


# In[11]:


# combine df and df1 
df2 = pd.concat([df,df1], axis=1)
df2.head(12)


# ### Explore and cluster the neighborhoods in Toronto

# In[12]:


# Import necessary Libraries
import requests # library to handle requests
import pandas as pd # library for data analsysis
import numpy as np # library to handle data in a vectorized manner
import random # library for random number generation

get_ipython().system('conda install -c conda-forge geopy --yes ')
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values

# libraries for displaying images
from IPython.display import Image 
from IPython.core.display import HTML 
    
# tranforming json file into a pandas dataframe library
from pandas.io.json import json_normalize

get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium # plotting library

print('Folium installed')
print('Libraries imported.')


# In[13]:


# Define Foursquare Credentials and Version
CLIENT_ID = 'DIRG35JTVWYHM2IL1Y0IKYQI0L5U0GE4YOQOFEHH20345W2J' # your Foursquare ID
CLIENT_SECRET = 'AIMHWOBGKFUFSVXGZHHMFE122HSTIVZ130HCUYHGUX1WCE2L' # your Foursquare Secret
VERSION = '20180604'
LIMIT = 30
print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[21]:


address = 'Scarborough'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print(latitude, longitude)


# In[31]:


search_query = 'Hotel'
radius = 500
print(search_query + ' .... OK!')


# In[32]:


url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT)
url


# In[33]:


results = requests.get(url).json()
results


# In[34]:


# assign relevant part of JSON to venues
venues = results['response']['venues']

# tranform venues into a dataframe
dataframe = json_normalize(venues)
dataframe.head()


# In[35]:


# keep only columns that include venue name, and anything that is associated with location
filtered_columns = ['name', 'categories'] + [col for col in dataframe.columns if col.startswith('location.')] + ['id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']

# filter the category for each row
dataframe_filtered['categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean column names by keeping only last term
dataframe_filtered.columns = [column.split('.')[-1] for column in dataframe_filtered.columns]

dataframe_filtered


# In[36]:


dataframe_filtered.name


# In[37]:


venues_map = folium.Map(location=[latitude, longitude], zoom_start=13) # generate map centred around the Conrad Hotel

# add a red circle marker to represent the Conrad Hotel
folium.features.CircleMarker(
    [latitude, longitude],
    radius=10,
    color='red',
    popup='Conrad Hotel',
    fill = True,
    fill_color = 'red',
    fill_opacity = 0.6
).add_to(venues_map)

# add the Italian restaurants as blue circle markers
for lat, lng, label in zip(dataframe_filtered.lat, dataframe_filtered.lng, dataframe_filtered.categories):
    folium.features.CircleMarker(
        [lat, lng],
        radius=5,
        color='blue',
        popup=label,
        fill = True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(venues_map)

# display map
venues_map


# In[ ]:




