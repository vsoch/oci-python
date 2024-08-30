# Copyright (C) 2019-2022 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from opencontainers.image.specs import Versioned
from opencontainers.logger import bot
from opencontainers.mediatype import RFC6838
from .mediatype import MediaTypeImageIndex, MediaTypeImageManifest
from .descriptor import Descriptor
import re


class Index(Struct):
    """
    Index references manifests for various platforms.

    This structure provides `application/vnd.oci.image.index.v1+json`
    mediatype when marshalled to JSON.
    """

    def __init__(self, manifests=None, schemaVersion=None, annotations=None,
                 mediaType=None, artifactType=None, subject=None):
        super().__init__()

        self.newAttr(name="schemaVersion", attType=Versioned, required=True)

        # MediaType must be "application/vnd.oci.image.index.v1+json" if given
        self.newAttr(
            name="MediaType",
            attType=str,
            jsonName="mediaType",
        )

        # ArtifactType must be a valid media type according to RFC6838
        self.newAttr(
            name="ArtifactType",
            attType=str,
            jsonName="artifactType",
            regexp=RFC6838,
        )

        # Manifests references platform specific manifests.
        self.newAttr(
            name="Manifests", attType=[Descriptor], jsonName="manifests", required=True
        )

        # Subject is a descriptor of another manifest
        self.newAttr(name="Subject", attType=Descriptor, jsonName="subject")

        # Annotations contains arbitrary metadata for the image index.
        self.newAttr(name="Annotations", attType=dict, jsonName="annotations")

        self.add("schemaVersion", schemaVersion)
        self.add("MediaType", mediaType)
        self.add("ArtifactType", artifactType)
        self.add("Manifests", manifests)
        self.add("Subject", subject)
        self.add("Annotations", annotations)

    def _validate(self):
        """
        Validation functions for an index.

        custom validation function to ensure that Manifests mediaTypes
        are valid.
        """
        valid = True

        valid_types = [MediaTypeImageManifest, MediaTypeImageIndex]

        mediaType = self.attrs.get("MediaType")
        if mediaType.value and mediaType.value != MediaTypeImageIndex:
            bot.error("%s must be %s" % (mediaType, MediaTypeImageIndex))
            valid = False


        manifests = self.attrs.get("Manifests").value
        if manifests:
            for manifest in manifests:
                mediaType = manifest.attrs.get("MediaType")
                if mediaType.value not in valid_types:

                    # Case 1: it's a custom media type (allowed) but give warning
                    if mediaType.validate_regexp(mediaType.value):
                        bot.warning(
                            "%s is valid, but not registered." % mediaType.value
                        )

                    # Case 2: not valid and doesn't match regular expression
                    else:
                        bot.error("%s is not valid for index manifest." % mediaType)
                        valid = False

        return valid
