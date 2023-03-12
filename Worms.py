''' Worms '''
#Copyright (c) 2023 Darwin Geiselbrecht
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import pygame, sys, time, random, math
from pygame.locals import *

pygame.init()

WINDOWWIDTH = 2100
WINDOWHEIGHT =1100
SCOREHEIGHT = 30     # HEIGHT OF THE SCORE TEXT AREA

BLACK = (0,0,0)
WHITE =  (255,255,255)
YELLOW = (255,255,0)
LIGHTYELLOW = (128,128,0)
RED = (255, 0 ,0)
LIGHTRED = (128,0,0)
BLUE = (0, 0, 255)
SKYBLUE = (135,206,250)
GREEN = (0,255,0)
LIGHTGREEN = (152,251,152)
AQUAMARINE = (123,255,212)
LIGHTBROWN = (210,180,140)
LIGHTGREY = (211,211,211)
DIMGREY = (105,105,105)
VIOLET = (238,130,238)
SALMON = (250,128,114)
GOLD = (255,165,0)
BACKGROUND = LIGHTGREY
ORANGE = (255,140,0)


windowSurface = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT])
pygame.display.set_caption('Worms')



#------------------------------------------------------------------
# Define the widget classes
#------------------------------------------------------------------

class Widget(object):
# Widget class for all widgets,  its  function is mainly to hold the
# dictionary of all widget objects by name as well as the application
# specific handler function. And support isclicked to
# see if cursor is clicked over widget.

    widgetlist = {} # dictionary of tubles of (button_object,app_handler)
    background_color = LIGHTGREY

    def __init__(self):
    # set up default dimensions in case they are not defined in
    # inherited class, this causes isclicked to default to False
        self.left = -1
        self.width = -1
        self.top = -1
        self.height = -1

    def find_widget(widget_name):
    # find the object handle for a widget by name        
        if widget_name in Widget.widgetlist:
            widget_object = Widget.widgetlist[widget_name][0]
            return  widget_object
        else:
            Print ('Error in find_widget, Widget not found ' + widget_name)
            return

    def isclicked (self, curpos):
    # button was clicked, is this the one? curpos is position tuple (x,y)
        

        covered = False

        if (curpos[0] >= self.left and
        curpos[0] <= self.left+self.width and
        curpos[1] >= self.top and
        curpos[1] <= self.top + self.height):
            covered = True

        return covered
    

    def handler(self):
    # prototype for a widget handler to be overridden if desired
        pass #do nothing    
            


class Text(Widget):

    def __init__(self,window=windowSurface,
                 color=BLACK,background_color=Widget.background_color,
                 topleft=(200,200),name= '',
                 font_size=20,max_chars=40,text='',
                 outline=True,outline_width=1,
                 justify = 'LEFT',
                 app_handler=Widget.handler):

        
        # initialize the properties
        self.window=window
        self.color= color
        self.background_color = background_color
        self.name = name
        self.font_size = font_size
        self.max_chars = max_chars
        self.text = text
        self.outline = outline
        self.outline_width = outline_width
        self.justify = justify
        self.app_handler = app_handler
        
        self.topleft=topleft
        self.left=topleft[0]    # reguired by isclicked method in Widget
        self.top=topleft[1]     # "
        
        # render a maximum size string to set size of text rectangle
        max_string = ''
        for i in range(0,max_chars):
            max_string += 'D'

        maxFont = pygame.font.SysFont(None,font_size)
        maxtext = maxFont.render(max_string,True,color)
        maxRect= maxtext.get_rect()
        maxRect.left = self.left
        maxRect.top = self.top
        self.maxRect = maxRect  # save for other references
        self.maxFont = maxFont

        # now set the rest required by isclicked method
        self.width = maxRect.right - maxRect.left
        self.height = maxRect.bottom -  maxRect.top


        # Add widget object keyed by name to widget dictionary.
        # Non-null Widget names must be unique.
        
        if ( (name != '') and (name not in Widget.widgetlist) ):
            Widget.widgetlist[name] = (self,app_handler)
        elif (name != ''):
            print ('Error - duplicate widget name of ' + name)

        self.draw()  # invoke the method to do the draw

        return   # end of Text initializer

    # Text method to draw the text and any outline on to the screen
    def draw(self):
        # fill the maxRect to background color to wipe any prev text
        pygame.draw.rect(self.window,self.background_color,
                         (self.maxRect.left,self.maxRect.top,
                          self.width, self.height),0)

        # if outline is requested, draw the outline 4 pixels bigger than
        # max text.  Reference topleft stays as specified
        
        if self.outline:
            pygame.draw.rect(self.window,self.color,
                             (self.maxRect.left-self.outline_width-2,
                              self.maxRect.top-self.outline_width-2,
                              self.width+(2*self.outline_width)+2,
                              self.height+(2*self.outline_width)+2),
                              self.outline_width)


        # Now put the requested text within maximum rectangle
        plottext = self.maxFont.render(self.text,True,self.color)
        plotRect = plottext.get_rect()

        plotRect.top = self.top # top doesn't move with justify

        # justify the text
        if self.justify == 'CENTER':
            plotRect.left = self.left + int(plotRect.width/2) 
        elif self.justify == 'LEFT':
            plotRect.left = self.left
        elif self.justify == 'RIGHT':
            plotRect.right = self.maxRect.right
        else:
            print('Illegal justification in Text object')

        # blit the text and update screen
        self.window.blit(plottext,plotRect)

        pygame.display.update()

    # Text method to update text and redraw
    def update(self,text):
        self.text = text
        self.draw()

