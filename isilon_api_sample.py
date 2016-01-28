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
        # The following examples are about snapshots.
        # The user sending the request must have the
        # ISI_PRIV_SNAPSHOT privilege.
        print
        print "Snapshot example"
        print
        collection_uri = SNAPSHOTS_URI

        # List all snapshots
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all snapshots:"
        print json.dumps(response_json, indent=4, sort_keys=True)

        # Create a new snapshot for the /ifs/data path. This example assumes
        # that the /ifs/data path exists on your system).
        post_body = {'name': 'example_snapshot', 'path': '/ifs/data'}
        response_json = send_request_and_validate(api_session, 'POST',
            collection_uri, {}, json.dumps(post_body))

	# The ID of the new object is returned on a successful create.
        item_id = response_json['id']
        item_uri = collection_uri + '/' + str(item_id)
        print "Successfully created snapshot with id:", item_id

        # List all snapshots
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all snapshots:"
        print json.dumps(response_json, indent=4, sort_keys=True)

        # DELETE a snapshot
        response_json = send_request_and_validate(api_session, 'DELETE',
            item_uri, {}, '')
        print "Deleted the snapshot."

        # List all snapshots
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all snapshots:"
        print json.dumps(response_json, indent=4, sort_keys=True)
    except:
        traceback.print_exc(file=sys.stdout)

    try:
        # The following examples are about quotas.
        # The user sending the request must have the
        # ISI_PRIV_QUOTA privilege.
        print
        print "Quota example"
        print
        collection_uri = QUOTAS_URI

        # List all quotas
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all quotas:"
        print json.dumps(response_json, indent=4, sort_keys=True)

        # Create a new quota for /ifs/data
	post_body = {
            'type': 'directory',
            'path': '/ifs/data',
            'include_snapshots': False,
            'thresholds_include_overhead': False,
            'enforced': False,
        }
        response_json = send_request_and_validate(api_session, 'POST',
            collection_uri, {}, json.dumps(post_body))

        item_id = response_json['id']
        item_uri = collection_uri + '/' + str(item_id)
        print "Successfully created quota with id:", item_id

        # List all quotas
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all quotas:"
        print json.dumps(response_json, indent=4, sort_keys=True)

        # DELETE the quota
        response_json = send_request_and_validate(api_session, 'DELETE',
            item_uri, {}, '')
        print "Deleted the quota."

        # List all quotas
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all quotas:"
        print json.dumps(response_json, indent=4, sort_keys=True)
    except:
        traceback.print_exc(file=sys.stdout)

    try:
        # The following examples are about NFS exports.
        # The user sending the request must have the
        # ISI_PRIV_NFS privilege.
        print
        print "NFS export example"
        print
        collection_uri = NFS_EXPORTS_URI

        # List exports
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all exports:"
        print json.dumps(response_json)

        # Create a new export for the /ifs/data path. This example assumes that
        # the /ifs/data path exists on your system).
        post_body = {'paths': ['/ifs/data']}
        response_json = send_request_and_validate(api_session, 'POST',
            collection_uri, {}, json.dumps(post_body))

        item_id = response_json['id']
        item_uri = collection_uri + '/' + str(item_id)
        print "Successfully created export with id:", item_id

        # List exports
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all exports:"
        print json.dumps(response_json)

        # GET an export
        response_json = send_request_and_validate(api_session, 'GET',
            item_uri, {}, '')

        block_size = response_json['exports'][0]['block_size']
        print "Initial value for block_size:", block_size

        # PUT to modify block_size
        put_body = {'block_size': 4096}
        response_json = send_request_and_validate(api_session, 'PUT',
            item_uri, {}, json.dumps(put_body))

        # GET the export after an update
        response_json = send_request_and_validate(api_session, 'GET',
            item_uri, {}, '')

        block_size = response_json['exports'][0]['block_size']
        print "Updated value for block_size:", block_size

        # List exports
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all exports:"
        print json.dumps(response_json)

        # DELETE the export
        response_json = send_request_and_validate(api_session, 'DELETE',
            item_uri, {}, '')
        print "Deleted the export."

        # List exports
        response_json = send_request_and_validate(api_session, 'GET',
            collection_uri, {}, '')
	print "Listing all exports:"
        print json.dumps(response_json)
    except:
        traceback.print_exc(file=sys.stdout)

    try:
        # The following examples show how to query documentation.
        # The user sending the request must have the
        # ISI_PRIV_AUTH privilege.
        print
        print "Querying server for auth privileges documentation."
        print
        collection_doc_uri = PRIVS_DOC_URI
        collection_doc_json_uri = PRIVS_JSON_URI

        # GET the json-formatted document for auth privileges
        response_json = send_request_and_validate(api_session, 'GET',
            collection_doc_json_uri, {}, '')

        print "Json schema documentation for auth privileges:"
        print json.dumps(response_json, indent=4, sort_keys=True)
    except:
        traceback.print_exc(file=sys.stdout)

    try:
        # Query the server for documented URIs
        print
        print "Querying server for documented URIs."
        print
	list_all_uri = RESOURCE_LIST_URI

        response_json = send_request_and_validate(api_session, 'GET',
            list_all_uri, {}, '')

        print "Documented URIs:"
        print json.dumps(response_json, indent=4, sort_keys=True)
    except:
        traceback.print_exc(file=sys.stdout)

    api_session.close_session()

if __name__ == "__main__":
    main()

