#!/usr/bin/python

from contextlib import contextmanager
import dataset
from datetime import date, datetime
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


def as_year(when):
    if when is None:
        return when
    when = str(when)
    when = when.replace('.', ' ')
    when = when.replace('-', ' ')
    when = when.replace('/', ' ')
    parts = when.split(' ')
    for part in parts:
        if len(part) == 4 and re.match('^[0-9]{4}$', part):
            return date(int(part), 1, 1)
    return None


def fix_website(x):
    if x is None:
        return x
    x = x.strip()
    x = x.split(' ')
    if len(x) == 0:
        return None
    return x[0]


def make_org(props):
    organization = {
        'name': anykey(props, "NAME", "CompanyName"),
        'phone': anykey(props, "PHONE", "WorkPhone"),
        'email': fix_email(anykey(props, "EMAIL", "Email Address")),
        'website': fix_website(anykey(props, "WEBSITE", "Web Address", None)),
        'description': anykey(props, "GOODS AND SERVICES", "Description", None),
        'year_founded': as_year(anykey(props, "year_founded", "year founded", None)),
        'access_rule_id': 1
        }
    if 'stamp' in props:
        if props['stamp'] is not None:
            organization['updated_at'] = date(int(props['stamp']), 1, 1)
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

    def index(self, tbl, columns):
        return self.cur[tbl].create_index(columns)

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
        vs = dict((k, values[k]) for k in keys)
        return self.cur[tbl].find_one(**vs)['id']

    def find(self, tbl, **conds):
        return self.cur[tbl].find(**conds)

    def find_one(self, tbl, **conds):
        return self.cur[tbl].find_one(**conds)

    @contextmanager
    def transaction(self):
        with self.cur as x:
            yield DirectToDB(x)

def is_blank(x):
    return x is None or x == ""

def blanky(x):
    if x == "" or x is None:
        return None
    return x


def floaty(x):
    if x is None or x == "":
        return None
    return float(x)


