import pygame
import random

# Swivelling idea
# Max: On each frame, rotate it a little around the point where it was some length of time ago.
# Swap directions after a certain length of time.
 
white = (255, 255, 255)
black = (0, 0, 0)
navy = (15, 20, 30)
 
pygame.init()
  
# Screen magic
width = 700
height = 500
size = [width, height]
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Tried to check if I kept the caption, did you? Ba. Haha. Bahaha. Outsmarted!")

# Variables
flakes_amount = 200
time_passed = 0 # converted to seconds
time_since = 0
num_changed = 0

# Flag for program
done = False
#wind_change = False
 
# Used to manage how fast the screen updates
clock=pygame.time.Clock()

# Listing off my lists
snow_list=[]
size_list=[]
color_list=[]

def createColour(loc):
    handle = random.randint(30, 255)
    color_list.append([handle, handle, handle])

for snowCount in range(flakes_amount):
    size = random.randint(2,4)
    size_list.append(size)
    x = random.randint(0, width)
    y = random.randint(0, height)
    snow_list.append([x,y])
    createColour(snowCount)
    
snow_half = int(len(snow_list)/2)

# Stuff of wizards; makes it snow
def letItSnow(firstSnow, lastSnow, x_wind, y_wind):
    for snows in range(firstSnow, lastSnow):
        pygame.draw.circle(screen, color_list[snows], snow_list[snows], size_list[snows])

        #TO DO: add an upper limit, loop up to it using flag
        global num_changed
        if time_since > (10000 + (10000 * num_changed)) :
            x_wind = 100
            #x_change = random.randint(-3,4)
            #y_change = random.randint(-4,5)
            #x_wind += x_change
            #y_wind += y_change
           # TO DO: if wind goes up to a certain value,
           # loop down to a smaller one

           
        # Drifting
        snow_list[snows][0] += x_wind
        snow_list[snows][1] += y_wind

        # If snow falls off screen, recycle!
        # Let it not be said that this game is not green.

        if snow_list[snows][1] > height+3:
            y=random.randrange(-50,-10)
            snow_list[snows][1] = y
            x=random.randrange(0,width-50)
            snow_list[snows][0] = x

        if snow_list[snows][0] > width+3:
            y=random.randrange(0,height-50)
            snow_list[snows][1] = y
            x=random.randrange(-50,-10)
            snow_list[snows][0] = x
 
# Main
while done==False:
    
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop 
 
    # Lessdraw
    screen.fill(navy)

    # Time
    time_passed = pygame.time.get_ticks()
    if (time_passed - time_since) >= 10000:
        time_since += 10000
        num_changed += 1

    print("Passed:",time_passed)
    print("Since:",time_since)
    print("Nums:",num_changed)

    # Snow ranges here
    letItSnow(0, snow_half, 1, 2)
    letItSnow(snow_half, len(snow_list), 4, 4)

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # Limit to 24 frames per second
    clock.tick(24)
     
# Anddd cut
pygame.quit ()
# That's a wrap
