#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wxOsciloDraw
'''

import wx

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    super(MyFrame, self).__init__(title=u'wxOsciloDraw',
      pos=(320, 240), size=(640, 480), *args, **kwargs)

if __name__ == '__main__':
  app = wx.App(False)
  frm = MyFrame(None, wx.NewId())
  app.SetTopWindow(frm)
  frm.Show()
  app.MainLoop()
