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

__all__ = ['ConfigValidator']

import wx

class Default(object):
    """Empty utility class to signal no default value for a control to allow None as a default value."""

class ConfigValidator(wx.PyValidator):
    """This validator handles getting and setting configuration values from
    a dictionary based config.
    
    It uses subclasses of ConfigHandler to do the actual validation, allowing
    for flexible validation.
    
    """
    
    def __init__(self, config, path, handler=None, default=Default(),
                 required=False, write_if_empty=False): 
        '''ConfigValidator initialisation.
        
        @param config: The configuration dictionary
        @param path: A sequence of keys that lead to the config option.
        @param handler: a subclass of ConfigHandler for validation and data coercion.
        @param default: An optional default value.
        @param required: If True an empty value is invalid.
        @param write_if_empty: Only add an empty value to the config if this is True.
        
        '''
        
        wx.PyValidator.__init__(self)
        
        self.config = config
        self.path = path
        if isinstance(self.path, (str, unicode)):
            self.path = [self.path]
        self.handler = handler
        self.default = default
        self.required = required
        self.write_if_empty = write_if_empty
        
        if not isinstance(default, Default):
            self.Bind(wx.EVT_CHAR, self.OnChar)

#===============================================================================
#   Validator Methods
#===============================================================================

    def Clone(self):
        return ConfigValidator(self.config, self.path, self.handler,
                               self.default, self.required)
    
    def Validate(self, win):
        """Validate the contents of the control."""
        
        ctrl = self.GetWindow()
        value = ctrl.GetValue()
        if not value:
            if self.required and isinstance(self.default, Default):
                ctrl.SetBackgroundColour("pink")
                ctrl.SetFocus()
                ctrl.Refresh()
                wx.MessageBox("%s requires a value" % ctrl.GetName()
                            , "Missing value", wx.OK|wx.ICON_ERROR)
                return False    # value is empty, is required and has no default
            else:
                return True
        
        if self.handler and not self.handler.validate(value):
            ctrl.SetBackgroundColour("pink")
            ctrl.SetFocus()
            ctrl.Refresh()
            wx.MessageBox("%s expected %s but recieved %s" % (ctrl.GetName(),
                            self.handler.info(), str(value)), "Invalid value",
                            wx.OK|wx.ICON_ERROR)
            return False
        else:
            ctrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True
    
    def TransferToWindow(self):
        """Get the value from the config dictionary."""
        
        config = self.config
        for key in self.path[:-1]:
            config = config.get(key, {})
        
        value = config.get(self.path[-1], Default())
        
        if isinstance(value, Default):
            if self.default:
                value = default
            else:
                value = ''
        
        if self.handler:
            value = self.handler.coerce_to_window(value)
        
        self.GetWindow().SetValue(value)
        
        return True
    
    def TransferFromWindow(self):
        """Set the value from the control to the config dictionary."""
        
        value = self.GetWindow().GetValue()
        
        if not value:
            if self.write_if_empty and self.default:
                value = self.default
            elif not self.write_if_empty:
                return True
        
        # do possible coercion of the value
        if self.handler:
            value = self.handler.coerce_from_window(value)
        
        config = self.config
        for key in self.path[:-1]:
            config = config.get(key, {})
        
        config[self.path[-1]] = value
        
        return True

    def GetData(self):
        """Get the data from the config dictionary.
        
        This provides a convenience method for use outside of the usual
        validator path.
        
        """
        
        config = self.config
        for key in self.path[:-1]:
            config = config.get(key, {})
        
        value = config.get(self.path[-1], Default())
        
        if isinstance(value, Default):
            if self.default:
                value = default
            else:
                value = ''
        
        if self.handler:
            value = self.handler.coerce_to_window(value)
        
        return value

if __name__ == '__main__':
    from confighandler import StringType, OneOf
    
    config = {'one': '',
              'two': 42,
              'three': 'test'}
    
    class TestDialog(wx.Dialog):
        def __init__(self, parent):
            wx.Dialog.__init__(self, parent, -1, 'Validator Test')
            
            self.one = wx.TextCtrl(self, -1,
                                   validator=ConfigValidator(config, ['one'], required=True),
                                   name='one')
            self.two = wx.TextCtrl(self, -1,
                                   validator=ConfigValidator(config, ['two'],
                                            handler=StringType(int)), name='two')
            self.three = wx.TextCtrl(self, -1,
                                   validator=ConfigValidator(config, ['three'],
                                            handler=OneOf(['test', 'testing'])), name='three')
            
            sizer = wx.FlexGridSizer(3, 2, 6, 6)
            sizer.Add(wx.StaticText(self, -1, 'One:'))
            sizer.Add(self.one, 1, wx.EXPAND)
            sizer.Add(wx.StaticText(self, -1, 'Two:'))
            sizer.Add(self.two, 1, wx.EXPAND)
            sizer.Add(wx.StaticText(self, -1, 'Three:'))
            sizer.Add(self.three, 1, wx.EXPAND)
            
            sizer.AddGrowableCol(1)
            
            btnsizer = wx.StdDialogButtonSizer()
            
            btn = wx.Button(self, wx.ID_OK)
            btn.SetHelpText("The OK button completes the dialog")
            btn.SetDefault()
            btnsizer.AddButton(btn)
    
            btn = wx.Button(self, wx.ID_CANCEL)
            btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
            btnsizer.AddButton(btn)
            btnsizer.Realize()
    
            sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP, 6)
            
            bsizer = wx.BoxSizer()
            bsizer.Add(sizer, 0, wx.EXPAND|wx.ALL, 6)
            
            self.SetSizerAndFit(bsizer)
    
    class MainWindow(wx.Frame):
        """ We simply derive a new class of Frame. """
        def __init__(self, parent, id, title):
            wx.Frame.__init__(self, parent, id, title, size=(200,100))
            self.control = wx.Button(self, -1, 'Test Dialog')
            self.Bind(wx.EVT_BUTTON, self.OnButton, self.control)
            self.Show(True)
        
        def OnButton(self, event):
            d = TestDialog(self)
            d.ShowModal()
            print config
            
    app = wx.PySimpleApp()
    frame=MainWindow(None, wx.ID_ANY, 'Small editor')
    app.MainLoop()
