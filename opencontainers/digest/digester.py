# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from hashlib import new


class Digester(Struct):
    """Digester calculates the digest of written data. Writes should go directly
       to the return value of Hash, while calling Digest will return the current
       value of the digest.
    """

    def __init__(self):

        self.Hash = digester.digest
        self.Digest = digester.digest
        super().__init__()


class digester(Struct):
    """digester provides a simple digester definition that embeds a hasher.
    """

    def __init__(self, alg=None, hashObj=None):

        super().__init__()
        self.alg = alg
        self.hash = hashObj

    def digest(self):
        from .digest import NewDigest

        return NewDigest(self.alg, self.hash)
