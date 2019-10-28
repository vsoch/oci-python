#!/usr/bin/python

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.image.v1 import Image
import os
import pytest


config_invalid_os = {
    "architecture": "amd64",
    "os": 123,
    "rootfs": {
      "diff_ids": [
        "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"
      ],
      "type": "layers"
    }
}

config_invalid_user = {
    "created": "2015-10-31T22:22:56.015925234Z",
    "author": "Alyssa P. Hacker <alyspdev@example.com>",
    "architecture": "amd64",
    "os": "linux",
    "config": {
        "User": 1234
    },
    "rootfs": {
      "diff_ids": [
        "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"
      ],
      "type": "layers"
    }
}

config_invalid_history = {
    "history": "should be an array",
    "architecture": "amd64",
    "os": "linux",
    "rootfs": {
      "diff_ids": [
        "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"
      ],
      "type": "layers"
    }
}

config_invalid_env = {
    "architecture": "amd64",
    "os": "linux",
    "config": {
        "Env": [
            7353
        ]
    },
    "rootfs": {
      "diff_ids": [
        "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"
      ],
      "type": "layers"
    }
}


def test_example_config(tmp_path):
    '''test creation of a simple sink plugin
    '''
    image = Image()

    # OS is int, and is invalid
    with pytest.raises(SystemExit):
        image.load(config_invalid_os)

    # User should be string
    with pytest.raises(SystemExit):
        image.load(config_invalid_user)

    # History should be list
    with pytest.raises(SystemExit):
        image.load(config_invalid_history)

    # stopped here - investigate this case (Env should be invalid)
    # Env is numeric, must be string
    with pytest.raises(SystemExit):
        image.load(config_invalid_env)

