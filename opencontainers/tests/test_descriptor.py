#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.image.v1 import Descriptor
from opencontainers.digest.exceptions import (
    ErrDigestInvalidFormat,
    ErrDigestInvalidLength,
    ErrDigestUnsupported,
)
import os
import pytest


valid_descriptor = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

mediatype_missing = {
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

mediatype_nosubtype = {
    "mediaType": "application",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

mediatype_invalidtype = {
    "mediaType": ".foo/bar",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

mediatype_invalidsubtype = {
    "mediaType": "foo/.bar",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

expected_success = {
    "mediaType": "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567/1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

type_toolong = {
    "mediaType": "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678/bar",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

subtype_toolong = {
    "mediaType": "foo/12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

size_missing = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

size_string = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": "7682",
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

digest_missing = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
}


no_algorithm = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": ":5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

no_hash = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256",
}

invalid_algchars = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "SHA256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}

uppercase_digest = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256:5B0BCABD1ED22E9FB1310CF6C2DEC7CDEF19F0AD69EFA1F392E94A4333501270",
}

valid_urls = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
    "urls": ["https://example.com/foo"],
}

invalid_urls = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
    "urls": ["value"],
}

valids = [
    {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256+b64:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256+b64:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256+foo-bar:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
    },
    {
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": 1470,
        "digest": "sha256.foo-bar:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b"
        # multihash example removed, not supported is invalid
    },
]

repeated_seps_invalid = {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "size": 1470,
    "digest": "sha256+foo+-b:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b",
}

invalid_digest_length = {
    "digest": "sha256+b64u:LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564",
    "size": 1000000,
    "mediaType": "application/vnd.oci.image.config.v1+json",
}

digest_unknown = {
    "digest": "sha256+b64u.unknownlength:LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564=",
    "size": 1000000,
    "mediaType": "application/vnd.oci.image.config.v1+json",
}


def test_descriptor(tmp_path):
    """test creation of opencontiners Descriptor
    """
    desc = Descriptor()

    # expected pass: valid descriptor
    desc.load(valid_descriptor)

    # expected failure: mediaType missing
    with pytest.raises(SystemExit):
        desc.load(mediatype_missing)

    # expected failure: mediaType does not match pattern (no subtype)
    with pytest.raises(SystemExit):
        desc.load(mediatype_nosubtype)

    # expected failure: mediaType does not match pattern (invalid first type character)
    with pytest.raises(SystemExit):
        desc.load(mediatype_invalidtype)

    # expected failure: mediaType does not match pattern (invalid first subtype character)
    with pytest.raises(SystemExit):
        desc.load(mediatype_invalidsubtype)

    # expected success: mediaType has type and subtype as long as possible
    desc.load(expected_success)

    # expected failure: mediaType does not match pattern (type too long)
    with pytest.raises(SystemExit):
        desc.load(type_toolong)

    # expected failure: mediaType does not match pattern (subtype too long)
    with pytest.raises(SystemExit):
        desc.load(subtype_toolong)

    # expected failure: size missing
    with pytest.raises(SystemExit):
        desc.load(size_missing)

    # expected failure: size is a string, expected integer
    with pytest.raises(SystemExit):
        desc.load(size_string)

    # expected failure: digest missing
    with pytest.raises(SystemExit):
        desc.load(digest_missing)

    # expected failure: digest does not match pattern (no algorithm)
    with pytest.raises(ErrDigestInvalidFormat):
        desc.load(no_algorithm)

    # expected failure: digest does not match pattern (no hash)
    with pytest.raises(ErrDigestInvalidFormat):
        desc.load(no_hash)

    # expected failure: digest does not match pattern (invalid aglorithm characters)
    with pytest.raises(ErrDigestInvalidFormat):
        desc.load(invalid_algchars)

    # expected failure: digest does not match pattern (characters needs to be lower for sha256)
    with pytest.raises(ErrDigestInvalidFormat):
        desc.load(uppercase_digest)

    # expected success: valid URL entry
    desc.load(valid_urls)

    # expected failure: urls does not match format (invalide url characters)
    with pytest.raises(SystemExit):
        desc.load(invalid_urls)

    # these are all valid
    for valid in valids:
        desc.load(valid)

    # fail: repeated separators in algorithm
    with pytest.raises(ErrDigestInvalidFormat):
        desc.load(repeated_seps_invalid)

    # invalid digest length (also chars)
    with pytest.raises(ErrDigestInvalidLength):
        desc.load(invalid_digest_length)

    # test for those who cannot use modulo arithmetic to recover padding.
    with pytest.raises(ErrDigestInvalidLength):
        desc.load(digest_unknown)
