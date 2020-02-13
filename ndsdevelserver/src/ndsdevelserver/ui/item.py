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

"""This module provides the Item class which represents an element in a user interface."""

__all__ = ['Item']

from viewelement import ViewElement

class Item(ViewElement):
    """An Item represents an element in a user interface."""
    
    def __init__(self, name, editor=None, id=None, label=None, tool_tip=None,
                 help=None, validator=None, read_only=False):
        '''Item initialiser.
        
        @param name: The name of the item.
        @param editor: An optional editor factory to use instead of the default editor.
        @param default: Optional default value for this item.
        @param id: An optional unique identifier for this Item.
        @param label: An optional label for this Item, if omitted name will be
            used instead.
        @param tool_tip: An optional tool tip for the editor.
        @param help: Optional string containing help for this Item.
        @param validator: An optional wx.Validator to be used by the editor for this item.
        @param read_only: If True the Item will be uneditable.
        
        '''
        
        self.name = name
        self.editor = editor
        if id != None:
            self.set_id(id)
        self.label = label
        self.tool_tip = tool_tip
        self.help = help
        self.validator = validator
        self.read_only = read_only
        
    def get_label(self):
        """Return the label for this item."""
        
        if self.label != None:
            return self.label
        else:
            return self.name
    
    def has_help(self):
        """Return True if this item has help associated with it."""
        
        return self.help != None
    
    def get_help(self):
        """Return the help string associated with this item."""
        
        return self.help
    
    def get_tooltip(self):
        """Return the tooltip for this item."""
        
        return self.tool_tip
