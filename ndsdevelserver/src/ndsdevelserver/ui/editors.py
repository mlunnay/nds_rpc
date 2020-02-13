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

"""This module provides editor factories for controls."""

__all__ = ['TextEditor', 'ListEditor', 'RangeEditor', 'SetEditor',
           'ReadOnlyEditor', 'SetComboEditor', 'CustomListEditor',
           'ChoiceEditor', 'FileEditor', 'DirectoryEditor', 'BooleanEditor',
           'RadioEditor']

import wx
from functools import partial

from controls import ListEditor as ListEditorCtrl
from controls import LE_ALLOW_NEW, LE_ALLOW_EDIT, LE_ALLOW_DELETE
from controls import ObjectListEditor as ObjectListEditorCtrl
from controls import RangeEditor as RangeEditorCtrl
from controls import RE_TEXT, RE_SPIN, RE_FLOAT, RE_INT
from controls import SetEditor as SetEditorCtrl
from controls import SE_ALLOW_MOVE_ALL, SE_ORDERED
from controls import TextEditor as TextEditorCtrl
from controls import ReadOnlyEditor as ReadOnlyEditorCtrl
from controls import ROE_PASSWORD
from controls import SetComboEditor as SetComboEditorCtrl
from controls import CustomListEditor as CustomListEditorCtrl 
from controls import CLE_ALLOW_NEW, CLE_ALLOW_EDIT, CLE_ALLOW_DELETE, CLE_STRING, CLE_LIST, CLE_DICT
from controls import RadioEditor as RadioEditorCtrl

def TextEditor(value='', default=None, default_color=None, password=False,
                 multiline=False):
    '''Default editor allows the user to edit values in a text editor.
    
    @param value: The initial value to set the text editor to.
    @param default: Optional default value.
    @param default_color: Color to use when displaying default values.
    @param password: If True text is displayed as asterisks/
    @param multiline: If True control will allow multiline input.    
    
    '''
    
    style_ = 0
    if password == True:
        style_ |= wx.TE_PASSWORD
    if multiline == True:
        style_ |= wx.TE_MULTILINE
    
    return partial(TextEditorCtrl, value=value, default=default,
                   default_color=default_color, style=style_)

def ListEditor(strings=[], allow_new=True, allow_edit=True,
               allow_delete=True):
    '''Allows the user to edit a list of strings
    
    @param strings: A list of strings to set the control to.
    @param allow_new: If True allow new strings to be added to the list.
    @param allow_edit: If True allow the strings in the list to be modified.
    @param allow_delete: If True allow strings to be removed from the list.
    
    '''
    
    style_ = 0
    if allow_new == True:
        style_ |= LE_ALLOW_NEW
    if allow_edit == True:
        style_ |= LE_ALLOW_EDIT
    if allow_delete == True:
        style_ |= LE_ALLOW_DELETE
    
    return partial(ListEditorCtrl, strings=strings, style=style_)

def RangeEditor(value=0, min=None, max=None, step=1, is_float=False,
                display_spin=True):
    '''Allow the user to edit a numeric value.
    
    @param value: Initial value for the control.
    @param min: Minimum value for the control.
    @param max: Maximum value for the control.
    @param step: The amount to increment the editor, only useful for the spin version.
    @param is_float: If True treat the contents as if a floating point number. 
    @param display_spin: if True display the control as a text box with spin buttons.
    
    '''
    
    style_ = 0
    if is_float == True:
        style_ |= RE_FLOAT
    else:
        style_ |= RE_INT
    if display_spin == True:
        style_ |= RE_SPIN
    else:
        style_ |= RE_TEXT
    
    return partial(RangeEditorCtrl, value=value, min=min, max=max, step=step,
                   style=style_)

