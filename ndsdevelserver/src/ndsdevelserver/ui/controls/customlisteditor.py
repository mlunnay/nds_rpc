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

"""This module provides a list editor for lists with custom item addition."""

__all__ = ['CustomListEditor']

import wx
import images

# Style defines
CLE_ALLOW_NEW = 0x1
CLE_ALLOW_EDIT = 0x2
CLE_ALLOW_DELETE = 0x4
CLE_STRING = 0x8
CLE_LIST = 0x10
CLE_DICT = 0x20

class CustomListEditor(wx.Panel):
    """This is a list editor with custom actions for adding and editing items,
    and custom button images.
    
    """
        
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, data=[],
                 style=CLE_ALLOW_NEW|CLE_ALLOW_EDIT|CLE_ALLOW_DELETE|CLE_STRING,
                 validator=wx.DefaultValidator, name='CustomListEditor',
                 object_name='item', add_bitmap=None, edit_bitmap=None,
                 remove_bitmap=None, up_bitmap=None, down_bitmap=None,
                 add_callback=None, edit_callback=None, object_key=None):
        """Initialiser.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param data: A list of objects to initialise the control with.
        @param style: The style flags for the control:
            B{CLE_ALLOW_NEW} - Allow new items to be added to the list.
            B{CLE_ALLOW_EDIT} - Allow items to be edited.
            B{CLE_ALLOW_DELETE} - Allow items to be deleted from the list.
            B{CLE_STRING} - The list holds string objects.
            B{CLE_LIST} - The list holds objects represented as lists.
            B{CLE_DICT} - The list holds objects represented as dictionaries. 
        @param validator: Window validator.
        @param name: The name of this control.
        @param object_name: Descriptive name for the objects this control contains.
        @param add_bitmap: A custom image for the add item button.
        @param edit_bitmap: A custom image for the edit item button.
        @param remove_bitmap: A custom image for the remove item button.
        @param up_bitmap: A custom image for the move item up button.
        @param down_bitmap: A custom image for the move item down button.
        @param add_callback: A callback function for when the user clicks on the add button.
        @param edit_callback: A callback function for when the user clicks on the edit button.
        @param object_key: The key value for looking up an objects string representation.
        
        """
        
        self.modified = False
        self.style = style
        self.add_callback = add_callback
        self.edit_callback = edit_callback
        
        if (style & CLE_LIST or style & CLE_DICT) and object_key == None:
            raise ValueError('object_key must be supplied if style contains either CLE_LIST or CLE_DICT')
        self.object_key = object_key
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        
        self.list = wx.ListBox(self)
        self.SetValue(data)
        
        if style & CLE_ALLOW_NEW:
            if add_bitmap != None:
                bmp = add_bitmap
            else:
                bmp = images.getAddBitmap()
            self.add = wx.BitmapButton(self, -1, bmp)
            self.add.SetToolTipString('Add %s' % object_name)
            self.Bind(wx.EVT_BUTTON, self.OnAdd, self.add)
        if style & CLE_ALLOW_EDIT:
            if edit_bitmap != None:
                bmp = edit_bitmap
            else:
                bmp = images.getPencilBitmap()
            self.edit = wx.BitmapButton(self, -1, bmp)
            self.edit.SetToolTipString('Update %s' % object_name)
            self.Bind(wx.EVT_BUTTON, self.OnEdit, self.edit)
        if style & CLE_ALLOW_DELETE:
            if remove_bitmap != None:
                bmp = remove_bitmap
            else:
                bmp = images.getDeleteBitmap()
            self.delete = wx.BitmapButton(self, -1, bmp)
            self.delete.SetToolTipString('Delete %s' % object_name)
            self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete)
        if up_bitmap != None:
            bmp = up_bitmap
        else:
            bmp = images.getArrow_UpBitmap()
        self.up = wx.BitmapButton(self, -1, bmp)
        self.up.SetToolTipString('Move %s Up' % object_name)
        if down_bitmap != None:
            bmp = down_bitmap
        else:
            bmp = images.getArrow_DownBitmap()
        self.down = wx.BitmapButton(self, -1, bmp)
        self.down.SetToolTipString('Move %s Down' % object_name)
        
        # layout
        spacing = 4 # spacing between elements
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.list, 1, wx.EXPAND)
        bsizer = wx.BoxSizer(wx.VERTICAL)
        if style & CLE_ALLOW_NEW:
            bsizer.Add(self.add, 0, wx.BOTTOM, spacing)
        if style & CLE_ALLOW_EDIT:
            bsizer.Add(self.edit, 0, wx.BOTTOM, spacing)
        if style & CLE_ALLOW_DELETE:
            bsizer.Add(self.delete, 0, wx.BOTTOM, spacing)
        bsizer.Add(self.up, 0, wx.BOTTOM, spacing)
        bsizer.Add(self.down)
        hsizer.Add(bsizer, 0, wx.LEFT, spacing)
        
        self.SetSizerAndFit(hsizer)
        
        self.Bind(wx.EVT_BUTTON, self.OnUp, self.up)
        self.Bind(wx.EVT_BUTTON, self.OnDown, self.down)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.list)
    
    def OnAdd(self, event):
        """Add button event handler.
        
        Calls the supplied callback which should expect no arguments and return
        either a string, sequence or dictionary depending on the value set for style.
        
        """
        
        if self.add_callback != None:
            data = self.add_callback()
            if self.style & CLE_STRING and not isinstance(data, (str, unicode)):
                    raise TypeError('The add callback must return a string')
            elif self.style & CLE_LIST and not isinstance(data, (list, tuple)):
                    raise TypeError('The add callback must return a sequence')
            elif self.style & CLE_DICT and not isinstance(data, dict):
                    raise TypeError('The add callback must return a dictionary')
            
            self.modified = True
            if self.style & CLE_LIST or self.style & CLE_DICT:
                self.list.Append(data[self.object_key], data)
            else:
                self.list.Append(data, data)
    
    def OnEdit(self, event):
        """Edit button handler.
        
        Calls the supplied callback which should the object to edit as its
        argument and return either a string, sequence or dictionary depending
        on the value set for style.
        
        """
        
        index = self.list.GetSelection()
        
        if self.edit_callback != None and index >= 0:
            data = self.edit_callback(self.list.GetClientData(index))
            if self.style & CLE_STRING and not isinstance(data, (str, unicode)):
                    raise TypeError('The add callback must return a string')
            elif self.style & CLE_LIST and not isinstance(data, (list, tuple)):
                    raise TypeError('The add callback must return a sequence')
            elif self.style & CLE_DICT and not isinstance(data, dict):
                    raise TypeError('The add callback must return a dictionary')
            
            self.modified = True
            if self.style & CLE_LIST or self.style & CLE_DICT:
                self.list.SetString(index, data[self.object_key])
                self.list.SetClientData(index, data)
            else:
                self.list.SetString(index, data)
                self.list.SetClientData(index, data)
    
    def OnDelete(self, event):
        index = self.list.GetSelection()
        if index != -1:
            self.modified = True
            self.list.Delete(index)
            
            if self.style & CLE_ALLOW_DELETE:
                self.delete.Disable()
            if self.style & CLE_ALLOW_EDIT:
                self.edit.Disable()
            self.up.Disable()
            self.down.Disable()
    
    def OnUp(self, event):
        index = self.list.GetSelection()
        if index > 0:
            tmp = self.list.GetString(index)
            tmp_data = self.list.GetClientData(index)
            self.list.SetString(index, self.list.GetString(index - 1))
            self.list.SetClientData(index, self.list.GetClientData(index - 1))
            self.list.SetString(index - 1, tmp)
            self.list.SetClientData(index - 1, tmp_data)
            self.list.SetSelection(index - 1)
            self.UpdateButtons()
    
    def OnDown(self, event):
        index = self.list.GetSelection()
        if index < self.list.GetCount() - 1:
            tmp = self.list.GetString(index)
            tmp_data = self.list.GetClientData(index)
            self.list.SetString(index, self.list.GetString(index + 1))
            self.list.SetClientData(index, self.list.GetClientData(index + 1))
            self.list.SetString(index + 1, tmp)
            self.list.SetClientData(index + 1, tmp_data)
            self.list.SetSelection(index + 1)
            self.UpdateButtons()
    
    def OnListBox(self, event):
        index = self.list.GetSelection()
        if index >= 0:
            if self.style & CLE_ALLOW_DELETE:
                self.delete.Enable()
            if self.style & CLE_ALLOW_EDIT:
                self.edit.Enable()
            self.UpdateButtons()
        else:
            if self.style & CLE_ALLOW_DELETE:
                self.delete.Disable()
            if self.style & CLE_ALLOW_EDIT:
                self.edit.Disable()
    
    def UpdateButtons(self):
        index = self.list.GetSelection()
        if index == 0:
            self.up.Disable()
            self.down.Enable()
        elif index == self.list.GetCount() - 1:
            self.up.Enable()
            self.down.Disable()
        else:
            self.up.Enable()
            self.down.Enable()
    
    def GetStrings(self):
        """Return a list containing the current items in this ListEditor."""
        
        return self.list.GetStrings()
    
    def Set(self, strings, data=None):
        """Set the contents of this ListEditor.
        
        @param strings: A list containging strings to set this ListEditor to.
        
        """
        
        self.Freeze()
        
        if data == None:
            data_ = strings
        else:
            data_ = data
        
        self.list.Set(strings, data_)
        self.text.Clear()
        self.modified = False
        
        self.Thaw()
    
    def Append(self, string, data=None):
        """Add a string to the end of the list box."""
        
        if data == None:
            data_ = string
        else:
            data_ = data
        self.list.Append(string, data_)
    
    def Insert(self, string, pos, data=None):
        """Insert a string into the ListBox at the given position."""
        
        if data == None:
            data_ = string
        else:
            data_ = data
        self.list.Insert(string, pos, data_)
    
    def IsModified(self):
        """Check to see if the ListEditor has been modified since the last call to SetStrings."""
        
        return self.modified
    
    def SetModified(self, mod=True):
        """Set the modified value of the control."""
        
        self.modified = mod
    
    def ResetModified(self):
        """Set the modified value to false."""
        
        self.modified = False
    
    def GetValue(self):
        """Called by ConfigValidator, does the same as GetStrings."""
        
        out = []
        for x in range(self.list.GetCount()):
            out.append(self.list.GetClientData(x))
        return out
    
    def SetValue(self, value):
        """Called by ConfigValidator, does the same as Set."""
        
        for data in value:
            self.modified = False
            if self.style & CLE_LIST or self.style & CLE_DICT:
                self.list.SetString(data[self.object_key])
                self.list.SetClientData(data)
            else:
                self.list.SetString(data)
                self.list.SetClientData(data)

if __name__ == '__main__':
    
    def test():
        return 'test'
    
    def edit(data):
        print 'editing:', data
        return 'edited data'
    
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'ListEditor test')
            
            panel = wx.Panel(self)
            self.editor = CustomListEditor(panel, add_callback=test, edit_callback=edit)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.editor, 1, wx.EXPAND|wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
    
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()    
