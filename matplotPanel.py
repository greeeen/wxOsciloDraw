#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''matplotPanel
参考
matplotlibをwxPythonで扱う 2010-03-27
http://d.hatena.ne.jp/white_wheels/20100327/p5
'''

import wx
import matplotlib
matplotlib.interactive(True)
matplotlib.use('WXAgg') # must load once and called before import backend_wxagg
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

class matplotPanel(wx.Panel):
  def __init__(self, drawfunc, parent, id, *args, **kwargs):
    super(matplotPanel, self).__init__(parent, id, *args, **kwargs)
    self.drawfunc = drawfunc
    self.parent = parent
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint)

  def _SetSize(self):
    # size = tuple(self.parent.GetClientSize())
    size = tuple(self.GetClientSize())
    # self.SetSize(size)
    self.figure = Figure(None)
    self.canvas = FigureCanvasWxAgg(self, wx.NewId(), self.figure)
    self.canvas.SetSize(size)
    dpi = self.figure.get_dpi()
    self.figure.set_size_inches(float(size[0]) / dpi, float(size[1]) / dpi)

  def OnSize(self, ev):
    self.Refresh()

  def OnPaint(self, ev):
    self._SetSize()
    dc = wx.PaintDC(self) # don't delete this line
    self.drawfunc(self)

if __name__ == '__main__':
  app = wx.App(False)
  frm = wx.Frame(None, -1, u'matplotPanel', pos=(320, 240), size=(640, 480))

  def draw(self):
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    import math
    x = np.arange(-math.pi, math.pi, 0.25)
    y = np.arange(-math.pi, math.pi, 0.25)
    X, Y = np.meshgrid(x, y)
    Z = np.cos(X) + np.sin(Y)
    if True:
      self.figure.set_facecolor((0.7, 1.0, 0.7))
      self.canvas.SetBackgroundColour(wx.Color(100, 255, 100))
      plt = self.figure.add_subplot(111)
      plt.plot(x, Z)
      plt.set_xlabel('x log')
      plt.set_ylabel('y log')
      plt.axis([-10, 10, -10, 10])
      plt.set_xscale('log')
      plt.set_yscale('log')
    else:
      ax = Axes3D(self.figure)
      ax.plot_wireframe(X, Y, Z)

  pnl = matplotPanel(draw, frm, wx.NewId())
  app.SetTopWindow(frm)
  frm.Show()
  app.MainLoop()
