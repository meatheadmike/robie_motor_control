import time, random
from resources.mode_plugin_abstract import ModePluginAbstract
from neopixel import Color

class BumpAndGo(ModePluginAbstract):
  def __init__(self, led_strip, left_fwd, left_rev, right_fwd, right_rev):
    self.strip = led_strip
    self.left_fwd = left_fwd
    self.left_rev = left_rev
    self.right_fwd = right_fwd
    self.right_rev = right_rev
    self.signalon = 0
    self.signaloff = 0
    self.distance_buffer = []
    self.buffer_size = 5
    self.duty = 100
    self.directionality = 'left'
    self.stopped = True

  def _doGoLeft(self, amt = None):
    if amt == None:
      amt = float(random.randint(30,70)) / 100
    self.left_fwd.stop()
    self.right_rev.stop()
    self.left_rev.start(self.duty)
    self.right_fwd.start(self.duty)
    time.sleep(amt)
    self.left_rev.stop()
    self.right_fwd.stop()

  def _doGoRight(self, amt = None):
    if amt == None:
      amt = float(random.randint(30,70)) / 100
    self.right_fwd.stop()
    self.left_rev.stop()
    self.right_rev.start(self.duty)
    self.left_fwd.start(self.duty)
    time.sleep(amt)
    self.right_rev.stop()
    self.left_fwd.stop()
 
  def leftHandPressed(self):
    self.directionality = 'left'
    self._doGoLeft(0.2)
    time.sleep(0.3)
    self._doGoForward()

  def rightHandPressed(self):
    self.directionality = 'right'
    self._doGoRight(0.2)
    time.sleep(0.3)
    self._doGoForward()

  def _doBumpStop(self):
    self.left_fwd.stop()
    self.right_fwd.stop()
    self.left_rev.start(self.duty)
    self.right_rev.start(self.duty) 
    time.sleep(0.4)
    self.left_rev.stop()
    self.right_rev.stop()
    time.sleep(0.3)
    if self.directionality == 'left':
      self._doGoLeft()
    else:
      self._doGoRight()

  def _doGoForward(self):
    self.left_rev.stop()
    self.right_rev.stop()
    self.left_fwd.start(self.duty)
    self.right_fwd.start(self.duty)

  def _doStop(self):
    self.left_rev.stop()
    self.right_rev.stop()
    self.left_fwd.stop()
    self.right_fwd.stop()

  def bumperPressed(self):
    if self.stopped == True:
      self.stopped = False
      time.sleep(0.3)
      self._doGoForward()
    else: #stopped == False
      self._doBumpStop()
      time.sleep(0.3)
      self._doGoForward()

  def echoCallback(self, pin, value):
    if value == 1:
      self.signalon = time.time()
      return
    self.signaloff = time.time()
    timepassed = self.signaloff - self.signalon
    distance = timepassed * 17000
    if distance > 0 and distance < 300:
      self.distance_buffer.insert(0,distance)
    if len(self.distance_buffer) > self.buffer_size:
      self.distance_buffer.pop()
    # average out our reading:
    if self.stopped == False and self.distance_buffer != []:
      distance_cm = sum(self.distance_buffer) / len(self.distance_buffer)
      if distance_cm < 15:
        #print "ping sensor stop!"
        self._doBumpStop() 
        time.sleep(0.3)
        self._doGoForward()

  def motorControl(self, left, right):
    pass

  def cleanup(self):
    self._doStop()
