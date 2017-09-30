#!/usr/bin/python

from contextlib import contextmanager
import dataset
from datetime import datetime
import json
import os
import re
from tqdm import tqdm
import uuid


def get_prop(key, rows):
    val = None
    many_versions = False
    for row in rows:
        v = row[key]
        if v is not None:
            if val is None:
                val = v
            if v != val:
                many_versions = True
    return val, many_versions


def get_props(keys, rows, first):
    result = {}
    for key in keys:
        val, many_versions = get_prop(key, rows)
        if many_versions and not(first):
            val = None
        result[key] = val
    return result


def get_common_props(rows):
    return get_props(rows[0].keys(), rows, False)


def get_main_props(rows):
    return get_props(rows[0].keys(), rows, True)


def anykey(props, *keys):
    optional = (None in keys)
    keys = list(filter(None, keys))
    prop_keys = dict((key.upper(), key) for key in props.keys())
    for key in keys:
        key = key.upper()
        if key in prop_keys:
            return props[prop_keys[key]]
    # fail deliberately
    if optional:
        return None
    return props[keys[0]]


def fix_email(email):
    if email is None:
        return email
    email = str(email)
    email = re.sub(r'mailto:', '', email)
    return email


def make_org(props):
    organization = {
        'name': anykey(props, "NAME", "CompanyName"),
        'phone': anykey(props, "PHONE", "WorkPhone"),
        'email': fix_email(anykey(props, "EMAIL", "Email Address")),
        'website': anykey(props, "WEBSITE", "Web Address", None),
        'description': anykey(props, "GOODS AND SERVICES", "Description", None),
        'access_rule_id': 1
        }
    return organization


def safe_access(props, key):
    if not(key in props):
        return None
    x = props[key]
    if x == "":
        return None
    return x


def make_loc(props, rid):
    location = {
        'physical_address1': anykey(props, "Street Address",
                                    "Street", "Physical Address"),
        'physical_address2': None,
        'physical_city': anykey(props, "city"),
        'physical_state': anykey(props, "state"),
        'physical_zip': anykey(props, "zip", "postal code"),
        'physical_country': anykey(props, "country"),
        'latitude': anykey(props, "Latitude", "lat", None),
        'longitude': anykey(props, "Longitude", "lng", None),
        'taggable_id': rid,
        'taggable_type': "Organization",
        'dccid': anykey(props, 'dccid')
        }
    return location


class DirectToDB(object):
    def __init__(self, cur):
        self.cur = cur

    def column(self, tbl, column, example):
        return self.cur[tbl].create_column_by_example(column, example)

    def insert(self, tbl, values):
        return self.cur[tbl].insert(values)

    def delete(self, tbl, **conds):
        return self.cur[tbl].delete(**conds)

    def update(self, tbl, values, keys):
        self.cur[tbl].update(values, keys)

    def upsert(self, tbl, values, keys):
        result = self.cur[tbl].upsert(values, keys)
        if result is not True:
            return result
        return self.cur[tbl].find_one(**values)['id']

    def find(self, tbl, **conds):
        return self.cur[tbl].find(**conds)

    def find_one(self, tbl, **conds):
        return self.cur[tbl].find_one(**conds)

    @contextmanager
    def transaction(self):
        with self.cur as x:
            yield DirectToDB(x)


def blanky(x):
    if x == "" or x is None:
        return None
    return x


def floaty(x):
    if x is None or x == "":
        return None
    return float(x)


