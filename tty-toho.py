#!/bin/python
# -*- coding: utf-8 -*-
'''
# tty toho
# ver 0.1
# 2012-04-01, take
'''

import traceback
import curses, locale
import time
import math, random

# debug flag
DEBUG = 0

# delay
WAIT = 0.1

# key input code
KEY_QUIT = 113
KEY_UP = 107
KEY_DOWN = 106
KEY_LEFT = 104
KEY_RIGHT = 108

class CursesWindow():
  def __init__(self, host=''):
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(self.loop, host)

  def loop(self, scr, host):

    #----------------
    # init
    #----------------
    self.init_curses()
    self.init_windows(scr)
    self.init_game()

    # marisa
    marisa = Marisa(self.cmd_window, self.msg_window, 20, 20)
    
    # enemy
    enemys = []

    # main loop
    t = 0
    numbuf = 0
    while 1:

      #----------------
      # 自機ターン
      #----------------
      # キー入力チェック
      input = self.getch()
      
      # 未入力
      if input == -1:
        pass

      # quit
      elif input == KEY_QUIT:
        break

      # 数字(vi like)
      elif (self.numFromKey(input) != -1):
        numbuf = numbuf * 10 + self.numFromKey(input)

      # 移動(vi like)
      elif (
        input == KEY_UP or 
        input == KEY_DOWN or 
        input == KEY_LEFT or 
        input == KEY_RIGHT ):
        marisa.move(input, numbuf)
        numbuf = 0

      else:
        numbuf = 0


      #----------------
      # 敵ターン
      #----------------
      # 生成
      for i in range(1, 2):
        #enemy = Enemy(self.cmd_window, self.msg_window, 0, random.randint(0, 50))
        enemy = EnemyStraight(self.cmd_window, self.msg_window, 0, random.randint(0, 50), slant=(random.random()-0.5))
        enemys.append(enemy)

      for i in range(1, 2):
        enemy = EnemyWave(self.cmd_window, self.msg_window, 0, random.randint(0, 50))
        enemys.append(enemy)

      for i in range(1, 2):
        enemy = EnemySlow(self.cmd_window, self.msg_window, 0, random.randint(0, 50))
        enemys.append(enemy)

      for enemy in enemys:
        enemy.move()

      #----------------
      # 再描画
      #----------------
      self.cmd_window.clear()
      if DEBUG:
        self.dmessage("t: %d" % (t,))
      marisa.render()
      for enemy in enemys:
        enemy.render()
      self.cmd_window.box()
      self.refresh

      #----------------
      # next frame
      #----------------
      time.sleep(WAIT);
      t += 1

    # fin
    self.fin_game()

  def numFromKey(self, input):
    if input >= 48 and input <=57:
      return input - 48
    else:
      return -1

  def init_curses(self):
    # color
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED,    curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN,  curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN,   curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # エコーバック off
    curses.noecho()

    # 入力行バッファリング off
    curses.cbreak()

    # カーソル非表示
    curses.curs_set(0)

    # 特殊キー対応
    #curses.keypad(1)

  def init_windows(self, scr):
    # main window
    self.cmd_window = scr.subwin(24, 50, 0, 0)
    self.cmd_window.box()
    
    # non-blocking key input
    self.cmd_window.nodelay(1)
    
    # sub window for message
    self.msg_window = scr.subwin(24, 30, 0, 50)
    #self.msg_window = scr.subwin(24, 60, 0, 50)
    self.msg_window.box()
    self.msg_window.scrollok(True)
    self.msg_window.move(1, 1)

  def init_game(self):
    self.message("tty 東方 ver0.1", 1)
    self.message("",)
    self.message("Usage: (vi like)")
    self.message("  'q' exit")
    self.message("  'k' up")
    self.message("  'j' down")
    self.message("  'h' left")
    self.message("  'l' right")
    self.message("",)

  def fin_game(self):
    pass

  def refresh(self, word=''):
    self.cmd_window.refresh()

  def getch(self, word=''):
    input = self.cmd_window.getch()
#    self.dmessage("input: " + str(input))
    return input

  def message(self, msg, color=0):
    msg = " " + msg + "\n"
    if color:
      self.msg_window.addstr(msg, curses.color_pair(color))
    else:
      self.msg_window.addstr(msg)
    self.msg_window.box()
    self.msg_window.refresh()

  def dmessage(self, msg):
    if DEBUG:
      self.message("debug: " + msg, 3)

  def refresh(self):
    self.cmd_window.refresh()


