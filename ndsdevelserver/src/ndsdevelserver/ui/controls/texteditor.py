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

"""This module provides the TextEditor that adds default value display to
wx.TextCtrl."""

import wx

class TextEditor(wx.TextCtrl):
    """This is a modification of wx.TextCtrl to add the capability to display
    a default string if the control is empty.
    
    """
    
    def __init__(self, parent, id=-1, value='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, strings=[], style=0,
                 validator=wx.DefaultValidator, name='ListEditor',
                 default=None, default_color=None):
        """Initialiser.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param strings: An array of strings with which to initialise the control.
        @param style: The style flags for this TextEditor
        @param validator: Window validator.
        @param name: The name of this control. 
        @param default: An optional string to display when the control is empty.
        @param default_color: The color to use when displaying the default value.
        
        """
        
        
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style,
                             validator, name)
        
        self.default = default
        if default_color:
            self.default_color = default_color
        else:
            self.default_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        
        self.normal_color = self.GetForegroundColour()
        
        if default != None:
            self.displaying_default = True
        else:
            self.displaying_default = False
        self.show_default = False
        if value == '' and default != None:
            self.show_default = True
            self.DisplayDefault()
        
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        
    def OnSetFocus(self, event):
        if self.show_default == True:
            self.RemoveDefault()
        event.Skip()
    
    def OnKillFocus(self, event):
        if self.displaying_default == True and (self.GetValue().strip() == '' or \
            self.GetValue() == self.default):
            self.DisplayDefault()
        event.Skip()
    
    def SetValue(self, value):
        """Overridden TextCtrl.SetValue."""
        
        if value == '':
            self.show_default = True
            self.DisplayDefault()
        else:
            self.show_default = False
            self.RemoveDefault()
            wx.TextCtrl.SetValue(self, value)
    
    def DisplayDefault(self):
        """Display the default string."""
        
        if self.show_default == False:
            self.show_default = True
            self.normal_color = self.GetForegroundColour()
            self.SetForegroundColour(self.default_color)
            wx.TextCtrl.SetValue(self, self.default)
            self.SetSelection(0,0)
    
    def RemoveDefault(self):
        """Set the display back to normal."""
        if self.show_default == True:
            self.show_default = False
            self.SetForegroundColour(self.normal_color)
            self.Clear()
    
    def SetDefault(self, default):
        """Set the default string."""
        
        self.default = default
    
    def ClearDefault(self):
        """Removes the default string."""
        
        self.default = None
    
    def SetDefaultColor(self, color):
        """Set the color to display the default text in."""
        
        self.default_color = color

if __name__ == '__main__':
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'TextEditor test')
            
            panel = wx.Panel(self)
            self.editor = TextEditor(panel, default='default test')
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.editor, 1, wx.EXPAND|wx.ALL, 6)
            
            sizer.Add(wx.Button(panel, -1, 'Ok'), 0, wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
    
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()    