def apply(params, state):

    path = merge_path = state['path']
    output_file = state['output_file']

    if 'merge_path' in params:
        merge_path = params['merge_path']
    target = os.path.abspath(os.path.join(merge_path,
                                          'stonesoup.sqlite3'))
    target_perm = os.path.abspath(os.path.join(path,
                                               'stonesoup.sqlite3'))
    state['sqlite_file'] = target_perm

    cur = DirectToDB(dataset.connect("sqlite:///" + target))
    ot = cur.upsert("tag_contexts", {
        'name': 'OrgType',
        'friendly_name': 'Organization Type'
    }, ['name'])
    ot = cur.upsert("tags", {
        'name': 'OrgType',
        'root_id': ot,
        'root_type': "TagContext"
    }, ['root_id', 'root_type'])

    cur.column('locations', 'mailing_address1', 'x')
    cur.column('locations', 'mailing_address2', 'x')
    cur.column('locations', 'mailing_city', 'x')
    cur.column('locations', 'mailing_state', 'x')
    cur.column('locations', 'mailing_zip', 'x')
    cur.column('locations', 'mailing_country', 'x')
    cur.column('locations', 'mailing_county', 'x')
    cur.column('locations', 'physical_county', 'x')
    for tab in ['organizations', 'locations']:
        cur.column(tab, 'created_at', datetime.now())
        cur.column(tab, 'updated_at', datetime.now())
    cur.column('people', 'firstname', 'x')
    cur.column('people', 'lastname', 'x')
    cur.column('organizations_people', 'person_id', 1)
    cur.column('organizations_people', 'organization_id', 1)
    cur.column('tags', 'effective_id', 1)
    cur.column('locations', 'note', 'x')
    cur.column('organizations', 'fax', 'x')
    cur.column('organizations', 'year_founded', 'x')
    cur.column('product_services', 'name', 'x')
    cur.column('product_services', 'organization_id', 1)
    cur.column('organizations_users', 'user_id', 1)
    cur.column('organizations_users', 'organization_id', 1)
    cur.column('users', 'login', 'x')

    cur.column('access_rules', 'access_type', 'PUBLIC')
    cur.upsert('access_rules', {'id': 1, 'access_type': 'PUBLIC'}, ['id'])

    cur.column('data_sharing_orgs', 'name', 'x')
    dso = params['organization']
    dso_id = cur.upsert('data_sharing_orgs',
                        {'name': params['organization']},
                        ['name'])

    org_names = []
    orgs = {}

    print("READING", output_file)
    tables = json.load(open(output_file))
    selection = tables['names'][0]
    lol = tables['tables'][selection]["rows"]

    tabs = ['locations', 'organizations', 'taggings',
            'data_sharing_orgs_taggables']

    def prep(tab):
        cur.column(tab, 'dso', 'x')
        cur.column(tab, 'dso_update', 'x')
        cur.update(tab, {
            'dso': dso,
            'dso_update': 'old'
        }, ['dso'])
    for tab in tabs:
        prep(tab)

    # collect all locations for each org
    for idx, row in tqdm(list(enumerate(lol))):
        name = anykey(row, 'NAME', 'CompanyName')
        if not(name in orgs):
            orgs[name] = []
            org_names.append(name)
        orgs[name].append(row)

    print("ORG COUNT " + str(len(org_names)))

    for idx, name in tqdm(list(enumerate(org_names))):
        rows = orgs[name]
        common = get_common_props(rows)
        main = get_main_props(rows)
        # print(name + " : " + str(common) + " " + str(len(rows)))
        organization = make_org(common)
        # print(organization, rows)
        # get a dccid
        ids = set(filter(None, [row['dccid'] for row in rows])) - set([''])
        oid = None
        for id in ids:
            y = list(cur.find('oids', dccid=id))
            if len(y) > 0:
                oid = y[0]['oid']
                break
        if oid is None:
            oid = str(uuid.uuid4())
        with cur.transaction() as cur1:
            for id in ids:
                cur1.upsert('oids', {'oid': oid, 'dccid': id}, ['dccid'])
        organization['oid'] = oid
        organization['dso'] = dso
        organization['dso_update'] = 'fresh'
        rid = cur.upsert("organizations", organization, ['oid'])
        fid = None
        with cur.transaction() as cur1:
            for row in rows:
                loc = make_loc(row, rid)
                if loc['latitude'] is None or loc['latitude'] == "":
                    loc['latitude'] = floaty(blanky(row['Latitude']))
                if loc['longitude'] is None or loc['longitude'] == "":
                    loc['longitude'] = floaty(blanky(row['Longitude']))
                if loc['physical_zip'] is None:
                    loc['physical_zip'] = blanky(row['Postal Code'])
                if loc['dccid'] is None:
                    loc['dccid'] = blanky(row['dccid'])
                loc['dso'] = dso
                loc['dso_update'] = 'fresh'
                fid0 = cur1.upsert("locations", loc, ['dccid'])
                if fid is None:
                    fid = fid0
        with cur.transaction() as cur1:
            cur1.update('organizations',
                        {'id': rid, 'primary_location_id': fid},
                        ['id'])
            cur1.upsert("data_sharing_orgs_taggables", {
                "data_sharing_org_id": dso_id,
                "taggable_id": rid,
                "taggable_type": "Organization",
                "verified": 1,
                "foreign_key_id": 999,
                "dso": dso,
                "dso_update": "fresh"
            }, ['data_sharing_org_id', 'taggable_id', 'taggable_type'])
        typs = main["TYPE"]
        if typs is None:
            typs = ""
        typs = typs.split(',')
        if "dcc_status" in main:
            typ0 = main['dcc_status']
            if typ0:
                typs.append(typ0)
        typs = [typ.strip() for typ in typs if typ.strip() != ""]
        for typ in typs:
            v = list(cur.find('org_types', name=typ))
            tid = None
            if len(v) == 0:
                tid = cur.insert("org_types", {
                        'name': typ
                        })
                tid = cur.insert("tags", {
                        'name': typ,
                        'root_id': tid,
                        'root_type': "OrgType",
                        'parent_id': ot
                        })
            else:
                tid = v[0]['id']
                tid = cur.find_one('tags', root_id=tid, root_type='OrgType')['id']
            cur.upsert("taggings", {
                "tag_id": tid,
                "taggable_id": rid,
                "taggable_type": "Organization",
                "dso": dso,
                "dso_update": "fresh"
            }, ['tag_id', 'taggable_id', 'taggable_type'])
        dex = main['Index']
        if dex:
            for dex in [x.strip() for x in dex.lower().split(',')]:
                v = list(cur.find('tags', name=dex))
                tid = None
                if len(v) == 0:
                    tid = cur.insert("tags", {
                            'name': dex
                            })
                else:
                    tid = v[0]['id']
                cur.insert("taggings", {
                        "tag_id": tid,
                        "taggable_id": rid,
                        "taggable_type": "Organization"
                        })
    for tab in tabs:
        cur.delete(tab, dso=dso, dso_update='old')

    from shutil import copyfile
    copyfile(target, target_perm)
