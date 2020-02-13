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

"""This module provides an editor for generating a list from a set of possible entries."""

__all__ = ['SetEditor']

import wx

# Style defines
SE_ALLOW_MOVE_ALL = 0x100
SE_ORDERED = 0x200

class SetEditor(wx.Panel):
    """This editor allows the generation of a list from a set of possible values."""
    
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, choices=[],
                 style=SE_ALLOW_MOVE_ALL|SE_ORDERED,
                 validator=wx.DefaultValidator, name='SetEditor',
                 left_title='', right_title=''): 
        '''SetEditor Initialisation.
        
        @param parent: The parent window for this control.
        @param id: The window ID.
        @param pos: Window position. wxDefaultPosition indicates that wxWidgets should generate a default position for the window. If using the wxWindow class directly, supply an actual position.
        @param size: Window size. wxDefaultSize indicates that wxWidgets should generate a default size for the window. If no suitable size can be found, the window will be sized to 20x20 pixels so that the window is visible but obviously not correctly sized.
        @param choices: A list of strings that the user may choose from
        @param style: The style flags for the control:
            B{SE_ALLOW_MOVE_ALL} - Show buttons to allow all items to be added, or removed from the list.
            B{SE_ORDERED} - The order of the list is modifiable, showing extra buttons from move up and down.
        @param validator: Window validator.
        @param name: The name of this SetEditor
        @param left_title: Optional title to appear above the left hand list.
        @param right_title: Optional title to appear above the right hand list.
        
        '''
        
        wx.Panel.__init__(self, parent, id, pos, size, name=name)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self.SetValidator(validator)
        
        if left_title or right_title:
            self.left_title = wx.StaticText(self, -1, left_title)
            self.right_title = wx.StaticText(self, -1, right_title)
        
        self.left_list = wx.ListBox(self, choices=choices, style=wx.LB_EXTENDED)
        
        # middle buttons
        if style & SE_ALLOW_MOVE_ALL:
            self.add_all = wx.Button(self, -1, '>>')
            self.add_all.SetToolTipString('Add All Items')
            self.Bind(wx.EVT_BUTTON, self.OnAddAll, self.add_all)
        self.add = wx.Button(self, -1, '>')
        self.add.SetToolTipString('Add Selected Items')
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.add)
        self.remove = wx.Button(self, -1, '<')
        self.remove.SetToolTipString('Remove Selected Items')
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.remove)
        if style & SE_ALLOW_MOVE_ALL:
            self.remove_all = wx.Button(self, -1, '<<')
            self.remove_all.SetToolTipString('Remove All Items')
            self.Bind(wx.EVT_BUTTON, self.OnRemoveAll, self.remove_all)
        if style & SE_ORDERED:
            self.up = wx.Button(self, -1, 'Move Up')
            self.up.SetToolTipString('Move Item Up')
            self.Bind(wx.EVT_BUTTON, self.OnUp, self.up)
            self.down = wx.Button(self, -1, 'Move Down')
            self.down.SetToolTipString('Move Item Down')
            self.Bind(wx.EVT_BUTTON, self.OnDown, self.down)
        
        self.right_list = wx.ListBox(self, style=wx.LB_EXTENDED)
        
        # layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        lsizer = wx.BoxSizer(wx.VERTICAL)
        if left_title or right_title:
            lsizer.Add(self.left_title)
        lsizer.Add(self.left_list, 1, wx.EXPAND)
        sizer.Add(lsizer, 1, wx.EXPAND)
        
        msizer = wx.BoxSizer(wx.VERTICAL)
        tsizer = wx.BoxSizer(wx.VERTICAL)
        if style & SE_ALLOW_MOVE_ALL:
            tsizer.Add(self.add_all, 0, wx.BOTTOM, 12)
        tsizer.Add(self.add, 0, wx.BOTTOM, 6)
        tsizer.Add(self.remove)
        if style & SE_ALLOW_MOVE_ALL:
            tsizer.Add(self.remove_all, 0, wx.TOP, 12)
        msizer.Add(tsizer, 1, wx.EXPAND)
        if style & SE_ORDERED:
            bsizer = wx.BoxSizer(wx.VERTICAL)
            bsizer.Add(self.up)
            bsizer.Add(self.down, 0, wx.TOP, 6)
            msizer.Add(bsizer, 0, wx.ALIGN_BOTTOM|wx.TOP, 12)
        sizer.Add(msizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 6)
        
        rsizer = wx.BoxSizer(wx.VERTICAL)
        if left_title or right_title:
            rsizer.Add(self.right_title)
        rsizer.Add(self.right_list, 1, wx.EXPAND)
        sizer.Add(rsizer, 1, wx.EXPAND)
        
        self.SetSizerAndFit(sizer)
        
    def OnAddAll(self, event):
        """Add all of the items from the available choices to the list."""
        
        self.right_list.Set(self.left_list.GetStrings())
        
    def OnAdd(self, event):
        """Add the selected items from the available choices to the list."""
        
        self.Freeze()
        choices = self.left_list.GetSelections()
        current = self.right_list.GetStrings()
        for choice in choices:
            s = self.left_list.GetString(choice)
            if s not in current:
                self.right_list.Append(s)
        self.Thaw()
        
    def OnRemove(self, event):
        """Remove the selected items from the list."""
        
        self.Freeze()
        choices = list(self.right_list.GetSelections())
        # we want to work backwards when deleting
        choices.reverse()
        for choice in choices:
            self.right_list.Delete(choice)
        self.Thaw()
        
    def OnRemoveAll(self, event):
        """Removes all of the items from the list."""
        
        self.right_list.Clear()
        
    def OnUp(self, event):
        """Move the currently selected item up in the list."""
        
        index = self.right_list.GetSelections()
        if len(index) == 0:
            return
        index = index[0]
        if index > 0:
            tmp = self.right_list.GetString(index)
            self.right_list.SetString(index, self.right_list.GetString(index - 1))
            self.right_list.SetString(index - 1, tmp)
            self.right_list.Deselect(index)
            self.right_list.SetSelection(index - 1)
        
    def OnDown(self, event):
        """Move the currently selected item down in the list."""
        
        index = self.right_list.GetSelections()
        if len(index) == 0:
            return
        index = index[0]
        if index < self.right_list.GetCount() - 1:
            tmp = self.right_list.GetString(index)
            self.right_list.SetString(index, self.right_list.GetString(index + 1))
            self.right_list.SetString(index + 1, tmp)
            self.right_list.Deselect(index)
            self.right_list.SetSelection(index + 1)
    
    def GetStrings(self):
        """Returns a the list of selected values from the set."""
        
        self.right_list.GetStrings()
    
    def Set(self, strings):
        """Sets the values of the list.
        
        @param strings: A list of strings to set the list to.
        @raise ValueError: Raised if any of the strings are not in the available choices. 
        
        """
        
        choices = self.left_list.GetStrings()
        for s in strings:
            if s not in choices:
                raise ValueError('%s is not an available choice.' % s)
        
        self.Freeze()
        self.right_list.Set(strings)
        self.Thaw()
    
    def SetChoices(self, choices):
        """Sets the available choices and clears the selected values.
        
        @param choices: A list of strings to set the choices to.
        
        """ 
        
        self.Freeze()
        self.left_list.Set(choices)
        self.right_list.Clear()
        self.Thaw()
    
    def GetValue(self):
        """Called by ConfigValidator, does the same as GetStrings."""
        
        return self.right_list.GetStrings()
    
    def SetValue(self, value):
        """Called by ConfigValidator, similar to Set but ignores strings not in the available choices."""
        
        self.Freeze()
        self.right_list.Clear()
        
        choices = self.left_list.GetStrings()
        for s in value:
            if s in choices:
                self.right_list.Append(s)
        
        self.Thaw()

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
            self.seteditor = SetEditor(panel, choices=['one', 'two', 'three', 'four'],
                                       validator=ConfigValidator(config, ['two']), name='SetTest')
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.seteditor, 1, wx.EXPAND|wx.ALL, 6)
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