class TargetDB(object):

    def __init__(self, target_db):
        cur = DirectToDB(target_db)
        cur.upsert("tag_contexts", {
            'name': 'OrgType',
            'friendly_name': 'Organization Type'
        }, ['name'])
        cur.upsert("tag_contexts", {
            'name': 'MemberOrg',
            'friendly_name': 'Member Organization Affiliation'
        }, ['name'])
        cur.upsert("tag_contexts", {
            'name': 'Sector',
            'friendly_name': 'Business Sector'
        }, ['name'])
        cur.upsert("tag_contexts", {
            'name': 'LegalStructure',
            'friendly_name': 'Legal Structure'
        }, ['name'])
        dcc = cur.upsert("tags", {
            'name': 'dcc',
            'root_id': 1,
            'root_type': "TagWorld"
        }, ['name'])
        for name in ['OrgType', 'Sector', 'MemberOrg', 'LegalStructure']:
            cur.upsert("tags", {
                'name': name,
                'root_id': cur.find_one('tag_contexts', name=name)['id'],
                'root_type': "TagContext",
                'parent_id': dcc
            }, ['name'])
        self.ot = cur.find_one("tags", name='OrgType')['id']
        cur.upsert("tag_worlds", {
            'name': 'dcc',
        }, ['name'])

        cur.column('users', 'login', 'x')
        cur.column('users', 'password', 'x')
        cur.column('users', 'is_admin', 1)
        cur.column('users', 'person_id', 1)
        cur.column('users', 'last_login', datetime.now())
        cur.column('organizations', 'grouping', 'x')
        cur.column('locations', 'mailing_address1', 'x')
        cur.column('locations', 'mailing_address2', 'x')
        cur.column('locations', 'mailing_city', 'x')
        cur.column('locations', 'mailing_state', 'x')
        cur.column('locations', 'mailing_zip', 'x')
        cur.column('locations', 'mailing_country', 'x')
        cur.column('locations', 'mailing_county', 'x')
        cur.column('locations', 'physical_zip', 'x')
        cur.column('locations', 'physical_county', 'x')
        for tab in ['organizations', 'locations']:
            cur.column(tab, 'dccid', 'x')
            cur.column(tab, 'created_at', datetime.now())
            cur.column(tab, 'updated_at', datetime.now())
        cur.column('people', 'firstname', 'x')
        cur.column('people', 'lastname', 'x')
        cur.column('people', 'updated_at', datetime.now())
        cur.column('organizations_people', 'person_id', 1)
        cur.column('organizations_people', 'organization_id', 1)
        cur.column('tags', 'effective_id', 1)
        cur.column('locations', 'note', 'x')
        cur.column('organizations', 'fax', 'x')
        cur.column('organizations', 'year_founded', datetime.now())
        cur.column('product_services', 'name', 'x')
        cur.column('product_services', 'organization_id', 1)
        cur.column('organizations_users', 'user_id', 1)
        cur.column('organizations_users', 'organization_id', 1)
        cur.column('users', 'login', 'x')

        cur.column('access_rules', 'access_type', 'PUBLIC')
        cur.upsert('access_rules', {'id': 1, 'access_type': 'PUBLIC'}, ['id'])

        cur.column('data_sharing_orgs', 'name', 'x')

        cur.column('data_sharing_orgs_users', 'user_id', 1)
        cur.column('data_sharing_orgs_users', 'data_sharing_org_id', 1)

        cur.column('member_orgs_organizations', 'member_org_id', 1)
        cur.column('member_orgs_organizations', 'organization_id', 1)

        cur.column('org_types_organizations', 'org_type_id', 1)
        cur.column('org_types_organizations', 'organization_id', 1)

        cur.column('organizations_sectors', 'sector_id', 1)
        cur.column('organizations_sectors', 'organization_id', 1)

        cur.column('member_orgs', 'name', 'x')

        cur.column('sectors', 'name', 'x')

        cur.column('taggings', 'tag_id', 1)
        cur.column('taggings', 'taggable_id', 1)
        cur.column('taggings', 'taggable_type', 'x')

        cur.column('data_sharing_orgs_taggables', 'data_sharing_org_id', 1)
        cur.column('data_sharing_orgs_taggables', 'taggable_id', 1)
        cur.column('data_sharing_orgs_taggables', 'taggable_type', 'x')
        cur.column('data_sharing_orgs_taggables', 'verified', 1)

        cur.index('locations', ['taggable_id', 'taggable_type'])
        cur.index('product_services', ['organization_id'])
        cur.index('organizations_sectors', ['organization_id'])
        cur.index('organizations_sectors', ['sector_id'])
        cur.index('organizations_people', ['organization_id'])
        cur.index('organizations_people', ['person_id'])
        cur.index('tags', ['name'])
        cur.index('tags', ['root_id', 'root_type'])
        cur.index('tags', ['parent_id'])
        cur.index('taggings', ['tag_id'])
        cur.index('taggings', ['taggable_id', 'taggable_type'])
        cur.index('tag_contexts', ['name'])
        cur.index('tag_worlds', ['name'])
        cur.index('data_sharing_orgs_taggables', ['data_sharing_org_id'])
        cur.index('data_sharing_orgs_taggables', ['taggable_type'])
        cur.index('data_sharing_orgs_taggables', ['taggable_id', 'taggable_type'])

        self.cur = cur

    def get_org_type(self):
        return self.ot

    def set_name(self, name):
        cur = self.cur
        dso = name
        dso_id = cur.upsert('data_sharing_orgs',
                            {'name': name},
                            ['name'])
        self.dso = dso
        self.dso_id = dso_id
        tabs = ['locations', 'organizations', 'taggings',
                'data_sharing_orgs_taggables',
                'data_sharing_orgs']

        def prep(tab):
            cur.column(tab, 'dso', 'x')
            cur.column(tab, 'dso_update', 'x')
            cur.update(tab, {
                'dso': dso,
                'dso_update': 'old'
            }, ['dso'])
        for tab in tabs:
            prep(tab)
        self.tabs = tabs

    def clear(self):
        for tab in self.tabs:
            self.cur.delete(tab, dso=self.dso, dso_update='old')


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

    tdb = TargetDB(dataset.connect("sqlite:///" + target))
    cur = tdb.cur
    tdb.set_name(params['organization'])
    dso = tdb.dso
    dso_id = tdb.dso_id
    ot = tdb.get_org_type()

    org_names = []
    orgs = {}

    print("READING", output_file)
    tables = json.load(open(output_file))
    selection = tables['names'][0]
    lol = tables['tables'][selection]["rows"]

    # collect all locations for each org
    for idx, row in tqdm(list(enumerate(lol))):
        name = anykey(row, 'row_group', 'NAME', 'CompanyName')
        if not(name in orgs):
            orgs[name] = []
            org_names.append(name)
        orgs[name].append(row)

    print("ORG COUNT " + str(len(org_names)))

    for idx, name in tqdm(list(enumerate(org_names))):
        rows = orgs[name]
        print("Org {} / {} has {} rows".format(idx, name, len(rows)))
        lct = 0
        for row in rows:
            loc = make_loc(row, None)
            if not(is_blank(loc['physical_state']) and is_blank(loc['physical_country'])
                    and is_blank(loc['physical_address1'])):
                lct += 1
        if lct == 0:
            continue
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
            else:
                tid = v[0]['id']
            nid = cur.find_one('tags', root_id=tid, root_type='OrgType')
            if nid is None:
                tid = cur.insert("tags", {
                        'name': typ,
                        'root_id': tid,
                        'root_type': "OrgType",
                        'parent_id': ot
                        })
            else:
                tid = nid['id']
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
                    "taggable_type": "Organization",
                    "dso": dso,
                    "dso_update": "fresh"
                })

    tdb.clear()

    from shutil import copyfile
    copyfile(target, target_perm)


