"""

Copyright (C) 2020-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from .defaults import DEFAULT_USER_AGENT, URL_REGEX, VALID_METHODS
from .config import BaseConfig
from requests.cookies import cookiejar_from_dict
from requests.adapters import HTTPAdapter
from requests.hooks import default_hooks
from collections import OrderedDict

import base64
import json
import re
import requests


class RequestConfig(BaseConfig):
    """
    A Request Configuration

    A RequestConfig is akin to a ClientConfig to hold options, but for a
    particular request.
    """

    valid_functions = [
        "WithName",
        "WithReference",
        "WithDigest",
        "WithSessionID",
        "WithRetryCallback",
        "WithProxy",
    ]

    def __init__(self, opts):
        """
        Instantiate a request config
        """
        self.Name = None
        self.Reference = None
        self.Digest = None
        self.SessionID = None
        self.RetryCallback = None
        self.Proxy = None
        self.required = [self.Name]
        super().__init__(opts or [])


def WithName(name):
    """
    WithName sets the namespace per a single request.
    """

    def WithName(config):
        config.Name = name

    return WithName


def WithReference(ref):
    """
    WithReference sets the reference per a single request.
    """

    def WithReference(config):
        config.Reference = ref

    return WithReference


def WithDigest(digest):
    """
    WithDigest sets the digest per a single request.
    """

    def WithDigest(config):
        config.Digest = digest

    return WithDigest


def WithSessionID(session_id):
    """
    WithSessionID sets the session ID per a single request.
    """

    def WithSessionID(config):
        config.SessionID = session_id

    return WithSessionID


def WithRetryCallback(retryCallback):
    """
    Set a retry callback on a request.

    WithRetryCallback specifies a callback that will be invoked before a request
    is retried.
    """

    def WithRetryCallback(config):
        config.RetryCallback = retryCallback

    return WithRetryCallback


def WithProxy(proxy):
    """
    WithProxy sets the proxy configuration setting for requests.
    """

    def WithProxy(config):
        config.Proxy = proxy

    return WithProxy


class RequestClient(requests.Session):
    """
    A Request Client.

    A RequestClient includes a request, and adds some courtesy functions
    (wrappers around the self.request object to manipulate settings and
    return the same object to allow for chaining. This is implemented to
    match the Reggie Go implementation.
    """

    def __init__(self):
        """
        Create a new request.

        Start with an empty request ready to go. We replicate the parent
        class but don't set headers as it is provided as a property.
        """

    def __init__(self):
        self.auth = None
        self.proxies = {}
        self.hooks = default_hooks()
        self.stream = False
        self.verify = True
        self.cert = None
        self.max_redirects = 30
        self.trust_env = True
        self.cookies = cookiejar_from_dict({})
        self.adapters = OrderedDict()
        self.mount("https://", HTTPAdapter())
        self.mount("http://", HTTPAdapter())
        self.retryCallback = None
        self.Request = None

    def __str__(self):
        return "[%s] %s" % (self.Request.method, self.Request.url)

    @property
    def url(self):
        return self.Request.url

    @property
    def method(self):
        return self.Request.method

    @property
    def headers(self):
        return self.Request.headers

    @property
    def body(self):
        return (
            self.Request.data.decode("utf-8")
            if self.Request.data and isinstance(self.Request.data, bytes)
            else self.Request.data
        )

    @property
    def params(self):
        return self.Request.params

    def clearParams(self):
        self.Request.params = {}

    @classmethod
    def NewRequest(cls):
        """
        Set a new Request object to replace original, still return client
        """
        newclient = RequestClient()
        newclient.Request = requests.Request()
        return newclient

    def SetMethod(self, method):
        """
        SetMethod sets the method for the request
        """
        assert method in VALID_METHODS
        self.Request.method = method
        return self

    def SetUrl(self, url):
        """
        SetMethod sets the method for the request
        """
        assert re.search(URL_REGEX, url)
        self.Request.url = url
        return self

    def SetBody(self, body):
        """
        SetBody wraps the resty SetBody and returns the request, allowing method chaining
        """
        if isinstance(body, dict):
            body = json.dumps(body)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.Request.data = body
        return self

    def SetHeader(self, header, content):
        """
        SetHeader wraps the resty SetHeader and returns the request, allowing method chaining
        """
        self.Request.headers[header] = content
        return self

    def SetQueryParam(self, param, content):
        """
        SetQueryParam wraps the resty SetQueryParam and returns the request, allowing method chaining
        """
        self.Request.params[param] = content
        return self

    def SetRetryCallback(self, callback):
        """
        Helper function to add retry callback as a hook
        """
        self.hooks["response"].append(callback)
        self.retryCallback = callback
        return self

    def SetAuthToken(self, token):
        """
        A wrapper to adding basic authentication to the Request
        """
        return self.SetHeader("Authorization", "Bearer %s" % token)

    def SetBasicAuth(self, username, password):
        """
        A wrapper to adding basic authentication to the Request
        """
        auth_str = "%s:%s" % (username, password)
        auth_header = base64.b64encode(auth_str.encode("utf-8"))
        return self.SetHeader("Authorization", "Basic %s" % auth_header.decode("utf-8"))

    def SetProxy(self, proxy):
        """
        SetProxy sets the proxy configuration setting for requests.
        """
        self.proxies.update(
            {
                "http": proxy,
                "https": proxy,
            }
        )
        return self

    def Execute(self, method=None, url=None):
        """
        Execute validates a Request and executes it.

        Optionally, a different url or method can be provided if not set yet.
        Typically this is controlled by the Client that uses SetMethod
        and SetUrl.
        """
        self.Request.method = method or self.Request.method
        self.Request.url = url or self.Request.url
        validateRequest(self.Request)

        # prepare and send the request, add callback
        p = self.Request.prepare()
        response = self.send(p)
        response.retryCallback = self.retryCallback
        return response


def validateRequest(req):
    """
    Ensure that we have no unfilled template strings
    """
    regex = re.compile("<name>|<reference>|<digest>|<session_id>|//{2,}")
    if not req.url:
        raise ValueError("A url is required to prepare a request.")

    if not req.method:
        raise ValueError("A method is required to prepare a request")

    if regex.search(req.url):
        raise ValueError("request is invalid")
