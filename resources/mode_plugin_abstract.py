from abc import ABCMeta, abstractmethod

class ModePluginAbstract(object):
  __metaclass__ = ABCMeta

  @abstractmethod
  def __init__(self, parent):
    pass

  @abstractmethod
  def leftHandPressed(self):
    pass

  @abstractmethod
  def rightHandPressed(self):
    pass

  @abstractmethod
  def bumperPressed(self):
    pass

  @abstractmethod
  def motorControl(self, left, right):
    pass

  @abstractmethod
  def echoCallback(self, pin, value):
    pass

  @abstractmethod
  def loopHook(self):
    pass

  @abstractmethod
  def cleanup(self):
    pass
