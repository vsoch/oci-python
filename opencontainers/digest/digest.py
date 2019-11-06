
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import StrStruct
from opencontainers.logger import bot
from .algorithm import Algorithm
import re


class Digest(StrStruct):
    '''Digest allows simple protection of hex formatted digest strings, prefixed
       by their algorithm. Strings of type Digest have some guarantee of being in
       the correct format and it provides quick access to the components of a
       digest string.

       The following is an example of the contents of Digest types:
       sha256:7173b809ca12ec5dee4506cd86be934c4596dd234ee82c0662eac04a8c2c71dc
       This allows to abstract the digest behind this type and work only in those
       terms.
    '''
    def __init__(self, value=None):
        super().__init__(value)

    def validate(self):
        '''Validate checks that the contents of self (the digest) is valid
        '''
        regexp = "^[a-z0-9]+(?:[+._-][a-z0-9]+)*:[a-zA-Z0-9=_-]+$"

        # Must match for a digest
        if not re.search(regexp, self):
            bot.exit("%s does not match %s" %(self, regexp))

        algorithm, encoded = (self).split(":")

        # Remove the extra component, if there
        match = re.search("[+._-]", algorithm)
        if match:
            algorithm = algorithm[:match.start()]
        algorithm = Algorithm(algorithm)

        # Also checks if algorithm.available()
        return algorithm.validate(encoded)

    def sepIndex(self):
        '''return the index of the : separator'''
        return self.index(":", 1)


    def algorithm(self):
        '''Algorithm returns the algorithm portion of the digest. 
        '''
        return Algorithm(self[:self.sepIndex()])


    def encoded(self):
        '''Encoded returns the encoded portion of the digest.
        '''
        return self[self.sepIndex()+1:]


    def verifier(self):
        '''Verifier returns a writer object that can be used to verify a stream of
           content against the digest. If the digest is invalid, the method will panic.
        '''
        from .verifiers import hashVerifier
        return hashVerifier(self.algorithm.hash(), digest=self)


# DigestRegexp matches valid digest types.
DigestRegexp = re.compile("[a-z0-9]+(?:[.+_-][a-z0-9]+)*:[a-zA-Z0-9=_-]+")

# DigestRegexpAnchored matches valid digest types, anchored to the start and end of the match.
DigestRegexpAnchored = re.compile("^%s$" % DigestRegexp)

def NewDigestFromEncoded(algorithm, encoded):
    '''NewDigestFromEncoded returns a Digest from alg and the encoded digest.
    '''
    return Digest("%s:%s" %(algorithm, encoded))


def Parse(string):
    '''Parse parses s and returns the validated digest object. An error will
       be returned if the format is invalid.
    '''
    d = Digest(s)
    d.validate()
    return d
