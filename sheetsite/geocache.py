import json
import requests
import sqlite3
import time

class GeoCache(object):
    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.db.execute("create table if not exists geocache("
                        "address TEXT PRIMARY KEY,"
                        "lat TEXT,"
                        "lng TEXT," 
                        "street TEXT,"
                        "locality TEXT,"
                        "region TEXT," 
                        "country TEXT,"
                        "postal_code TEXT,"
                        "status TEXT)")
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.commit()
        self.db.close()

    def complete(self, result):
        if 'lat' in result and 'lng' in result:
            if result['lat'] is not None and result['lng'] is not None:
                if result['lat'] != '' and result['lng'] != '':
                    result['latlng'] = "{},{}".format(result['lat'], result['lng'])
        return result

    def find(self, address):
        results = self.cursor.execute("select address, lat, lng, street, "
                                      "locality, region, country, postal_code, "
                                      "status from geocache where address = ?", [address]).fetchall()
        for row in results:
            return self.complete({
                'address': address,
                'lat': row[1],
                'lng': row[2],
                'street': row[3],
                'locality': row[4],
                'region': row[5],
                'country': row[6],
                'postal_code': row[7],
                'status': row[8]
            })
        result = self.find_without_cache(address)
        if result is None:
            result = {
                'address': address,
                'status': 'unknown'
            }
            self.cursor.execute("insert into geocache (address,status) values(?, ?)",
                                [address, 'unknown'])
        else:
            result['status'] = 'ok'
            self.cursor.execute("insert into geocache (address,lat,lng,"
                                "street,locality,region,country,postal_code,"
                                "status) values(?,?,?,?,?,?,?,?,?)",
                                [result[key] for key in ['address','lat','lng',
                                                         'street','locality','region',
                                                         'country','postal_code','status']])
        return self.complete(result)

    def find_all(self, rows, key_id, cols):
        for row in rows:
            address = row[key_id]
            result = self.find(address)
            if result['status'] == 'ok':
                for col in cols:
                    name = col[0].lower()
                    idx = col[1]
                    val = result[name]
                    if row[idx] is None or row[idx] == '':
                        row[idx] = val

    def find_without_cache(self, address):
        print "Looking up", address
        return self.find_without_cache_gmap(address)

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
                "status": 'valid'
            }
        except:
            return None

    def find_without_cache_gmap(self, address, fallback=None):
        try:
            def get_part(cmp, name, fallback=None):
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
            cmps = v["results"][0]["address_components"]
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
                "country": get_part(cmp, 'country'),
                "postal_code": get_part(cmp, 'postal_code')
                }
        except Exception as e:
            print "PROBLEM", e
            return None

if __name__ == '__main__':
    cache = GeoCache("cache.db")
    print cache.find("305 Memorial Dr, Cambridge, MA")
