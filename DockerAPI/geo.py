import geocoder
from geopy.geocoders import Nominatim
from geopy import distance



# origem = geocoder.ip('177.154.39.158')
# origem = geocoder.ip('179.125.223.102')
origem = geocoder.ip('200.133.218.93')
# origem = geocoder.ip('128.110.153.107')
# origem = geocoder.ip('143.106.73.65')

# destino = geocoder.ip('128.110.153.107')
# destino = geocoder.ip('143.106.73.65')
destino = geocoder.ip('177.154.39.158')
# destino = geocoder.ip('179.125.223.102')

lat_long_o = origem.latlng
endereco_o = origem.address
lat_long_d = destino.latlng
endereco_d = destino.address

print(f'Latitude_Longitude_Origem: {lat_long_o}')
print(f'Endereço Origem: {endereco_o}')

print(f'Latitude_Longitude_Destino: {lat_long_d}')
print(f'Endereço Destino: {endereco_d}')

geolocator = Nominatim(user_agent="user",timeout=10)
location_o = geolocator.geocode(endereco_o)
location_d = geolocator.geocode(endereco_d)
endereco1_o = location_o.address
endereco1_d = location_d.address
print(f'Latitude_Longitude Origem: {location_o.latitude} | {location_o.longitude}')
print(f'Endereço Origem: {endereco1_o}')
print(f'Latitude_Longitude Destino: {location_d.latitude} | {location_d.longitude}')
print(f'Endereço Destino: {endereco1_d}')

# print(f'Endereço: {endereco}')

# coords_1 = (endereco_o)
# coords_2 = (endereco_d)
# distancia = distance.distance(coords_1, coords_2).km
coords_1 = (location_o.latitude, location_o.longitude)
coords_2 = (location_d.latitude, location_d.longitude)
distancia = distance.distance(coords_1, coords_2).km
print(f'Distância: {distancia:.1f} Km')