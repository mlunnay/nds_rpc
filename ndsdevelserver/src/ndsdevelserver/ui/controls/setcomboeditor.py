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

"""This module provides an editor for generating a list from a set of possible entries via a combo check list."""

__all__ = ['SetComboEditor']

import wx
import wx.combo

# modified from xrced version by Roman Rolinsky
class CheckListBoxComboPopup(wx.CheckListBox, wx.combo.ComboPopup):
    """This class makes the combopopup a checklist box, and displays the
    choices a character separated string.""" 
    
    def __init__(self, choices, separator='|', equal=None):
        """CheckListBoxComboPopup initialiser.
        
        @param values: A list of choices.
        @param separator: The character to separate the selected choices in the
            display string.
        @param equal: A dictionary mapping alternate strings to strings in values.
        
        """
        
        self.choices = choices
        if equal != None:
            self.equal = equal
        else:
            self.equal = {}
        self.separator = separator
        self.PostCreate(wx.PreCheckListBox())
        wx.combo.ComboPopup.__init__(self)
        
    def Create(self, parent):
        wx.CheckListBox.Create(self, parent)
        self.InsertItems(self.choices, 0)
        return True

    def GetControl(self):
        return self

    def OnPopup(self):
        """Show the CheckListBox, checking items that are in the display string."""
        
        combo = self.GetCombo()
        value = [x.strip() for x in combo.GetValue().split(self.separator)]
        if value == ['']: value = []
        
        for i in range(self.GetCount()):
            self.Check(i, False)
        
        for i in value:
            try:
                self.Check(self.choices.index(i))
            except ValueError:
                # Try to find equal
                if self.equal.has_key(i):
                    self.Check(self.choices.index(self.equal[i]))

        wx.combo.ComboPopup.OnPopup(self)

    def OnDismiss(self):
        """Set the display string to a character seperated string of the
        checked items."""
        
        combo = self.GetCombo()
        value = []
        for i in range(self.GetCount()):
            if self.IsChecked(i):
                value.append(self.choices[i])

        strValue = self.separator.join(value)
        if combo.GetValue() != strValue:
            combo.SetText(strValue)

        wx.combo.ComboPopup.OnDismiss(self)

class SetComboEditor(wx.Panel):
    """This editor allows the generation of a list from a set of possible values."""
    
    def __init__(self, parent, id=-1, choices=[], pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0,
                 validator=wx.DefaultValidator, name='SetComboEditor',
                 separator='|', equal=None): 
        '''SetComboEditor Initialisation.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param choices: A list of choices.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param style: The style flags for the wx.combo.ComboCtrl:
        @param validator: Window validator.
        @param name: The name of this SetEditor.
        @param separator: The character to separate the selected choices in the
            display string.
        @param equal: A dictionary mapping alternate strings to strings in values.
        
        '''
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        self.SetValidator(validator)
        
        self.combo = wx.combo.ComboCtrl(self)
        self.clb = CheckListBoxComboPopup(choices, separator, equal)
        # the plus 1 stops the scroll bars from showing
        self.combo.SetPopupMaxHeight(self.clb.GetBestSize().GetHeight() + 1)
        self.combo.SetPopupControl(self.clb)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.combo, 1, wx.EXPAND)
        self.SetSizer(sizer)
    
    def SetValue(self, value):
        """Set the value of the control.
        
        @param value: A string or list of strings to set the control to. This
            ignores items that are not in values passed to the constructor.
        
        """
        
        if isinstance(value, (str, unicode)):
            values = value.split(self.clb.separator)
        else:
            values = value
        
        valid_values = []
        for i in values:
            if i in self.clb.choices:
                valid_values.append(i)
            elif self.clb.equal.has_key(i):
                valid_values.append(self.clb.equal[i])
        
        self.combo.SetText(self.clb.separator.join(valid_values))
    
    def GetValue(self):
        """Return a list of checked items, ignoring invalid items."""
        
        str_value = self.combo.GetValue()
        value = [x.strip() for x in str_value.split(self.clb.separator)]
        if value == ['']: value = []
        
        valid_values = []
        for i in value:
            if i in self.clb.choices:
                valid_values.append(i)
            elif self.clb.equal.has_key(i):
                valid_values.append(self.clb.equal[i])
        
        return valid_values
    
    def SetEqual(self, equal):
        """Set the value mapping for the CheckListBoxComboPopup.
        
        @param equal: A dictionary mapping alternate strings to strings in values.
        
        """
        
        self.clb.equal = equal

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
            self.editor = SetComboEditor(panel, choices=['one','two','three','four'],
                                       validator=ConfigValidator(config, ['two']), name='SetComboTest')
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.editor, 0, wx.EXPAND|wx.ALL, 6)
            button = wx.Button(panel, -1, 'OK')
            self.Bind(wx.EVT_BUTTON, self.Ok, button)
            sizer.Add(button, 0, wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
            
            self.InitDialog()
        
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
