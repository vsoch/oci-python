
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct

# VersionMajor is for an API incompatible changes
VersionMajor = 1

# VersionMinor is for functionality in a backwards-compatible manner
VersionMinor = 0

# VersionPatch is for backwards-compatible bug fixes
VersionPatch = 1

# VersionDev indicates development branch. Releases will be empty string.
VersionDev = "-dev"

# Version is the specification version that the package types support.
Version = "%d.%d.%d%s" %(VersionMajor, VersionMinor, VersionPatch, VersionDev)

# Versioned provides a struct with the manifest schemaVersion and mediaType.
# Incoming content with unknown schema version can be decoded against this
# struct to check the version.

class Versioned(Struct):
    def __init__(self, schemaVersion=None):

        # SchemaVersion is the image manifest schema that this image follows
        self.newAttr(name="SchemaVersion", 
                     attType=int,
                     required=True, 
                     jsonName='schemaVersion')

        self.add("SchemaVersion", schemaVersion or VersionMajor)
