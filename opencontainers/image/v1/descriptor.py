
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from opencontainers.digest import Digest


class Descriptor(Struct):
    '''Descriptor describes the disposition of targeted content.
       This structure provides `application/vnd.oci.descriptor.v1+json`
       mediatype when marshalled to JSON.
    '''
    def __init__(self, digest, size, mediatype=None, urls=None, 
                       annotations=None, platform=None):
   
        # MediaType is the media type of the object this schema refers to.
        self.newAttr(name="MediaType", attType=str, jsonName="mediaType")

        # Digest is the digest of the targeted content.
        self.newAttr(name="Digest", attType=Digest, jsonName="digest", required=True)

        # Size specifies the size in bytes of the blob.
        self.newAttr(name="Size", attType=int, jsonName="size", required=True)

        # URLs specifies a list of URLs from which this object MAY be downloaded
        self.newAttr(name="URLs", attType=[str], jsonname="urls")

        # Annotations contains arbitrary metadata relating to the targeted content.
        self.newAttr(name="Annotations", attType=dict, jsonName="annotations")

        # Platform describes the platform which the image in the manifest runs on.
        # This should only be used when referring to a manifest.
        self.newAttr(name="Platform", attType=Platform, jsonName="platform")

        self.add("Digest", digest)
        self.add("Size", size)
        self.add("MediaType", mediatype)
        self.add("URLs", urls)
        self.add("Annotations", annotations)
        self.add("Platform", platform)


class Platform(Struct):
    '''Platform describes the platform which the image in the manifest runs on.
    '''
    def __init__(self, arch, platform_os, 
                       os_version=None, os_features=None, variant=None):

        # Architecture field specifies the CPU architecture, for example
        # `amd64` or `ppc64`.
        self.newAttr(name="Architecture", attType=str, jsonName="architecture", required=True)

        # OS specifies the operating system, for example `linux` or `windows`.
        self.newAttr(name="OS", attType=str, jsonName="os", required=True)

        # OSVersion is an optional field specifying the operating system
        # version, for example on Windows `10.0.14393.1066`.
        self.newAttr(name="OSVersion", attType=str, jsonName="os.version")

        # OSFeatures is an optional field specifying an array of strings,
        # each listing a required OS feature (for example on Windows `win32k`).
        self.newAttr(name="OSFeatures", attType=[str], jsonName="os.features")

        # Variant is an optional field specifying a variant of the CPU, for
        # example `v7` to specify ARMv7 when architecture is `arm`.
        self.newAttr(name="Variant", attType=str, jsonName="variant")

        self.add("Architecture", arch)
        self.add("OS", platform_os)
        self.add("OSVersion", os_verison)
        self.add("OSFeatures", os_features)
        self.add("Variant", variant)
