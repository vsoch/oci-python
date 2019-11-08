#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.digest import Parse, NewDigestFromEncoded

from opencontainers.digest.exceptions import (
    ErrDigestInvalidLength,
    ErrDigestInvalidFormat,
    ErrDigestUnsupported,
)
import os
import pytest


digests = [
    {
        "input": "sha256:e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b",
        "algorithm": "sha256",
        "encoded": "e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b",
    },
    {
        "input": "sha384:d3fc7881460b7e22e3d172954463dddd7866d17597e7248453c48b3e9d26d9596bf9c4a9cf8072c9d5bad76e19af801d",
        "algorithm": "sha384",
        "encoded": "d3fc7881460b7e22e3d172954463dddd7866d17597e7248453c48b3e9d26d9596bf9c4a9cf8072c9d5bad76e19af801d",
    },
    {
        # empty hex
        "input": "sha256:",
        "err": ErrDigestInvalidFormat,
    },
    {
        # empty hex
        "input": ":",
        "err": ErrDigestInvalidFormat,
    },
    {
        # just hex
        "input": "d41d8cd98f00b204e9800998ecf8427e",
        "err": ErrDigestInvalidFormat,
    },
    {
        # not hex
        "input": "sha256:d41d8cd98f00b204e9800m98ecf8427e",
        "err": ErrDigestInvalidLength,
    },
    {
        # too short
        "input": "sha256:abcdef0123456789",
        "err": ErrDigestInvalidLength,
    },
    {
        # too short (from different algorithm)
        "input": "sha512:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
        "err": ErrDigestInvalidLength,
    },
    {"input": "foo:d41d8cd98f00b204e9800998ecf8427e", "err": ErrDigestUnsupported},
    {
        # repeated separators
        "input": "sha384__foo+bar:d3fc7881460b7e22e3d172954463dddd7866d17597e7248453c48b3e9d26d9596bf9c4a9cf8072c9d5bad76e19af801d",
        "err": ErrDigestInvalidFormat,
    },
    {
        # ensure that we parse, but we don't have support for the algorithm
        "input": "sha384.foo+bar:d3fc7881460b7e22e3d172954463dddd7866d17597e7248453c48b3e9d26d9596bf9c4a9cf8072c9d5bad76e19af801d",
        "algorithm": "sha384.foo+bar",
        "encoded": "d3fc7881460b7e22e3d172954463dddd7866d17597e7248453c48b3e9d26d9596bf9c4a9cf8072c9d5bad76e19af801d",
        "err": ErrDigestUnsupported,
    },
    {
        "input": "sha384_foo+bar:d3fc7881460b7e22e3d172954463dddd7866d17597e7248453c48b3e9d26d9596bf9c4a9cf8072c9d5bad76e19af801d",
        "algorithm": "sha384_foo+bar",
        "encoded": "d3fc7881460b7e22e3d172954463dddd7866d17597e7248453c48b3e9d26d9596bf9c4a9cf8072c9d5bad76e19af801d",
        "err": ErrDigestUnsupported,
    },
    {
        "input": "sha256:E58FCF7418D4390DEC8E8FB69D88C06EC07039D651FEDD3AA72AF9972E7D046B",
        "err": ErrDigestInvalidFormat,
    },
]

digest_unsupported = {
    "input": "sha256+b64:LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564",
    "algorithm": "sha256+b64",
    "encoded": "LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564",
    "err": ErrDigestInvalidLength,  # also unsupported
}


def test_digests(tmp_path):
    """test creation of an opencontainers Digest
    """
    with pytest.raises(digest_unsupported["err"]):
        d = Parse(digest_unsupported["input"])

    for digest in digests:

        # Case 1: we expect an error (algorithm not provided)
        if "err" in digest and "algorithm" not in digest:
            with pytest.raises(digest["err"]):
                Parse(digest["input"])

        else:

            d = Parse(digest["input"])

            # These are cases we can parse, but don't have support for algorithm
            if "err" in digest:
                assert d.algorithm != digest["algorithm"]
            else:
                assert d.algorithm == digest["algorithm"]
            assert d.encoded() == digest["encoded"]

            # Try creating new digest from encoded
            if "encoded" in digest and "algorithm" in digest:
                newFromEncoded = NewDigestFromEncoded(
                    digest["algorithm"], digest["encoded"]
                )
                assert newFromEncoded == d
