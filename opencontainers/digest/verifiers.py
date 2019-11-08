# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from hashlib import new
from .digest import Digest, NewDigest


class hashVerifier(Struct):
    def __init__(self, hashObj=None, digest=None):

        super().__init__()

        self.hash = hashObj
        self.digest = digest

    def write(self, content):
        """add bytes of content to the hash object
        """
        if not isinstance(content, bytes):
            content = bytes(content, "utf-8")
        self.hash.update(content)
        self.digest = NewDigest(self.digest.algorithm, self.hash)
        self.digest.validate()

    def verified(self):
        """calculate the hex digest against the digest
        """
        return self.digest == NewDigest(self.digest.algorithm, self.hash)


# The GoLang implementation has another Verifier class, not used here
