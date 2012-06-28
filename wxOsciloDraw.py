#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wxOsciloDraw
'''

import sys, os
import math

import wx
import wxaddons.sized_controls as sc
from matplotPanel import matplotPanel
import numpy as np

APP_TITLE = u'wxOsciloDraw'
APP_FILE = u'testdata'
APP_EXT = u'turtle'

DEF_T_MIN = -math.pi
DEF_T_MAX = math.pi
DEF_T_TICK = 0.001
DEF_TWIDTH = 400
DEF_X_MIN = -2.0
DEF_X_MAX = 2.0
DEF_XWIDTH = 200
DEF_YWIDTH = 200
DEF_Y_MIN = -2.0
DEF_Y_MAX = 2.0
DEF_FACOLOR_R = (1.0, 0.7, 0.7)
DEF_FACOLOR_G = (0.7, 1.0, 0.7)
DEF_FACOLOR_B = (0.7, 0.7, 1.0)
DEF_BGCOLOR_R = wx.Color(255, 100, 100)
DEF_BGCOLOR_G = wx.Color(100, 255, 100)
DEF_BGCOLOR_B = wx.Color(100, 100, 255)

def loaddata(fname):
  orbit = []
  if not os.path.exists(fname):
    wx.MessageBox(u'file is not found: %s' % fname, APP_TITLE, wx.OK)
  else:
    try:
      ifp = open(fname, 'rb')
      c = 0
      for line in ifp.readlines():
        c += 1
        p = map(float, line.rstrip().lstrip().split())
        orbit.append((int(p[0]), p[1], p[2]))
    except (IOError,), e:
      wx.MessageBox(u'file read error: %s' % fname, APP_TITLE, wx.OK)
    except (IndexError, ValueError), e:
      wx.MessageBox(u'bad data in [%s] line %d' % (fname, c), APP_TITLE, wx.OK)
    finally:
      if ifp: ifp.close()
  return orbit

def getnextpoint(p, qa, qx, qy):
  pa = qa + p[1]
  ra = pa * math.pi / 180.0
  return (pa, int(qx + p[2] * math.cos(ra)), int(qy + p[2] * math.sin(ra)))

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    super(MyFrame, self).__init__(title=APP_TITLE,
      pos=(240, 240), size=(640, 640), *args, **kwargs)
    hsz = wx.BoxSizer(wx.HORIZONTAL)
    self.lpnl = sc.SizedPanel(self, -1)
    self.lpnl.SetSizerType('grid', {'cols': 2})

    autoscale = True # False のときは下行の各値を gauge で set
    x_min, x_max, y_min, y_max = DEF_X_MIN, DEF_X_MAX, DEF_Y_MIN, DEF_Y_MAX
    usefft = False # True
    if usefft:
      t = np.arange(DEF_T_MIN, DEF_T_MAX, DEF_T_TICK)
      x = reduce(lambda a, b: a + np.sin(b*t)/b, xrange(1, 65), 0.0)
      y = reduce(lambda a, b: a + np.cos(b*t), xrange(1, 65), 0.0)
    else:
      o = loaddata(os.path.abspath(u'./%s.%s' % (APP_FILE, APP_EXT)))
      t = [1000.0 * (float(n) / len(o)) for n in xrange(len(o))] # (+ 1 原点含)
      x = [] # ([0] 原点含)
      y = [] # ([0] 原点含)
      qa, qx, qy = 0.0, 0, 0
      for p in o:
        qa, qx, qy = getnextpoint(p, qa, qx, qy)
        x.append(qx)
        y.append(qy)

    def drawY(self):
      self.figure.set_facecolor(DEF_FACOLOR_R)
      self.canvas.SetBackgroundColour(DEF_BGCOLOR_R)
      plt = self.figure.add_subplot(111)
      plt.plot(t, y)
      plt.set_xlabel('t')
      plt.set_ylabel('y')
      if not autoscale: plt.axis([DEF_T_MIN, DEF_T_MAX, y_min, y_max])
    self.mppY = matplotPanel(drawY, self.lpnl, wx.NewId())
    self.mppY.SetMinSize((DEF_TWIDTH, DEF_YWIDTH))
    self.mppY.SetSizerProps(expand=True, proportion=1)

    def drawXY(self):
      self.figure.set_facecolor(DEF_FACOLOR_G)
      self.canvas.SetBackgroundColour(DEF_BGCOLOR_G)
      plt = self.figure.add_subplot(111)
      plt.plot(x, y)
      plt.set_xlabel('x')
      plt.set_ylabel('y')
      if not autoscale: plt.axis([x_min, x_max, y_min, y_max])
      # plt.set_xscale('log')
      # plt.set_yscale('log')
    self.mppXY = matplotPanel(drawXY, self.lpnl, wx.NewId())
    self.mppXY.SetMinSize((DEF_XWIDTH, DEF_YWIDTH))
    self.mppXY.SetSizerProps(expand=True, proportion=1)

    self.ctl = wx.Panel(self.lpnl, wx.NewId())
    self.ctl.SetSizerProps(expand=True, proportion=1)

    def drawX(self):
      self.figure.set_facecolor(DEF_FACOLOR_B)
      self.canvas.SetBackgroundColour(DEF_BGCOLOR_B)
      plt = self.figure.add_subplot(111)
      plt.plot(x, t)
      plt.set_xlabel('x')
      plt.set_ylabel('t')
      if not autoscale: plt.axis([x_min, x_max, DEF_T_MIN, DEF_T_MAX])
    self.mppX = matplotPanel(drawX, self.lpnl, wx.NewId())
    self.mppX.SetMinSize((DEF_XWIDTH, DEF_TWIDTH))
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
