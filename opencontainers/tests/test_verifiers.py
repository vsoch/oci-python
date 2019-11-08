#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.digest import Digest, FromBytes

import string
import io
import random
import pytest


def test_digest_verifier(tmp_path):
    """test creation of an opencontainers verifiers
    """
    asciitext = "".join([random.choice(string.ascii_letters) for n in range(20)])
    p = bytes(asciitext, "utf-8")
    digest = FromBytes(p)
    verifier = digest.verifier()
    verifier.write(p)
    verifier.verified()


def test_digest_verifier_unsupported(tmp_path):
    """TestVerifierUnsupportedDigest ensures that unsupported digest validation is
       flowing through verifier creation.
    """
    # expected failure: empty digest
    digest = Digest("")
    with pytest.raises(SystemExit):
        digest.verifier()

    # expected failure, empty algorithm
    digest = Digest(":")
    with pytest.raises(SystemExit):
        digest.verifier()

    # expected failure, unsupported algorithm
    digest = Digest("bean:0123456789abcdef")
    with pytest.raises(SystemExit):
        verifier = digest.verifier()

    # expected failure
    digest = Digest("sha256-garbage:pure")
    verifier = digest.verifier()
    assert not verifier.verified()
