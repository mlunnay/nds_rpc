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

__all__ = ['Config', 'default_config']

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import types

class Config:
    """A wrapper around a yaml document for application configuration."""
    
    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        try:
            self.data = load(open(filename), Loader=Loader)
        except:
            # the CLoader has problems with throwing exceptions so call the python version here to get a meaningful exception
            load(open(filename))
    
    def reload(self):
        self.data = load(open(self.filename), Loader=Loader)
    
    def save(self, filename=''):
        if filename:
            cf = open(filename, 'w')
        else:
            cf = open(self.filename, 'w')
        
        dump(self.data, cf, Dumper=Dumper)
        cf.close()
    
    def __contains__(self, name):
        """Return true if the name is contained in this configuration."""
        return name in self.data
    
    def __getitem__(self, name):
        return self.data[name]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __delitem__(self, key):
        del self.data[key]
    
    def __len__(self):
        return len(self.data)
    
    def __str__(self):
        return str(self.data)
    
    def keys(self):
        return self.data.keys()
    
    def has_key(self, key):
        return self.data.has_key(key)
    
    def get(self, key, default=None):
        if self.data.has_key(key):
            return self.data[key]
        else:
            return default

_defaultConfig = None

def default_config(filename=None):
    global _defaultConfig
    
    if _defaultConfig:
        return _defaultConfig
    
    if filename:
        _defaultConfig = Config(filename)
        return _defaultConfig
    
    return None
