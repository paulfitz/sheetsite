import dataset
import json
import logging
import os
import requests
import six
from sqlalchemy import types
import time
import warnings


class GeoCache(object):
    def __init__(self, filename, geocoder=None):
        logging.basicConfig()
        logging.getLogger("dataset.persistence.table").setLevel(
            logging.ERROR
        )
        if '://' not in filename:
            filename = "sqlite:///{}".format(os.path.abspath(filename))
        self.db = dataset.connect(filename)
        self.geocache = self.db['geocache']
        self.update_schema()
        self.geocoder = geocoder

    def update_schema(self):
        if 'geocache' not in self.db:
            self.db.create_table('geocache',
                                 primary_id='address',
                                 primary_type='String')
        columns = [
            ('lat', types.Float),
            ('lng', types.Float),
            ('street', types.String),
            ('locality', types.String),
            ('region', types.String),
            ('country', types.String),
            ('postal_code', types.String),
            ('administrative_area_level_2', types.String),
            ('status', types.String)
        ]
        self.geocache = self.db['geocache']
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for name, kind in columns:
                self.geocache.create_column(name, kind)

    def complete(self, result):
        if 'lat' in result and 'lng' in result:
            if result['lat'] is not None and result['lng'] is not None:
                if result['lat'] != '' and result['lng'] != '':
                    result['latlng'] = "{},{}".format(result['lat'],
                                                      result['lng'])
        return result

    def find(self, address):
        if address is None or address.lower() == 'n/a':
            return {
                'status': "not applicable"
            }
        results = self.geocache.find(address=address)
        for row in results:
            return self.complete(dict(row))
        result = self.find_without_cache(address)
        print("--- geocoded [{}]".format(result))
        if result is None:
            result = {
                'address': address,
                'status': 'unknown'
            }
            self.geocache.insert(result)
        else:
            result['status'] = 'ok'
            self.geocache.insert(result)
            self.db.commit()
        return self.complete(result)

    def find_all(self, rows, pattern, cols):
        for row in rows:
            parts = []
            for p in pattern:
                if isinstance(p, int):
                    parts.append(row[p])
                else:
                    parts.append(p)
            if six.PY2:
                address = " ".join(str((x or '').encode('utf-8')) for x in parts)
            else:
                address = " ".join(str(x or '') for x in parts)
            result = self.find(address)
            if result['status'] == 'ok':
                for col in cols:
                    name = col[0].lower()
                    idx = col[1]
                    val = result[name]
                    if idx>=len(row):
                        row.append(None)
                    if row[idx] is None or row[idx] == '':
                        row[idx] = val

    def find_without_cache(self, address):
        print("--- geocoding [{}]".format(address))
        if self.geocoder == "datasciencetoolkit":
            return self.find_without_cache_dstk(address)
        if self.geocoder == "google" or self.geocoder is None:
            return self.find_without_cache_gmap(address)
        if self.geocoder == "dummy":
            return self.find_without_cache_dummy(address)
        raise ValueError('unknown geocoder {}'.format(self.geocoder))

    def find_without_cache_dummy(self, address):
        return {
            "address": address,
            "lat": 10.0,
            "lng": 10.0,
            "street": "Street St",
            "locality": "Cityville",
            "region": "New State",
            "country": "Countryland",
            "postal_code": "PO-STAL",
            "administrative_area_level_2": "Glig County",
            "status": 'valid'
        }

    def find_without_cache_dstk(self, address):
        try:
            r = requests.post("http://www.datasciencetoolkit.org/street2coordinates/", address,
                              timeout=15)
            v = json.loads(r.text)
            v = v[address]
            return {
                "address": address,
                "lat": v['latitude'],
                "lng": v['longitude'],
                "street": v['street_address'],
                "locality": v['locality'],
                "region": v['region'],
                "country": v['country_name'],
                "postal_code": None,
                "administrative_area_level_2": v['fips_county'],
                "status": 'valid'
            }
        except:
            return None

    def find_without_cache_gmap(self, address, fallback=None):
        try:
            def get_part(cmps, name, fallback=None):
                zips = [cmp["long_name"] for cmp in cmps if name in cmp["types"]]
                zip = zips[0] if len(zips)>0 else fallback
                return zip

            r = requests.get("http://maps.googleapis.com/maps/api/geocode/json",
                             params = {"sensor": "false", "address": address})
            time.sleep(1)
            v = json.loads(r.text)
            coord = v["results"][0]["geometry"]["location"]
            lat = coord["lat"]
            lng = coord["lng"]
            cmp = v["results"][0]["address_components"]
            try:
                street = get_part(cmp, 'street_number', '') + ' ' + get_part(cmp, 'route')
            except:
                street = None
            return {
                "address": address,
                "lat": lat,
                "lng": lng,
                "street": street,
                "locality": get_part(cmp, 'locality'),
                "region": get_part(cmp, 'administrative_area_level_1'),
                "administrative_area_level_2": get_part(cmp, 'administrative_area_level_2'),
                "country": get_part(cmp, 'country'),
                "postal_code": get_part(cmp, 'postal_code')
                }
        except Exception as e:
            print("PROBLEM", e)
            return None


if __name__ == '__main__':
    cache = GeoCache("cache.db")
    print(cache.find("305 Memorial Dr, Cambridge, MA"))
