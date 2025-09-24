import pygame, sys, math

wWindow, hWindow = 960, 540
white, black, gray, red = (255, 255, 255), (0, 0, 0), (120, 120, 120), (250, 50, 50)

win = pygame.display.set_mode((wWindow, hWindow))
pygame.display.set_caption('Projectile Motion')
# pygame.display.set_icon(pass)

class ball(object):
    def __init__(self, x, y, radius, color):
        self.x = x 
        self.y = y
        self.radius = radius
        self.color = color
        

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)


    @staticmethod
    def trajectory(xinitial, yinitial, vinitial, angle, time):
        angle = launchAngle
        xvel = math.cos(angle) * vinitial
        yvel = math.sin(angle) * vinitial

        xdist = xvel * time
        ydist = (yvel * time) + ((-4.9 * (time)**2)/2)

        newx = round(xdist + xinitial)
        newy = round(yinitial - ydist)

        return(newx, newy)

FLOOR = hWindow - 200
redBall = ball(200, FLOOR - 10, 10, red)

def findAngle(pos):
    #find angle 
    xorigin = redBall.x
    yorigin = redBall.y

    mousex = pos[0]
    mousey = pos[1]

    # find angle of line
    try:
        launchAngle = math.atan((yorigin - mousey) / (xorigin - mousex))
    except:
        launchAngle = math.pi / 2

    if mousey < yorigin & mousex > xorigin:
        launchAngle = abs(launchAngle)
    elif mousey < yorigin & mousex < xorigin:
        launchAngle = math.pi - launchAngle
    elif mousey > yorigin & mousex < xorigin:
        launchAngle = math.pi + abs(launchAngle)
    elif mousey > yorigin & mousex > xorigin:
        launchAngle = (math.pi * 2) - launchAngle
    return launchAngle

linevis = False
def drawWindow():
    win.fill(white)
    pygame.draw.line(win, black, (0, FLOOR), (wWindow, FLOOR), 1)
    if linevis:
        pygame.draw.line(win, gray, line[0], line[1])
    redBall.draw(win)

    pygame.display.update()

# main loop
pygame.init()

framerate = 60
running = True
time = 0
vinitial = 0
launchAngle = 0
held = False
offset = 0
launch = False
clock = pygame.time.Clock()

while running:
    clock.tick(framerate)
    drawWindow()

    for event in pygame.event.get():

        # quit
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
        # launch line
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                mousex, mousey = pos[0], pos[1]
                sqDeltaX = (mousex - redBall.x)**2
                sqDeltaY = (mousey - redBall.y)**2
                on_ball = math.sqrt(sqDeltaX + sqDeltaY) < redBall.radius
                if on_ball:
                    print('Ball clicked')
                    held = True
        if (event.type == pygame.MOUSEMOTION) & held:
            linevis = True
            pos = pygame.mouse.get_pos()
            line = [(redBall.x, redBall.y), (pos[0], pos[1])]
            if redBall.y + redBall.radius < pos[1]:
                if pos[0] < redBall.x:
                    line[1] = ((2 * redBall.x - pos[0]), (redBall.y - (pos[1] - redBall.y)))
                if pos[0] > redBall.x:
                    line[1] = ((redBall.x - (pos[0] - redBall.x)), (redBall.y - (pos[1] - redBall.y)))
            offset = math.sqrt((pos[0] - redBall.x)**2 + (pos[1] - redBall.y)**2)
        if (event.type == pygame.MOUSEBUTTONUP) & held & (offset != 0):
            if event.button == 1:
                held = False
                linevis = False
                if not launch:
                    launch = True
                    x = redBall.x
                    y = redBall.y
                    vinitial = math.sqrt((line[1][1]-line[0][1])**2 +(line[1][0]-line[0][1])**2)/4
                    offset = 0

                    pos = pygame.mouse.get_pos()
                    launchAngle = findAngle(pos)
        elif (event.type == pygame.MOUSEBUTTONUP):
            if event.button == 1:
                held = False
                launch = False
                offset = 0

    if launch:
        time += 0.05
        shot = ball.trajectory(x, y, vinitial, launchAngle, time)
        redBall.x = shot[0]
        redBall.y = shot[1]
        if redBall.y < FLOOR - redBall.radius + 1:
            time += 0.05
            shot = ball.trajectory(x, y, vinitial, launchAngle, time)
            redBall.x = shot[0]
            redBall.y = shot[1]
        else:
            launch = False
            time = 0
            offset = 0
            redBall.y = FLOOR - redBall.radius
            print('excepted')

                
            

            

pygame.quit()