class Shoot():
  def __init__(self, view=None):
    self.view = view


class GameCh():

  SELF_CHAR = '.'
  SELF_ATTR = 0

  def __init__(self, view=None, msgView=None, y=0, x=0):
    self.view = view
    self.msgView = msgView
    self.x = x
    self.y = y
    self.age = 0

    # ウィンドウのサイズを取得して、
    (self.maxy, self.maxx) = self.view.getmaxyx()
    # 両端のboxの1文字分を狭くする
    self.miny  = 1
    self.minx  = 1
    self.maxy -= 2
    self.maxx -= 2

  def render(self):
    if (
      self.x >= self.minx and 
      self.x <= self.maxx and 
      self.y >= self.miny and 
      self.y <= self.maxy ):
      self.view.addch(self.y, self.x, self.SELF_CHAR, self.SELF_ATTR)
    self.age += 1

  def dmessage(self, msg):
    if DEBUG:
      self.msgView.addstr("debug: %s\n" % msg)
      self.msgView.refresh()

  def fin(self):
    self = None

class Marisa(GameCh):
  '''
  自機
  '''

  SELF_CHAR = '@'
  SELF_ATTR = 0

  def __init__(self, view=None, msgView=None, y=0, x=0):
    GameCh.__init__(self, view, msgView, y, x)
    self.dmessage("init Marisa")
    
  def move(self, input, step=0):
    # stepが未指定なら、1つずつ
    if step == 0:
      step = 1

    if input == KEY_UP:
      self.y = self.y - step
    elif input == KEY_DOWN:
      self.y = self.y + step
    elif input == KEY_LEFT:
      self.x = self.x - step
    elif input == KEY_RIGHT:
      self.x = self.x + step

    # 行き過ぎたら、戻る
    if self.x < self.minx:
      self.x = self.minx
    if self.x > self.maxx:
      self.x = self.maxx
    if self.y < self.miny:
      self.y = self.miny
    if self.y > self.maxy:
      self.y = self.maxy

    self.dmessage("self.y: %d, self.x: %d" % (self.y, self.x))

class Enemy(GameCh):
  '''
  敵-基底クラス
  '''

  SELF_CHAR = 'x'
  SELF_ATTR = 0
  SELF_SPEED = 1

  def __init__(self, view=None, msgView=None, y=0, x=0, **opt):
    GameCh.__init__(self, view, msgView, y, x)
    self.dmessage("init Enemy")
  
  def move(self):
    self.y += self.SELF_SPEED
    self.x += 0
    self.dmessage("age: %d, self.y: %.1f, self.x: %.1f" % (self.age, self.y, self.x))

    if self.y > self.maxy:
      self.fin()


class EnemyStraight(Enemy):
  '''
  敵-直線型
  '''

  SELF_CHAR = 'V'
  SELF_ATTR = 0
  SELF_SPEED = 1

  def __init__(self, view=None, msgView=None, y=0, x=0, **opt):
    GameCh.__init__(self, view, msgView, y, x)
    self.slant = opt["slant"]
  
  def move(self):
    self.y += self.SELF_SPEED
    self.x += self.slant
    self.dmessage("age: %d, self.y: %.1f, self.x: %.1f" % (self.age, self.y, self.x))

    if self.y > self.maxy:
      self.fin()

class EnemyWave(Enemy):
  '''
  敵-ゆらゆら型
  '''

  SELF_CHAR = 'Q'
  SELF_ATTR = 1
  SELF_SPEED = 0.8

  def __init__(self, view=None, msgView=None, y=0, x=0, **opt):
    GameCh.__init__(self, view, msgView, y, x)
  
  def move(self):
    self.y += self.SELF_SPEED
    self.x += math.sin(self.age) * 2 * self.SELF_SPEED
    self.dmessage("age: %d, self.y: %.1f, self.x: %.1f" % (self.age, self.y, self.x))

    if self.y > self.maxy:
      self.fin()

class EnemySlow(Enemy):
  '''
  敵-遅い(弾幕替わり)
  '''

  SELF_CHAR = '*'
  SELF_ATTR = 0
  SELF_SPEED = 0.4

  def __init__(self, view=None, msgView=None, y=0, x=0, **opt):
    GameCh.__init__(self, view, msgView, y, x)
  
  def move(self):
    self.y += self.SELF_SPEED
    self.dmessage("age: %d, self.y: %.1f, self.x: %.1f" % (self.age, self.y, self.x))

    if self.y > self.maxy:
      self.fin()


'''
main
'''

CursesWindow()

