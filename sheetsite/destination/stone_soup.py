#!/usr/bin/python

import re
import csv
import json
import os
import time
import sys

import sqlite3 as lite


schema = '''
CREATE TABLE IF NOT EXISTS access_rules (id INTEGER PRIMARY KEY,access_type TEXT);
CREATE TABLE IF NOT EXISTS data_sharing_orgs (id INTEGER PRIMARY KEY,name TEXT,created_at DATETIME,updated_at DATETIME,default_import_plugin_name TEXT);
CREATE TABLE IF NOT EXISTS data_sharing_orgs_taggables (id INTEGER PRIMARY KEY,data_sharing_org_id INTEGER NOT NULL,taggable_id INTEGER NOT NULL,verified INTEGER NOT NULL,created_at DATETIME,updated_at DATETIME,foreign_key_id TEXT,taggable_type TEXT);
CREATE TABLE IF NOT EXISTS data_sharing_orgs_users (data_sharing_org_id INTEGER NOT NULL,user_id INTEGER NOT NULL,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY,name TEXT,physical_address1 TEXT,physical_address2 TEXT,physical_city TEXT,physical_state TEXT,physical_zip TEXT,physical_country TEXT,mailing_address1 TEXT,mailing_address2 TEXT,mailing_city TEXT,mailing_state TEXT,mailing_zip TEXT,mailing_country TEXT,phone1 TEXT,phone2 TEXT,fax TEXT,email TEXT,website TEXT,preferred_contact TEXT,description TEXT,created_at DATETIME,updated_at DATETIME,created_by_id INTEGER,updated_by_id INTEGER,latitude REAL,longitude REAL,distance REAL,member_id INTEGER,prod_serv1 TEXT,prod_serv2 TEXT,prod_serv3 TEXT,support_organization INTEGER,worker_coop INTEGER,producer_coop INTEGER,marketing_coop INTEGER,housing_coop INTEGER,consumer_coop INTEGER,community_land_trust INTEGER,conservation_ag_land_trust INTEGER,alternative_currency INTEGER,intentional_community INTEGER,collective INTEGER,artist_run_center INTEGER,community_center INTEGER,community_development_financial_institution INTEGER,cooperative_financial_institution INTEGER,mutual_aid_self_help_group INTEGER,activist_social_change_organization INTEGER,union_labor_organization INTEGER,government INTEGER,fair_trade_organization INTEGER,network_association INTEGER,non_profit_org INTEGER,esop INTEGER,majority_owned_esop INTEGER,percentage_owned INTEGER,other INTEGER,type_of_other TEXT,naics_code INTEGER,informal INTEGER,cooperative INTEGER,partnership INTEGER,llc INTEGER,s_corporation INTEGER,c_corporation INTEGER,non_profit_corporation_501c3 INTEGER,non_profit_corporation_501c4 INTEGER,non_profit_corporation_other INTEGER,other_type_of_incorp INTEGER,type_of_other_incorp TEXT,have_a_fiscal_sponsor INTEGER,year_founded DATETIME,democratic INTEGER,union_association INTEGER,which_union TEXT);
CREATE TABLE IF NOT EXISTS legal_structures (id INTEGER PRIMARY KEY,name TEXT,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS locations (id INTEGER PRIMARY KEY,taggable_id INTEGER NOT NULL,note TEXT,physical_address1 TEXT,physical_address2 TEXT,physical_city TEXT,physical_state TEXT,physical_zip TEXT,physical_country TEXT,mailing_address1 TEXT,mailing_address2 TEXT,mailing_city TEXT,mailing_state TEXT,mailing_zip TEXT,mailing_country TEXT,latitude REAL,longitude REAL,created_at DATETIME,updated_at DATETIME,mailing_county TEXT,physical_county TEXT,taggable_type TEXT);
CREATE TABLE IF NOT EXISTS member_orgs (id INTEGER PRIMARY KEY,name TEXT,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS member_orgs_organizations (member_org_id INTEGER NOT NULL,organization_id INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS org_types (id INTEGER PRIMARY KEY,name TEXT,description TEXT,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS org_types_organizations (org_type_id INTEGER NOT NULL,organization_id INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS organizations (id INTEGER PRIMARY KEY,name TEXT NOT NULL,description TEXT,created_by_id INTEGER,updated_by_id INTEGER,phone TEXT,fax TEXT,email TEXT,website TEXT,year_founded DATETIME,democratic INTEGER,primary_location_id INTEGER,created_at DATETIME,updated_at DATETIME,legal_structure_id INTEGER,access_rule_id INTEGER NOT NULL,import_notice_sent_at DATETIME,email_response_token TEXT,responded_at DATETIME,response TEXT);
CREATE TABLE IF NOT EXISTS organizations_people (id INTEGER PRIMARY KEY,organization_id INTEGER NOT NULL,person_id INTEGER NOT NULL,role_name TEXT,phone TEXT,email TEXT,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS organizations_sectors (organization_id INTEGER NOT NULL,sector_id INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS organizations_users (organization_id INTEGER NOT NULL,user_id INTEGER NOT NULL,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS people (id INTEGER PRIMARY KEY,firstname TEXT,lastname TEXT,phone_mobile TEXT,phone_home TEXT,fax TEXT,email TEXT,phone_contact_preferred INTEGER,email_contact_preferred INTEGER,created_at DATETIME,updated_at DATETIME,access_rule_id INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS product_services (id INTEGER PRIMARY KEY,name TEXT,organization_id INTEGER,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sectors (id INTEGER PRIMARY KEY,name TEXT,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS tag_contexts (id INTEGER PRIMARY KEY,name TEXT,friendly_name TEXT);
CREATE TABLE IF NOT EXISTS tag_worlds (id INTEGER PRIMARY KEY,name TEXT);
CREATE TABLE IF NOT EXISTS taggings (id INTEGER PRIMARY KEY,tag_id INTEGER,taggable_id INTEGER,taggable_type TEXT,created_at DATETIME);
CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY,name TEXT,root_id INTEGER,root_type TEXT,parent_id INTEGER,effective_id INTEGER,created_at DATETIME,updated_at DATETIME);
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,login TEXT,password TEXT,is_admin INTEGER,created_at DATETIME,last_login DATETIME,person_id INTEGER,update_notifications_enabled INTEGER);
'''


