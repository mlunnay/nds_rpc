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

"""This module provides an editor for objects with multiple editors."""

import wx

import images

# Style defines

class ObjectListEditor(wx.Panel):
    """This editor is for editing objects with multiple editors."""
    
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name='ObjectEditor', editors=None):
        '''ObjectListEditor Initialisation.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param validator: Window validator.
        @param name: The name of this control.
        @param editors: A list of Items that make up this editor.
        
        '''
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        
        self.SetLabel(name)
        
        if editors == None:
            raise ValueError('Editors list not supplied to initialiser.')
        
        self._controls = {}
        
        for editor in editors:
            
        
        

if __name__ == '__main__':
    from ndsdevelserver.ui.configvalidator import ConfigValidator
    
    config = {'one': '',
              'two': ['one', 'three'],
              'three': 'test'}
    
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'ObjectEditor test')
            self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
            panel = wx.Panel(self)
            self.editor = ObjectEditor(panel, name='ObjectEditorTest')
            
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
