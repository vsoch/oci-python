
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from opencontainers.image.specs import Versioned
from .descriptor import Descriptor


class Index(Struct):
    '''Index references manifests for various platforms.
       This structure provides `application/vnd.oci.image.index.v1+json` 
       mediatype when marshalled to JSON.
    '''
    def __init__(self, manifests, schemaVersion, annotations=None):
        Versioned = Versioned(schemaVersion)

        # Manifests references platform specific manifests.
        self.newAttr(name="Manifests", attType=[Descriptor], jsonName="manifests", required=True)

        # Annotations contains arbitrary metadata for the image index.
        self.newAttr(name="Annotations", attType=dict, jsonName="annotations")

        self.add("Manifests", manifests)
        self.add("annotations", annotations)
