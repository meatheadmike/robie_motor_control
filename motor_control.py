#!/usr/bin/python

import socket, struct
import RPi.GPIO as GPIO
from time import sleep
from neopixel import *

# configure LED's:

LED_COUNT 	= 14 	  # 2 x 7 NeoPixel Jewels
LED_PIN		= 18	  # Hardware PCM pin (Pin 12, GPIO18) 
LED_FREQ_HZ	= 800000  # LED frequency (800Khz)
LED_DMA		= 5	  # DMA channel
LED_BRIGHTNESS	= 15	  # Can go up to 255, but it's good to keep power usage low
LED_INVERT	= False	  # I believe this is for ws2811's
 
GPIO.setmode(GPIO.BOARD)

HZ = 100
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
BUFFER_SIZE = 512

# set up our GPIO pins
Motor1A = 16
Motor1B = 18
Motor2A = 23
Motor2B = 21

left_fwd = None
left_rev = None
right_fwd = None
right_rev = None
strip = None

def go_left_fwd(duty):
  left_rev.stop()
  left_fwd.start(duty)
  for x in range(LED_COUNT/2,LED_COUNT):
    strip.setPixelColor(x,Color(0,255,0)) #green
  strip.show() 

def go_left_rev(duty):
  left_fwd.stop()
  left_rev.start(duty)
  for x in range(LED_COUNT/2,LED_COUNT):
    strip.setPixelColor(x,Color(255,0,0)) #red
  strip.show() 

def go_left_stop():
  left_rev.stop()
  left_fwd.stop()
  for x in range(LED_COUNT/2,LED_COUNT):
    strip.setPixelColor(x,Color(0,0,255)) #blue
  strip.show()

def go_right_fwd(duty):
  right_rev.stop()
  right_fwd.start(duty)
  for x in range(LED_COUNT/2):
    strip.setPixelColor(x,Color(0,255,0)) #green
  strip.show() 

def go_right_rev(duty):
  right_fwd.stop()
  right_rev.start(duty)
  for x in range(LED_COUNT/2):
    strip.setPixelColor(x,Color(255,0,0)) #red
  strip.show() 

def go_right_stop():
  right_rev.stop()
  right_fwd.stop()
  for x in range(LED_COUNT/2):
    strip.setPixelColor(x,Color(0,0,255)) #blue
  strip.show()

if __name__ == '__main__':
  try: 

    GPIO.setup(Motor1A,GPIO.OUT)
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.setup(Motor2A,GPIO.OUT)
    GPIO.setup(Motor2B,GPIO.OUT)

    left_fwd = GPIO.PWM(Motor1B, HZ)
    left_rev = GPIO.PWM(Motor1A, HZ)
    right_fwd = GPIO.PWM(Motor2A, HZ)
    right_rev = GPIO.PWM(Motor2B, HZ)

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()

    sock = socket.socket(socket.AF_INET, # Internet
                 socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    print "Rover initialized. Ctl-c to exit/stop.\n"

    while True:
      data, addr = sock.recvfrom(512) # buffer size is 512 bytes
      # unpack our raw data:
      check_byte = struct.unpack("b", data[0])[0]
      if check_byte == 1:
        left_wheel = struct.unpack("b", data[1])[0]
        right_wheel = struct.unpack("b", data[2])[0]
        print "left wheel:%s right wheel:%s" % (left_wheel, right_wheel)
        if left_wheel < 0:
          go_left_rev(0 - left_wheel)
        elif left_wheel > 0:
          go_left_fwd(left_wheel)
        else:
          go_left_stop()
        if right_wheel < 0:
          go_right_rev(0 - right_wheel)
        elif right_wheel > 0:
          go_right_fwd(right_wheel)
        else:
          go_right_stop()
      sleep(0.02)
  except Exception, e:
    print "Exception: %s" % e
  finally:
    left_fwd.stop()
    right_fwd.stop()
    left_rev.stop()
    right_rev.stop()
    for x in range(LED_COUNT):
      strip.setPixelColor(x, Color(0,0,0))
      strip.show()
    GPIO.cleanup()
    print "\nRover stopped."
 
