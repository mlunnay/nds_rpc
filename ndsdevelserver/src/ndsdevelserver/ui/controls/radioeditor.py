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

"""This module provides the RadioEditor that allows the user to select a single
value from a list of values using radio buttons."""

__all__ = ['RadioEditor', 'EVT_RADIOEDITOR']

import wx

EVT_RADIOEDITOR_TYPE = wx.NewEventType()
EVT_RADIOEDITOR = wx.PyEventBinder(EVT_RADIOEDITOR_TYPE, 1)

class RadioEditor(wx.Panel):
    """This is similar to wx.RadioBox, but uses Gnome style labeling."""
    
    def __init__(self, parent, id=-1, label='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, choices=[], selected=0,
                 validator=wx.DefaultValidator, name="RadioEditor"):
        """Initialiser.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param label: A label to display above the editor, no label is displayed
            if this is an empty string.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param choices: An array of strings from which the user may choose.
        @param selected: Index of the default selected item.
        @param validator: Window validator.
        @param name: The name of this control. 
        
        """
        
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        self.SetValidator(validator)
        
        self.label_str = label
        self.selected = selected
        
        self.label = wx.StaticText(self, -1, label)
        font = self.label.GetFont()
        font.SetWeight(wx.BOLD)
        self.label.SetFont(font)
        
        rsizer = wx.BoxSizer(wx.VERTICAL)
        self.choices = []
        first = True
        for c in choices:
            if first:
                first = False
                radio = wx.RadioButton(self, -1, c, style = wx.RB_GROUP)
                space = 0
            else:
                radio = radio1 = wx.RadioButton(self, -1, c)
                space = 6
            self.choices.append(radio)
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, radio)
            rsizer.Add(radio, 0, wx.TOP, space)
        
        self.choices[selected].SetValue(True)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 0, wx.BOTTOM, 6)
        if label == '':
            self.label.Hide()
            space = 0
        else:
            space = 6
        sizer.Add(rsizer, 0, wx.LEFT, space)
        
        self.SetSizerAndFit(sizer)
    
    def OnRadioButton(self, event):
        radio_selected = event.GetEventObject()
        i = 0
        for c in self.choices:
            if c == radio_selected:
                self.selected = i
                s_string = c.GetLabel()
                break
            i += 1
        evt = wx.CommandEvent(EVT_RADIOEDITOR_TYPE, self.GetId())
        evt.SetInt(self.selected)
        evt.SetString(s_string)
        self.GetEventHandler().ProcessEvent(evt)
        event.Skip()
    
    def GetValue(self):
        """Get the string of the currently selected radio button."""
        
        return self.choices[self.selected].GetLabel()
    
    def SetValue(self, val):
        """Set the radio button that matches the value to selected."""
        
        for c in self.choices:
            if val == c.GetLabel():
                c.SetValue(True)
                break
    
    # RadioBox methods
    
    def GetSelection(self):
        """Return the index of the currently selected radio button."""
        
        return self.selected
    
    def SetSelection(self, index):
        """Set the radio button at index to selected."""
        
        self.choices[index].SetValue(True)
    
    def GetStringSelection(self):
        """Return the label of the selected radio button."""
        
        return self.choices[self.selected].GetLabel()
    
    def SetStringSelection(self, val):
        """Set the radio button that matches the value to selected."""
        
        for c in self.choices:
            if val == c.GetLabel():
                c.SetValue(True)
                break
    
    def GetLabel(self):
        """Return the label for this RadioEditor."""
        
        return self.label_str
    
    def SetLabel(self, label):
        """Set the label for this RadioEditor."""
        
        self.Freeze()
        self.label_str = label
        self.label.SetLabel(label)
        self.Layout()
        self.Thaw()
    
    def GetString(self, index):
        """Return the label of the radio button at index.
        
        @param index: The index of the radio button to get the label of.
        
        """
        
        return self.choices[index].GetLabel()
    
    def GetItemToolTip(self):
        """Return the string of the tool tip for the radio buttons of this editor."""
        
        return self.choices[0].GetToolTip()
    
    def SetItemToolTip(self, text):
        """Set the tool tips of the radio buttons of this RadioEditor.
        
        @param text: The text to set the tool tip to.
        
        """
        
        for c in self.choices:
            c.SetToolTip(text)
            
    def FindString(self, string):
        """Finds a button matching the given string, returning the position if
        found, or -1 if not found."""
        
        i = 0
        for c in self.choices:
            if c.GetLabel() == string:
                return i
            i += 1
        
        return -1
    
    def Enable(self, flag=True):
        """Enable or disable all of the radio buttons of this editor.
        
        @param flag: If True enable all of the radio buttons, otherwise disable
            all of the radio buttons.
        
        """
        
        for c in self.choices:
            c.Enable(flag)
    
    def EnableItem(self, n, flag=True):
        """Enable or disable a single radio button of this editor.
        
        @param n: The index of the item to enable or disable.
        @param flag: If True enable the radio button, otherwise disable it.
        
        """
        
        self.choices[n].Enable(flag)

if __name__ == '__main__':
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'RadioEditor test')
            
            panel = wx.Panel(self)
            self.editor = RadioEditor(panel, label='RadioEditor', choices=['foo', 'bar'])
            self.Bind(EVT_RADIOEDITOR, self.OnRadioEditor, self.editor)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.editor, 1, wx.EXPAND|wx.ALL, 6)
            
            sizer.Add(wx.Button(panel, -1, 'Ok'), 0, wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
        
        def OnRadioEditor(self, event):
            print 'OnRadioEditor: selected index: %d, label: %s' % (event.GetInt(), event.GetString())
    
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()    
