
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct

# ImageLayoutFile is the file name of oci image layout file
ImageLayoutFile = "oci-layout"

# ImageLayoutVersion is the version of ImageLayout
ImageLayoutVersion = "1.0.0"


class ImageLayout(Struct): 
    '''ImageLayout is the structure in the "oci-layout" file, found in the root 
       of an OCI Image-layout directory.
    '''
    def __init__(self, version=None):
        super().__init__()

        # This is for semver, but without the v
        regexp = r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patchlevel>\d+)~?(?P<special>[a-z]\w+[\d+])?$"
        self.newAttr(name="Version", attType=str, jsonName="imageLayoutVersion",
                     required=True, regexp=regexp)
        self.add("Version", version or ImageLayoutVersion)
