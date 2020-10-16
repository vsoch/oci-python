"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import re
import requests
from .defaults import DEFAULT_USER_AGENT, URL_REGEX, VALID_METHODS
from .config import BaseConfig


class RequestConfig(BaseConfig):
    """A RequestConfig is akin to a ClientConfig to hold options, but for a
    particular request.
    """

    valid_functions = [
        "WithName",
        "WithReference",
        "WithDigest",
        "WithSessionID",
        "WithRetryCallback",
    ]

    def __init__(self, opts):
        """Instantiate a config."""
        """Instantiate a request config
        """
        self.Name = None
        self.Reference = None
        self.Digest = None
        self.SessionID = None
        self.RetryCallback = None
        self.required = [self.Name]
        super().__init__(opts)


def WithName(name):
    """WithName sets the namespace per a single request."""

    def WithName(config):
        config.Name = name

    return WithName


def WithReference(ref):
    """WithReference sets the reference per a single request."""

    def WithReference(config):
        config.Reference = ref

    return WithReference


def WithDigest(digest):
    """WithDigest sets the digest per a single request."""

    def WithDigest(config):
        config.Digest = digest

    return WithDigest


def WithSessionID(session_id):
    """WithSessionID sets the session ID per a single request."""

    def WithSessionID(config):
        config.SessionID = session_id

    return WithSessionID


def WithRetryCallback(retryCallback):
    """WithRetryCallback specifies a callback that will be invoked before a request
    is retried.
    """

    def WithRetryCallback(config):
        config.RetryCallback = retryCallback

    return WithRetryCallback


class RequestClient(requests.Session):
    """A RequestClient includes a request, and adds some courtesy functions
    (wrappers around the self.request object to manipulate settings and
    return the same object to allow for chaining. This is implemented to
    match the Reggie Go implementation.
    """

    def __init__(self):
        """Start with an empty request ready to go."""
        super().__init__()
        self.retryCallback = None
        self.NewRequest()

    def NewRequest(self):
        """Set a new Request object to replace original, still return client"""
        self.Request = requests.Request()
        return self

    def SetMethod(self, method):
        """SetMethod sets the method for the request"""
        assert method in VALID_METHODS
        self.Request.method = method
        return self

    def SetBody(self, body):
        """SetBody wraps the resty SetBody and returns the request, allowing method chaining"""
        self.Request.data = body
        return self

    def SetHeader(self, header, content):
        """SetHeader wraps the resty SetHeader and returns the request, allowing method chaining"""
        self.Request.headers[header] = content
        return self

    def SetQueryParam(self, param, content):
        """SetQueryParam wraps the resty SetQueryParam and returns the request, allowing method chaining"""
        self.Request.params[param] = content
        return self

    def SetRetryCallback(self, callback):
        """Helper function to add retry callback as a hook"""
        self.hooks["response"].append(callback)
        self.retryCallback = callback

    def Execute(self, method=None, url=None):
        """Execute validates a Request and executes it. Optionally,
        a different url or method can be provided if not set yet.
        Typically this is controlled by the Client that uses SetMethod
        and SetUrl.
        """
        self.Request.method = method or self.Request.method
        self.Request.url = url or self.Request.url
        validateRequest(self.Request)

        # prepare and send the request, add callback
        p = self.Request.prepare()
        response = self.send(p)
        response.retryCallBack = self.retryCallBack
        return response


def validateRequest(req):
    """Ensure that we have no unfilled template strings"""
    regex = re.compile("<name>|<reference>|<digest>|<session_id>|//{2,}")
    if not req.url:
        raise ValueError("A url is required to prepare a request.")

    if not req.method:
        raise ValueError("A method is required to prepare a request")

    if regex.search(req.url):
        raise ValueError("request is invalid")