class Rectangle(Widget):
# class to wrap the pygame rectangle class to standardize with Widgets 

    def __init__(self, window=windowSurface,color=BLACK,
                 topleft = (200,200), width = 30, height = 20,
                 name = '',outline_width = 1, # width of outline, 0 = fill
                 app_handler=Widget.handler):

        self.window = window
        self.color = color
        self.topleft = topleft
        self.left = topleft[0]      # required by isclicked method in Widget
        self.top = topleft[1]       # "
        self.width = width          # "
        self.height = height        # "
        self.right = self.left + width
        self.bottom = self.top + height
        self.name = name
        self.outline_width = outline_width
        self.app_handler = app_handler

        # Add widget object keyed by name to widget dictionary.
        # Non-null Widget names must be unique.
        
        if ( (name != '') and (name not in Widget.widgetlist) ):
            Widget.widgetlist[name] = (self,app_handler)
        elif (name != ''):
            print ('Error - duplicate widget name of ' + name)

        self.draw()  # invoke the draw method to draw it

        return

    def draw(self):     # Rectangle method to do the draw
        
        # get a rectangle object and draw it
        self.rect = pygame.Rect(self.left,self.top,self.width,self.height)
        pygame.draw.rect(self.window,self.color,self.rect,
                         self.outline_width)
        pygame.display.update(self.rect)

        return
    
    def handler(self):  # Rectangle handler
        self.app_handler(self)  # nothing special to do, call app_handler
        return




        
 