def apply_direct(target_db, name, source_db):
    tdb = TargetDB(target_db)
    tdb.set_name(name)

    oids = {}
    pids = {}

    types = {}

    caps = {
        'OrgType': 'org_types',
        'Sector': 'sectors',
        'LegalStructure': 'legal_structures',
        'MemberOrg': 'member_orgs',
        'TagContext': 'tag_contexts'
    }

    dsos = {}

    # add dsos
    with tdb.cur.transaction() as cur:
        print('dsos')
        for rec in tqdm(list(source_db['data_sharing_orgs'].all())):
            fid = rec['id']
            dccid = '{}_{}_{}'.format(name, 'DSO', fid)
            rec['dccid'] = dccid
            rec['dso'] = name
            rec['dso_update'] = 'fresh'
            rec.pop('id')
            oid = cur.upsert("data_sharing_orgs", rec, ['dccid'])
            dsos[fid] = oid

    # add types
    for k in ['org_types', 'sectors', 'legal_structures', 'member_orgs', 'tag_contexts']:
        print(k)
        ts = types[k] = {}
        with tdb.cur.transaction() as cur:
            for rec in tqdm(list(source_db[k].all())):
                fid = rec.pop('id')
                tid = cur.upsert(k, rec, ['name'])
                ts[fid] = tid

    # add organizations
    with tdb.cur.transaction() as cur:
        print('organizations')
        for org in tqdm(list(source_db['organizations'].all())):
            fid = org['id']
            dccid = '{}_{}_{}'.format(name, 'Organization', fid)
            org['dccid'] = dccid
            org['dso'] = name
            org['dso_update'] = 'fresh'
            pids[org['primary_location_id']] = fid
            org.pop('id')
            org.pop('created_by_id')
            org.pop('updated_by_id')
            org.pop('primary_location_id')
            org.pop('legal_structure_id')
            org.pop('access_rule_id')
            org['access_rule_id'] = 1
            oid = cur.upsert("organizations", org, ['dccid'])
            oids[fid] = oid

    # add locations
    with tdb.cur.transaction() as cur:
        print('locations')
        for org in tqdm(list(source_db['locations'].all())):
            fid = org['id']
            dccid = '{}_{}_{}'.format(name, 'Location', fid)
            org['dccid'] = dccid
            org['dso'] = name
            org['dso_update'] = 'fresh'
            org.pop('id')
            if org['taggable_type'] != 'Organization':
                continue
            org['taggable_id'] = oids[org['taggable_id']]
            oid = cur.upsert("locations", org, ['dccid'])
            pid = pids.get(fid)
            if pid is not None:
                cur.update("organizations", {
                    'primary_location_id': oid,
                    'id': oids[pid]
                }, ['id'])

    tids = {}

    # add tags
    with tdb.cur.transaction() as cur:
        print('tags')
        for rec in tqdm(list(source_db['tags'].all())):
            fid = rec.pop('id')
            rtype = rec['root_type']
            rid = rec['root_id']
            if rtype in caps:
                rtypes = types[caps[rtype]]
                rid = rtypes[rid]
                rec['root_id'] = rid
            else:
                rec.pop('root_id')
                rec.pop('root_type')
            pid = rec['parent_id']
            rec.pop('parent_id')
            if pid is not None:
                if pid in tids:
                    rec['parent_id'] = tids[pid]
            rec.pop('effective_id')
            tid = cur.upsert("tags", rec, ['name'])
            tids[fid] = tid

    # add taggings
    ct = 0
    goods = 0
    with tdb.cur.transaction() as cur:
        print('taggings')
        for rec in tqdm(list(source_db['taggings'].all())):
            if rec['taggable_type'] != 'Organization':
                continue
            ct += 1
            if rec['taggable_id'] is None:
                continue
            if rec['tag_id'] is None:
                continue
            fid = rec['id']
            dccid = '{}_{}_{}'.format(name, 'Taggings', fid)
            rec['dccid'] = dccid
            rec.pop('id')
            tid = rec['tag_id']
            if tid not in tids:
                continue
            rec['tag_id'] = tids[tid]
            oid = rec['taggable_id']
            if oid not in oids:
                continue
            rec['taggable_id'] = oids[oid]
            rec['dso'] = name
            rec['dso_update'] = 'fresh'
            cur.upsert("taggings", rec, ['dccid'])
            goods += 1
    print("taggings {} of which {} good".format(ct, goods))

    # add dso_taggables
    with tdb.cur.transaction() as cur:
        print('dso_taggables')
        for rec in tqdm(list(source_db['data_sharing_orgs_taggables'].all())):
            fid = rec['id']
            dccid = '{}_{}_{}'.format(name, 'DSO_taggables', fid)
            rec['dccid'] = dccid
            rec['dso'] = name
            rec['dso_update'] = 'fresh'
            rec.pop('id')
            did = rec['data_sharing_org_id']
            if did not in dsos:
                continue
            rec['data_sharing_org_id'] = dsos[did]
            if rec['taggable_type'] != 'Organization':
                continue
            tid = rec['taggable_id']
            if tid not in oids:
                continue
            rec['taggable_id'] = oids[tid]
            oid = cur.upsert("data_sharing_orgs_taggables", rec, ['dccid'])
            dsos[fid] = oid


    tdb.clear()


if __name__ == '__main__':
    import sys
    target = sys.argv[1]
    name = sys.argv[2]
    source = sys.argv[3]
    target_db = dataset.connect('sqlite:///' + target)
    source_db = dataset.connect('sqlite:///' + source)
    apply_direct(target_db, name, source_db)
