# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import StrStruct
from opencontainers.logger import bot
from .digester import digester
from .exceptions import (
    ErrDigestInvalidFormat,
    ErrDigestUnsupported,
    ErrDigestInvalidLength,
)

import hashlib
import re
import io


class Algorithm(StrStruct):
    """Algorithm identifies and implementation of a digester by an identifier.
       Note the that this defines both the hash algorithm used and the string
       encoding.
    """

    def __init__(self, value=None):
        self._algorithm = value
        super().__init__(value)

    def available(self):
        """Available returns true if the digest type is available for use. 
           If this returns false, Digester and Hash will return None.
           we are flexible to allow the user to also provide a full digest
        """
        algorithm = self.value

        # If we have a full digest, name is separated by :
        match = re.search("^(?P<algorithm>.+?):(?P<digest>.+)", self.value)
        if match:
            algorithm = match.group("algorithm")

        self._algorithm = algorithm

        return algorithm in algorithms

    def digester(self):
        """Digester returns a new digester for the specified algorithm. If the algorithm
           does not have a digester implementation, nil will be returned. This can be
           checked by calling Available before calling Digester. Note that
           the GoLang implementation also had a Hash() function that (seemed to)
           return the same, and instead I'm going to return the same hashlib new.
        """
        return digester(self, self.hash())

    def hash(self):
        """Hash returns a new hash as used by the algorithm.
        """
        if not self.available():
            return None
        return hashlib.new(self._algorithm)

    def validate(self, encoded):
        """Validate validates the encoded portion string. This means
           ensuring that the algorithm is available, checking it's length,
           and the characters provided.
        """
        if not self.available():
            raise ErrDigestUnsupported()

        # Digests much always be hex-encoded, ensuring that their hex portion will
        # always be size*2
        hashy = hashlib.new(self._algorithm)
        if hashy.digest_size * 2 != len(encoded):
            raise ErrDigestInvalidLength()

        regexp = anchoredEncodedRegexps.get(self._algorithm)
        if not regexp.search(encoded):
            raise ErrDigestInvalidFormat()
        return True

    def size(self):
        """Size returns number of bytes returned by the hash.
        """
        if not self.available():
            return 0
        hashy = hashlib.new(self._algorithm)

        # Need to ensure that the digest size == bytes and we don't want block_size
        return hashy.digest_size

    def set(self, value):
        """Set implemented to allow use of Algorithm as a command line flag.
           This isn't useful, as we could already call load (but this will
           mirror GoLang.
        """
        self = self.load(value)
        if not self.available():
            raise ErrDigestUnsupported()

    def encode(self, content):
        """Encode encodes the raw bytes of a digest, typically from a hash.Hash, into
           the encoded portion of the digest.
        """
        # Currently, all algorithms use a hex encoding. When we
        # add support for back registration, we can modify this accordingly.
        # https://github.com/opencontainers/go-digest/blob/master/algorithm.go#L137
        if not isinstance(content, bytes):
            content = bytes(content, "utf-8")
        return content.hex()

    def fromReader(self, ioReader):
        """FromReader returns the digest of the reader using the algorithm.
           the input must be type bytes, usually from io.BytesIO.read(). 
           This function likely isn't needed, but is provided to mirror
           the GoLang implementation.
        """
        if not isinstance(ioReader, io.BytesIO):
            bot.exit("input must be io.BytesIO")
        return self.fromBytes(ioReader.read())

    def fromBytes(self, content):
        """FromBytes digests the input and returns a Digest.
        """
        digester = self.digester()
        digester.hash.update(content)
        return digester.digest()

    def fromString(self, content):
        """FromString digests the string input and returns a Digest.
           TODO not sure what this is intended for.
        """
        if not isinstance(content, str):
            bot.exit("input must be string")
        content = bytes(content, "utf-8")
        return self.fromBytes(content)


# supported digest types only to match GoLang

SHA256 = Algorithm("sha256")  # sha256 with hex encoding (lower case only)
SHA384 = Algorithm("sha384")  # sha384 with hex encoding (lower case only)
SHA512 = Algorithm("sha512")  # sha512 with hex encoding (lower case only)

# Canonical is the primary digest algorithm used with the distribution
# project. Other digests may be used but this one is the primary storage digest
Canonical = SHA256

# algorithms maps values to hash.Hash implementations. Other algorithms
# may be available but they cannot be calculated by the digest package.
# this mirrors GoLang (there are more available in Python)

algorithms = {"sha256": SHA256, "sha384": SHA384, "sha512": SHA512}

# anchoredEncodedRegexps contains anchored regular expressions for hex-encoded
# digests. Note that /A-F/ disallowed.

anchoredEncodedRegexps = {
    SHA256: re.compile("^[a-f0-9]{64}$"),
    SHA384: re.compile("^[a-f0-9]{96}$"),
    SHA512: re.compile("^[a-f0-9]{128}$"),
}
