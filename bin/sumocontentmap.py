#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exaplanation: sumocontent: an easy way to get all of the content in your personal folder

Usage:
   $ python  sumocontent  [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           sumocontentmap
    @version        1.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   Apache 2.0
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 1.00
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

### beginning ###
import json
import csv
import os
import sys
import time
import datetime
import argparse
import http
import requests
sys.dont_write_bytecode = 1

MY_CFG = 'undefined'
PARSER = argparse.ArgumentParser(description="""
sumocontentmap prints out a map of all content you have in your personal folder
""")

PARSER.add_argument("-a", metavar='<secret>', dest='MY_SECRET', \
                    help="set api (format: <key>:<secret>) ")
PARSER.add_argument("-k", metavar='<client>', dest='MY_CLIENT', \
                    help="set key (format: <site>_<orgid>) ")
PARSER.add_argument("-e", metavar='<endpoint>', dest='MY_ENDPOINT', \
                    help="set endpoint (format: <endpoint>) ")
PARSER.add_argument("-c", metavar='<cfg>', dest='cfgfile', \
                    help="Specify config file")
PARSER.add_argument("-f", metavar='<fmt>', default="stdout", dest='oformat', \
                    help="Specify output format (default = stdout )")

ARGS = PARSER.parse_args()

if ARGS.MY_SECRET:
    (MY_APINAME, MY_APISECRET) = ARGS.MY_SECRET.split(':')
    os.environ['SUMO_UID'] = MY_APINAME
    os.environ['SUMO_KEY'] = MY_APISECRET

if ARGS.MY_CLIENT:
    (MY_DEPLOYMENT, MY_ORGID) = ARGS.MY_CLIENT.split('_')
    os.environ['SUMO_LOC'] = MY_DEPLOYMENT
    os.environ['SUMO_ORG'] = MY_ORGID
    os.environ['SUMO_TAG'] = ARGS.MY_CLIENT

if ARGS.MY_ENDPOINT:
    os.environ['SUMO_END'] = ARGS.MY_ENDPOINT
else:
    os.environ['SUMO_END'] = os.environ['SUMO_LOC']

try:
    SUMO_UID = os.environ['SUMO_UID']
    SUMO_KEY = os.environ['SUMO_KEY']
    SUMO_LOC = os.environ['SUMO_LOC']
    SUMO_ORG = os.environ['SUMO_ORG']
    SUMO_END = os.environ['SUMO_END']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

DELAY_TIME = .2

CONTENTMAP = dict()

OFORMAT = ARGS.oformat

CACHEDIR  = '/var/tmp'

FILETAG = 'contentmap'

RIGHTNOW = datetime.datetime.now()

DATESTAMP = RIGHTNOW.strftime('%Y%m%d')

TIMESTAMP = RIGHTNOW.strftime('%H%M%S')

### beginning ###

def main():
    """
    Setup the Sumo API connection, using the required tuple of region, id, and key.
    Once done, then issue the command required
    """
    source = SumoApiClient(SUMO_UID, SUMO_KEY, SUMO_END)
    run_sumo_cmdlet(source)

def build_details(source, parent_name, child):
    """
    Build the details for the client entry. If a folder recurse
    """

    my_name = child['name']
    my_path_list = ( parent_name, my_name )
    my_path_name = '/'.join(my_path_list)
    my_type = child['itemType']

    uid_myself = child['id']
    uid_parent = child['parentId']

    if my_type == "Folder":
        content_list = source.get_myfolder(uid_myself)
        for content_child in content_list['children']:
            build_details(source, my_path_name, content_child)

    CONTENTMAP[uid_myself] = dict()
    CONTENTMAP[uid_myself]["parent"] = uid_parent
    CONTENTMAP[uid_myself]["myself"] = uid_myself
    CONTENTMAP[uid_myself]["name"] = my_name
    CONTENTMAP[uid_myself]["path"] = my_path_name
    CONTENTMAP[uid_myself]["type"] = my_type

def create_output():
    """
    Now construct the output we want from the CONTENTMAP data structure we made.
    sample format is JSON or CSV ; outputs sampls might be source category, file, and stdout
    """

    if OFORMAT != "stdout":
        outputname = '.'.join([FILETAG, DATESTAMP, TIMESTAMP, OFORMAT])
        outputfile = os.path.join(CACHEDIR, outputname)

    if OFORMAT == "stdout":
        print('{},{},{},{},{}'.format("uid_myself", "uid_parent", "my_type", "my_name", "my_path"))

    if OFORMAT == "csv":
        csvfileobject = csv.writer(open(outputfile, "w"))
        csvfileobject.writerow(["uid_myself", "uid_parent", "my_type", "my_name", "my_path"])

    for content_item in CONTENTMAP:
        uid_parent = CONTENTMAP[content_item]["parent"]
        uid_myself = CONTENTMAP[content_item]["myself"]
        my_name = CONTENTMAP[content_item]["name"]
        my_path = CONTENTMAP[content_item]["path"]
        my_type = CONTENTMAP[content_item]["type"]

        if OFORMAT == "csv":
            csvfileobject.writerow([uid_myself, uid_parent, my_type, my_name, my_path])

        if OFORMAT == "stdout":
            print('{},{},{},{},{}'.format(uid_myself, uid_parent, my_type, my_name, my_path))

    if OFORMAT == "json":
        with open(outputfile, 'w') as jsonfile:
            json.dump(CONTENTMAP, jsonfile)

def run_sumo_cmdlet(source):
    """
    This will collect the information on object for sumologic and then collect that into a list.
    the output of the action will provide a tuple of the orgid, objecttype, and id
    """
    contentlist = dict()
    contentlist[SUMO_ORG] = dict()
    parent_name = "/Personal"

    content_list = source.get_myfolders()
    for child in content_list['children']:
        build_details(source, parent_name, child)

    create_output()

### class ###
class SumoApiClient():
    """
    This is defined SumoLogic API Client
    The class includes the HTTP methods, cmdlets, and init methods
    """

    def __init__(self, access_id, access_key, region, cookieFile='cookies.txt'):
        """
        Initializes the Sumo Logic object
        """
        self.session = requests.Session()
        self.session.auth = (access_id, access_key)
        self.session.headers = {'content-type': 'application/json', \
            'accept': 'application/json'}
        self.apipoint = 'https://api.' + region + '.sumologic.com/api'
        cookiejar = http.cookiejar.FileCookieJar(cookieFile)
        self.session.cookies = cookiejar

    def delete(self, method, params=None, headers=None, data=None):
        """
        Defines a Sumo Logic Delete operation
        """
        response = self.session.delete(self.apipoint + method, \
            params=params, headers=headers, data=data)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def get(self, method, params=None, headers=None):
        """
        Defines a Sumo Logic Get operation
        """
        response = self.session.get(self.apipoint + method, \
            params=params, headers=headers)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def post(self, method, data, headers=None, params=None):
        """
        Defines a Sumo Logic Post operation
        """
        response = self.session.post(self.apipoint + method, \
            data=json.dumps(data), headers=headers, params=params)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def put(self, method, data, headers=None, params=None):
        """
        Defines a Sumo Logic Put operation
        """
        response = self.session.put(self.apipoint + method, \
            data=json.dumps(data), headers=headers, params=params)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

### class ###
### methods ###

    def get_myfolders(self):
        """
        Using an HTTP client, this uses a GET to retrieve all connection information.
        """
        url = "/v2/content/folders/personal/"
        body = self.get(url).text
        results = json.loads(body)
        return results

    def get_myfolder(self, myself):
        """
        Using an HTTP client, this uses a GET to retrieve single connection information.
        """
        url = "/v2/content/folders/" + str(myself)
        body = self.get(url).text
        results = json.loads(body)
        time.sleep(DELAY_TIME)
        return results

### methods ###

if __name__ == '__main__':
    main()
