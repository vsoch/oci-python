#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.image.v1 import ImageLayout
import os
import pytest


def test_imagelayout(tmp_path):
    """test creation of an opencontainers ImageLayout
    """
    layout = ImageLayout()

    # expected faulure:  imageLayoutVersion does not match pattern or type
    with pytest.raises(SystemExit):
        layout.load({"imageLayoutVersion": 1.0})

    with pytest.raises(SystemExit):
        layout.load({"imageLayoutVersion": "1.0"})

    # valid layout
    layout.load({"imageLayoutVersion": "1.0.0"})
