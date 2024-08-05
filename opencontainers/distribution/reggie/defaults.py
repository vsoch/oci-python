"""

Copyright (C) 2020-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from opencontainers.version import __version__

DEFAULT_USER_AGENT = "reggie-python/%s (https://github.com/vsoch/oci-python)" % (
    __version__
)
URL_REGEX = (
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
VALID_METHODS = ["HEAD", "GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"]
