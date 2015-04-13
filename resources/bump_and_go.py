import time, random
from resources.mode_plugin_abstract import ModePluginAbstract
from neopixel import Color

class BumpAndGo(ModePluginAbstract):

  global distance_buffer
  global blocking
 
  def __init__(self, parent):
    global distance_buffer
    global blocking
    self.parent = parent
    self.strip = parent.strip
    self.left_fwd = parent.left_fwd
    self.left_rev = parent.left_rev
    self.right_fwd = parent.right_fwd
    self.right_rev = parent.right_rev
    self.signalon = 0
    self.signaloff = 0
    distance_buffer = []
    self.buffer_size = 5
    self.duty = 100
    self.directionality = 'left'
    blocking = False
    self.stopped = True

  def _doGoLeft(self, amt = None):
    if amt == None:
      amt = float(random.randint(40,80)) / 100
    self.left_fwd.stop()
    self.right_rev.stop()
    self.left_rev.start(self.duty)
    self.right_fwd.start(self.duty)
    time.sleep(amt)
    self.left_rev.stop()
    self.right_fwd.stop()

  def _doGoRight(self, amt = None):
    if amt == None:
      amt = float(random.randint(40,80)) / 100
    self.right_fwd.stop()
    self.left_rev.stop()
    self.right_rev.start(self.duty)
    self.left_fwd.start(self.duty)
    time.sleep(amt)
    self.right_rev.stop()
    self.left_fwd.stop()
 
  def leftHandPressed(self):
    global blocking
    if blocking:
      return
    blocking = True
    self.directionality = 'left'
    self._doGoLeft(0.2)
    if self.stopped == False:
      time.sleep(0.3)
      self._doGoForward()
    blocking = False

  def rightHandPressed(self):
    global blocking
    if blocking:
      return
    blocking = True
    self.directionality = 'right'
    self._doGoRight(0.2)
    if self.stopped == False:
      time.sleep(0.3)
      self._doGoForward()
    blocking = False
  
  def _scanForBestDirection(self):
    global distance_buffer
    old_buffer_size = self.buffer_size
    self.buffer_size = 10 
    amt = 20.0
    best_loc={'x_loc':0, 'distance':0.0}
    for x in range(0,6):
      if self.parent.mode_changed:
        return
      if self.directionality == 'left':
        self._doGoLeft(amt / 100)
      else:
        self._doGoRight(amt / 100)
      distance_buffer = []
      for y in range(0,10):
        self.parent._doPing()
        time.sleep(0.01)
      if distance_buffer != []:
        distance_cm = sum(distance_buffer) / len(distance_buffer)
        #print "distance = %s" % distance_buffer
        if distance_cm > best_loc['distance']:
          best_loc['x_loc'] = x
          best_loc['distance'] = distance_cm
    time.sleep(0.05)
    #print "best_loc:%s" % best_loc
    if best_loc['x_loc'] < 5:
      if self.directionality == 'left':
        self._doGoRight((amt * (5-best_loc['x_loc']))/100)
      else:
        self._doGoLeft((amt * (5-best_loc['x_loc']))/100)
    time.sleep(0.3)
    self.buffer_size = old_buffer_size
 
  def _doBumpStop(self):
    self.left_fwd.stop()
    self.right_fwd.stop()
    time.sleep(0.3)
    self.left_rev.start(self.duty)
    self.right_rev.start(self.duty) 
    time.sleep(0.5)
    self.left_rev.stop()
    self.right_rev.stop()
    time.sleep(0.3)
    #print "scan for best direction"
    self._scanForBestDirection()
    #print "done scanning"

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
    global blocking
    if blocking:
      return
    blocking = True
    if self.stopped == True:
      self.stopped = False
      time.sleep(0.3)
      self._doGoForward()
    else: #stopped == False
      self._doBumpStop()
      time.sleep(0.3)
      self._doGoForward()
    blocking = False

  def echoCallback(self, pin, value):
    global distance_buffer
    if value == 1:
      self.signalon = time.time()
      return
    self.signaloff = time.time()
    timepassed = self.signaloff - self.signalon
    distance = timepassed * 17000
    if distance > 0 and distance < 3000:
      distance_buffer.insert(0,distance)
    if len(distance_buffer) > self.buffer_size:
      distance_buffer.pop()

  def motorControl(self, left, right):
    pass

  def loopHook(self):
    global distance_buffer
    global blocking
    if blocking:
      return
    # average out our reading:
    if self.stopped == False and distance_buffer != []:
      distance_cm = sum(distance_buffer) / len(distance_buffer)
      if distance_cm < 17:
        blocking = True
        #print "ping sensor stop!"
        self._doBumpStop()
        time.sleep(0.3)
        self._doGoForward()
        blocking = False
     
  def cleanup(self):
    self._doStop()
