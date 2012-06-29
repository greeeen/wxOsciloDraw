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
APP_DFT = u'dft'

DEF_TWIDTH, DEF_T_MIN, DEF_T_MAX, DEF_T_TICK = 400, -math.pi, math.pi, 0.001
DEF_XWIDTH, DEF_X_MIN, DEF_X_MAX = 200, -2.0, 2.0
DEF_YWIDTH, DEF_Y_MIN, DEF_Y_MAX = 200, -2.0, 2.0
DEF_BGCOLOR_R = ((1.0, 0.7, 0.7), wx.Color(255, 100, 100))
DEF_BGCOLOR_G = ((0.7, 1.0, 0.7), wx.Color(100, 255, 100))
DEF_BGCOLOR_B = ((0.7, 0.7, 1.0), wx.Color(100, 100, 255))

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

def load_dft(fname):
  F = []
  X = []
  Y = []
  return F, X, Y

def save_dft(fname, F, X, Y):
  try:
    ofp = open(fname, 'wb')
    for i in xrange(len(F)):
      if F[i] >= 0.0:
        ofp.write('%f %f %f %f %f\n' % (
          F[i], X[i].real, X[i].imag, Y[i].real, Y[i].imag))
  except (IOError,), e:
    wx.MessageBox(u'file write error: %s' % fname, APP_TITLE, wx.OK)
  finally:
    if ofp: ofp.close()

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    super(MyFrame, self).__init__(title=APP_TITLE,
      pos=(240, 240), size=(640, 640), *args, **kwargs)
    hsz = wx.BoxSizer(wx.HORIZONTAL)
    self.lpnl = sc.SizedPanel(self, -1)
    self.lpnl.SetSizerType('grid', {'cols': 2})

    autoscale = True # False のときは下行の各値を gauge で set
    x_min, x_max, y_min, y_max = DEF_X_MIN, DEF_X_MAX, DEF_Y_MIN, DEF_Y_MAX
    usefft = True # False # True
    if usefft:
      F, X, Y = load_dft(os.path.abspath(u'./%s.%s' % (APP_FILE, APP_DFT)))
      if False: # test
        t = np.arange(DEF_T_MIN, DEF_T_MAX, DEF_T_TICK)
        x = reduce(lambda a, b: a + np.sin(b*t)/b, xrange(1, 65), 0.0)
        y = reduce(lambda a, b: a + np.cos(b*t), xrange(1, 65), 0.0)
      else:
        t = np.arange(DEF_T_MIN, DEF_T_MAX, DEF_T_TICK)
        x = reduce(lambda a, b: a + np.sin(b*t)/b, xrange(1, 65), 0.0)
        y = reduce(lambda a, b: a + np.cos(b*t), xrange(1, 65), 0.0)
    else:
      o = loaddata(os.path.abspath(u'./%s.%s' % (APP_FILE, APP_EXT)))
      # (原点を含めるときは xrange(len(o) + 2) として x, y = [0], [0] で初期化)
      # t = [(1000.0 * float(n) / len(o)) for n in xrange(len(o) + 1)] # 正規化
      t = [(2.0 * math.pi * float(n) / len(o) - math.pi) \
        for n in xrange(len(o) + 1)] # -π ～ +π で正規化
      x = [] # ([0] 原点含)
      y = [] # ([0] 原点含)
      qa, qx, qy = 0.0, 0, 0
      for p in o:
        qa, qx, qy = getnextpoint(p, qa, qx, qy)
        x.append(qx)
        y.append(qy)
      x.append(x[0])
      y.append(y[0])
    f = len(t) # 100.0
    F = np.fft.fftfreq(len(t), 1.0 / f) # t[1] - t[0])
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    XA = np.sqrt(X.real ** 2 + X.imag ** 2)
    YA = np.sqrt(Y.real ** 2 + Y.imag ** 2)
    if not usefft:
      save_dft(os.path.abspath(u'./%s.%s' % (APP_FILE, APP_DFT)), F, X, Y)

    def drawY(self):
      self.figure.set_facecolor(DEF_BGCOLOR_R[0])
      self.canvas.SetBackgroundColour(DEF_BGCOLOR_R[1])
      pfft = self.figure.add_subplot(121)
      pfft.plot(F, YA, 'ro', markersize=3) # red dot
      #pfft.set_xscale('log')
      pfft.set_yscale('log')
      pfft.axis([0, f / 2, 0, 10000])
      plt = self.figure.add_subplot(122)
      plt.plot(t, y)
      plt.set_xlabel('t')
      plt.set_ylabel('y')
      if not autoscale: plt.axis([DEF_T_MIN, DEF_T_MAX, y_min, y_max])
    self.mppY = matplotPanel(drawY, self.lpnl, wx.NewId())
    self.mppY.SetMinSize((DEF_TWIDTH, DEF_YWIDTH))
    self.mppY.SetSizerProps(expand=True, proportion=1)

    def drawXY(self):
      self.figure.set_facecolor(DEF_BGCOLOR_G[0])
      self.canvas.SetBackgroundColour(DEF_BGCOLOR_G[1])
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
      self.figure.set_facecolor(DEF_BGCOLOR_B[0])
      self.canvas.SetBackgroundColour(DEF_BGCOLOR_B[1])
      pfft = self.figure.add_subplot(212)
      pfft.plot(XA, F, 'bo', markersize=3) # blue dot
      pfft.set_xscale('log')
      #pfft.set_yscale('log')
      pfft.axis([0, 10000, 0, f / 2])
      plt = self.figure.add_subplot(211)
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
