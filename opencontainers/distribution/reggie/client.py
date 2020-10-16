"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import re
import requests
from .defaults import DEFAULT_USER_AGENT, URL_REGEX
from .request import RequestConfig, RequestClient
from .config import BaseConfig


class ClientConfig(BaseConfig):
    """A Client config holds attributes for a Reggie Client. Configuration setting
    functions are validation at creation time, and further validation is done
    with ClientConfig.validate().
    """

    valid_functions = [
        "WithUsernamePassword",
        "WithUserAgent",
        "WithDebug",
        "WithDefaultName",
        "WithAuthScope",
    ]

    def __init__(self, opts):
        """Instantiate a config."""
        self.Address = None
        self.AuthScope = None
        self.Username = None
        self.Password = None
        self.Debug = False
        self.DefaultName = None
        self.UserAgent = DEFAULT_USER_AGENT
        self.required = [self.Address, self.UserAgent]
        super().__init__(opts)

    def _validate(self):
        """Custom validation on top of BaseConfig validation."""
        # Validation 2: Address starts with http
        if not re.search(URL_REGEX, self.Address):
            raise ValueError("%s does not appear to be a http address." % self.Address)


# Attribute setting functions for ClientConfig


def WithUsernamePassword(username, password):
    """WithUsernamePassword sets registry username and password configuration settings."""

    def WithUsernamePassword(config):
        config.Username = username
        config.Password = password

    return WithUsernamePassword


def WithAuthScope(authScope):
    """WithAuthScope overrides the scope provided by the authorization server."""

    def WithAuthScope(config):
        config.AuthScope = authScope

    return WithAuthScope


def WithDefaultName(namespace):
    """WithDefaultName sets the default registry namespace configuration setting."""

    def WithDefaultName(config):
        config.DefaultName = namespace

    return WithDefaultName


def WithDebug(debug):
    """WithDebug enables or disables debug mode."""

    def WithDebug(config):
        config.Debug = debug

    return WithDebug


def WithUserAgent(userAgent):
    """WithUserAgent overrides the client user agent"""

    def WithUserAgent(config):
        config.UserAgent = userAgent

    return WithUserAgent


# Client


class Client:
    """A Client is a handle to create and issue requests to an OCI distribution
    registry. It is based on the Go version of reggie by BloodOrange.io,
    https://github.com/bloodorangeio/reggie/blob/master/client.go
    """

    def __init__(self, address, opts):
        """create a new client, requiring an address, and a Client Config.
        Matched to NewClient: builds a new Client from provided options.
        """
        self.Config = ClientConfig(address)
        self.Config.set_options(opts)
        self.Client = RequestClient()
        self.Debug = self.Config.Debug

        # Set max redirects (we don't set a transport here, not sure if required)
        self.Client.max_redirects = 20

    def SetDefaultName(self, namespace):
        """SetDefaultName sets the default registry namespace to use for building a Request."""
        self.Config.DefaultName = namespace

    def NewRequest(self, method, path, opts):
        """Prepare a request for some method, path (url) and set of options."""
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
        path = path.rstrip("/")
        url = "%s/%s" % (client.Config.Address, path)
        requestClient.setUrl(url)
        requestClient.SetHeader("User-Agent", self.Config.UserAgent)

        # TODO need to check here if setting attributes on returned class sets for parent too
        print("TODO check")
        import IPython

        IPython.embed()

        requestClient.SetRetryCallback(rc.RetryCallback)

        # Return the Client, which has Request and retryCallback
        return requestClient

    def Do(self, req):
        """Given a request (an instance of the RequestClient, execute the request
        and return a response.
        """
        # a requests.Repsponse with additional retryCallback
        response = req.Execute()

        # Unauthorized response
        if response.status_code == 401:
            response = self.retryRequestWithAuth(req, resp)
        return response

    def retryRequestWithAuth(originalRequest, originalResponse):
        """Given a 401 response (Authentication needed) retrieve the WWW-Authenticate
        header and retry with authentication
        """
        authHeaderRaw = originalResponse.headers.get("Www-Authenticate")
        if not authHeaderRaw:
            return originalResponse

        # Clear query parameters for original request
        for key, _ in originalRequest.params.items():
            del originalRequest.params[key]

        # If there is a callback, use it, should raise exception if issue
        if originalRequest.retryCallback:
            try:
                originalRequest.retryCallback(originalRequest)
            except Exception as exc:
                sys.exit("retry callback returned error: %s" % exc)

        authenticationType = re.match("(?i).*(bearer|basic).*", authHeaderRaw)
        if not authenticationType:
            sys.exit("www-Authenticate header is malformed.")

        # Given a bearer token, prepare request for it
        if authenticationType.groups()[0] == "bearer":
            h = parseAuthHeader(authHeaderRaw)
            req = (
                self.Client.NewRequest()
                .SetQueryParam("service", h.Service)
                .SetHeader("Accept", "application/json")
                .SetHeader("User-Agent", self.Config.UserAgent)
                .SetBasicAuth(self.Config.Username, self.Config.Password)
            )

            # Set the scope, first priority to config, then header
            if self.Config.AuthScope != "":
                req.SetQueryParam("scope", self.Config.AuthScope)
            elif h.Scope != "":
                req.SetQueryParam("scope", h.Scope)

            # Request the token
            authResponse = req.Execute("GET", h.Realm)
            info = authResponse.json()
            token = info.get("token")
            if not token:
                token = info.get("access_token")

            # Set the token to the original request and retry
            originalRequest.SetAuthToken(token)

        elif authenticationType.groups()[0] == "basic":
            originalRequest.SetBasicAuth(self.Config.Username, self.Config.Password)

        return originalRequest.Execute(originalRequest.Method, originalRequest.URL)


def parseAuthHeader(authHeaderRaw):
    """parse authentication header into pieces"""
    regex = re.compile('([a-zA-z]+)="(.+?)"')
    matches = regex.find_all(authHeaderRaw)
    lookup = dict()
    for match in matches:
        lookup[match[0]] = match[1]
    return authHeader(lookup)


class authHeader:
    def __init__(self, lookup):
        """Given a dictionary of values, match them to class attributes"""
        for key in lookup:
            if key in ["realm", "service", "scope"]:
                setattr(self, key.capitalize(), lookup[key])
