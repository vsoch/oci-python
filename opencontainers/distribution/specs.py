# Copyright (C) 2020-2022 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import IntStruct

# VersionMajor is for an API incompatible changes
VersionMajor = 0

# VersionMinor is for functionality in a backwards-compatible manner
VersionMinor = 1

# VersionPatch is for backwards-compatible bug fixes
VersionPatch = 0

# VersionDev indicates development branch. Releases will be empty string.
VersionDev = "-dev"

# Version is the specification version that the package types support.
Version = "%d.%d.%d%s" % (VersionMajor, VersionMinor, VersionPatch, VersionDev)
