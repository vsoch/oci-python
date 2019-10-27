# Open Containers Python

[![PyPI version](https://badge.fury.io/py/opencontainers.svg)](https://pypi.org/project/opencontainers/)

A simple Python implementation of Open Containers specifications. The code
is intentionally structured to mirror the go implementations for usability.
This include:

 - [opencontainers/image-spec](https://github.com/opencontainers/image-spec/tree/master/specs-go) maps to [image](opencontainers/image)
 - [opencontainers/go-digest](https://github.com/opencontainers/go-digest) maps to [digest](opencontainers/digest)

## Thinking About

 - Should a new struct be validated right after init (for all fields, other than
those being added at init?)

This repository is **under development** and is not ready for use! @vsoch will
make proper docs and testing when it is.
