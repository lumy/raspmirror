import time
import RPi.GPIO as GP
import pygame
import vlc
from playlist import playlist
from pygame.locals import *
import sys, pygame

BUTTON1=40
BUTTON2=38
BUTTON3=36
PIR=0
WHITE = (255, 255, 255)
PINK = (255, 192, 203)

def init_setup(i, mode=GP.IN, pull_up=None):
  GP.setup(i, mode, pull_up_down=pull_up)

def init_main():
  try:
    GP.setmode(GP.BOARD)
    init_setup(BUTTON1, pull_up=GP.PUD_UP)
    init_setup(BUTTON2, pull_up=GP.PUD_UP)
    init_setup(BUTTON3, pull_up=GP.PUD_UP)
  except KeyboardInterrupt:
    return -1
  return 0

def init_pygame():
  pygame.init()
  pygame.font.init()
  font = pygame.font.get_default_font()
  normal_font = pygame.font.SysFont(font, 30)
  titleFont = pygame.font.Font('freesansbold.ttf', 80)
  x = pygame.display.Info()
  size = x.current_w, x.current_h
  screen = pygame.display.set_mode(size)
  Instance = vlc.Instance()
  player = Instance.media_player_new()
  return screen, normal_font, Instance, player, titleFont, size
  
def get_render(normal_font, radios, index, in_reading=-1):
  ret = []
  for i in range(0, len(radios)):
    if in_reading == index and index == i:
      normal_font.set_underline(True)
      name = normal_font.render(radios[i][0], False, PINK) 
      normal_font.set_underline(False)
      ret.append(name)
      
    elif in_reading == i:
      # USE PINK COLOR
      name = normal_font.render(radios[i][0], False, PINK) 
      ret.append(name)
    elif index == i:
      # Surlignage
      normal_font.set_underline(True)
      name = normal_font.render(radios[i][0], False, WHITE)
      normal_font.set_underline(False)
      ret.append(name)
    else:
      # Normal Color
      ret.append( normal_font.render(radios[i][0], False, WHITE) ) 
  return ret

PRESSED=True
UNPRESSED=False
LONGPRESS=1
SHORTPRESS=2
NOTPRESSED=0
state_button = {
}
def pressed(button):
  if button not in state_button:
    #                      # Last State # Timestamp # Current State
    state_button[button] = (UNPRESSED, time.time())
  i = GP.input(button)
  if state_button[button][0] == UNPRESSED and not i: # Was unpressed and is pressed
    state_button[button] = (PRESSED, time.time())
  elif state_button[button][0] == PRESSED and i: # was pressed and is unpressed
    r = round(time.time() - state_button[button][1], 2)
    state_button[button] = (UNPRESSED, None)
    print r
    return LONGPRESS if r >= 0.3 else SHORTPRESS
  return NOTPRESSED
   
PLAYING = False

def displayGui(screen, renders, titleFont, backgroundImage, size):
  screen.fill((0, 0, 0))
#  screen.blit(backgroundImage, (0, 0))
  TextSurf = titleFont.render("DopeRadio", True, (255,0,0))
  TextRect = TextSurf.get_rect()
  TextRect.center = ((size[0] / 2), (0))
  screen.blit(TextSurf, ((size[0] / 2), (0)))
  x = 150
  for elem in renders:
      screen.blit(elem, (30, x))
      x += 80
  pygame.display.flip()


def loop(screen, normal_font, instance, player, titleFont, size):


  LIST_RADIO = playlist
  volume = 100
  index = 0
  index_reading = -1
  try:
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
      stateb = pressed(BUTTON1)
      if stateb != UNPRESSED:
        index_reading = play_pause(LIST_RADIO, (instance, player), (index, index_reading))
       
      stateb = pressed(BUTTON2)
      if stateb == LONGPRESS:
        volume = volume_up(player, volume)
      elif stateb == SHORTPRESS:
	index = next_radio(LIST_RADIO, index)

      stateb = pressed(BUTTON3)
      if stateb == LONGPRESS:
        volume = volume_down(player, volume)
      elif stateb == SHORTPRESS:
        index = prev_radio(LIST_RADIO, index)

      renders = get_render(normal_font, LIST_RADIO, index, in_reading=index_reading)

      displayGui(screen, renders, titleFont, False, size)
      # Display Update
#      screen.fill((0, 0, 0))
#      x = 10
#      for elem in renders:
#        screen.blit(elem, (10, x))
#        x += 20
#      pygame.display.flip()
  except KeyboardInterrupt:
    GP.cleanup()


def volume_up(player, volume):
  volume += 5
  if volume > 100:
    volume = 100
  player.audio_set_volume(volume)
  return volume

def volume_down(player, volume):
  volume -= 5
  if volume < 0:
    volume = 0
  player.audio_set_volume(volume)
  return volume

def play_pause(list_radio, iplayer, indexs):
  global PLAYING
  index, index_reading = indexs
  instance, player = iplayer
  if PLAYING:
    player.stop()
    PLAYING = False
    index_reading = -1
  else:
     media = instance.media_new(unicode(list_radio[index][1]))
     player.set_media(media)
     player.play()
     index_reading = index
     PLAYING = True
  return index_reading

def next_radio(list_radio, index):
  index += 1
  if index >= len(list_radio):
    index = 0
  return index

def prev_radio(list_radio, index):
  index -= 1
  if index < 0:
    index = len(list_radio) - 1
  return index




if __name__ == '__main__':
  if -1 == init_main():
    print "Error during Init"
  loop(*init_pygame())

