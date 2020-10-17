#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .mock_server import get_free_port, start_mock_server
from opencontainers.distribution.reggie import *
import os
import re
import pytest


# Use the same port across tests
port = get_free_port()
mock_server = None
mock_server_thread = None


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global mock_server
    global mock_server_thread
    mock_server, mock_server_thread = start_mock_server(port)


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    mock_server.server_close()


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
