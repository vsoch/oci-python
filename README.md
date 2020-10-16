# Open Containers Python

[![PyPI version](https://badge.fury.io/py/opencontainers.svg)](https://pypi.org/project/opencontainers/)
[![GitHub actions status](https://github.com/vsoch/oci-python/workflows/oci-python-ci/badge.svg?branch=master)](https://github.com/vsoch/oci-python/actions?query=branch%3Amaster+workflow%3Aoci-python-ci)

A simple Python implementation of Open Containers specifications. The code
is intentionally structured to mirror the go implementations for usability.
This include:

 - [opencontainers/image-spec](https://github.com/opencontainers/image-spec/tree/master/specs-go) maps to [opencontainers/image](opencontainers/image)
 - [opencontainers/go-digest](https://github.com/opencontainers/go-digest) maps to [opencontainers/digest](opencontainers/digest)
 - [opencontainers/distribution-spec](https://github.com/opencontainers/distribution-spec) maps to [opencontainers/distribution](opencontainers/distribution), which also includes a Python version of the [Reggie client](https://github.com/bloodorangeio/reggie) to interact with an OCI registry.


## QUESTIONS

- GetAbsoluteLocation can return nil/None,while Get RelativeLocation returns an empty string. Is this intentional? My thinking is that it would be logical for them to be consistent.
- For response.Errors it seems to be important that Errors is defined *and* not empty. Is it okay if Errors is not defined? Wouldn't a response without errors not pass along this attribute? I'd like to return an empty list either way, and the only real check is if the json parses.

See the documentation at [vsoch.github.io/oci-python](https://vsoch.github.io/oci-python).
