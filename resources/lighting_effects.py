import time, random
from resources.mode_plugin_abstract import ModePluginAbstract
from neopixel import Color

class LightingEffects(ModePluginAbstract):

  global distance_buffer
  global current_pattern
  global current_color
  global bumper_color

  def __init__(self, parent):
    global distance_buffer
    global current_pattern
    global current_color
    global bumper_color
    distance_buffer = []
    current_pattern = 0
    current_color = 0
    bumper_color = 0
    self.parent = parent
    self.signalon = 0
    self.signaloff = 0
    self.buffer_size = 1
    self.max_distance = 50.0
    self.patterns = self.__getPatterns()
    self.colors = self.__getColors()

  def __getPatterns(self):
    pix_map = [
      # up left eye, down right eye:
      [
        [9],
        [7],
        [12],
        [3],
        [0],
        [6]
      ],
      # left -> right (both eyes):
      [
        [9,10],   #left
        [11,7,8],
        [12,13],
        [2,3],
        [4,0,1],
        [5,6]     #right
      ],
      # left -> right (eyes separate):
      [
        [2,3],	#left
        [4,0,1],
        [5,6]	#right
      ],
      # circle:
      [
        [0,1],
        [0,2],
        [0,3],
        [0,4],
        [0,5],
        [0,6]
      ],
      # snake:
      [
        [3],
        [2],
        [1],
        [0],
        [4],
        [5],
        [6]
      ],
      # compress top and bottom
      [
        [4,1],
        [3,5,2,6],
        [0]
      ],
      # bottom -> top:
      [
        [1],	#bottom
        [6,2],
        [0],
        [3,5],
        [4]	#top
      ]
    ]
    return pix_map

  def __getColors(self):
    return [
      [255.0,   0.0,   0.0],
      [255.0, 128.0,   0.0],
      [255.0, 255.0,   0.0],
      [128.0, 255.0,   0.0],
      [  0.0, 255.0,   0.0],
      [  0.0, 255.0, 128.0],
      [  0.0, 255.0, 255.0],
      [  0.0, 128.0, 255.0],
      [  0.0,   0.0, 255.0],
      [128.0,   0.0, 255.0],
      [255.0,   0.0, 255.0],
      [255.0,   0.0, 128.0]
    ]

  # select next background color
  def bumperPressed(self):
    global bumper_color
    tmp_color = bumper_color
    tmp_color += 2
    if tmp_color >= len(self.colors):
      tmp_color = 0
    bumper_color = tmp_color

  # select random color
  def rightHandPressed(self):
    global current_color
    current_color = random.randint(0,len(self.colors)-1)

  # select next pattern:
  def leftHandPressed(self):
    global current_pattern
    tmp_pattern = current_pattern
    tmp_pattern += 1
    if tmp_pattern >= len(self.patterns):
      tmp_pattern = 0
    current_pattern = tmp_pattern

  def echoCallback(self, pin, value):
    global distance_buffer
    if value == 1:
      self.signalon = time.time()
      return
    self.signaloff = time.time()
    timepassed = self.signaloff - self.signalon
    distance = timepassed * 17000
    if distance > 0 and distance < 3000:
      if distance > self.max_distance:
        distance = self.max_distance
      elif distance < 7:
        distance = 0
      distance_buffer.insert(0,distance)
    if len(distance_buffer) > self.buffer_size:
      distance_buffer.pop()

  def __makeColorMap(self,len):
    global current_color
    (r,g,b) = self.colors[current_color]
    col_map = [Color(255,255,255)]
    for x in range(0,len):
      col_map.append(Color(int(r),int(g),int(b)))
      r = r * .6
      g = g * .6
      b = b * .6
    return col_map

  def __wipe(self, use_distance = False):
    global distance_buffer
    global bumper_color
    r = 0
    g = 0
    b = 0
    if use_distance:
      if distance_buffer != []:
        distance_cm = sum(distance_buffer) / len(distance_buffer)
        val = 255.0 / self.max_distance
        (r, g, b) = self.colors[bumper_color]
        r = r - (distance_cm * val)
        g = g - (distance_cm * val)
        b = b - (distance_cm * val)
        if r < 0:
          r = 0
        if g < 0:
          g = 0
        if b < 0:
          b = 0
    for x in range(0,14):
      self.parent.strip.setPixelColor(x, Color(int(r),int(g),int(b)))

  def __showPattern(self,pattern):
    tail_len = 5
    pix_map = self.patterns[pattern]
    for x in range(0,len(pix_map)+(tail_len-1)):
      self.__wipe(use_distance=True)
      col_map = self.__makeColorMap(tail_len)
      for i in range(0, tail_len):
        pos = x-i
        if pos < 0 or pos > len(pix_map)-1:
          continue
        for y in range(0,len(pix_map[pos])):
          self.parent.strip.setPixelColor(pix_map[pos][y], col_map[i])
          if pattern > 1:
            self.parent.strip.setPixelColor(pix_map[pos][y]+7, col_map[i])
      self.parent.strip.show()
      time.sleep(0.06)
    for x in range(len(pix_map)-1,-(tail_len),-1):
      self.__wipe(use_distance=True)
      col_map = self.__makeColorMap(tail_len)
      for i in range(tail_len-1,-1,-1):
        pos = x+i
        if pos < 0 or pos > len(pix_map)-1:
          continue
        for y in range(0,len(pix_map[pos])):
          self.parent.strip.setPixelColor(pix_map[pos][y], col_map[i])
          if pattern > 1:
            self.parent.strip.setPixelColor(pix_map[pos][y]+7, col_map[i])
      self.parent.strip.show()
      time.sleep(0.02)

     
  def motorControl(self, left, right):
    pass

  def loopHook(self):
    global current_pattern
    self.__showPattern(current_pattern)

  def cleanup(self):
    self.__wipe()
    self.parent.strip.show()

