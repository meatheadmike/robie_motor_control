#!/usr/bin/python

import socket, struct, time
import RPi.GPIO as GPIO
from neopixel import *
from resources.remote_control import RemoteControl
from resources.bump_and_go import BumpAndGo
from resources.lighting_effects import LightingEffects

class RobieRover(object):

  def __init__(self):

    # configure LED's:
    self.LED_COUNT 		= 14 	  # 2 x 7 NeoPixel Jewels
    self.LED_PIN		= 18	  # Hardware PCM pin (Pin 12, GPIO18) 
    self.LED_FREQ_HZ		= 800000  # LED frequency (800Khz)
    self.LED_DMA		= 5	  # DMA channel
    self.LED_BRIGHTNESS		= 15	  # Can go up to 255, but it's good to keep power usage low
    self.LED_INVERT		= False	  # I believe this is for ws2811's
    
    # configure UDP server:
    self.UDP_IP 		= "0.0.0.0"
    self.UDP_PORT 		= 5005
    self.BUFFER_SIZE 		= 512

    # set up our GPIO:
    self.Motor1A 		= 16
    self.Motor1B 		= 18
    self.Motor2A 		= 23
    self.Motor2B 		= 21
    self.TopButton 		= 29
    self.LeftHand 		= 31
    self.RightHand 		= 33
    self.Bumper 		= 35
    self.HZ			= 50
    self.DEBOUNCE_TIME		= 300   # Debounce threshold in ms
    self.PING_TRIGGER		= 11	# Ping sensor trigger pin 
    self.PING_ECHO		= 7	# Ping sensor echo pin
    self.PING_BUFFER_SIZE 	= 15	# How many distance measurements to average against

    # set up some instance variables:
    self.left_fwd 		= None
    self.left_rev 		= None
    self.right_fwd 		= None
    self.right_rev 		= None
    self.strip 			= None
    self.lockthread		= False

    # do GPIO configuration:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(self.PING_TRIGGER,GPIO.OUT)
    GPIO.setup(self.PING_ECHO,GPIO.IN)
    GPIO.output(self.PING_TRIGGER, False)
    GPIO.setup(self.Motor1A,GPIO.OUT)
    GPIO.setup(self.Motor1B,GPIO.OUT)
    GPIO.setup(self.Motor2A,GPIO.OUT)
    GPIO.setup(self.Motor2B,GPIO.OUT)
    GPIO.setup(self.TopButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(self.LeftHand, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.RightHand, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.Bumper, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    self.left_fwd = GPIO.PWM(self.Motor1B, self.HZ)
    self.left_rev = GPIO.PWM(self.Motor1A, self.HZ)
    self.right_fwd = GPIO.PWM(self.Motor2A, self.HZ)
    self.right_rev = GPIO.PWM(self.Motor2B, self.HZ)

    self.currentMode = 0
    self.modeClass = None

  """ modes:
      0 = remote control
      1 = bump-n-go
      2 = lighting effects
  """
  def doModeSwitch(self, pin, mode = None):
    if self.lockthread == True:
      return
    self.lockthread = True
    if mode == None:
      mode = self.currentMode + 1
    if mode > 2:
      mode = 0
    if mode != self.currentMode:
      self.modeClass.cleanup()
      self.currentMode = mode
    print "Selected mode: %s" % mode
    self.blankLEDs()
    if mode == 1:
      self._showPixels([2,0,5,9,7,12],Color(255,102,0))
      self.modeClass = BumpAndGo(self.strip, self.left_fwd, self.left_rev, self.right_fwd, self.right_rev)
    elif mode == 2:
      self._showPixels([3,0,6,10,7,13],Color(255,255,0))
      self.modeClass = LightingEffects(self.strip, self.left_fwd, self.left_rev, self.right_fwd, self.right_rev)
    else: # assume mode 0
      self._showPixels([1,0,4,8,7,11],Color(255,0,0))
      self.modeClass = RemoteControl(self.strip, self.left_fwd, self.left_rev, self.right_fwd, self.right_rev) 
    self.lockthread = False

  def _showPixels(self, pixels, color):
    for p in pixels:
      self.strip.setPixelColor(p,color)
    self.strip.show() 
    
  def bumperPressed(self, pin):
    if self.lockthread == True:
      return
    self.lockthread = True
    print "Bumper pressed"
    try:
      self.modeClass.bumperPressed()
    except Exception, e:
      print "Bumper exception: %s" % e
    self.lockthread = False

  def leftHandPressed(self, pin):
    if self.lockthread == True:
      return
    self.lockthread = True
    print "Left hand pressed"
    try:
      self.modeClass.leftHandPressed()
    except Exception, e:
      print "Left hand exception: %s" % e
    self.lockthread = False

  def rightHandPressed(self, pin):
    if self.lockthread == True:
      return
    self.lockthread = True
    print "Right hand pressed"
    try:
      self.modeClass.rightHandPressed()
    except Exception, e:
      print "Right hand exception: %s" % e
    self.lockthread = False

  def echoCallback(self, pin):
    if self.lockthread == True:
      return
    self.lockthread = True
    try:
      self.modeClass.echoCallback(pin, GPIO.input(pin))
    except Exception, e:
      print "Echo exception: %s" % e
    self.lockthread = False

  def motorControl(self, left, right):
    try:
      self.modeClass.motorControl(left, right)
    except Exception, e:
      print "Motor exception: %s" % e

  def doMainLoop(self):
    self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN,
      self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS)
    self.strip.begin()
    self.modeClass = RemoteControl(self.strip, self.left_fwd, self.left_rev, self.right_fwd, self.right_rev)
    GPIO.add_event_detect(self.PING_ECHO, GPIO.BOTH, callback=self.echoCallback)
    GPIO.add_event_detect(self.TopButton, GPIO.FALLING,
      callback=self.doModeSwitch, bouncetime=self.DEBOUNCE_TIME)
    GPIO.add_event_detect(self.Bumper, GPIO.FALLING,
      callback=self.bumperPressed, bouncetime=self.DEBOUNCE_TIME)
    GPIO.add_event_detect(self.LeftHand, GPIO.FALLING,
      callback=self.leftHandPressed, bouncetime=self.DEBOUNCE_TIME)
    GPIO.add_event_detect(self.RightHand, GPIO.FALLING,
      callback=self.rightHandPressed, bouncetime=self.DEBOUNCE_TIME)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.bind((self.UDP_IP, self.UDP_PORT))

    print "Rover initialized. Ctl-c to exit/stop.\n"

    while True:
      # fire off a ping:
      GPIO.output(self.PING_TRIGGER, True)
      time.sleep(0.00001)
      GPIO.output(self.PING_TRIGGER, False)
      time.sleep(0.05) # allow callbacks to process
      
      try: 
        # acquire UDP data:
        data, addr = sock.recvfrom(self.BUFFER_SIZE)
        check_byte = struct.unpack("b", data[0])[0]
        if check_byte == 1:
          left_wheel = struct.unpack("b", data[1])[0]
          right_wheel = struct.unpack("b", data[2])[0]
          self.motorControl(left_wheel,right_wheel)
      except Exception,e:
        #print "Main loop exception: %s" % e
        pass


  # Make the LEDs go dark:
  def blankLEDs(self):
    self._showPixels(range(self.LED_COUNT),Color(0,0,0))

  def cleanup(self):
    self.modeClass.cleanup()
    GPIO.cleanup()
    self.blankLEDs()
    print "\nRover stopped."
      
if __name__ == '__main__':
  try:
    rr = RobieRover()
    rr.doMainLoop()
  except Exception, e:
    print "Exception: %s" % e
  finally:
    rr.cleanup()
