"""

Copyright (C) 2020-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from .defaults import DEFAULT_USER_AGENT, URL_REGEX
from .request import RequestConfig, RequestClient
from .config import BaseConfig
from copy import deepcopy

import sys
import re
import requests
import urllib.parse


class ClientConfig(BaseConfig):
    """
    A Client config holds attributes for a Reggie Client.

    Configuration setting
    functions are validation at creation time, and further validation is done
    with ClientConfig.validate().
    """

    valid_functions = [
        "WithUsernamePassword",
        "WithUserAgent",
        "WithDebug",
        "WithDefaultName",
        "WithAuthScope",
        "WithProxy",
    ]

    def __init__(self, address, opts=None):
        """
        Instantiate a config. An address is required.
        """
        self.Address = address
        self.AuthScope = None
        self.Username = None
        self.Password = None
        self.Debug = False
        self.DefaultName = None
        self.UserAgent = DEFAULT_USER_AGENT
        self.required = [self.Address, self.UserAgent]
        self.Proxy = None
        super().__init__()

    def _validate(self):
        """
        Custom validation on top of BaseConfig validation.
        """
        # Validation 2: Address starts with http
        if not re.search(URL_REGEX, self.Address):
            raise ValueError("%s does not appear to be a http address." % self.Address)


# Attribute setting functions for ClientConfig


def WithUsernamePassword(username, password):
    """
    WithUsernamePassword sets registry username and password configuration settings.
    """

    def WithUsernamePassword(config):
        config.Username = username
        config.Password = password

    return WithUsernamePassword


def WithAuthScope(authScope):
    """
    WithAuthScope overrides the scope provided by the authorization server.
    """

    def WithAuthScope(config):
        config.AuthScope = authScope

    return WithAuthScope


def WithDefaultName(namespace):
    """
    WithDefaultName sets the default registry namespace configuration setting.
    """

    def WithDefaultName(config):
        config.DefaultName = namespace

    return WithDefaultName


def WithDebug(debug):
    """
    WithDebug enables or disables debug mode.
    """

    def WithDebug(config):
        config.Debug = debug

    return WithDebug


def WithUserAgent(userAgent):
    """
    WithUserAgent overrides the client user agent
    """

    def WithUserAgent(config):
        config.UserAgent = userAgent

    return WithUserAgent


def WithProxy(proxy):
    """
    WithProxy sets the proxy configuration setting.
    """

    def WithProxy(config):
        config.Proxy = proxy

    return WithProxy


# Client


class NewClient:
    """
    A handle to create and issue requests to an OCI distribution registry

    It is based on the Go version of reggie by BloodOrange.io,
    https://github.com/bloodorangeio/reggie/blob/master/client.go
    """

    def __init__(self, address, *opts):
        """
        Create a new client

        Requiring an address, and a Client Config.
        Matched to NewClient: builds a new Client from provided options.
        """
        self.Config = ClientConfig(address)
        self.Config.set_options(opts)
        self.Config.validate()
        self.Client = RequestClient()
        self.Debug = self.Config.Debug

        # Set max redirects (we don't set a transport here, not sure if required)
        self.Client.max_redirects = 20

    def SetDefaultName(self, namespace):
        """
        SetDefaultName sets the default registry namespace to use for building a Request.
        """
        self.Config.DefaultName = namespace

    def NewRequest(self, method, path, *opts):
        """
        Prepare a request for some method, path (url) and set of options.
        """
        rc = RequestConfig(opts)
        requestClient = self.Client.NewRequest()
        requestClient.SetMethod(method)

        # Set default namespace, and fill in string replacements
        namespace = rc.Name or self.Config.DefaultName

        # Substitute known path paramaters
        replacements = {
            "<name>": namespace,
            "<reference>": rc.Reference,
            "<digest>": rc.Digest,
            "<session_id>": rc.SessionID,
        }
        for key, value in replacements.items():
            if value:
                path = path.replace(key, value, -1)

        # Remove trailing slash and prepare url
        url = urllib.parse.urljoin(self.Config.Address, path)
        requestClient.SetUrl(url)
        requestClient.SetHeader("User-Agent", self.Config.UserAgent)
        requestClient.SetRetryCallback(rc.RetryCallback)
        if self.Config.Proxy:
            requestClient.SetProxy(self.Config.Proxy)

        # Return the Client, which has Request and retryCallback
        return requestClient

    def Do(self, req):
        """
        Execut a request.

        Given a request (an instance of the RequestClient, execute the request
        and return a response.
        """
        # a requests.Response with additional retryCallback
        response = req.Execute()

        # Unauthorized response
        if response.status_code == 401:
            response = self.retryRequestWithAuth(req, response)
        return response

    def retryRequestWithAuth(self, originalRequest, originalResponse):
        """
        Retry a request with authentication.

        Given a 401 response (Authentication needed) retrieve the WWW-Authenticate
        header and retry with authentication
        """
        authHeaderRaw = originalResponse.headers.get("Www-Authenticate")
        if not authHeaderRaw:
            return originalResponse

        # If there is a callback, use it, should raise exception if issue
        if originalRequest.retryCallback:
            try:
                originalRequest.retryCallback(originalRequest)
            except Exception as exc:
                raise Exception("retry callback returned error: %s" % exc)

        # Prepare request to retry
        h = parseAuthHeader(authHeaderRaw)
        req = (
            self.Client.NewRequest()
            .SetQueryParam("service", h.Service)
            .SetHeader("Accept", "application/json")
            .SetHeader("User-Agent", self.Config.UserAgent)
        )

        # Do not set basic auth if no username/password provided
        if self.Config.Username and self.Config.Password:
            req = req.SetBasicAuth(self.Config.Username, self.Config.Password)

        # Set the scope, first priority to config, then header
        if self.Config.AuthScope:
            req.SetQueryParam("scope", self.Config.AuthScope)
        elif h.Scope:
            req.SetQueryParam("scope", h.Scope)

        authResponse = req.Execute("GET", h.Realm)

        # Request the token
        info = authResponse.json()
        token = info.get("token")
        if not token:
            token = info.get("access_token")

        # Set the token to the original request and retry
        originalRequest.SetAuthToken(token)
        return originalRequest.Execute(
            method=originalRequest.method, url=originalRequest.url
        )


def parseAuthHeader(authHeaderRaw):
    """
    Parse an authentication header into pieces
    """
    regex = re.compile('([a-zA-z]+)="(.+?)"')
    matches = regex.findall(authHeaderRaw)
    lookup = dict()
    for match in matches:
        lookup[match[0]] = match[1]
    return authHeader(lookup)


class authHeader:
    def __init__(self, lookup):
        """
        Given a dictionary of values, match them to class attributes
        """
        for key in lookup:
            if key in ["realm", "service", "scope"]:
                setattr(self, key.capitalize(), lookup[key])