#------------------ Application Classes ------------------------------------
#Worm class
class Worm(object):

  worms = []  # create an empty list of all worms

  def process():
  # Worm movement processor, called from the main loop at the class
  # level to move worms and check for other actions
    for worm_object in Worm.worms:
      
      if not (worm_object.handler == ''): # see if handler exists
        worm_object.handler(self) # call the handler
                    
  def __init__(self,name='',color=WHITE,location_x =200,location_y=200,size=2,
               track_length=50,IQ=20,handler='',score_loc=(200,5) ):
  # constructor for worm
    self.name = name
    self.color = color
    self.location_x = location_x
    self.location_y = location_y
    self.track = []                 # keeps the location tuples for the visible track
    self.track_length=track_length  # length of the visible track
    self.size = size
    self.IQ = IQ
    self.handler = handler
    Worm.worms += [self]   # add to list of all worms
    self.rect =   pygame.Rect(self.location_x-int(size/2),
                                self.location_y-int(size/2),size,size)      
    self.dx = 0
    self.dy = 0
    self.score_loc = score_loc

  def move(self):
  # This handles movement of the worm. Called with a worm object.
    
    food_rect=self.seek_food()     # look for nearest food, updates self.dx and self.dy

    if self.rect.colliderect(food_rect):
      self.eat_food(food_rect)
    
    if random.randint(1,200) < self.IQ:  # If smart enough, tend toward your goal
      self.location_x += random.randint(-3,+3)+self.dx
      self.location_y += random.randint(-3,+3)+self.dy
    else:
      self.location_x += random.randint(-3,+3)
      self.location_y += random.randint(-3,+3)
      
    self.check_wall()
    self.rect.center = (self.location_x,self.location_y)
    #pygame.draw.rect(windowSurface,self.color,self.rect,0)
    pygame.draw.rect(windowSurface,self.color,self.rect,0)
    self.manage_track()           # shorten the worm length to max specified
    
  def seek_food(self):
  # look for the nearest food, updates self.dx,self.dy and returns the food rectangle of
  # the nearest food

    if len(Food.food)== 0:
      Food.stock_food(self)     # self is wrong type object, but not used in method
    
    shortest_distance = 10000
    for food in Food.food:
      distance = math.sqrt( (food.center[0] - self.location_x)**2 +(food.center[1] - self.location_y)**2 ) 
      if distance < shortest_distance:
        food_target = food
        shortest_distance = distance
        
    # set the direction bias .dx and .dy based on direction to food
      food_x = food_target.center[0]
      food_y = food_target.center[1]
      if food_x > self.location_x:
        self.dx = +1
      elif food_x < self.location_x:
        self.dx = -1
      else:
        self.dx = 0

      if food_y > self.location_y:
        self.dy = +1
      elif food_y < self.location_y:
        self.dy = -1
      else:
        self.dy = 0

    return food_target

  def eat_food(self,food_rect):
  # This 'eats' a food rectangle detected by a collision with a worm.
  # Simply removes it from the list of available food and rewards the worm
    Food.food.remove(food_rect)   # will find a new one on the next round
    pygame.draw.rect(windowSurface,BLACK,food_rect,0)   # blank the food 
    self.IQ += 1          # food eaten, makes the worm smarter
    
    if(food_rect.size[0] > self.size):     # this is the identifier for poison
      self.IQ += random.randint(-10,-5)    # penalize for eating poison
      if self.IQ < 1:
        self.IQ = 1    # don't let him get too dumb
        
    blank_text=pygame.Rect(self.score_loc[0],self.score_loc[1],150,20)
    pygame.draw.rect(windowSurface,BLACK,blank_text,0)
    text= self.name+' IQ=  '+str(self.IQ)
    write_text(text,topleft=self.score_loc,font_size=20,color=self.color)
    if self.IQ >= 200:
      blank_text=pygame.Rect(self.score_loc[0],self.score_loc[1],150,20)
      pygame.draw.rect(windowSurface,BLACK,blank_text,0)
      text = self.name+' reaches Nirvana'
      write_text(text,topleft=self.score_loc,font_size=20,color=self.color)
      self.explode()
      Worm.worms.remove(self)

  def manage_track(self):
  #This handle the process of keeping up with the last movements to define the segments
  #segments of the worm and also blanking the oldest segment when the desired length is reached 
    self.track.insert(0, self.rect.center )
    if len(self.track) >= self.track_length:
      oldest=self.track.pop()
      blank_rect = pygame.Rect(oldest[0],oldest[1],self.size,self.size)
      blank_rect.center=(oldest[0],oldest[1])
      pygame.draw.rect(windowSurface,BLACK,blank_rect,0)

      
  def check_wall(self):
  # method to test if an  hit a wall.
  # Call with a worm object
    # restricts x and y location to the viewable screen
  # Returns None if no wall struck, otherwise 'TOP','BOTTOM','RIGHT','LEFT'
    if ( (self.location_x+5) >= WINDOWWIDTH):
      self.location_x = WINDOWWIDTH-5
      return 'RIGHT'
    elif ( (self.location_x) <= 5):
      self.location_x = 5
      return 'LEFT'
    elif ( (self.location_y ) <= SCOREHEIGHT):
      self.location_y = SCOREHEIGHT
      return 'TOP'
    elif (self.location_y+5 >= WINDOWHEIGHT):
      self.location_y = WINDOWHEIGHT-5
      return 'BOTTOM'
    else:
      return None

  def explode(self):
  # method to explode the worm when it reaches "Nirvana"

    for density in range(20):
      for radius in range(self.track_length):
        x_radius = random.randint(-self.track_length,self.track_length)
        y_radius = random.randint(-self.track_length,self.track_length)
        if math.sqrt( x_radius**2 +y_radius**2)  < self.track_length:
          explode_rect=pygame.Rect(self.location_x+x_radius,
                                   self.location_y+y_radius,
                                   2,2)
          pygame.draw.rect(windowSurface,self.color,explode_rect,0)
          pygame.display.update()
          time.sleep(.001)