def SetEditor(choices=[], left_title=None, right_title=None, allow_move_all=True, ordered=True):
    '''Allow the user to select items from a range of values.
    
    @param choices: A list of strings with the available choices.
    @param left_title: Optional title to appear above the left hand list.
    @param right_title:Optional title to appear above the right hand list.
    @param allow_move_all: If True show buttons to allow adding and removing all values.
    @param ordered: If True show buttons to allow changing the order of values.
    
    '''
    
    style_ = 0
    if allow_move_all == True:
        style_ |= SE_ALLOW_MOVE_ALL
    if ordered == True:
        style_ |= SE_ORDERED
    
    return partial(SetEditorCtrl, choices=choices, left_title=left_title,
                   right_title=right_title, style=style_)

def ReadOnlyEditor(value='', password=False, alignment='left'):
    '''Allow the user to read but not edit a value.
    
    @param value: The Value to display.
    @param password: If True the value will be displayed as asterisks.
    @param alignment: The alignment of the text, one of left, right or centre.
    
    '''
    
    style_ = 0
    if aligment == 'left':
        style_ |= wx.ALIGN_LEFT
    elif aligment == 'right':
        style_ |= wx.ALIGN_RIGHT
        style_ |= wx.ST_NO_AUTORESIZE
    elif aligment == 'centre' or alignment == 'center':
        style_ |= wx.ALIGN_CENTRE
        style_ |= wx.ST_NO_AUTORESIZE
    
    extra = 0
    if password == True:
        extra |= ROE_PASSWORD
    
    return partial(ReadOnlyEditorCtrl, label=value, style=style_,
                   extra_style=extra)

def SetComboEditor(choices=[], separator='|', equal=None):
    """Allow the user to select items from a range of values from a
    CheckListBox via a popup from a combo control.
    
    @param choices: A list of strings to allow a choice from.
    @param separator: The character to separate the selected choices in the
        display string.
    @param equal: A dictionary mapping alternate strings to strings in values.
    
    """
    
    return partial(SetComboEditorCtrl, choices=choices, separator=separator,
                   equal=equal)

def CustomListEditor(data=[], object_key=None, object_name='item',
                     allow_new=True, allow_edit=True, allow_delete=True,
                     data_type='string', add_bitmap=None, edit_bitmap=None,
                     remove_bitmap=None, up_bitmap=None, down_bitmap=None,
                     add_callback=None, edit_callback=None):
    '''Allows the user to edit a list of objects.
    
    @param strings: A list of data objects to set the control to.
    @param object_key: The key value for looking up an objects string representation.
    @param object_name: Descriptive name for the objects this control contains.
    @param allow_new: If True allow new strings to be added to the list.
    @param allow_edit: If True allow the strings in the list to be modified.
    @param allow_delete: If True allow strings to be removed from the list.
    @param data_type: The data type the editor holds, one of 'string', 'list',
        'dict', or one of the types str, list, tuple, dict.
    @param add_bitmap: A custom image for the add item button.
    @param edit_bitmap: A custom image for the edit item button.
    @param remove_bitmap: A custom image for the remove item button.
    @param up_bitmap: A custom image for the move item up button.
    @param down_bitmap: A custom image for the move item down button.
    @param add_callback: A callback function for when the user clicks on the add button.
    @param edit_callback: A callback function for when the user clicks on the edit button.
    
    '''
    
    if data_type == 'string' or (isinstance(data_type, type) and data_type == str):
        style_ = CLE_STRING
    elif data_type == 'list' or \
        (isinstance(data_type, type) and (data_type == list or data_type == tuple)):
        style_ = CLE_LIST
    elif data_type == 'dict' or (isinstance(data_type, type) and data_type == dict):
        style_ = CLE_DICT
    else:
        raise ValueError("data_type must be one of 'string', 'list', 'dict', or one of the types str, list, tuple, dict.")
    
    if allow_new == True:
        style_ |= CLE_ALLOW_NEW
    if allow_edit == True:
        style_ |= CLE_ALLOW_EDIT
    if allow_delete == True:
        style_ |= CLE_ALLOW_DELETE
    
    return partial(CustomListEditorCtrl, data=data, object_key=object_key,
                   object_name=object_name, style=style_,
                   add_bitmap=add_bitmap, edit_bitmap=edit_bitmap,
                   remove_bitmap=remove_bitmap, up_bitmap=up_bitmap,
                   down_bitmap=down_bitmap, add_callback=add_callback,
                   edit_callback=edit_callback)

