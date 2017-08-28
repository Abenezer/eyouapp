def toArea(lon, lat):
    from geopy.geocoders import Nominatim
    from eyou.models import Area
    geolocator = Nominatim(timeout=10, country_bias='Ethiopia')
    location = geolocator.reverse([lat, lon],language='en')
    if location==None:
        return None
    print (location.raw['address'])
    return Area(lat=location.latitude, lon=location.longitude, displayName=location.address,
                city=location.raw['address']['city'],
                country=location.raw['address']['country'],
                localName=location.raw['address'].get('suburb',''),
                boundingBox=''.join(location.raw['boundingbox']),
                OSM_id=location.raw['osm_id'],
                nom_place_id= location.raw['place_id'],

                )
