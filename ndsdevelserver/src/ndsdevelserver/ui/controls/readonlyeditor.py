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

"""This module provides a read-only display with extra features compared to wx.StaticText."""

import wx

# extra style defines
ROE_PASSWORD = 0x1

class ReadOnlyEditor(wx.StaticText):
    """This is a modification to wx.StaticText to add validator features and password display."""
    
    _has_label = True
    
    def __init__(self, parent, id=-1, label='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name='ReadOnlyEditor',
                 validator=wx.DefaultValidator, extra_style=0):
        '''ReadOnlyEditor initialiser.
        
        @param parent: The parent of this control.
        @param id: The id for this control.
        @param label: A string to display.
        @param pos: The position of this control
        @param size: The size of this control.
        @param style: wx.StaticText style flags.
        @param name: An optional name for this control.
        @param extra_style: Style flags for this ReadOnlyEditor currently the
            only flag is ROE_PASSWORD which will cause the characters to be
            displayed as asterisks. 
        
        '''
        
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)
        self.SetValidator(validator)
        
        self.value = label
        
        self.password_display = False
        if extra_style & ROE_PASSWORD:
            self.password_display = True
            wx.StaticText.SetLabel(self, u'\u25CF' * len(label))
        
    def SetValue(self, value):
        """Set the value of the control."""
        
        self.value = value
        if self.password_display == True:
            wx.StaticText.SetLabel(self, u'\u25CF' * len(value))
        else:
            wx.StaticText.SetLabel(self, value)
    
    def GetValue(self):
        """Return the contents of this control."""
        
        return self.value
    
    def SetLabel(self, label):
        """Overrides wx.StaticText.SetLabel to handle password display."""
        
        self.value = label
        if self.password_display == True:
            wx.StaticText.SetLabel(self, u'\u25CF' * len(label))
        else:
            wx.StaticText.SetLabel(self, label)

if __name__ == '__main__':
    from ndsdevelserver.ui.configvalidator import ConfigValidator
    
    config = {'one': '',
              'two': ['one', 'three'],
              'three': 'test'}
    
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'ReadOnlyEditor test')
            self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
            panel = wx.Panel(self)
            self.editor = ReadOnlyEditor(panel,
                                validator=ConfigValidator(config, ['three']),
                                name='ReadOnlyTest', extra_style=ROE_PASSWORD)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.editor, 0, wx.ALL, 6)
            button = wx.Button(panel, -1, 'OK')
            self.Bind(wx.EVT_BUTTON, self.Ok, button)
            sizer.Add(button, 0, wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
            
            self.InitDialog()
#            self.Show()
        
        def Ok(self, event):
            if not self.Validate():
                print 'invalid'
                return
            self.TransferDataFromWindow()
            self.Close()
    
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()
    
    print config
