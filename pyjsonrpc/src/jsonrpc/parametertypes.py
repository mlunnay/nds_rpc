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

# JSON-RPC Parameter types for procedure descriptions

__all__ = ['ParameterBase', 'Boolean', 'Number', 'String', 'Array', 'Object', 'Any']

parameterStrings = ['bit', 'num', 'str', 'arr', 'obj', 'any']

class ParameterBase(object):
    def __init__(self, t, name=None):
        self._type = t
        self.name = name
    
    def getObject(self):
        """If name is supplied returns a dictionary with keys name and type, otherwise returns a string representation."""
        if self.name:
            return {"name": self.name, "type": self._type}
        else:
            return self._type

class Boolean(ParameterBase):
    def __init__(self, name=None):
        ParameterBase.__init__(self, 'bit', name)

class Number(ParameterBase):
    def __init__(self, name=None):
        ParameterBase.__init__(self, 'num', name)
        
class String(ParameterBase):
    def __init__(self, name=None):
        ParameterBase.__init__(self, 'str', name)

class Array(ParameterBase):
    def __init__(self, name=None):
        ParameterBase.__init__(self, 'arr', name)

class Object(ParameterBase):
    def __init__(self, name=None):
        ParameterBase.__init__(self, 'obj', name)

class Any(ParameterBase):
    def __init__(self, name=None):
        ParameterBase.__init__(self, 'any', name)
        