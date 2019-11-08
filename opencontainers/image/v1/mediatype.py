# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


# MediaTypeDescriptor specifies the media type for a content descriptor.
MediaTypeDescriptor = "application/vnd.oci.descriptor.v1+json"

# MediaTypeLayoutHeader specifies the media type for the oci-layout.
MediaTypeLayoutHeader = "application/vnd.oci.layout.header.v1+json"

# MediaTypeImageManifest specifies the media type for an image manifest.
MediaTypeImageManifest = "application/vnd.oci.image.manifest.v1+json"

# MediaTypeImageIndex specifies the media type for an image index.
MediaTypeImageIndex = "application/vnd.oci.image.index.v1+json"

# MediaTypeImageLayer is the media type used for layers referenced by the manifest.
MediaTypeImageLayer = "application/vnd.oci.image.layer.v1.tar"

# MediaTypeImageLayerGzip is the media type used for gzipped layers
# referenced by the manifest.
MediaTypeImageLayerGzip = "application/vnd.oci.image.layer.v1.tar+gzip"

# MediaTypeImageLayerZstd is the media type used for zstd compressed
# layers referenced by the manifest.
MediaTypeImageLayerZstd = "application/vnd.oci.image.layer.v1.tar+zstd"

# MediaTypeImageLayerNonDistributable is the media type for layers referenced by
# the manifest but with distribution restrictions.
MediaTypeImageLayerNonDistributable = (
    "application/vnd.oci.image.layer.nondistributable.v1.tar"
)

# MediaTypeImageLayerNonDistributableGzip is the media type for
# gzipped layers referenced by the manifest but with distribution
# restrictions.
MediaTypeImageLayerNonDistributableGzip = (
    "application/vnd.oci.image.layer.nondistributable.v1.tar+gzip"
)

# MediaTypeImageLayerNonDistributableZstd is the media type for zstd#
# compressed layers referenced by the manifest but with distribution
# restrictions.
MediaTypeImageLayerNonDistributableZstd = (
    "application/vnd.oci.image.layer.nondistributable.v1.tar+zstd"
)

# MediaTypeImageConfig specifies the media type for the image configuration.
MediaTypeImageConfig = "application/vnd.oci.image.config.v1+json"
