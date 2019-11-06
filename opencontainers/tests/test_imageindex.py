#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.image.v1 import Index
import os
import pytest


mediatype_invalid_pattern = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "invalid",
      "size": 7143,
      "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f",
      "platform": {
        "architecture": "ppc64le",
        "os": "linux"
      }
    }
  ]
}

manifest_invalid_string = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": "7682",
      "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    }
  ]
}

digest_missing = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 7682,
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    }
  ]
}


platform_arch_missing = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 7682,
      "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
      "platform": {
        "os": "linux"
      }
    }
  ]
}

invalid_manifest_mediatype = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "invalid",
      "size": 7682,
      "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    }
  ]
}

empty_manifest_mediatype = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "",
      "size": 7682,
      "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    }
  ]
}

index_with_optional = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 7143,
      "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f",
      "platform": {
        "architecture": "ppc64le",
        "os": "linux"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 7682,
      "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    }
  ],
  "annotations": {
    "com.example.key1": "value1",
    "com.example.key2": "value2"
  }
}

index_with_required = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 7143,
      "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f"
    }
  ]
}

index_with_custom = {
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "application/customized.manifest+json",
      "size": 7143,
      "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f",
      "platform": {
        "architecture": "ppc64le",
        "os": "linux"
      }
    }
  ]
}



def test_imageindex(tmp_path):
    '''test creation of a simple sink plugin
    '''
    index = Index()

    # expected failure: mediaType does not match pattern
    with pytest.raises(SystemExit):
        index.load(mediatype_invalid_pattern)

    # expected failure: manifest.size is string, expected integer
    with pytest.raises(SystemExit):
        index.load(manifest_invalid_string)

    # expected failure: manifest.digest is missing, expected required
    with pytest.raises(SystemExit):
        index.load(digest_missing)
 
    # expected failure: in the optional field platform platform.architecture is missing, expected required
    with pytest.raises(SystemExit):
        index.load(platform_arch_missing)

    # expected failure: invalid referenced manifest media type
    with pytest.raises(SystemExit):
        index.load(invalid_manifest_mediatype)

    # expected failure: empty referenced manifest media type
    with pytest.raises(SystemExit):
        index.load(empty_manifest_mediatype)

    # valid image index, with optional fields
    index.load(index_with_optional)

    # valid image index, with required fields only
    index.load(index_with_required)

    # valid image index, with customized media type of referenced manifest
    # TODO: need to figure out how custom works
    # index.load(valid_with_custom)
