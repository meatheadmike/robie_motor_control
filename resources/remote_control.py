import time
from resources.mode_plugin_abstract import ModePluginAbstract
from neopixel import Color

class RemoteControl(ModePluginAbstract):
  def __init__(self, led_strip, left_fwd, left_rev, right_fwd, right_rev):
    self.strip = led_strip
    self.left_fwd = left_fwd
    self.left_rev = left_rev
    self.right_fwd = right_fwd
    self.right_rev = right_rev
    self.bump_stop_left = False
    self.bump_stop_right = False
    self.led_count = led_strip.numPixels()
    self.signalon = 0
    self.signaloff = 0
    self.distance_buffer = []
    self.buffer_size = 5

  def _go_left_fwd(self, duty):
    self.left_rev.stop()
    if self.bump_stop_left:
      self.left_fwd.stop()
      return
    self.left_fwd.start(duty)
    for x in range(self.led_count/2, self.led_count):
      self.strip.setPixelColor(x,Color(0,255,0)) #green
    self.strip.show() 

  def _go_left_rev(self, duty):
    self.bump_stop_left = False
    self.left_fwd.stop()
    self.left_rev.start(duty)
    for x in range(self.led_count/2, self.led_count):
      self.strip.setPixelColor(x,Color(255,0,0)) #red
    self.strip.show() 

  def _go_left_stop(self):
    self.left_rev.stop()
    self.left_fwd.stop()
    for x in range(self.led_count/2, self.led_count):
      self.strip.setPixelColor(x,Color(0,0,255)) #blue
    self.strip.show()

  def _go_right_fwd(self, duty):
    self.right_rev.stop()
    if self.bump_stop_right:
      self.right_fwd.stop()
      return
    self.right_fwd.start(duty)
    for x in range(self.led_count/2):
      self.strip.setPixelColor(x,Color(0,255,0)) #green
    self.strip.show() 

  def _go_right_rev(self, duty):
    self.bump_stop_right = False
    self.right_fwd.stop()
    self.right_rev.start(duty)
    for x in range(self.led_count/2):
      self.strip.setPixelColor(x,Color(255,0,0)) #red
    self.strip.show() 

  def _go_right_stop(self):
    self.right_rev.stop()
    self.right_fwd.stop()
    for x in range(self.led_count/2):
      self.strip.setPixelColor(x,Color(0,0,255)) #blue
    self.strip.show()


  def bumperPressed(self):
    self.bump_stop_left = True
    self.bump_stop_right = True
    for x in range(self.led_count):
      self.strip.setPixelColor(x,Color(255,0,255)) #purple
    self.strip.show()

  def leftHandPressed(self):
    pass

  def rightHandPressed(self):
    pass

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
    if self.distance_buffer != []:
      distance_cm = sum(self.distance_buffer) / len(self.distance_buffer)
      if distance_cm < 13:
        #print "ping sensor stop!"
        self.bumperPressed() 

  def motorControl(self, left, right):
    #print "left wheel:%s right wheel:%s" % (left, right)
    if left < 0:
      self._go_left_rev(0 - left)
    elif left > 0:
      self._go_left_fwd(left)
    else:
      self._go_left_stop()
    if right < 0:
      self._go_right_rev(0 - right)
    elif right > 0:
      self._go_right_fwd(right)
    else:
      self._go_right_stop()

  def cleanup(self):
    self.right_rev.stop()
    self.right_fwd.stop()
    self.left_fwd.stop()
    self.left_rev.stop()
