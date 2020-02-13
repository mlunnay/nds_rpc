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

"""This module provides an alternate to EditableListCtrl from wx.gizmos."""

__all__ = ['ListEditor']

import wx
import images

# Style defines
LE_ALLOW_NEW = 0x100
LE_ALLOW_EDIT = 0x200
LE_ALLOW_DELETE = 0x400

class ListEditor(wx.Panel):
    """This is an alternative to wx.gizmos.EditableListCtrl, that uses a text
    control instead of an imbedded editor.
    
    """
        
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, strings=[],
                 style=LE_ALLOW_NEW|LE_ALLOW_EDIT|LE_ALLOW_DELETE,
                 validator=wx.DefaultValidator, name='ListEditor'):
        """Initialiser.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param strings: An array of strings with which to initialise the control.
        @param style: The style flags for the control:
            B{LE_ALLOW_NEW} - Allow new items to be added to the list.
            B{LE_ALLOW_EDIT} - Allow items to be edited.
            B{LE_ALLOW_DELETE} - Allow items to be deleted from the list.
        @param validator: Window validator.
        @param name: The name of this control. 
        
        """
        
        self.modified = False
        self.style = style
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        
        self.text = wx.TextCtrl(self, -1, '', validator=validator)
        if style & LE_ALLOW_NEW:
            self.add = wx.BitmapButton(self, -1, images.getTextfield_AddBitmap())
            self.add.SetToolTipString('Add Item')
            self.Bind(wx.EVT_BUTTON, self.OnAdd, self.add)
        self.list = wx.ListBox(self, -1, choices=strings)
        if style & LE_ALLOW_EDIT:
            self.edit = wx.BitmapButton(self, -1, images.getTextfield_RenameBitmap())
            self.edit.SetToolTipString('Update Item')
            self.Bind(wx.EVT_BUTTON, self.OnEdit, self.edit)
        if style & LE_ALLOW_DELETE:
            self.delete = wx.BitmapButton(self, -1, images.getTextfield_DeleteBitmap())
            self.delete.SetToolTipString('Delete Item')
            self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete)
        self.up = wx.BitmapButton(self, -1, images.getArrow_UpBitmap())
        self.up.SetToolTipString('Move Item Up')
        self.down = wx.BitmapButton(self, -1, images.getArrow_DownBitmap())
        self.down.SetToolTipString('Move Item Down')
        
        # layout
        spacing = 4 # spacing between elements
        msizer = wx.BoxSizer(wx.VERTICAL)
        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.Add(self.text, 1, wx.EXPAND)
        if style & LE_ALLOW_NEW:
            tsizer.Add(self.add, 0, wx.LEFT, spacing)
        msizer.Add(tsizer, 0, wx.EXPAND)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.list, 1, wx.EXPAND)
        bsizer = wx.BoxSizer(wx.VERTICAL)
        if style & LE_ALLOW_EDIT:
            bsizer.Add(self.edit, 0, wx.BOTTOM, spacing)
        if style & LE_ALLOW_DELETE:
            bsizer.Add(self.delete, 0, wx.BOTTOM, spacing)
        bsizer.Add(self.up, 0, wx.BOTTOM, spacing)
        bsizer.Add(self.down)
        hsizer.Add(bsizer, 0, wx.LEFT, spacing)
        
        msizer.Add(hsizer, 1, wx.EXPAND|wx.TOP, spacing)
        self.SetSizerAndFit(msizer)
        
        self.Bind(wx.EVT_BUTTON, self.OnUp, self.up)
        self.Bind(wx.EVT_BUTTON, self.OnDown, self.down)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.list)
    
    def OnAdd(self, event):
        txt = self.text.GetValue()
        if txt != '':
            self.modified = True
            self.list.Append(txt)
            self.list.SetSelection(-1)
            self.text.SetSelection(-1, -1)
            self.text.SetFocus()
            if self.style & LE_ALLOW_DELETE:
                self.delete.Disable()
            if self.style & LE_ALLOW_EDIT:
                self.edit.Disable()
            self.up.Disable()
            self.down.Disable()
    
    def OnEdit(self, event):
        index = self.list.GetSelection()
        txt = self.text.GetValue()
        if txt != '':
            self.modified = True
            self.list.SetString(index, txt)
    
    def OnDelete(self, event):
        index = self.list.GetSelection()
        if index != -1:
            self.modified = True
            self.list.Delete(index)
            
            if self.style & LE_ALLOW_DELETE:
                self.delete.Disable()
            if self.style & LE_ALLOW_EDIT:
                self.edit.Disable()
            self.up.Disable()
            self.down.Disable()
            self.text.SetValue('')
            self.text.SetFocus()
    
    def OnUp(self, event):
        index = self.list.GetSelection()
        if index > 0:
            tmp = self.list.GetString(index)
            self.list.SetString(index, self.list.GetString(index - 1))
            self.list.SetString(index - 1, tmp)
            self.list.SetSelection(index - 1)
            self.UpdateButtons()
    
    def OnDown(self, event):
        index = self.list.GetSelection()
        if index < self.list.GetCount() - 1:
            tmp = self.list.GetString(index)
            self.list.SetString(index, self.list.GetString(index + 1))
            self.list.SetString(index + 1, tmp)
            self.list.SetSelection(index + 1)
            self.UpdateButtons()
    
    def OnListBox(self, event):
        index = self.list.GetSelection()
        if index >= 0:
            self.text.SetValue(self.list.GetStringSelection())
            if self.style & LE_ALLOW_DELETE:
                self.delete.Enable()
            if self.style & LE_ALLOW_EDIT:
                self.edit.Enable()
            self.UpdateButtons()
        else:
            self.text.SetFocus()
            if self.style & LE_ALLOW_DELETE:
                self.delete.Disable()
            if self.style & LE_ALLOW_EDIT:
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
    
    def Set(self, strings):
        """Set the contents of this ListEditor.
        
        @param strings: A list containging strings to set this ListEditor to.
        
        """
        
        self.Freeze()
        
        self.list.Set(strings)
        self.text.Clear()
        self.modified = False
        
        self.Thaw()
    
    def Append(self, string):
        """Add a string to the end of the list box."""
        
        self.list.Append(string)
    
    def Insert(self, string, pos):
        """Insert a string into the ListBox at the given position."""
        
        self.list.Insert(string, pos)
    
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
        
        self.list.GetStrings()
    
    def SetValue(self, value):
        """Called by ConfigValidator, does the same as Set."""
        
        self.Set(value)

if __name__ == '__main__':
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'ListEditor test')
            
            panel = wx.Panel(self)
            self.listeditor = ListEditor(panel)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.listeditor, 1, wx.EXPAND|wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
    
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()    
