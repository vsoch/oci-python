#!/usr/bin/python

# Copyright (C) 2019-2022 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .mock_server import get_free_port, start_mock_server
from opencontainers.distribution.reggie import *
import os
import re
import pytest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread


# Use the same port across tests
port = get_free_port()
mock_server = None
mock_server_thread = None


# Simple HTTP proxy server for testing proxy functionality
class SimpleProxyHandler(BaseHTTPRequestHandler):
    """A simple HTTP proxy handler that logs requests"""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Request proxied successfully")
        print(f"Proxy handled request: {self.path}")

    def do_PUT(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Request proxied successfully")
        print(f"Proxy handled PUT request: {self.path}")

    def log_message(self, format, *args):
        # Customize logging to show it's from the proxy
        print(f"PROXY LOG: {format % args}")


# Global variables for proxy server
proxy_port = get_free_port()
proxy_server = None
proxy_server_thread = None


def setup_module(module):
    """setup any state specific to the execution of the given module."""
    global mock_server
    global mock_server_thread
    global proxy_server
    global proxy_server_thread

    # Start the mock registry server
    mock_server, mock_server_thread = start_mock_server(port)

    # Start the proxy server
    proxy_server = HTTPServer(("localhost", proxy_port), SimpleProxyHandler)
    proxy_server_thread = Thread(target=proxy_server.serve_forever)
    proxy_server_thread.setDaemon(True)
    proxy_server_thread.start()
    print(f"Proxy server started on port {proxy_port}")


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    mock_server.server_close()
    proxy_server.server_close()


def test_distribution_mock_server(tmp_path):
    """test creation and communication with a mock server"""

    mock_url = "http://localhost:{port}".format(port=port)

    print("Testing creation of generic client")
    client = NewClient(
        mock_url,
        WithUsernamePassword("testuser", "testpass"),
        WithDefaultName("testname"),
        WithUserAgent("reggie-tests"),
    )
    assert not client.Config.Debug

    print("Testing creation of client with proxy")
    proxy_url = f"http://localhost:{proxy_port}"
    proxy_client = NewClient(
        mock_url,
        WithUsernamePassword("testuser", "testpass"),
        WithDefaultName("testname"),
        WithUserAgent("reggie-tests"),
        WithProxy(proxy_url),
    )
    assert proxy_client.Config.Proxy == proxy_url

    # Make a request with the proxy client
    req = proxy_client.NewRequest("GET", "/v2/<n>/tags/list")
    response = proxy_client.Do(req)
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"

    print("Testing setting debug option")
    clientDebug = NewClient(mock_url, WithDebug(True))
    assert clientDebug.Config.Debug

    print("Testing providing auth scope")
    testScope = (
        'realm="https://silly.com/v2/auth",service="testservice",scope="pull,push"'
    )
    client3 = NewClient(mock_url, WithAuthScope(testScope))
    assert client3.Config.AuthScope == testScope

    print("Testing that default name is replaced in template.")
    req = client.NewRequest("GET", "/v2/<name>/tags/list")

    # The name should be replaced in the template
    if "/v2/<name>/tags/list" in req.url or "testname" not in req.url:
        sys.exit("NewRequest does not add default namespace to URL")

    print("Checking user agent")
    uaHeader = req.headers.get("User-Agent")
    if uaHeader != "reggie-tests":
        sys.exit(
            'Expected User-Agent header to be "reggie-tests" but instead got "%s"'
            % uaHeader
        )

    print("Testing doing the request %s" % req)
    response = client.Do(req)
    if response.status_code != 200:
        sys.exit("Expected response code 200 but was %d", response.status_code)

    print("Test default name reset")
    client.SetDefaultName("othername")
    req = client.NewRequest("GET", "/v2/<name>/tags/list")
    if "othername" not in req.url:
        sys.exit("NewRequest does not add runtime namespace to URL")

    print("Test custom name on request")
    req = client.NewRequest("GET", "/v2/<name>/tags/list", WithName("customname"))
    if "/v2/customname/tags/list" not in req.url:
        sys.exit("NewRequest does not add runtime namespace to URL")

    print("test Location header on request")
    req = client.NewRequest("GET", "/v2/<name>/tags/list", WithName("withlocation"))
    response = client.Do(req)
    relativeLocation = response.GetRelativeLocation()
    if re.search("(http://|https://)", relativeLocation):
        sys.exit("Relative Location contains host")
    if relativeLocation == "":
        sys.exit("Location header not present")

    print("Testing absolute location")
    absoluteLocation = response.GetAbsoluteLocation()
    if not re.search("(http://|https://)", absoluteLocation):
        sys.exit("Absolute location missing http prefix")
    if absoluteLocation == "":
        sys.exit("Location header not present.")

    print("Test error function on response")
    req = client.NewRequest("GET", "/v2/<name>/tags/list", WithName("witherrors"))
    response = client.Do(req)
    errorList = response.Errors()
    if not errorList:
        sys.exit("Error list has length 0.")

    e1 = errorList[0]
    if e1["code"] == "":
        sys.exit("Code not returned in response body.")

    if e1["message"] == "":
        sys.exit("Message not returned in response body.")

    if e1["detail"] == "":
        sys.exit("Detail not returned in response body.")

    print("Test reference on request")
    req = client.NewRequest(
        "HEAD", "/v2/<name>/manifests/<reference>", WithReference("silly")
    )
    if not req.url.endswith("silly"):
        sys.exit("NewRequest does not add runtime reference to URL.")

    print("Test digest on request")
    digest = "6f4e69a5ff18d92e7315e3ee31c62165ebf25bfa05cad05c0d09d8f412dae401"
    req = client.NewRequest("GET", "/v2/<name>/blobs/<digest>", WithDigest(digest))
    if not req.url.endswith(digest):
        sys.exit("NewRequest does not add runtime digest to URL")

    print("Test session id on request")
    session_id = "f0ca5d12-5557-4747-9c21-3d916f2fc885"
    req = client.NewRequest(
        "GET", "/v2/<name>/blobs/uploads/<session_id>", WithSessionID(session_id)
    )
    if not req.url.endswith(session_id):
        sys.exit("NewRequest does not add runtime digest to URL")

    print("invalid request (no ref)")
    req = client.NewRequest("HEAD", "/v2/<name>/manifests/<reference>")

    # We should expect an error
    with pytest.raises(ValueError):
        response = client.Do(req)

    print("invalid request (no digest)")
    req = client.NewRequest("GET", "/v2/<name>/blobs/<digest>")
    with pytest.raises(ValueError):
        response = client.Do(req)

    print("invalid request (no session id)")
    req = client.NewRequest("GET", "/v2/<name>/blobs/uploads/<session_id>")
    with pytest.raises(ValueError):
        response = client.Do(req)

    print("bad address on client")
    with pytest.raises(ValueError):
        badClient = NewClient("xwejknxw://jshnws")

    print("Make sure headers and body match after going through auth")
    req = (
        client.NewRequest("PUT", "/a/b/c")
        .SetHeader("Content-Length", "3")
        .SetHeader("Content-Range", "0-2")
        .SetHeader("Content-Type", "application/octet-stream")
        .SetQueryParam("digest", "xyz")
        .SetBody(b"abc")
    )
    response = client.Do(req)

    print("Checking for expected headers")
    assert len(req.headers) == 5
    for header in [
        "Content-Length",
        "Content-Range",
        "Content-Type",
        "Authorization",
        "User-Agent",
    ]:
        assert header in req.headers

    print("Check that the body did not get lost somewhere")
    assert req.body == "abc"

    print("Test proxy request with different configuration")
    # Create a client with a different proxy configuration
    alt_proxy_url = f"http://localhost:{proxy_port}/alternate"
    alt_proxy_client = NewClient(
        mock_url,
        WithProxy(alt_proxy_url),
    )
    assert alt_proxy_client.Config.Proxy == alt_proxy_url

    # Verify that proxy setting is correctly passed to the request
    proxy_req = alt_proxy_client.NewRequest("GET", "/v2/test/tags/list")
    assert (
        proxy_req.proxies
    ), "Request should have non-empty proxies dictionary when proxy is set"
    assert (
        proxy_req.proxies.get("http") == alt_proxy_url
    ), "HTTP proxy not correctly set"
    assert (
        proxy_req.proxies.get("https") == alt_proxy_url
    ), "HTTPS proxy not correctly set"

    print("Test that the retry callback is invoked, if configured.")
    newBody = "not the original body"

    # Function to take a request and set a new body
    def func(r):
        r.SetBody(newBody)

    req = client.NewRequest("PUT", "/a/b/c", WithRetryCallback(func))
    req.SetBody("original body")
    response = client.Do(req)
    assert req.body == "not the original body"

    print("Test the case where the retry callback returns an error")

    def errorFunc(r):
        raise ValueError("ruhroh")

    req = client.NewRequest("PUT", "/a/b/c", WithRetryCallback(errorFunc))
    try:
        response = client.Do(req)
        raise ValueError(
            "Expected error from callback function, but request returned no error"
        )
    except Exception as exc:
        assert "ruhroh" in str(exc)

    print("Test proxy setting in request client")
    # Directly test the SetProxy method on the request client
    req = client.NewRequest("GET", "/test/endpoint")
    proxy_addr = f"http://localhost:{proxy_port}/direct-test"
    req.SetProxy(proxy_addr)
    # Verify that the proxy is set in the underlying request object when it's executed
    response = client.Do(req)
    assert response.status_code == 200, "Request through proxy should succeed"
