

# Useful imports, etc.
import pandas as pd 
from pandas.io.gbq import read_gbq
import json,requests
import numpy as np
import polyline
import matplotlib.pyplot as plt

# Useful declarations
project = "spheric-crow-161317"
googleKey = 'AIzaSyBvuKUfCCTNzc8etkAuaU-16uzl3N4f6Vw'

# Data imports: station locations
query = "SELECT station_id, name, short_name, latitude, longitude FROM `bigquery-public-data.new_york.citibike_stations`"
station_locations = read_gbq(query=query, project_id=project, dialect='standard',verbose=False).set_index('station_id')

# User input
point_A = '133 Water Street, Brooklyn'
point_B = "60 5th Ave, New York"

# Georeferencing the results
d = json.loads(requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+point_A+' NY, United States&key='+googleKey).content)
lat1 = d['results'][0]['geometry']['location']['lat']
lon1 = d['results'][0]['geometry']['location']['lng']

d = json.loads(requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+point_B+' NY, United States&key='+googleKey).content)
lat2 = d['results'][0]['geometry']['location']['lat']
lon2 = d['results'][0]['geometry']['location']['lng']

# Assign status to each of those stations.
station_status = pd.read_json('https://gbfs.citibikenyc.com/gbfs/en/station_status.json')

for stations in station_status['data']['stations']:
	try: 
		stations['latitude'] = station_locations.loc[int(stations['station_id'])]['latitude']
		stations['longitude'] = station_locations.loc[int(stations['station_id'])]['longitude']
		stations['dist_A'] = np.sqrt((lat1-stations['latitude'])**2+(lon1-stations['longitude'])**2)
		stations['dist_B'] = np.sqrt((lat2-stations['latitude'])**2+(lon2-stations['longitude'])**2)
	except KeyError:	
		del(stations)


# Fetch list of closest stations (sort, limit, etc) and find the first station that is available.

ss = pd.DataFrame(station_status['data']['stations'])
ss = ss.sort_values('dist_A', ascending=1)

available = False

for index, row in ss.iterrows():
	if row['num_bikes_available'] > 0:
		start_station = row
		break

ss = ss.sort_values('dist_B', ascending=1)

available = False

for index, row in ss.iterrows():
	if row['num_docks_available'] > 0:
		end_station = row
		break

station_locations.loc[int(end_station['station_id'])]
station_locations.loc[int(start_station['station_id'])]



#final_call = json.loads(requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?origins='+point_A+'&destinations='+lat1+','+lon1+'&key='+googleKey).content)

d = json.loads(requests.get('https://maps.googleapis.com/maps/api/directions/json?origin='+point_A+'&destination='+point_B+'&waypoints='+str(lat1)+','+str(lon1)+'|'+str(lat2)+','+str(lon2)+'&mode=bicycling	&key='+googleKey).content)

geom = polyline.decode(d['routes'][0]['overview_polyline']['points'])
plt.plot(geom)
plt.show()



# Add walking routes to path (especially since the destination might not be within the Citi Bike domain)


