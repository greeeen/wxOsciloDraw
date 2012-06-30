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

# DEF_T_TICK 変更時の .dft 出力データサンプル数の目安
# (usefft を False にすると .turtle データから .dft データに変換)
# 1.0 のときは .turtle と同数(変換後の共役複素数=負値は保存しないので実質半数)
# 0.1(32) 0.05(64) 0.025(128) 0.0125(256) 0.01(320) 0.005(640) 0.001(3200)
DEF_T_TICK = 0.005 # 0.01 でほぼ充分だが test mode (preset) のデータだと粗い為
DEF_TWIDTH, DEF_T_MIN, DEF_T_MAX = 400, -math.pi, math.pi
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

def load_turtle(fname):
  o = loaddata(fname)
  # (原点を含めるときは xrange(len(o) + 2) として x, y = [0], [0] で初期化)
  # t = [(1000.0 * float(n) / len(o)) for n in xrange(len(o) + 1)] # 正規化
  t = [(2.0 * math.pi * float(n) / len(o) - math.pi) \
    for n in xrange(len(o) + 1)] # -π ～ +π で正規化 (interp 準備兼用)
  x, y = [], [] # ([0], [0] 原点含)
  qa, qx, qy = 0.0, 0, 0
  for p in o:
    qa, qx, qy = getnextpoint(p, qa, qx, qy)
    x.append(qx), y.append(qy)
  x.append(x[0]), y.append(y[0])
  return np.array(t, float), np.array(x, int), np.array(y, int)

def load_dft(fname):
  t, x, y, o = np.arange(DEF_T_MIN, DEF_T_MAX, DEF_T_TICK), [], [], []
  if False: # test mode return preset value
    x = reduce(lambda a, b: a + np.sin(b*t)/b, xrange(1, 65), 0.0)
    y = reduce(lambda a, b: a + np.cos(b*t), xrange(1, 65), 0.0)
    return t, x, y
  if not os.path.exists(fname):
    wx.MessageBox(u'file is not found: %s' % fname, APP_TITLE, wx.OK)
  else:
    try:
      ifp = open(fname, 'rb')
      c = 0
      for line in ifp.readlines():
        c += 1
        p = map(float, line.rstrip().lstrip().split())
        o.append((c - 1, p[0], p[1], p[2], p[3]))
    except (IOError,), e:
      wx.MessageBox(u'file read error: %s' % fname, APP_TITLE, wx.OK)
    except (IndexError, ValueError), e:
      wx.MessageBox(u'bad data in [%s] line %d' % (fname, c), APP_TITLE, wx.OK)
    finally:
      if ifp: ifp.close()
  x = reduce(lambda a, b: \
    a + o[b][1] * np.cos(b * t) + o[b][2] * np.sin(b * t), xrange(len(o)), 0.0)
  y = reduce(lambda a, b: \
    a + o[b][3] * np.cos(b * t) + o[b][4] * np.sin(b * t), xrange(len(o)), 0.0)
  return t, x, y

def save_dft(fname, F, X, Y):
  try:
    ofp = open(fname, 'wb')
    for i in xrange(len(F)):
      if F[i] >= 0.0:
        ofp.write('%f %f %f %f\n' % (
          X[i].real, X[i].imag, Y[i].real, Y[i].imag))
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
    usefft = False # True
    if not usefft:
      t, x, y = load_turtle(os.path.abspath(u'./%s.%s' % (APP_FILE, APP_EXT)))
      if DEF_T_TICK < 1.0: # re-sampling by enhanced scale
        et = np.arange(DEF_T_MIN, DEF_T_MAX, DEF_T_TICK) # enhanced scale
        x, y = np.interp(et, t, x), np.interp(et, t, y)
        t = et # set new scale after np.interp()
    else:
      t, x, y = load_dft(os.path.abspath(u'./%s.%s' % (APP_FILE, APP_DFT)))
    x *= .9 / np.max(np.abs(x))
    y *= .9 / np.max(np.abs(y))

    N = len(t) # number of samples
    f = N # frequency (now N / 1)
    F = np.fft.fftfreq(N, 1.0 / f) # (tick = t[1] - t[0])
    X, Y = np.fft.fft(x), np.fft.fft(y)
    XA = np.sqrt(X.real ** 2 + X.imag ** 2)
    YA = np.sqrt(Y.real ** 2 + Y.imag ** 2)
    if not usefft:
      save_dft(os.path.abspath(u'./%s.%s' % (APP_FILE, APP_DFT)), F, X, Y)
    # print u'len t: %d, x: %d, y: %d, F: %d, X: %d, Y: %d, XA: %d, YA: %d' % (
    #   len(t), len(x), len(y), len(F), len(X), len(Y), len(XA), len(YA))

    def drawY(self):
      self.figure.set_facecolor(DEF_BGCOLOR_R[0])
      self.canvas.SetBackgroundColour(DEF_BGCOLOR_R[1])
      plt = self.figure.add_subplot(122)
      if not usefft: plt.plot(t, y, 'ro', markersize=1) # red dot
      else: plt.plot(t, y)
      plt.set_xlabel('t')
      plt.set_ylabel('y')
      if not autoscale: plt.axis([DEF_T_MIN, DEF_T_MAX, y_min, y_max])
      pfft = self.figure.add_subplot(121)
      pfft.plot(F, YA, 'ro', markersize=2) # red dot
      #pfft.set_xscale('log')
      pfft.set_yscale('log')
      pfft.axis([0, f / 2, 0, 100])
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
      plt = self.figure.add_subplot(211)
      if not usefft: plt.plot(x, t, 'bo', markersize=1) # blue dot
      else: plt.plot(x, t)
      plt.set_xlabel('x')
      plt.set_ylabel('t')
      if not autoscale: plt.axis([x_min, x_max, DEF_T_MIN, DEF_T_MAX])
      pfft = self.figure.add_subplot(212)
      pfft.plot(XA, F, 'bo', markersize=2) # blue dot
      pfft.set_xscale('log')
      #pfft.set_yscale('log')
      pfft.axis([0, 100, 0, f / 2])
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
