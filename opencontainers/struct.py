
# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from opencontainers.logger import bot
from datetime import datetime
import copy
import json


class StructAttr(object):
    '''A struct attribute holds a name, jsonName, value, attribute type,
       and if it's required or not. The name should hold the parameter name
       as reflected in the original (usually GoLang) implementation, while
       the jsonName is how it should be serialized to json.

       Parameters
       ==========
       name: the name (key) for the attribute
       attType: the attribute type (a python type), can be provided in list
       required: boolean if required or not
       jsonName: the name to serialize to json (not required, will use name)
       value: optionally, provide a value on init
       omitempty: if true, don't serialize with response.       
    '''
    def __init__(self, name, attType, required, 
                       jsonName=None, value=None, omitempty=True):
        self.name = name
        self.value = value
        self.attType = attType
        self.required = required
        self.jsonName = jsonName or name
        self.omitempty = omitempty

    def __str__(self):
        return "<opencontainers.struct.StructAttr-%s:%s>" %(self.name, self.value)

    def __repr__(self):
        return self.__str__()

    def _is_struct(self, attType=None):
        '''determine if an attType is another struct we need to populate
        '''
        # We can provide a nested attType to check
        if not attType:
            attType = self.attType
        try:
            return Struct in attType.__bases__
        except:
            return False

    def set(self, value):
        '''set a new value, and validate the type. Return true if set
        '''
        # First pass, it might be another object to add
        if self._is_struct():
            newStruct = self.attType()
            value = newStruct.load(value)

        # If it's a list with another type
        elif isinstance(self.attType, list) and self.attType:
            child = self.attType[0]

            # It's either a nested structure
            if self._is_struct(child):

                # If we have a list of values, generate them
                if isinstance(value, list):
                    values = []
                    for v in value:
                        newStruct = child()
                        values.append(newStruct.load(v))
                    value = values
                else:
                    newStruct = child()
                    value = newStruct.load(value)

        if self.validate_type(value):
            self.value = value
            return True
        return False


    def validate_datetime(self, value):
        '''validate a datetime string, but be generous to only check day,
           month, year. This is a road nobody wants to go down.
        '''
        value = value.split('T')[0]
        try: # "2015-10-31T22:22:56.015925234Z"
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False


    def validate_type(self, value):
        '''ensure that an attribute is of the correct type. If we are given
           a list as type, then the value within it is the type we are checking.
        '''
        # If it's a list with something inside
        if isinstance(self.attType, list):

            # If value not a list, invalid
            if not isinstance(value, list):
                return False

            # A type to check is inside
            if self.attType:
                attType = self.attType[0]
                for entry in value:
                    if not isinstance(entry, attType):
                        return False

        # If it's a datetime, should be valid string
        elif self.attType == datetime:
            return self.validate_datetime(value)

        # Otherwise, validate as is
        else:
            if not isinstance(value, self.attType):
                return False
        return True


class Struct(object):
    '''a Struct is a general base class that allows for printing 
       and validating a set of attributes according to their defined subclass.
       the subclass should have an init function that uses the functions
       here to add required attributes.
    '''
    def __init__(self):
        self.attrs = {}

    def newAttr(self, name, attType, required=False, jsonName=None, omitempty=True):
        '''add a new attribute, including a name, json key to dump,
           type, and if required. We don't need a value here. You can
           also update a current attribute here.

           Parameters
           ==========
           name: the name (key) for the attribute
           attType: the attribute type (a python type), can be provided in list
           required: boolean if required or not
           jsonName: the name to serialize to json (not required, will use name)
           omitempty: if true, don't serialize with response.
        '''
        self.attrs[name] = StructAttr(name=name, 
                                      attType=attType,
                                      required=required,
                                      jsonName=jsonName, 
                                      omitempty=omitempty)

    def _clear_values(self):
        '''if a load is done, we remove previously loaded values for any
           attributes
        '''
        for name, att in self.attrs.items():
            self.attrs[name].value = None        


    def to_dict(self):
        '''return a Struct as a dictionary, must be valid
        '''
        # A lookup of "empty" values based on types (mirrors Go)
        lookup = {str: "", int: None, list: [], dict: {}}

        if self.validate():      
            result = {}
            for name, att in self.attrs.items():
                if not att.value and att.omitempty:
                    continue
                if not att.value:
                    value = lookup.get(att.attType, [])
                    result[att.jsonName] = value            
                else:
                    result[att.jsonName] = att.value
            return result

    def to_json(self):
        '''get the dictionary of a struct and return pretty printed json
        '''
        result = self.to_dict()
        if result:
            result = json.dumps(result, indent=4)
        return result


    def add(self, name, value):
        '''add a value to an existing attribute, normally when used by a client
        '''
        if name not in self.attrs:
            bot.exit("%s is not a valid attribute." % name)

        attr = self.attrs[name]

        # Don't validate the type if provided is empty
        if value:
            if not attr.set(value):
                bot.exit("%s must be type %s." %(name, attr.attType))


    def load(self, content, validate=True):
        '''given a dictionary load into its respective object
           if validate is True, we require it to be completely valid.
        '''
        if not isinstance(content, dict):
            bot.exit("Please provide a dictionary or list to load.")

        # Look up attributes based on jsonKey
        lookup = self.generate_json_lookup()

        for key, value in content.items():
            att = lookup.get(key)
            if not att:
                bot.exit("%s is not a valid json attribute." % key)

        # If we get here, all parameters are valid, replace
        self._clear_values()

        for key, value in content.items():
            att = lookup.get(key)
            valid = att.set(value)
            if not valid and validate:
                bot.exit("%s (%s) is not valid." % (att.name, att.jsonName))
            self.attrs[att.name] = att

        return self


    def generate_json_lookup(self):
        '''based on the attributes, generate a jsonName lookup object.
           keys are jsonNames we find in the wild, names are attribute names.
        '''
        lookup = dict()
        for name, att in self.attrs.items():
            lookup[att.jsonName] = att
        return lookup


    def validate(self):
        '''validate goes through each attribute, and ensure that it is of the
           correct type, and if required it is defined. This is already done
           to some extent when add is called.
        '''
        for name, att in self.attrs.items():

            # Not required, undefined
            if not att.required and not att.value:
                continue

            # A required attribute cannot be None or empty
            if att.required and not att.value:
                bot.error('%s is required.' % name)
                return False

            # The attribute must match its type
            if not isinstance(att.value, att.attType):
                bot.error("%s should be type %s" %(name, att.attType))
                return False

        return True