def get_prop(key,rows):
    val = None
    many_versions = False
    for row in rows:
        v = row[key]
        if v != None:
            if val == None:
                val = v
            if v != val:
                many_versions = True
    return val, many_versions

def get_props(keys,rows,first):
    result = {}
    for key in keys:
        val, many_versions = get_prop(key,rows)
        if many_versions and not(first):
            val = None
        result[key] = val
    return result

def get_common_props(rows):
    return get_props(rows[0].keys(),rows,False)

def get_main_props(rows):
    return get_props(rows[0].keys(),rows,True)

def fix_email(email):
    if email==None:
        return email
    email = str(email)
    email = re.sub(r'mailto:','',email)
    return email

def make_org(props):
    organization = {
        'name': props["NAME"],
        'phone': props["PHONE"],
        'email': fix_email(props["EMAIL"]),
        'website': props["WEBSITE"],
        'description': props["GOODS AND SERVICES"],
        'access_rule_id': 1
        }
    return organization

def safe_access(props,key):
    if not(key in props):
        return None
    x = props[key]
    if x == "":
        return None
    return x

def make_loc(props,rid):
    location = {
        'physical_address1': props["Physical Address"],
        'physical_address2': None,
        'physical_city': props["City"],
        'physical_state': props["State"],
        'physical_zip': safe_access(props,"Postal Code"),
        'physical_country': props["Country"],
        'latitude': safe_access(props,"Latitude"),
        'longitude': safe_access(props,"Longitude"),
        'taggable_id': rid,
        'taggable_type': "Organization"
        }
    return location

