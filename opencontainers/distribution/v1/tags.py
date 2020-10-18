# Copyright (C) 2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


from opencontainers.struct import Struct
from opencontainers.logger import bot


class TagList(Struct):
    """TagList is a list of tags for a given repository."""

    def __init__(self, name, tags=None):
        super().__init__()
        self.newAttr(name="Name", attType=str, jsonName="name", required=True)
        self.newAttr(name="Name", attType=[str], jsonName="tags", required=True)
        self.add("Name", name)
        self.add("Tags", tags or [])
