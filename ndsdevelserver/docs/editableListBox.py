import wx

class MyDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        
        self.text = wx.TextCtrl(self, -1, '')
        self.add = wx.BitmapButton(self, -1, wx.Bitmap("C:\\devel\\graphic resources\\famfamfam_silk_icons_v013\\icons\\textfield_add.png", wx.BITMAP_TYPE_ANY))
        self.list = wx.ListBox(self, -1, choices=['list', 'box'])
        self.edit = wx.BitmapButton(self, -1, wx.Bitmap("C:\\devel\\graphic resources\\famfamfam_silk_icons_v013\\icons\\textfield_rename.png", wx.BITMAP_TYPE_ANY))
        self.delete = wx.BitmapButton(self, -1, wx.Bitmap("C:\\devel\\graphic resources\\famfamfam_silk_icons_v013\\icons\\textfield_delete.png", wx.BITMAP_TYPE_ANY))
        self.up = wx.BitmapButton(self, -1, wx.Bitmap("C:\\devel\\graphic resources\\famfamfam_silk_icons_v013\\icons\\arrow_up.png", wx.BITMAP_TYPE_ANY))
        self.down = wx.BitmapButton(self, -1, wx.Bitmap("C:\\devel\\graphic resources\\famfamfam_silk_icons_v013\\icons\\arrow_down.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle("Editable List Box Test")
        #~ _icon = wx.EmptyIcon()
        #~ _icon.CopyFromBitmap(wx.Bitmap("C:\\devel\\graphic resources\\famfamfam_silk_icons_v013\\icons\\plugin.png", wx.BITMAP_TYPE_ANY))
        #~ self.SetIcon(_icon)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer = wx.GridBagSizer(4,4)
        
        sizer.Add(self.text, (0,0), flag=wx.EXPAND)
        sizer.Add(self.add, (0,1))
        sizer.Add(self.list, (1,0), (4,1), flag=wx.EXPAND)
        sizer.Add(self.edit, (1,1))
        sizer.Add(self.delete, (2,1))
        sizer.Add(self.up, (3,1))
        sizer.Add(self.down, (4,1))
        
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(4)
        
        self.SetSizerAndFit(sizer)
        self.Layout()
        # end wxGlade

# end of class MyDialog


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    dialog_1 = MyDialog(None, -1, "")
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()