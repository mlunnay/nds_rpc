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

"""This module provides an editor for generating a list of objects with multiple editors."""

import wx

import images

# Style defines

class ObjectListEditor(wx.Panel):
    """This editor allows the generation of a list of objects with multiple editors."""
    
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name='ObjectListEditor', object_name='item', add_bitmap=None,
                 remove_bitmap=None, editor=None):
        '''ObjectListEditor Initialisation.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param validator: Window validator.
        @param name: The name of this control.
        @param object_name: Descriptive name for the objects this control contains.
        @param add_bitmap: Custom bitmap image for the add button.
        @param remove_bitmap: Custom bitmap image for the remove button.
        @param editor: An ObjectEditor containing the editors for the object. 
        
        '''
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        
        self.object_name = object_name.strip()
        self._objects = {}
        self._current = None
        
        self.SetLabel(name)
                
        self._list = wx.ListBox(self)
        if add_bitmap:
            bmp = add_bitmap
        else:
            bmp = images.getAddBitmap()
        add_button = wx.BitmapButton(self, -1, bmp)
        add_button.SetToolTipString('Add %s' % self.object_name)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, add_button)
        
        if remove_bitmap:
            bmp = remove_bitmap
        else:
            bmp = images.getDeleteBitmap()
        remove_button = wx.BitmapButton(self, -1, bmp)
        remove_button.SetToolTipString('Remove %s' % self.object_name)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, remove_button)
        
        lsizer = wx.BoxSizer(wx.VERTICAL)
        lsizer.Add(self._list, 1, wx.EXPAND)
        
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(add_button)
        bsizer.Add(remove_button, 0, wx.LEFT, 4)
        lsizer.Add(bsizer, 0, wx.ALIGN_RIGHT)
        
        self._editor_panel = wx.Panel(self)
        text = wx.StaticText(self._editor_panel, -1, 'test')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(text, 0, wx.ALL, 6)
        self._editor_panel.SetSizer(sizer)
        #TODO: add editor panel generation
        #self._editor_panel = editor.build(self, validator)
        
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.Add(lsizer, 1, wx.EXPAND)
        msizer.Add(self._editor_panel, 2, wx.EXPAND|wx.LEFT, 6)
        self.SetSizerAndFit(msizer)
                
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self._list)
        
        self._list.Set(['one', 'two'])
    
    def OnAdd(self, event):
        pass
    
    def OnRemove(self, event):
        pass
    
    def OnListBox(self, event):
        """Handle the list box selection event."""
        
        pass
    
    def GetValue(self):
        """Return the current value of the object list."""
        
        if self._current != None:
            pass
            #TODO: get values from editor panel
            #self._objects[self._current] = 
        return self._objects
        
    def SetValue(self, value):
        """Set the current value of the object list.
        
        @param value: A dictionary with the object names as keys, and the
            values being dictionaries containing the objects.
        
        """
        
        self._objects = value
        self._list.Set(value.keys())
        self._list.SetSelection(0)

if __name__ == '__main__':
    from ndsdevelserver.ui.configvalidator import ConfigValidator
    
    config = {'one': '',
              'two': ['one', 'three'],
              'three': 'test'}
    
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'ListEditor test')
            self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
            panel = wx.Panel(self)
            self.editor = ObjectListEditor(panel, name='ObjectsTest')
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.editor, 1, wx.EXPAND|wx.ALL, 6)
            button = wx.Button(panel, -1, 'OK')
            self.Bind(wx.EVT_BUTTON, self.Ok, button)
            sizer.Add(button, 0, wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
            
            self.InitDialog()
#            self.Show()
        
        def Ok(self, event):
            if not self.Validate():
                return
            self.TransferDataFromWindow()
            self.Close()
    
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()
    
    print config 
