
NAMES = {
    'lat': 'lat',
    'latitude': 'lat',
    'lng': 'lng',
    'lon': 'lng',
    'longitude': 'lng',
    'address': 'address',
    'zip': 'postal_code',
    'zipcode': 'postal_code',
    'zip_code': 'postal_code',
    'zip code': 'postal_code',
    'postal_code': 'postal_code',
    'postal code': 'postal_code',
    'locality': 'locality',
    'city': 'locality',
    'country': 'country',
    'street': 'street',
    'region': 'region',
    'state': 'region',
    'province': 'region',
    'county': 'administrative_area_level_2',
    'geo_county': 'administrative_area_level_2',
    'latlng': 'latlng'
}


def normalize_name(name):
    name = name.lower()
    return NAMES.get(name, name)