# Food Class
class Food(object):
  food = []       # a list to keep all active food objects

  def __init__(self,size=4,color=WHITE):
    self.size = size
    self.color = color
    

  def stock_food(self,amount=10,size=4):
    for i in range(amount-1):   # Stock the food with tuples of (x,y) locations
      Food.food.append( pygame.Rect(random.randint(10,WINDOWWIDTH-10),
                                    random.randint(SCOREHEIGHT,WINDOWHEIGHT-10),
                                    self.size,self.size) )  # store food rectangle as food object
      pygame.draw.rect(windowSurface,self.color,Food.food[-1],0)

# Now store one 'poison pill' identified by its orange color and size > self.size    
    Food.food.append( pygame.Rect(random.randint(10,WINDOWWIDTH-10),
                                  random.randint(SCOREHEIGHT,WINDOWHEIGHT-10),
                                  self.size+4,self.size+4) )  # store food rectangle as food object
    pygame.draw.rect(windowSurface,ORANGE,Food.food[-1],0)
      
  def show_food(self,color=WHITE):
    for food_rect in Food.food:
      if food_rect.size[0] > self.size:   # this indicates poison
        pygame.draw.rect(windowSurface,ORANGE,food_rect,0)
      else:     # normal food
        pygame.draw.rect(windowSurface,self.color,food_rect,0)
      
#---------------- General purpose functions not part of a class ver 0.1 ---------

def write_text(text='TEXT TEST',topleft=(200,200),font_size=50,color=YELLOW):
# General purpose function to write text on the screen
    myfont = pygame.font.SysFont(0,font_size)#setting for the font size
    label = myfont.render(text, 1,color)#("text",alias flag, color
    textrec = label.get_rect()  # get a rectangle to put it in
    textrec.left = topleft[0]  # set the position
    textrec.top = topleft[1]

    windowSurface.blit(label,textrec)#put the text rec onto the surface
    pygame.display.update()

#----------------- Mainline setup and loop for the game -----------------------------
yellow = Worm(name ="Old Yeller",color=YELLOW,location_x=random.randint(1,WINDOWWIDTH-1),
              location_y=random.randint(1,WINDOWHEIGHT-1),size=4,
              IQ=50,handler=Worm.move,score_loc=(200,5) )
red = Worm(name ="Riding Hood",color=RED,location_x=random.randint(1,WINDOWWIDTH-1),
              location_y=random.randint(1,WINDOWHEIGHT-1),size=4,
              IQ=50,handler=Worm.move,score_loc=(400,5))
green = Worm(name ="Green Arrow",color=GREEN,location_x=random.randint(1,WINDOWWIDTH-1),
              location_y=random.randint(1,WINDOWHEIGHT-1),size=4,
              IQ=50,handler=Worm.move,score_loc=(600,5) )


food = Food()
food.stock_food(amount = 10,size=4)
clock = 0        # perpetual counter to time repeating events
while True:
  clock += 1
  if len(Worm.worms) > 0:
    for worm in Worm.worms:
      worm.move()
    if clock % 100 == 0:
      food.show_food()  # periodically reshow food in case walked over without eating
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
  else:
    print ('Game over')
    pygame.quit()
    sys.exit()
  time.sleep(.001)

#pygame.quit()
#sys.exit