def insert_hash(cur,tbl,values):
    columns = ', '.join([('"'+v+'"') for v in values.keys()])
    placeholders = ', '.join('?' * len(values))
    sql = 'INSERT INTO {} ({}) VALUES ({})'.format(tbl,columns,placeholders)
    # print(sql)
    # print(values.values())
    cur.execute(sql, list(values.values()))
    return cur.lastrowid

def blanky(x):
    if x == "" or x == None:
        return None
    return x


def write_destination_stone_soup(params, state):

    path = state['path']
    output_file = state['output_file']

    target = os.path.join(path, 'stonesoup.sqlite3')
    state['sqlite_file'] = target

    if os.path.exists(target):
        os.remove(target)
    con = lite.connect(target)
    cur = con.cursor()

    global schema
    cur.executescript(schema)

    ot = insert_hash(cur, "tag_contexts", {
            'name': 'OrgType',
            'friendly_name': 'Organization Type'
            })
    ot = insert_hash(cur, "tags", {
            'name': 'OrgType',
            'root_id': ot,
            'root_type': "TagContext"
            })

    cur.execute('INSERT OR REPLACE INTO access_rules VALUES (1,"PUBLIC");')

    cur.execute('INSERT OR REPLACE INTO data_sharing_orgs (id,name) VALUES (1,?);',
                [params['organization']])

    org_names = []
    orgs = {}

    lol = json.load(open(output_file))["tables"]["directory"]["rows"]

    # collect all locations for each org
    for idx, row in enumerate(lol):
        name = row['NAME']
        if not(name in orgs):
            orgs[name] = []
            org_names.append(name)
        orgs[name].append(row)

    organizations = []

    print("ORG COUNT " + str(len(org_names)))

    for idx, name in enumerate(org_names):
        rows = orgs[name]
        common = get_common_props(rows)
        main = get_main_props(rows)
        print(name + " : " + str(common) + " " + str(len(rows)))
        organization = make_org(common)
        rid = insert_hash(cur, "organizations", organization)
        fid = None
        for row in rows:
            loc = make_loc(row, rid)
            if loc['latitude'] == None:
                loc['latitude'] = blanky(row['Latitude'])
            if loc['longitude'] == None:
                loc['longitude'] = blanky(row['Longitude'])
            if loc['physical_zip'] == None:
                loc['physical_zip'] = blanky(row['Postal Code'])
            fid0 = insert_hash(cur,"locations",loc)
            if fid == None:
                fid = fid0
        cur.execute("UPDATE organizations SET primary_location_id = ? WHERE id = ?",
                    [fid, rid])
        insert_hash(cur,"data_sharing_orgs_taggables",{
                "data_sharing_org_id": 1,
                "taggable_id": rid,
                "taggable_type": "Organization",
                "verified": 1,
                "foreign_key_id": 999
                })
        typ = main["TYPE"]
        if typ:
            v = cur.execute('SELECT id FROM org_types WHERE name = ?',[typ]).fetchall()
            tid = None
            if len(v) == 0:
                tid = insert_hash(cur,"org_types",{
                        'name': typ
                        })
                tid = insert_hash(cur,"tags",{
                        'name': typ,
                        'root_id': tid,
                        'root_type': "OrgType",
                        'parent_id': ot
                        })
            else:
                tid = v[0][0]
                tid = cur.execute('SELECT id FROM tags WHERE root_id = ? AND root_type = "OrgType"',[tid]).fetchall()[0][0]
            insert_hash(cur,"taggings",{
                    "tag_id": tid,
                    "taggable_id": rid,
                    "taggable_type": "Organization"
                    })
        dex = main['Index']
        if dex:
            for dex in [x.strip() for x in dex.lower().split(',')]:
                v = cur.execute('SELECT id FROM tags WHERE name = ?',[dex]).fetchall()
                tid = None
                if len(v) == 0:
                    tid = insert_hash(cur,"tags",{
                            'name': dex
                            })
                else:
                    tid = v[0][0]
                insert_hash(cur,"taggings",{
                        "tag_id": tid,
                        "taggable_id": rid,
                        "taggable_type": "Organization"
                        })

    with open('junk.json', 'w') as outfile:
      json.dump(organizations, outfile)

    con.commit()
    con.close()

