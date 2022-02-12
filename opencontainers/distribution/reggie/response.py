"""

Copyright (C) 2020-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from requests.models import Response


def GetRelativeLocation(self):
    """
    GetRelativeLocation returns the path component of the URL contained
    """
    loc = self.headers.get("Location", "")
    if loc and loc.startswith("http"):
        loc = "/%s" % "/".join(loc.split("/")[3:])
    return loc


def GetAbsoluteLocation(self):
    """
    Get the absolute url

    GetAbsoluteLocation returns the full URL, including protocol and host,
    of the location contained in the `Location` header of the response.
    """
    return self.headers.get("Location")


def IsUnauthorized(self):
    """
    Determine if a status code indicates the request was not authorized.

    IsUnauthorized returns whether or not the response is a 401
    """
    return self.status_code == 401


def Errors(self):
    """
    Parse a response into OCI-compliant errors.

    Errors attempts to parse a response as OCI-compliant errors array.
    If there are no errors, return an empty list.
    """
    try:
        errorResponse = self.json()
    except:
        return

    return errorResponse.get("errors", [])


setattr(Response, "GetRelativeLocation", GetRelativeLocation)
setattr(Response, "GetAbsoluteLocation", GetAbsoluteLocation)
setattr(Response, "IsUnauthorized", IsUnauthorized)
setattr(Response, "Errors", Errors)
