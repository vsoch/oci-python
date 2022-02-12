#!/usr/bin/python

# Copyright (C) 2019-2022 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import socket
import base64
from threading import Thread

import requests
import json


class MockRegistryRequestHandler(BaseHTTPRequestHandler):
    """The mock server can handle authentication"""

    AUTH_PATTERN = re.compile(r"/auth")

    def do_GET(self):
        print("GET %s" % self.path)

        # Authentication request
        if re.search(self.AUTH_PATTERN, self.path):

            # We expect these credentials
            expectedAuthHeader = "Basic " + base64.b64encode(
                b"testuser:testpass"
            ).decode("utf-8")
            foundAuthHeader = self.headers.get("Authorization")

            if foundAuthHeader != expectedAuthHeader:
                self.send_response(requests.codes.unauthorized)
            else:
                self.send_response(requests.codes.ok)
                self.end_headers()
                if self.authUseAccessToken:
                    self.wfile.write(
                        json.dumps({"access_token": "abc123"}).encode("utf-8")
                    )
                else:
                    self.wfile.write(json.dumps({"token": "abc123"}).encode("utf-8"))

            # Add response headers.
            # self.send_header('Content-Type', 'application/json; charset=utf-8')

            # Add response content.
            # response_content = json.dumps([])
            # self.wfile.write(response_content.encode('utf-8'))
            return

        # Registry request to return Location header
        elif re.search("withlocation", self.path):
            print("/tags/list withlocation endpoint was hit.")
            self.send_response(requests.codes.ok)

            # This is an artificially generated (successful) case that includes errors and Location to parse
            self.send_header(
                "Location",
                "http://abc123location.io/v2/blobs/uploads/e361aeb8-3181-11ea-850d-2e728ce88125",
            )
            self.end_headers()
            return

        # Registry request that has errors
        elif re.search("witherrors", self.path):
            print("/tags/list with errors endpoint was hit.")
            self.send_response(requests.codes.ok)
            error_response = {
                "errors": [
                    {
                        "code": "BLOB_UNKNOWN",
                        "message": "blob unknown to registry",
                        "detail": "lol",
                    }
                ]
            }
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode("utf-8"))
            return

        # Registry request that doesn't require auth
        elif re.search("/tags/list", self.path):
            print("/tags/list endpoint was hit.")
            self.send_response(requests.codes.ok)
            self.end_headers()
            return

    def do_PUT(self):
        print("PUT %s" % self.path)
        header = self.headers.get("Authorization")
        if header == "Bearer abc123":
            self.send_response(requests.codes.ok)
            self.send_header(
                "Location",
                "http://abc123location.io/v2/blobs/uploads/e361aeb8-3181-11ea-850d-2e728ce88125",
            )
            self.end_headers()
        else:
            self.send_response(requests.codes.unauthorized)
            wwwHeader = (
                'Bearer realm="http://localhost:%s/auth",service="testservice",scope="testscope"'
                % self.port
            )
            self.send_header("www-authenticate", wwwHeader)
            self.end_headers()
        return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port, authUseAccessToken=True):
    MockRegistryRequestHandler.port = port
    MockRegistryRequestHandler.authUseAccessToken = authUseAccessToken
    mock_server = HTTPServer(("localhost", port), MockRegistryRequestHandler)
    mock_server.authUseAccessToken = authUseAccessToken
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()
    return mock_server, mock_server_thread
