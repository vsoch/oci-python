# Copyright (C) 2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


from opencontainers.struct import Struct
from opencontainers.logger import bot


class RepositoryList(Struct):
    """RepositoryList returns a catalog of repositories maintained on the registry."""

    def __init__(self, repositories=None):
        super().__init__()
        self.newAttr(
            name="Repositories", attType=[str], jsonName="repositories", required=True
        )
        self.add("Repositories", repositories or [])
