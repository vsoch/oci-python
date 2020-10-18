# Copyright (C) 2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


from opencontainers.struct import Struct
from opencontainers.logger import bot

# ErrRegistry is the string returned by and ErrorResponse error.
ErrRegistry = "distribution: registry returned error"


class ErrorInfo(Struct):
    """ErrorInfo describes a server error returned from a registry."""

    def __init__(self, code, message, detail):
        super().__init__()
        self.newAttr(name="Code", attType=str, jsonName="code", required=True)
        self.newAttr(name="Message", attType=str, jsonName="message", required=True)
        self.newAttr(name="Detail", attType=str, jsonName="detail", required=True)

        self.add("Code", code)
        self.add("Message", message)
        self.add("Detail", detail)


class ErrorResponse(Struct):
    """ErrorResponse is returned by a registry on an invalid request."""

    def __init__(self, errors=None):
        super().__init__()
        self.newAttr(
            name="Errors", attType=[ErrorInfo], jsonName="errors", required=True
        )
        self.add("Errors", errors or [])

    def Error(self):
        """Error implements the Error interface."""
        return ErrRegistry

    def Detail(self):
        """Detail returns an ErrorInfo"""
        return self.attrs.get("Errors").value


class ErrRegistry(Struct):
    """ErrorResponse is returned by a registry on an invalid request."""

    def __init__(self, errors=None):
        super().__init__()
        self.newAttr(
            name="Errors", attType=[ErrorInfo], jsonName="errors", required=True
        )
        self.add("Errors", errors or [])
