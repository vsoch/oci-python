
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from hashlib import new
from .digest import Digest

class hashVerifier(Struct):
    def __init__(self, hashObj=None, digest=None):

        super().__init__()

        self.newAttr(name="hash", attType=new)
        self.newAttr(name="digest", attType=Digest)
        self.add("digest", digest)
        self.add("hash", hashObj)

#// Verifier presents a general verification interface to be used with message
#// digests and other byte stream verifications. Users instantiate a Verifier
#// from one of the various methods, write the data under test to it then check
#// the result with the Verified method.
#type Verifier interface {
#	io.Writer

#	// Verified will return true if the content written to Verifier matches
#	// the digest.
#	Verified() bool
#}

#type hashVerifier struct {
#	digest Digest
#	hash   hash.Hash
#}

#func (hv hashVerifier) Write(p []byte) (n int, err error) {
#	return hv.hash.Write(p)
#}

#func (hv hashVerifier) Verified() bool {
#	return hv.digest == NewDigest(hv.digest.Algorithm(), hv.hash)
#}
