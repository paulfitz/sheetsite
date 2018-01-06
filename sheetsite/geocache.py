import dataset
import json
import logging
import os
import requests
import six
import time


class GeoCache(object):
    def __init__(self, filename, geocoder=None, group_key=None):
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
        self.group_key = group_key
        self.prev_row = None

    def update_schema(self):
        if 'geocache' not in self.db:
            self.db.create_table('geocache',
                                 primary_id='address',
                                 primary_type=self.db.types.string)

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

    def blank(self, val):
        return val is None or val == ""

    def find_all(self, rows, pattern, cols):
        for row in rows:
            parts = []
            for p in pattern:
                if isinstance(p, int):
                    if ((self.blank(row[p]) and self.prev_row and
                         self.prev_row[self.group_key] == row[self.group_key] and
                         not self.blank(self.group_key) and
                         not self.blank(row[self.group_key]))):
                        parts.append(self.prev_row[p])
                    else:
                        parts.append(row[p])
                else:
                    parts.append(p)
            parts = [part for part in parts if not self.blank(part)]
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
                    if idx >= len(row):
                        row.append(None)
                    if row[idx] is None or row[idx] == '':
                        row[idx] = val
            if self.group_key:
                if self.prev_row:
                    if self.prev_row[self.group_key] != row[self.group_key]:
                        self.prev_row = row
                else:
                    self.prev_row = row

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

            v = None
            xaddress = address
            for delay in [1, 2, 4, 8]:
                r = requests.get("http://maps.googleapis.com/maps/api/geocode/json",
                                 params={"sensor": "false", "address": xaddress})
                time.sleep(delay)
                v = json.loads(r.text)
                if 'status' in v:
                    if v['status'] == 'ZERO_RESULTS':
                        if ',' in xaddress:
                            xaddress = xaddress.split(',', 1)[1]
                            continue
                    if v['status'] != 'OVER_QUERY_LIMIT':
                        break
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
    # print(cache.find("305 Memorial Dr, Cambridge, MA"))
    # print(cache.find("Chittenden, Franklin County, Connecticut, United States"))
    print(cache.find("Lamoille County, Connecticut, United States"))
