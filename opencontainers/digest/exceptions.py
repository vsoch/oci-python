
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


class ErrDigestInvalidFormat(Exception):
    '''ErrDigestInvalidFormat returned when digest format invalid.
    '''
    def __init__(self, message, errors):
        super().__init__("invalid checksum digest format")
        self.errors = errors


class ErrDigestInvalidLength(Exception):
    '''ErrDigestInvalidLength returned when digest has invalid length.
    '''
    def __init__(self, message, errors):
        super().__init__("invalid checksum digest length")
        self.errors = errors

class ErrDigestUnsupported(Exception):
    '''returned when the digest algorithm is unsupported.
    '''
    def __init__(self, message, errors):
        super().__init__("unsupported digest algorithm")
        self.errors = errors

