# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct
from opencontainers.digest import Digest

from datetime import datetime


class ImageConfig(Struct):
    """ImageConfig defines the execution parameters which should be used as a
       base when running a container using an image.
    """

    def __init__(
        self,
        user=None,
        ports=None,
        env=None,
        entrypoint=None,
        cmd=None,
        volumes=None,
        workingDir=None,
        labels=None,
        stopSignal=None,
    ):

        super().__init__()

        # User defines the username or UID which the process in the container should run as.
        self.newAttr(name="User", attType=str)

        # ExposedPorts a set of ports to expose from a container running this image.
        self.newAttr(name="ExposedPorts", attType=dict)

        # Env is a list of environment variables to be used in a container.
        self.newAttr(
            name="Env", attType=[str], regexp="^(?P<var_name>.+?)=(?P<var_value>.+)"
        )

        # Entrypoint defines a list of arguments to use as the command to execute when the container starts.
        self.newAttr(name="Entrypoint", attType=list)

        # Cmd defines the default arguments to the entrypoint of the container.
        self.newAttr(name="Cmd", attType=list)

        # Volumes is a set of directories describing where the process is likely write data specific to a container instance.
        self.newAttr(name="Volumes", attType=dict)

        # WorkingDir sets the current working directory of the entrypoint process in the container.
        self.newAttr(name="WorkingDir", attType=str)

        # Labels contains arbitrary metadata for the container.
        self.newAttr(name="Labels", attType=dict)

        # StopSignal contains the system call signal that will be sent to the container to exit.
        self.newAttr(name="StopSignal", attType=str)

        self.add("User", user)
        self.add("ExposedPorts", ports)
        self.add("Env", env)
        self.add("Entrypoint", entrypoint)
        self.add("Cmd", cmd)
        self.add("Volumes", volumes)
        self.add("WorkingDir", workingDir)
        self.add("Labels", labels)
        self.add("StopSignal", stopSignal)


class RootFS(Struct):
    """ RootFS describes a layer content addresses
    """

    def __init__(self, rootfs_type=None, diff_ids=None):
        super().__init__()

        # Type is the type of the rootfs, different from GoLang since type can't be used
        self.newAttr(name="RootFSType", attType=str, omitempty=False, jsonName="type")

        # DiffIDs is an array of layer content hashes (DiffIDs), in order from bottom-most to top-most.
        self.newAttr(
            name="DiffIDs", attType=[Digest], omitempty=False, jsonName="diff_ids"
        )

        self.add("RootFSType", rootfs_type)
        self.add("DiffIDs", diff_ids)


class History(Struct):
    """History describes the history of a layer.
    """

    def __init__(
        self, created=None, created_by=None, author=None, comment=None, empty_layer=None
    ):

        super().__init__()

        # Created is the combined date and time at which the layer was created, formatted as defined by RFC 3339, section 5.6.
        self.newAttr("Created", attType=datetime, jsonName="created")

        # CreatedBy is the command which created the layer.
        self.newAttr("CreatedBy", attType=str, jsonName="created_by")

        # Author is the author of the build point.
        self.newAttr("Author", attType=str, jsonName="author")

        # Comment is a custom message set when creating the layer.
        self.newAttr("Comment", attType=str, jsonName="comment")

        # EmptyLayer is used to mark if the history item created a filesystem diff.
        self.newAttr("EmptyLayer", attType=bool, jsonName="empty_layer")

        self.add("Created", created)
        self.add("CreatedBy", created_by)
        self.add("Author", author)
        self.add("Comment", comment)
        self.add("EmptyLayer", empty_layer)


class Image(Struct):
    """Image is the JSON structure which describes some basic information about 
       the image. This provides the `application/vnd.oci.image.config.v1+json` 
       mediatype when marshalled to JSON.
    """

    def __init__(
        self,
        created=None,
        author=None,
        arch=None,
        imageOS=None,
        imageConfig=None,
        rootfs=None,
        hist=None,
    ):

        super().__init__()

        # Created is the combined date and time at which the image was created, formatted as defined by RFC 3339, section 5.6.
        self.newAttr("Created", attType=datetime, jsonName="created")

        # Author defines the name and/or email address of the person or entity which created and is responsible for maintaining the image.
        self.newAttr("Author", attType=str, jsonName="author")

        # Architecture is the CPU architecture which the binaries in this image are built to run on.
        self.newAttr(
            name="Architecture", attType=str, jsonName="architecture", required=True
        )

        # OS is the name of the operating system which the image is built to run on.
        self.newAttr("OS", attType=str, jsonName="os", required=True)

        # Config defines the execution parameters which should be used as a base when running a container using the image.
        self.newAttr("Config", attType=ImageConfig, jsonName="config")

        # RootFS references the layer content addresses used by the image.
        self.newAttr("RootFS", attType=RootFS, jsonName="rootfs", required=True)

        # History describes the history of each layer.
        self.newAttr("History", attType=[History], jsonName="history")

        self.add("Created", created)
        self.add("Author", author)
        self.add("Architecture", arch)
        self.add("OS", imageOS)
        self.add("Config", imageConfig)
        self.add("RootFS", rootfs)
        self.add("History", hist)