def ChoiceEditor(value='', choices=[], read_only=True):
    '''Allow the user to select a value from a drop down list. 
    
    @param value: The initial value of the control.
    @param choices: A list of strings the user can choose from.
    @param read_only: If True only items from the list may be selected.
    
    '''
    
    style_ = 0
    if read_only == True:
        style_ |= wx.CB_READONLY
    
    return partial(wx.ComboBox, value=value, choices=choices, style=style_)

def FileEditor(path='', message='Select a file', wildcard='*.*', open=True,
               prompt=True, must_exist=False):
    '''Allow a user to select enter a file path, with a browse button that
    will show the FileDialog if pressed.
    
    @param path: The initial path.
    @param message: A message to display on the dialog title.
    @param wildcard: A wildcard which defines user selectable files, or
        multiple file types with a | separated string of description|wildcard|...
    @param open: If True displays the dialog to load a file, otherwise displays
        the dialog to save a file.
    @param prompt: If True confirm with the user if file exists, only relevant
        if open is False.
    @param must_exist: If True then the selected file must exist, only
        relevant if open is True
    
    '''
    
    style_ = wx.FLP_USE_TEXTCTRL
    if open == True:
        style_ |= wx.FLP_OPEN
        if must_exist == True:
            style_ |= wx.FLP_FILE_MUST_EXIST
    else:
        style_ |= wx.FLP_SAVE
        if prompt == True:
            style_ |= wx.FLP_OVERWRITE_PROMPT
    
    return partial(wx.FilePickerCtrl, path=path, message=message,
                   wildcar=wildcard, style=style_)

def DirectoryEditor(path='', message = "Select a folder", must_exist=False):
    '''Allow the user to select a directory, with a browse button that
    will show the DirectoryDialog if pressed.
    
    @param path: Initial path of the control.
    @param message: A message to display on the dialog title.
    @param must_exist: If True users are only allowed to select only
        existing directories.
    
    '''
    
    style_ = wx.DIRP_USE_TEXTCTRL
    if must_exist == True:
        style_ |= wx.DIRP_DIR_MUST_EXIST
    
    return partial(wx.DirPickerCtrl, path=path, message=message, style=style_)

def BooleanEditor(checked=False):
    """Allow the user to edit a Boolean value.
    
    @param checked: If True the CheckBox is initially checked.
    
    """
    
    def CheckBoxWrapper(*args, **keywords):
        cb = wx.CheckBox(*args, **keywords)
        cb.SetValue(checked)
        return cb
    
    return CheckBoxWrapper

def RadioEditor(choices, label='', selected=0):
    """Allow the user to select a value from a set of values using radio buttons.
    
    @param choices: A sequence of strings that the user may choose from.
    @param label: An optional string to set the choices label to.
    @param selected: The index of the initially selected value.
    
    """
    
    return partial(RadioEditorCtrl, choices=choices, selected=selected)

if __name__ == '__main__':
    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'Editors test')
            
            panel = wx.Panel(self)
            self.text = TextEditor('TextEditor', default='default test')(panel)
            self.list = ListEditor(['one', 'two'], allow_edit=False)(panel)
            self.set = SetComboEditor(['foo', 'bar'], equal={'bas': 'bar'})(panel)
            self.bool = BooleanEditor(True)(panel)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.text, 0, wx.EXPAND|wx.ALL, 6)
            sizer.Add(self.list, 1, wx.EXPAND|wx.ALL, 6)
            sizer.Add(self.set, 0, wx.EXPAND|wx.ALL, 6)
            sizer.Add(self.bool, 0, wx.EXPAND|wx.ALL, 6)
            sizer.Add(wx.Button(panel, -1, 'Ok'), 0, wx.ALL, 6)
            
            panel.SetSizerAndFit(sizer)
            sizer.Fit(self)
    
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()
