#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wxOsciloDraw
'''

import wx
from matplotPanel import matplotPanel

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    super(MyFrame, self).__init__(title=u'wxOsciloDraw',
      pos=(320, 240), size=(640, 480), *args, **kwargs)

    def draw(self):
      import numpy as np
      import math
      x = np.arange(-math.pi, math.pi, 0.25)
      y = np.arange(-math.pi, math.pi, 0.25)
      X, Y = np.meshgrid(x, y)
      Z = np.cos(X) + np.sin(Y)
      self.figure.set_facecolor((0.7, 1.0, 0.7))
      self.canvas.SetBackgroundColour(wx.Color(100, 255, 100))
      plt = self.figure.add_subplot(111)
      plt.plot(x, Z)
      plt.set_xlabel('x')
      plt.set_ylabel('y')
      plt.axis([-5, 5, -5, 5])
      # plt.set_xscale('log')
      # plt.set_yscale('log')

    self.mpp = matplotPanel(draw, self, wx.NewId())
    self.Bind(wx.EVT_CLOSE, self.OnClose)

  def OnClose(self, ev):
    # if not self.checkDisposedOK(self.GetTitle(), u'Quit'): return
    # if not self.CanVeto():
    self.Destroy()

if __name__ == '__main__':
  app = wx.App(False)
  frm = MyFrame(None, wx.NewId())
  app.SetTopWindow(frm)
  frm.Show()
  app.MainLoop()
