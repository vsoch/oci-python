# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from opencontainers.image.specs import Versioned
from opencontainers.logger import bot
from .descriptor import Descriptor
from .mediatype import (
    MediaTypeImageConfig,
    MediaTypeImageLayer,
    MediaTypeImageLayerGzip,
    MediaTypeImageLayerZstd,
    MediaTypeImageLayerNonDistributable,
    MediaTypeImageLayerNonDistributableGzip,
    MediaTypeImageLayerNonDistributableZstd,
)


class Manifest(Struct):
    """Manifest provides `application/vnd.oci.image.manifest.v1+json` 
       mediatype structure when marshalled to JSON.
    """

    def __init__(
        self, manifestConfig=None, layers=None, schemaVersion=None, annotations=None
    ):
        super().__init__()

        self.newAttr(name="schemaVersion", attType=Versioned, required=True)

        # Config references a configuration object for a container, by digest.
        # The referenced configuration object is a JSON blob that the runtime uses to set up the container.
        self.newAttr(
            name="Config", attType=Descriptor, jsonName="config", required=True
        )

        # Layers is an indexed list of layers referenced by the manifest.
        self.newAttr(
            name="Layers", attType=[Descriptor], jsonName="layers", required=True
        )

        # Annotations contains arbitrary metadata for the image manifest.
        self.newAttr(name="Annotations", attType=dict, jsonName="annotations")

        self.add("Config", manifestConfig)
        self.add("Layers", layers)
        self.add("Annotations", annotations)
        self.add("schemaVersion", schemaVersion)

    def _validate(self):
        """custom validation function to ensure that Config and Layers mediaTypes
           are valid. By the time we get here, we know there is a Config object,
           and there can be one or more layers.
        """
        if not self._validateLayerMediaTypes() or not self._validateConfigMediaType():
            return False
        return True

    def _validateConfigMediaType(self):
        """validate the config media type.
        """
        # The media type of the config must be for the config
        manifestConfig = self.attrs.get("Config").value

        # Missing config is not valid
        if not manifestConfig:
            return False

        mediaType = manifestConfig.attrs.get("MediaType").value
        if not mediaType:
            return False

        if mediaType != MediaTypeImageConfig:
            bot.error(
                "config mediaType %s is invalid, should be %s"
                % (mediaType, MediaTypeImageConfig)
            )
            return False
        return True

    def _validateLayerMediaTypes(self):
        """validate the Layer Media Types
        """
        # These are valid mediaTypes for layers
        layerMediaTypes = [
            MediaTypeImageLayer,
            MediaTypeImageLayerGzip,
            MediaTypeImageLayerZstd,
            MediaTypeImageLayerNonDistributable,
            MediaTypeImageLayerNonDistributableGzip,
            MediaTypeImageLayerNonDistributableZstd,
        ]

        # No layers, not valid
        layers = self.attrs.get("Layers").value
        if not layers:
            return False

        # Check against valid mediaType Layers
        for layer in layers:
            mediaType = layer.attrs.get("MediaType").value
            if mediaType not in layerMediaTypes:
                bot.error("layer mediaType %s is invalid" % mediaType)
                return False

        return True
