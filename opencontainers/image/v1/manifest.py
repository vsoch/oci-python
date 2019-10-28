
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from opencontainers.image.specs import Versioned
from .descriptor import Descriptor


class Manifest(Struct):
    '''Manifest provides `application/vnd.oci.image.manifest.v1+json` 
       mediatype structure when marshalled to JSON.
    '''
    def __init__(self, manifestConfig=None, layers=None, schemaVersion=None, annotations=None):
        super().__init__()

        self.newAttr(name="specs.Versioned", attType=Versioned, required=True, hide=True)

        # Config references a configuration object for a container, by digest.
        # The referenced configuration object is a JSON blob that the runtime uses to set up the container.
        self.newAttr(name="Config", attType=Descriptor, jsonName="config", required=True)

        # Layers is an indexed list of layers referenced by the manifest.
        self.newAttr(name="Layers", attType=[Descriptor], jsonName="layers", required=True)

        # Annotations contains arbitrary metadata for the image manifest.
        self.newAttr(name="Annotations", attType=dict, jsonName="annotations")

        self.add("Config", manifestConfig)
        self.add("Layers", layers)
        self.add("Annotations", annotations)
        self.add("specs.Versioned", Versioned(schemaVersion))
