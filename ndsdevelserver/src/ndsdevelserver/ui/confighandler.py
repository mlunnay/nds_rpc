# Copyright (c) 2008, Michael Lunnay <mlunnay@gmail.com.au>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""This module provides the ConfigHandler base class that provied validation
and value coercion, and the default handler classes.

"""

__all__ = ['ConfigHandler', 'Type', 'StringType', 'OneOf', 'Mapping', 'List', 'Set']

import types
import sys

_sequences = (list, tuple)

class ConfigHandler(object):
    """This base class provides validation and data coercion for ConfigValidator."""
    
    # subclasses should set this if their default editor is different from TextEditor
    default_editor = 'TextEditor'
    
    def validate(self, data):
        """This method is called to validate data.
        
        @param data: The data to validate.
        @return: True if data is valid, False otherwise.
        
        """
        
        # by default all data is valid
        return True
    
    def coerce_to_window(self, data):
        """This method may be overridden by subclasses to perform coercion on
        the data before it is set as the value of the control.
        
        @param data: The data to coerce.
        @return: The coerced data.
        
        """
        
        # by default convert it to a string
        return str(data)
    
    def coerce_from_window(self, data):
        """This method may be overridden by subclasses to perform coercion on
        the data before it is written to the config.
        
        @param data: The data to coerce.
        @return: The coerced data.
        
        """
        
        # by default do nothing and just return what was passed in
        return data
    
    def info(self):
        """Subclasses may override this method to provide a meaningful string
        to describe a valid value.
        
        """
        
        return 'a valid value.'
    
    def get_default_editor(self):
        """Return the default editor for this ConfigHandler."""
        
        return self.default_editor

class Type(ConfigHandler):
    """Assures that the value assigned to an option is of the correct type(s)."""
    
    def __init__(self, types_):
        """Initialiser method.
        
        @param types: The type or sequence of types that the option must adhere to.
        
        """
        
        self.types = []
        if not isinstance(types_, types.TypeType):
            if isinstance(types_, _sequences) and len(types_) != 0:
                for t in types_:
                    if not isinstance(t, TypeType):
                        self.types.append(type(t))
                    else:
                        self.types.append(t)
            else:
                self.types.append(type(types_))
        else:
            self.types.append(types_)
    
    def validate(self, data):
        for type_ in self.types:
            if type(data) == type_:
                return True
        
        return False
    
    def info(self):
        if len(self.types) == 1:
            plural = ''
        else:
            plural = "'s"
        return 'of type%s %s' % (plural, ' '.join([x.__name__ for x in self.types]))

class StringType(ConfigHandler):
    """Assures that the value assigned to an option is of the correct type(s)."""
    
    def __init__(self, types_=[types.StringType]):
        """Initialiser method.
        
        @param types: The type or sequence of types that the option must
            adhere to. The types must be able to be constructed from a string.
        
        """
        
        self.types = []
        if not isinstance(types_, types.TypeType):
            if isinstance(types_, _sequences) and len(types_) != 0:
                for t in types_:
                    if not isinstance(t, types.TypeType):
                        self.types.append(type(t))
                    else:
                        self.types.append(t)
            else:
                self.types.append(type(types_))
        else:
            self.types.append(types_)
    
    def validate(self, data):
        for type_ in self.types:
            try:
                type_(data)
                return True
            except:
                return False
    
    def coerce_from_window(self, data):
        for type_ in self.types:
            try:
                var = type_(data)
                return var
            except:
                pass
    
    def coerce_to_window(self, data):
        return str(data)
    
    def info(self):
        if len(self.types) == 1:
            plural = ''
        else:
            plural = "'s"
        return 'of type%s %s' % (plural, ' '.join([x.__name__ for x in self.types]))

class OneOf(ConfigHandler):
    """Assures that the value is one of a given set of values."""
    
    default_editor = 'ChoiceEditor'
    
    def __init__(self, values):
        """Initialiser method.
        
        @param values: A sequence of values the data must conform to.
        
        """
        
        self.values = []
        if not isinstance(values, (str, unicode)):
            if isinstance(values, _sequences) and len(values) != 0:
                for t in values:
                    if not isinstance(t, (str, unicode)):
                        self.values.append(str(t))
                    else:
                        self.values.append(t)
            else:
                self.values.append(str(values))
        else:
            self.values.append(values)
    
    def validate(self, data):
        return data in self.values
    
    def info(self):
        return 'one of %s' % ', '.join(self.values)

class Mapping(ConfigHandler):
    """This validates that the value is one of the keys of a dictionary, and
    coerces the result to the value of that key in the dictionary."""
    
    def __init__(self, map, value_handler=None):
        """Initalisation method.
        
        @param map: A dictionary mapping gui values to config values.
        @param value_handler: Optional handler that is applied to validation
            for key values that are not in map, and all coercions.
        
        """
        
        self.map = map
        self.value_handler = value_handler
    
    def validate(self, data):
        if not data in map:
            if self.value_handler and self.value_handler.validate(data):
                return True
            else:
                return False
        
        return True
    
    def coerce_from_window(self, data):
        val = self.map.get(data, data)
        if self.value_handler:
            return self.value_handler.coerce_from_window(data)
        else:
            return val
    
    def coerce_to_window(self, data):
        for key, value in self.map.iteritems():
            if type(data) == type(value) and data == value:
                return key
        if self.value_handler:
            return self.value_handler.coerce_to_window(data)
        else:
            return str(data)
    
    def info(self):
        out = 'must be '
        if self.value_handler:
            out += '%s or ' % self.value_handler.info()
        out += 'one of %s' % ' '.join(self.map)
        return out

class List(ConfigHandler):
    """Config handler for lists."""
    
    default_editor = 'ListEditor'
    
    def __init__(self, min_len=0, max_len=sys.maxint, handler=None):
        '''List Initialiser.
        
        @param min_len: The minimum length of the list.
        @param max_len: The maximum length of the list.
        @param handler: Either a single handler that all values of the list must
            conform to, or a sequence of handlers one for each value in the list.
            If this is a sequence then min_len and max_len are ignored and the list
            must have the same length as this sequence.
        
        '''
        
        self.min_len = min_len
        self.max_len = max_len
        self.handler = traits
    
    def validate(self, data):
        """Validate the list."""
        
        if self.handler and isinstance(self.handler, _sequences):
            if len(data) != len(self.handler):
                return False
            for d, handler in zip(data, self.handler):
                if handler.validate(d) == False:
                    return False
            return True
        elif self.handler:
            for d in data:
                if self.handler.validate(d) == False:
                    return False
            return True
        
        length = len(data)
        if len < self.min_len or len > self.max_len:
            return False
        
        return True
    
    def coerce_to_window(self, data):
        return data
    
    def info(self):
        out = 'a list'
        if self.min_len > 0 and self.max_len < sys.maxint:
            out += ' with length '
            if self.min_len == self.max_len:
                out += str(self.min_len)
            elif self.min_len == 0:
                out += 'less than %d' % self.max_len
            elif self.max_len == sys.maxint:
                out += 'greater than %d' % self.min_len
            else:
                out += 'between %d and %d' % (self.min_len, self.max_len)
        if self.handler and isinstance(self.handler, ConfigHandler):
            out += ' containing %s' % self.handler.info()
        return out

class Set(ConfigHandler):
    """This config handler validates a list that contains only values from a given set."""
    
    default_editor = 'SetEditor'
    
    def __init__(self, values, min_len=0, max_len=sys.maxint):
        '''Set initialiser.
        
        @param values: A list of strings that data must conform to.
        @param min_len: The minimum length of the list.
        @param max_len: The maximum length of the list.
        
        '''
        
        self.set = frozenset(values)
        self.min_len = min_len
        self.max_len = max_len
    
    def validate(self, data):
        """Make sure that all strings in data are in self.set."""
        
        return set(data).difference(self.set) == 0
    
    def coerce_to_window(self, data):
        return data
