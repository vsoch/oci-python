#!/usr/bin/python

# Copyright (C) 2019-2022 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.struct import Struct, IntStruct, StrStruct
import os
import pytest


class StructTest(Struct):
    def __init__(
        self, Dict=None, List=None, Int=None, Str=None, Another=None, AnotherList=None
    ):
        super().__init__()

        self.newAttr(name="Dict", attType=dict)
        self.newAttr(name="List", attType=list)
        self.newAttr(name="Int", attType=IntStruct)
        self.newAttr(name="Str", attType=StrStruct)

        self.newAttr(name="Another", attType=AnotherStruct)
        self.newAttr(name="AnotherList", attType=[AnotherStruct])

        self.add("Dict", Dict)
        self.add("List", List)
        self.add("Int", Int)
        self.add("Str", Str)
        self.add("Another", Another)
        self.add("AnotherList", AnotherList)


class AnotherStruct(Struct):
    def __init__(self, Attr=None, AttrList=None):
        super().__init__()

        self.newAttr("Attr", attType=StrStruct)
        self.newAttr("AttrList", attType=[AnotherStruct])

        self.add("Attr", Attr)
        self.add("AttrList", AttrList)


def test_add(tmp_path):
    t = StructTest()

    t.add("Dict", {"a": "b"})
    t.add("List", [0, 1, 2])
    t.add("Int", 987)
    t.add("Str", "abc")

    t.add("List", 3)
    assert t.to_dict()["List"] == [0, 1, 2, 3]

    t.add("Dict", {"a": "c", "b": "d"})
    assert t.to_dict()["Dict"] == {"a": "b", "b": "d"}

    t.add("Int", 13)
    assert t.to_dict()["Int"] == 1000

    t.add("Str", "def")
    assert t.to_dict()["Str"] == "abcdef"

    # Test support for nested Structs (list of Structs containing list of Structs)
    t.add(
        "Another",
        AnotherStruct(
            Attr="test",
            AttrList=[
                {
                    "Attr": "abc",
                    "AttrList": [
                        {
                            "Attr": "onetwothree",
                        }
                    ],
                }
            ],
        ),
    )
    assert t.to_dict()["Another"] == {
        "Attr": "test",
        "AttrList": [
            {
                "Attr": "abc",
                "AttrList": [
                    {
                        "Attr": "onetwothree",
                    }
                ],
            }
        ],
    }

    # We can add Structs as object
    t.add("Another", AnotherStruct("test"))
    assert t.to_dict()["Another"] == {"Attr": "test"}

    # Or as Dict
    t.add("Another", {"Attr": "test"})
    assert t.to_dict()["Another"] == {"Attr": "test"}

    t.add("AnotherList", AnotherStruct("test"))
    assert t.to_dict()["AnotherList"] == [{"Attr": "test"}]

    t.add("AnotherList", {"Attr": "123"})
    t.add("AnotherList", [AnotherStruct("value"), {"Attr": "456"}])
    assert {"Attr": "test"} in t.to_dict()["AnotherList"]
    assert {"Attr": "123"} in t.to_dict()["AnotherList"]
    assert {"Attr": "value"} in t.to_dict()["AnotherList"]
    assert {"Attr": "456"} in t.to_dict()["AnotherList"]

    assert (
        StructTest(
            Dict={"a": "b", "b": "d"},
            List=[0, 1, 2, 3],
            Int=1000,
            Str="abcdef",
            Another={"Attr": "test"},
            AnotherList=[
                {"Attr": "test"},
                {"Attr": "123"},
                {"Attr": "value"},
                {"Attr": "456"},
            ],
        ).to_dict()
        == t.to_dict()
    )
