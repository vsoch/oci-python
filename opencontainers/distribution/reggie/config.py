"""

Copyright (C) 2020-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import re
import requests
from .defaults import DEFAULT_USER_AGENT, URL_REGEX


class BaseConfig:
    """
    A Base client configuration.

    A BaseClient config holds attributes for some type of Reggie Client.
    Setting functions are validation at creation time, and further validation is done
    with BaseClient.validate().
    """

    def __init__(self, opts=None):
        """
        Instantiate a config.

        The subclass is required to call validate(), in case
        additional parameters or manipulation needs to be done.
        """
        # Opts must be a list of known functions
        if opts:
            self.set_options(opts)

        # List of valid function names, set by subclass
        self.valid_functions = getattr(self, "valid_functions", [])

        # Required attributes
        self.required = getattr(self, "required", [])

    def set_options(self, opts):
        """
        Validate and set a list of options.

        We loop through the list to set
        them for the config client. We also perform validation. Any issues
        with one of the functions raises an error.
        """
        if not isinstance(opts, (list, tuple)):
            raise ValueError(
                "Options should be provided as a list or tuple of functions."
            )

        for func in opts:
            self.validate_function(func)
            func(self)

    def validate_function(self, func):
        """
        Ensure that a function is in fact a function.

        And that is it one of the known ones to set an attribute.
        """
        if not hasattr(func, "__name__"):
            raise ValueError(
                "%s does not have a __name__ attribute, is it a function?" % func
            )
        if not callable(func):
            raise ValueError("%s is not a callable function." % func.__name__)
        if func.__name__ not in self.valid_functions:
            raise ValueError(
                "%s is not a valid config setting function." % func.__name__
            )

    def validate(self):
        """
        Validate config settings, done after initialization.
        """
        # Validation 1: required fields
        for setting in self.required:
            if not setting:
                raise ValueError("%s is required, and is not defined." % setting)

        # Call any custom validation routines for the Client
        if hasattr(self, "_validate"):
            self._validate()
