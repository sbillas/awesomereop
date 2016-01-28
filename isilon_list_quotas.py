#!/usr/bin/env python

# The following sample code shows how to access the OneFS API for file system
# configuration with python. This sample includes a ConfigAPISession class
# for session-based authentication.

# You can modify this sample code for your own use by replacing HOST, USER, and
# PASSWORD below with the IP address or hostname of your cluster and with
# appropriate account credentials for your cluster.

import httplib
import json
import base64
import string
import sys
import traceback

# IN A REAL APPLICATION STORE USER & PASSWORD SECURELY.
HOST = '10.64.188.130'
USER = 'root'
PASSWORD = '1s1l0n'
PORT = 8080
API_VERSION = '1'

# URIs used below.
SESSION_URI = '/session/' + API_VERSION + '/session'
SNAPSHOTS_URI = '/' + API_VERSION + '/snapshot/snapshots'
QUOTAS_URI = '/' + API_VERSION + '/quota/quotas'
NFS_EXPORTS_URI = '/' + API_VERSION + '/protocols/nfs/exports'
PRIVS_DOC_URI = '/' + API_VERSION + '/auth/privileges?describe'
PRIVS_JSON_URI = '/' + API_VERSION + '/auth/privileges?describe&json'
RESOURCE_LIST_URI = '/?describe&list&all'
STATISTICS_URI = '/session/' + API_VERSION + 'statistics/current'

# The following utility class starts and ends OneFS API sessions. This class
# enables you to store a cookie with a session ID for authentication instead of
# sending your username and password with every request, as with HTTP Basic
# Authentication.
class ConfigAPISession():
    def __init__(self):
        isisessid = None

    # Parse isisessid (the OneFS session ID) from the session URI response
    # headers.
    @staticmethod
    def extract_session_id(response_headers):
        isisessid = None
        cookie_header = None
        for h in response_headers:
            if h[0].lower() == "set-cookie":
                cookie_header = h[1]
            if cookie_header:
                cookie_strs = cookie_header.split(';')
                for cs in cookie_strs:
                    nv = cs.split('=')

                    if len(nv) > 1:
                        if nv[0].strip().lower() == 'isisessid':
                            isisessid = nv[1].strip()
        return isisessid

    # Create a new session by querying the session URI with your
    # log in credentials.
    @staticmethod
    def create_session():
        api_session = ConfigAPISession()

        headers = {'content-type': 'application/json'}
        headers['Authorization'] = 'Basic ' + string.strip(
            base64.encodestring(USER + ':' + PASSWORD))

        body = json.dumps({'username': USER, 'password': PASSWORD,
            'services': ['platform', 'namespace']})

        uri = SESSION_URI

        connection = httplib.HTTPSConnection(HOST, PORT)
        connection.connect()

        try:
            connection.request('POST', uri, body, headers)
            response = connection.getresponse()
            api_session.isisessid = ConfigAPISession.extract_session_id(
                response.getheaders())
        except Exception, e:
            print e
            connection.close()
        except httplib.BadStatusLine, e:
            print e
            connection.close()

        return api_session

    # End your session with a DELETE request to the session URI.
    def close_session(self):
        uri = SESSION_URI
        headers = {}
        headers['Cookie'] = 'isisessid=' + self.isisessid

        connection = httplib.HTTPSConnection(HOST, PORT)
        connection.connect()

        try:
            connection.request('DELETE', uri, '', headers)
            response = connection.getresponse()
        except Exception, e:
            print e
            connection.close()
        except httplib.BadStatusLine, e:
            print e
            connection.close()

        self.isisessid = None

    def send_request(self, method, uri, headers, body):
        response = None
        headers['Cookie'] = 'isisessid=' + str(self.isisessid)
        uri = '/platform' + uri

        connection = httplib.HTTPSConnection(HOST, PORT)
        connection.connect()

        try:
            connection.request(method, uri, body, headers)
            response = connection.getresponse()
        except Exception, e:
            print e
            connection.close()
        except httplib.BadStatusLine, e:
            print e
            connection.close()

        return response

def print_errors(response_json):
    if response_json.has_key('errors'):
        errors = response_json['errors']
        for e in errors:
            print e['message']

def send_request_and_validate(api_session, method, uri, headers, body):
    response = api_session.send_request(method, uri, headers, body)
    response_body = response.read()

    response_json = None
    if response_body != None and response_body != '':
        response_json = json.loads(response_body)

    # The status code must be set to 2XX, otherwise an error will occur.
    if response.status < 200 or response.status >= 300:
        print "Error:", response.status, method, uri
        if response_json != None:
            print_errors(response_json)
            raise Exception("Response status: " + str(response.status))

    return response_json

def main():
    api_session = ConfigAPISession.create_session()

    try:
        # The following examples are about quotas.
        # The user sending the request must have the
        # ISI_PRIV_QUOTA privilege.
        print
        print "Quota example"
        print
        collection_uri = QUOTAS_URI
        # List notifications
#         response_json = send_request_and_validate(api_session, 'GET',
#             collection_uri, {}, '')
          
            
        quota_id = "/e3LnAwEAAADSBwAAAAAAEAQAAAAAAAAA/notifications"
        post_body = {
            'action_alert': True,
            'condition': 'exceeded',
            'threshold': 'advisory',
            'holdoff': 60,
        }    
        print "Changing notifitaions of quota e3LnAwEAAADSBwAAAAAAEAQAAAAAAAAA"
        response_json = send_request_and_validate(api_session, 'POST',
            collection_uri + quota_id, {}, json.dumps(post_body))  
              
            
        # List all quotas
# 	print "Listing all quotas:"
#         print json.dumps(response_json, indent=4, sort_keys=True)
# 
#         print response_json["quotas"]
#         for k in range(len(response_json["quotas"])):
#                 if response_json["quotas"][k]["type"] == "user":
#                     if response_json["quotas"][k]["path"]:
#                         path = response_json["quotas"][k]["path"]
#                     else:
#                        path = "None"
#                     if response_json["quotas"][k]["persona"]:    
#                         user = response_json["quotas"][k]["persona"]["id"]
#                     else:
#                         user = "None"
#                     usage = response_json["quotas"][k]["usage"]["logical"]
#                     print user, path, usage 
    except:
        traceback.print_exc(file=sys.stdout)


    api_session.close_session()

if __name__ == "__main__":
    main()

