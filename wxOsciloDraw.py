#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wxOsciloDraw
'''

import wx
import wxaddons.sized_controls as sc
from matplotPanel import matplotPanel
import numpy as np
import math

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    super(MyFrame, self).__init__(title=u'wxOsciloDraw',
      pos=(240, 240), size=(640, 640), *args, **kwargs)
    hsz = wx.BoxSizer(wx.HORIZONTAL)
    self.lpnl = sc.SizedPanel(self, -1)
    self.lpnl.SetSizerType('grid', {'cols': 2})

    t = np.arange(-math.pi, math.pi, 0.001)
    x = reduce(lambda a, b: a + np.sin(b*t)/b, xrange(1, 65), 0.0)
    y = reduce(lambda a, b: a + np.cos(b*t), xrange(1, 65), 0.0)

    def drawY(self):
      self.figure.set_facecolor((1.0, 0.7, 0.7))
      self.canvas.SetBackgroundColour(wx.Color(255, 100, 100))
      plt = self.figure.add_subplot(111)
      plt.plot(t, y)
      # plt.set_xlabel('t')
      # plt.set_ylabel('y')
      # plt.axis([-math.pi, math.pi, -5, 5])
    self.mppY = matplotPanel(drawY, self.lpnl, wx.NewId())
    self.mppY.SetMinSize((400, 200))
    self.mppY.SetSizerProps(expand=True, proportion=1)

    def drawXY(self):
      self.figure.set_facecolor((0.7, 1.0, 0.7))
      self.canvas.SetBackgroundColour(wx.Color(100, 255, 100))
      plt = self.figure.add_subplot(111)
      plt.plot(x, y)
      # plt.set_xlabel('x')
      # plt.set_ylabel('y')
      # plt.axis([-4, 4, -4, 4])
      # plt.set_xscale('log')
      # plt.set_yscale('log')
    self.mppXY = matplotPanel(drawXY, self.lpnl, wx.NewId())
    self.mppXY.SetMinSize((200, 200))
    self.mppXY.SetSizerProps(expand=True, proportion=1)

    self.ctl = wx.Panel(self.lpnl, wx.NewId())
    self.ctl.SetSizerProps(expand=True, proportion=1)

    def drawX(self):
      self.figure.set_facecolor((0.7, 0.7, 1.0))
      self.canvas.SetBackgroundColour(wx.Color(100, 100, 255))
      plt = self.figure.add_subplot(111)
      plt.plot(x, t)
      # plt.set_xlabel('x')
      # plt.set_ylabel('t')
      # plt.axis([-5, 5, -math.pi, math.pi])
    self.mppX = matplotPanel(drawX, self.lpnl, wx.NewId())
    self.mppX.SetMinSize((200, 400))
    self.mppX.SetSizerProps(expand=True, proportion=1)

    self.lpnl.Fit()
    self.lpnl.SetMinSize(self.lpnl.GetSize())
    hsz.Add(self.lpnl, 1, wx.EXPAND)
    # self.rpnl = wx.Panel(self, -1)
    # hsz.Add(self.rpnl, 0, wx.EXPAND)
    self.SetSizer(hsz)
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
