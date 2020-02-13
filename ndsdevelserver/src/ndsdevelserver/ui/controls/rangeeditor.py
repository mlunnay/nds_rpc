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

"""This module provides an editor for numeric ranges."""

__all__ = ['RangeEditor', 'RE_SLIDER', 'RE_TEXT', 'RE_SPIN', 'RE_FLOAT', 'RE_INT']

import wx
from decimal import Decimal
try:
    from nicefloat import nicefloat
    _have_nicefloat = True
except:
    _have_nicefloat = False

# Style defines
RE_TEXT = 0x100
RE_SPIN = 0x200
RE_FLOAT = 0x400
RE_INT = 0x8000

class RangeEditor(wx.Panel):
    """This editor allows the modification of numeric ranges."""
    
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=RE_INT|RE_SPIN,
                 value=0, min=None, max=None, step=1,
                 validator=wx.DefaultValidator, name='SetEditor'): 
        '''RangeEditor Initialisation.
        
        @param parent: The parent window for this control.
        @param value: The initial value of the editor.
        @param min: The minimum value of the range.
        @param max: The maximum value of the range.
        @param step: The amount to increment the editor, only useful for the spin version
        @param id: The window ID.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param style: The style flags for the control:
            B{RE_TEXT} - Display the editor as a text control.
            B{RE_SPIN} - Display the editor as a text control with spin buttons.
            B{RE_FLOAT} - The values and bounds of the editor are floating point numbers.
            B{RE_INT} - The values and bounds of the editor are floating point numbers.
        @param validator: Window validator.
        @param name: The name of this SetEditor
        
        '''
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.SetValidator(validator)
        
        self.style = style
        
        if style & RE_FLOAT:
            # value conversion
            if isinstance(value, float):
                if _have_nicefloat == True:
                    self.value = Decimal(nicefloat().str(value))
                else:
                    self.value = Decimal(value)
            else:
                self.value = Decimal(value)
            # step conversion
            if isinstance(step, float):
                if _have_nicefloat == True:
                    self.step = Decimal(nicefloat().str(step))
                else:
                    self.step = Decimal(step)
            else:
                self.step = Decimal(step)
            # min conversion
            if min == None:
                self.min = None
            elif isinstance(min, float):
                if _have_nicefloat == True:
                    self.min = Decimal(nicefloat().str(min))
                else:
                    self.min = Decimal(min)
            else:
                self.min = Decimal(min)
            # max conversion
            if max == None:
                self.max = None
            elif isinstance(max, float):
                if _have_nicefloat == True:
                    self.max = Decimal(nicefloat().str(max))
                else:
                    self.max = Decimal(max)
            else:
                self.max = Decimal(max)
        else:
            self.value = int(value)
            self.step = int(step)
            if min == None:
                self.min = None
            else:
                self.min = int(min)
            if max == None:
                self.max = None
            else:
                self.max = int(max)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self, -1, str(self.value))
        self.sizer.Add(self.text, 1, wx.EXPAND)
        
        if style & RE_SPIN:
#            height = self.text.GetHeight()
            self.spin = wx.SpinButton(self, -1, size=(-1,22), style=wx.SP_VERTICAL|wx.SP_WRAP)
            self.sizer.Add(self.spin)
            self.Bind(wx.EVT_SPIN_UP, self.OnSpinUp)
            self.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDown)
        
        self.valid_keys = range(48,57)
        self.valid_keys.extend([45,46, wx.WXK_LEFT, wx.WXK_RIGHT])
        
        self.text.Bind(wx.EVT_CHAR, self.OnChar)
        self.text.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        
        self.SetSizerAndFit(self.sizer)
    
    def OnSpinUp(self, event):
        """Handle the up arrow button event."""
        
        if self.style & RE_FLOAT:
            value = Decimal(self.value)
        else:
            value = int(self.value)
        if self.InRange(value + self.step):
            value += self.step
            self.SetValue(value)
    
    def OnSpinDown(self, event):
        """Handle the down arrow button event."""
        
        if self.style & RE_FLOAT:
            value = Decimal(self.value)
        else:
            value = int(self.value)
        if self.InRange(value - self.step):
            value -= self.step
            self.SetValue(value)
    
    def OnChar(self, event):
        """Handle key press events."""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_UP:
            self.OnSpinUp(None)
        elif keycode == wx.WXK_DOWN:
            self.OnSpinDown(None)
        else:
            if keycode not in self.valid_keys: # number keys
                return
            event.Skip()
    
    def OnKillFocus(self, event):
        """Handle the loss of focus from the text control."""
        
        val = self.text.GetValue().strip()
        if self.style & RE_FLOAT:
            val = Decimal(val)
        else:
            val = int(val)
        
        self.SetValue(val)
        
        event.Skip()
    
    def GetValue(self):
        """Return the current value of the editor."""
        value = self.value
        if isinstance(value, Decimal):
            value = float(value)
        return value
    
    def SetValue(self, value):
        """Set the value of the editor."""
        
        if isinstance(value, (str, unicode)):
            if self.style & RE_FLOAT:
                val = Decimal(value)
            else:
                val = int(value)
        elif isinstance(value, float):
            if self.style & RE_FLOAT:
                if _have_nicefloat:
                    val = Decimal(nicefloat().str(value))
                else:
                    val = Decimal(value)
            else:
                val = int(value)
        else:
            val = value
        
        if self.min != None and val < self.min:
            val = self.min
        elif self.max != None and val > self.max:
            val = self.max 
        
        self.value = val
        self.text.SetValue(str(val))
    
    def InRange(self, value):
        """Test if a value is within the controls range."""
        
        if self.min != None and value < self.min:
            return False
        elif self.max != None and value > self.max:
            return False
        else:
            return True

if __name__ == '__main__':
    from ndsdevelserver.ui.configvalidator import ConfigValidator
    
    config = {'one': '3.4',
              'two': ['one', 'three'],
              'three': 'test'}
    
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'ListEditor test')
            self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
            panel = wx.Panel(self)
            self.rangeeditor = RangeEditor(panel, 0, min=0, max=5, step=0.1, style=RE_FLOAT|RE_SPIN, validator=ConfigValidator(config, ['one']))
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.rangeeditor, 0, wx.EXPAND|wx.ALL, 6)
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
