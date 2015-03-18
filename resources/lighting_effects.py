import time
from resources.mode_plugin_abstract import ModePluginAbstract
from neopixel import Color

class LightingEffects(ModePluginAbstract):
  def __init__(self, led_strip, left_fwd, left_rev, right_fwd, right_rev):
    pass

  def leftHandPressed(self):
    pass

  def rightHandPressed(self):
    pass

  def bumperPressed(self):
    pass

  def echoCallback(self, pin, value):
    pass

  def motorControl(self, left, right):
    pass

  def cleanup(self):
    pass

