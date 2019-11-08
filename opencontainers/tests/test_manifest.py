#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.image.v1 import Manifest
from opencontainers.digest.exceptions import ErrDigestInvalidFormat
import os
import pytest

invalid_mediatype_pattern = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "invalid",
        "size": 1470,
        "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 148,
            "digest": "sha256:c57089565e894899735d458f0fd4bb17a0f1e0df8d72da392b85c9b35ee777cd",
        }
    ],
}

invalid_config_size_string = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": "1470",
        "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 148,
            "digest": "sha256:c57089565e894899735d458f0fd4bb17a0f1e0df8d72da392b85c9b35ee777cd",
        }
    ],
}

invalid_layers_size_string = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": "675598",
            "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
        }
    ],
}


valid_with_optional = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 675598,
            "digest": "sha256:9d3dd9504c685a304985025df4ed0283e47ac9ffa9bd0326fddf4d59513f0827",
        },
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 156,
            "digest": "sha256:2b689805fbd00b2db1df73fae47562faac1a626d5f61744bfe29946ecff5d73d",
        },
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 148,
            "digest": "sha256:c57089565e894899735d458f0fd4bb17a0f1e0df8d72da392b85c9b35ee777cd",
        },
    ],
    "annotations": {"key1": "value1", "key2": "value2"},
}

valid_with_required = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 675598,
            "digest": "sha256:9d3dd9504c685a304985025df4ed0283e47ac9ffa9bd0326fddf4d59513f0827",
        },
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 156,
            "digest": "sha256:2b689805fbd00b2db1df73fae47562faac1a626d5f61744bfe29946ecff5d73d",
        },
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 148,
            "digest": "sha256:c57089565e894899735d458f0fd4bb17a0f1e0df8d72da392b85c9b35ee777cd",
        },
    ],
}

invalid_empty_layers = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [],
}

expected_bounds_pass = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256+b64:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 1470,
            "digest": "sha256+foo-bar:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
        },
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 1470,
            "digest": "sha256.foo-bar:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
        }
        # multihash is not registered, but still valid formatting, but here we would consider it invalid
        # {
        #  "mediaType": "application/vnd.oci.image.config.v1+json",
        #  "size": 1470,
        #   "digest": "multihash+base58:QmRZxt2b1FVZPNqd8hsiykDL3TdBDeTSPX9Kv46HmX4Gx8"
        # }
    ],
}

expected_bounds_fail = {
    "schemaVersion": 2,
    "config": {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256+b64:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    "layers": [
        {
            "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "size": 1470,
            "digest": "sha256+foo+-b:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
        }
    ],
}


def test_manifests(tmp_path):
    """test creation of an opencontainers Manifest
    """
    manifest = Manifest()

    # expected failure: mediaType does not match pattern
    with pytest.raises(SystemExit):
        manifest.load(invalid_mediatype_pattern)

    # config size is string, should be int
    with pytest.raises(SystemExit):
        manifest.load(invalid_config_size_string)

    # layers.size is string, should be integer
    with pytest.raises(SystemExit):
        manifest.load(invalid_layers_size_string)

    # valid manifest with optional fields
    manifest.load(valid_with_optional)

    # valid manifest with only required fields
    manifest.load(valid_with_required)

    # expected failure: empty layer, expected at least one
    with pytest.raises(SystemExit):
        manifest.load(invalid_empty_layers)

    # expected pass: test bounds of algorithm field in digest.
    manifest.load(expected_bounds_pass)

    # expected failure: push bounds of algorithm field in digest too far.
    with pytest.raises(ErrDigestInvalidFormat):
        manifest.load(expected_bounds_fail)
