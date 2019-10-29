
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
from typing import List,Tuple
from ...logger import bot
from opencontainers.struct import Struct
from opencontainers.image.specs import Versioned
from .descriptor import Descriptor
from . import (
    DEFAULT_CONFIG_MEDIATYPE,
    DEFAULT_IMAGELAYER_MEDIATYPE,
    KNOWN_CONFIG_MEDIATYPE,
    KNOWN_IMAGELAYER_MEDIATYPE
)

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

    @staticmethod
    def verifyConfigMediaType(config: Descriptor,
        default: str = DEFAULT_CONFIG_MEDIATYPE,
        known_mediatypes: Tuple[str] = KNOWN_CONFIG_MEDIATYPE) -> bool:

        if not config.MediaType.value:
            config.MediaType.set(default)
            return True
        if config.MediaType.value in known_mediatypes:
            return True
        bot.error("{} is not a valid Config MediaType for this artifact.".format(config.MediaType.value))
        return False

    @staticmethod
    def verifyImageLayerMediaType(layers: List[Descriptor],
        default: str = DEFAULT_IMAGELAYER_MEDIATYPE,
        known_mediatypes: Tuple[str] = KNOWN_IMAGELAYER_MEDIATYPE
        ):

        if len(layers) == 0:
            return True

        for layer in layers:
            if not layer.MediaType.value:
                layer.MediaType.set(default)
                continue
            if layer.MediaType.value in known_mediatypes:
                continue
            bot.error("{} is not a valid ImageLayer MediaType for this artifact.".format(layer.MediaType.value))
            return False
        # At this point all layers are valid
        return True

    def validate(self) -> bool:
        attribute_type_validation = super().validate()
        if self.verifyConfigMediaType(self.Config) and self.verifyImageLayerMediaType(self.Layers):
           return attribute_type_validation
        else:
            return False
