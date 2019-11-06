
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from opencontainers.image.specs import Versioned
from opencontainers.logger import bot
from .mediatype import (
    MediaTypeImageIndex, 
    MediaTypeImageManifest
)
from .descriptor import Descriptor


class Index(Struct):
    '''Index references manifests for various platforms.
       This structure provides `application/vnd.oci.image.index.v1+json` 
       mediatype when marshalled to JSON.
    '''
    def __init__(self, manifests=None, schemaVersion=None, annotations=None):
        super().__init__()

        self.newAttr(name="schemaVersion", attType=Versioned, required=True)

        # Manifests references platform specific manifests.
        self.newAttr(name="Manifests", attType=[Descriptor], jsonName="manifests", required=True)

        # Annotations contains arbitrary metadata for the image index.
        self.newAttr(name="Annotations", attType=dict, jsonName="annotations")

        self.add("Manifests", manifests)
        self.add("Annotations", annotations)
        self.add("schemaVersion", schemaVersion)


    def _validate(self):
        '''custom validation function to ensure that Manifests mediaTypes
           are valid.
        '''
        valid_types = [MediaTypeImageManifest, MediaTypeImageIndex]

        manifests = self.attrs.get('Manifests').value
        if manifests:
            for manifest in manifests:
                mediaType = manifest.attrs.get('MediaType')
                if mediaType.value not in valid_types:
                    bot.error("%s is not valid for index manifest." % mediaType)
                    return False
        return True
