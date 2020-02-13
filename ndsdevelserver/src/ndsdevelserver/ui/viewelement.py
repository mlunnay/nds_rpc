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

"""This module provides the ViewElement base class for user interface representations."""

__all__ = ['ViewElement']

class ViewElement(object):
    """This is a base class for user interface items."""
    
    __id_store = {}
    __next_id = 1
    
    def __init__(self):
        """ViewElement initialiser."""
        
        self.container = None
        self.id = None
        
    def set_container(self, container):
        """Set the container this ViewElement is held by.
        
        @param container: A ViewElement subclass the holds this item.
        @raise ValueError: Raised if container is not a subclass of ViewElement.
        
        """
        
        if not isinstance(container, ViewElement):
            raise ValueError('container must be a subclass of ViewElement.')
        
        self.container =  container
    
    def get_container(self):
        """Return the container that holds this ViewElement."""
        
        return self.container
    
    def set_id(self, id):
        """Set the id for this ViewElement.
        
        @param id: A unique identifier for this ViewElement.
        @raise ValueError: Raised if id is not unique.
        
        """
        
        if id == self.id:
            return  # nothing to do as no-op
        if id in self.__id_store:
            raise ValueError('ViewElement id %s is already assigned.' % id)
        
        # remove the old id if applicable
        if self.id != None and self.id in seld.__id_store:
            del self.__id_store[id]
        
        self.__id_store[id] = self
    
    def get_id(self):
        """Return the current unique id of this ViewElement, creating a new id
        if one does not yet exist."""
        
        if self.id == None:
            while self.__next_id in self.__id_store:
                self.__next_id += 1
            self.id = self.__next_id
            self.__id_store[self.id] = self
            self.id += 1
        
        return self.id
    
    def __eq__(self, other):
        """ViewElement comparison.
        
        @raise NotImplemented: Raised if other is not a ViewElement subclass.
        
        """
        
        if not isinstance(other, ViewElement):
            raise NotImplemented('ViewElement only supports comparison with other ViewElement subclasses.')
        
        return self.get_id() == other.get_id()
