# Open Containers Python

[![PyPI version](https://badge.fury.io/py/opencontainers.svg)](https://pypi.org/project/opencontainers/)
[![GitHub actions status](https://github.com/vsoch/oci-python/workflows/oci-python-ci/badge.svg?branch=master)](https://github.com/vsoch/oci-python/actions?query=branch%3Amaster+workflow%3Aoci-python-ci)

A simple Python implementation of Open Containers specifications. The code
is intentionally structured to mirror the go implementations for usability.
This include:

 - [opencontainers/image-spec](https://github.com/opencontainers/image-spec/tree/master/specs-go) maps to [opencontainers/image](opencontainers/image)
 - [opencontainers/go-digest](https://github.com/opencontainers/go-digest) maps to [opencontainers/digest](opencontainers/digest)
 - [opencontainers/distribution-spec](https://github.com/opencontainers/distribution-spec) maps to [opencontainers/distribution](opencontainers/distribution), which also includes a Python version of the [Reggie client](https://github.com/bloodorangeio/reggie) to interact with an OCI registry.

See the documentation at [vsoch.github.io/oci-python](https://vsoch.github.io/oci-python).
