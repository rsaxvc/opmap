from geopy.geocoders import GoogleV3
geolocator = GoogleV3()
location = geolocator.geocode("5022 LANSDOWNE AVE SAINT LOUIS MO 63109")
print(location.address)
print((location.latitude, location.longitude))
print(location.raw)
