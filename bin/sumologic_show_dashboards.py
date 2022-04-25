#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exaplanation: sumologic_show_dashboards: extract out your content folders into a file system

Usage:
   $ python  sumologic_show_dashboards [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           sumologic_show_dashboards
    @version        2.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   Apache 2.0
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 2.00
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

### beginning ###
import json
import csv
import os
import sys
import time
import datetime
import argparse
import configparser
import http
import pandas
import requests
sys.dont_write_bytecode = 1

MY_CFG = 'undefined'
PARSER = argparse.ArgumentParser(description="""
sumologic_show_dashboards shows all of the dashboards and their OID
""")

PARSER.add_argument("-a", metavar='<secret>', dest='MY_SECRET', \
                    help="set api (format: <key>:<secret>) ")

PARSER.add_argument("-k", metavar='<client>', dest='MY_CLIENT', \
                    help="set key (format: <site>_<orgid>) ")

PARSER.add_argument("-c", metavar='<cfg>', dest='CONFIG', \
                    help="Specify config file")

PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="increase verbosity")

ARGS = PARSER.parse_args(args=None if sys.argv[1:] else ['--help'])

def resolve_option_variables():
    """
    Validates and confirms all necessary variables for the script
    """

    if ARGS.MY_SECRET:
        (keyname, keysecret) = ARGS.MY_SECRET.split(':')
        os.environ['SUMO_UID'] = keyname
        os.environ['SUMO_KEY'] = keysecret

    if ARGS.MY_CLIENT:
        (deployment, organizationid) = ARGS.MY_CLIENT.split('_')
        os.environ['SUMO_LOC'] = deployment
        os.environ['SUMO_ORG'] = organizationid

def resolve_config_variables():
    """
    Validates and confirms all necessary variables for the script
    """

    if ARGS.CONFIG:
        cfgfile = os.path.abspath(ARGS.CONFIG)
        configobj = configparser.ConfigParser()
        configobj.optionxform = str
        configobj.read(cfgfile)

        if ARGS.verbose > 8:
            print('Displaying Config Contents:')
            print(dict(configobj.items('Default')))

        if configobj.has_option("Default", "SUMO_TAG"):
            os.environ['SUMO_TAG'] = configobj.get("Default", "SUMO_TAG")

        if configobj.has_option("Default", "SUMO_UID"):
            os.environ['SUMO_UID'] = configobj.get("Default", "SUMO_UID")

        if configobj.has_option("Default", "SUMO_KEY"):
            os.environ['SUMO_KEY'] = configobj.get("Default", "SUMO_KEY")

        if configobj.has_option("Default", "SUMO_LOC"):
            os.environ['SUMO_LOC'] = configobj.get("Default", "SUMO_LOC")

        if configobj.has_option("Default", "SUMO_END"):
            os.environ['SUMO_END'] = configobj.get("Default", "SUMO_END")

        if configobj.has_option("Default", "SUMO_ORG"):
            os.environ['SUMO_ORG'] = configobj.get("Default", "SUMO_ORG")

def initialize_variables():
    """
    Validates and confirms all necessary variables for the script
    """

    resolve_option_variables()

    resolve_config_variables()

    try:
        my_uid = os.environ['SUMO_UID']
        my_key = os.environ['SUMO_KEY']

    except KeyError as myerror:
        print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

    return my_uid, my_key

( sumo_uid, sumo_key ) = initialize_variables()

try:
    SUMO_UID = os.environ['SUMO_UID']
    SUMO_KEY = os.environ['SUMO_KEY']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

DELAY_TIME = .2

CONTENTMAP = dict()

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
    source = SumoApiClient(sumo_uid, sumo_key)

    print("uid_myself,uid_parent,dashboard_id,my_name")

    dashboard_output = source.list_dashboards()
    for dashboard_item in dashboard_output['dashboards']:
        myself_oid = dashboard_item['contentId']
        parent_oid = dashboard_item['folderId']
        myname = dashboard_item['title']
        dashboard_id = dashboard_item['id']
        print('{},{},{},{}'.format(myself_oid, parent_oid, dashboard_id, myname))

### class ###
class SumoApiClient():
    """
    This is defined SumoLogic API Client
    The class includes the HTTP methods, cmdlets, and init methods
    """

    def __init__(self, access_id, access_key, endpoint=None, cookieFile='cookies.txt'):
        """
        Initializes the Sumo Logic object
        """
        self.session = requests.Session()
        self.session.auth = (access_id, access_key)
        self.session.headers = {'content-type': 'application/json', \
            'accept': 'application/json'}
        cookiejar = http.cookiejar.FileCookieJar(cookieFile)
        self.session.cookies = cookiejar
        if endpoint is None:
            self.apipoint = self._get_endpoint()
        elif len(endpoint) < 3:
            self.apipoint = 'https://api.' + endpoint + '.sumologic.com/api'
        else:
            self.apipoint = endpoint
        if self.apipoint[-1:] == "/":
            raise Exception("Endpoint should not end with a slash character")

    def _get_endpoint(self):
        """
        SumoLogic REST API endpoint changes based on the geo location of the client.
        It contacts the default REST endpoint and resolves the 401 to get the right endpoint.
        """
        self.endpoint = 'https://api.sumologic.com/api'
        self.response = self.session.get('https://api.sumologic.com/api/v1/collectors')
        endpoint = self.response.url.replace('/v1/collectors', '')
        return endpoint

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

    def post(self, method, data=None, headers=None, params=None):
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

    def export_content_results(self, myself, myjobid):
        """
        This should get the results
        """
        url = "/v2/content/" + str(myself) + "/export/" + str(myjobid) + "/result"
        body = self.get(url).text
        results = json.loads(body)
        time.sleep(DELAY_TIME)
        return results

    def export_content_status(self, myself, myjobid):
        """
        This should get the status
        """
        url = "/v2/content/" + str(myself) + "/export/" + str(myjobid) + "/status"
        body = self.get(url).text
        results = json.loads(body)
        time.sleep(DELAY_TIME)
        return results

    def list_dashboards(self):
        """
        Show all of the dashboards
        """
        url = "/v2/dashboards"
        body = self.get(url).text
        results = json.loads(body)
        time.sleep(DELAY_TIME)
        return results

    def list_dashboard(self, myself):
        """
        Show all of the dashboards
        """
        url = "/v2/dashboards/" + str(myself)
        body = self.get(url).text
        results = json.loads(body)
        time.sleep(DELAY_TIME)
        return results

    def export_content(self, myself):
        """
        Launch an export job. This should return a JOBID.
        """
        url = "/v2/content/" + str(myself) + "/export"
        body = self.post(url).text
        results = json.loads(body)
        time.sleep(DELAY_TIME)
        return results

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

    def get_globalfolders(self):
        """
        Using an HTTP client, this uses a GET to retrieve all connection information.
        """
        url = "/v2/content/folders/global"
        body = self.get(url).text
        results = json.loads(body)
        return results

    def get_globalfolder(self, myself):
        """
        Using an HTTP client, this uses a GET to retrieve single connection information.
        """
        url = "/v2/content/folders/global/" + str(myself)
        body = self.get(url).text
        results = json.loads(body)
        return results

### methods ###

if __name__ == '__main__':
    main()
