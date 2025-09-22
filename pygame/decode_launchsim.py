# using cm as the base unit for everything here so sorry everything's a nightmare to parse

import pygame, sys, math

wWindow, hWindow = 960, 540
bg_color = (250, 240, 180) # this is yellow
gutter = 20
white, black, light_gray, medium_gray, dark_gray = (255, 255, 255), (0, 0, 0), (220, 220, 220), (200, 200, 200), (120, 120, 120)
red, purple, green = (200, 80, 80), (160, 40, 200), (80, 200, 100)
divider_color = (240, 150, 60)
blue, dark_blue = (150, 200, 200), (120, 160, 200)

FLOOR = 340
CM = 1.5
STEP = 10 * CM  # 10 pixels per 0.1 meter

# lengths (cm)
maxdist = 408.93 * CM           # field is 6x6 of 24" square tiles, the farthest  valid
                                # distance you can shoot from the goal is from the sma-
                                # ler launch zone that forms a 4 x 6 tile triangle with 
                                # the goal, so
                                # sqrt((4*24)^2 + (6*24)^2) * 2.54     (distance in cm)
robot_width = 45.72 * CM
artifact_radius = 6.35 * CM
goal_width = 46.45 * CM
goal_height = 98.45 * CM
goal_backboard = goal_height + 38.1*CM



g = -9.8 * 10          # acceleration due to gravity in cm/s

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
            # 
            # s is position
            #
            # vf^2 = vi^2 + 2a(sf-si)
            # sf = si + vi*t + (a*t)/2
            # vf = vi + a*t
            #
            # vix = vi*cos(theta)
            # viy = vi*sin(theta)
            #
            # xf = vi*cos(theta)*t                     vertical distance
            # yf = vi*sin(theta)*t + (a*t)/2           horizontal distance 
            #                                          
            # vfy = vi*sin(theta) + a*t                vfy at time t
            # current angle = arctan(vfy/vix)          
            #
        angle = launchAngle
        xvel = vinitial * math.cos(angle)
        yivel = vinitial * math.sin(angle)
        yfvel = vinitial*math.sin(launchAngle) + g*time
        speed = math.sqrt(yfvel**2+xvel**2)
        curang = math.atan(yfvel/xvel)
        
        if yfvel < 0:
            curvel = 'NEGATIVE'
        elif yfvel > 0:
            curvel = 'POSITIVE'
        else:
            curvel = 'ZERO'

        xdist = xvel * time
        ydist = (yivel * time) + ((g * (time)**2)/2)

        newx = round(xdist + xinitial)
        newy = round(yinitial - ydist)

        return(newx, newy, curang)

class rectangle(object):
    def __init__(self, x, y, length, width, color):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.length, self.width)

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.length, self.width))
        shooter.x, shooter.y = self.x + shooter.radius+4, self.y
    

# window setup
win = pygame.display.set_mode((wWindow, hWindow))
pygame.display.set_caption('DECODE Launch Simulator')
pygame.font.init()
pygame.font.get_init()
font1 = pygame.font.SysFont('dejavusansmono', 10)

artifact = ball(500, FLOOR - artifact_radius, artifact_radius, purple)
robot = rectangle(wWindow-gutter*2-maxdist+1, FLOOR - robot_width/3, robot_width, robot_width/3, blue)
shooter = ball(robot.x + artifact_radius+4, robot.y, artifact_radius + 2, dark_blue)

# update window
def drawWindow():
    win.fill(bg_color)
    # graph area
    pygame.draw.rect(win, white, pygame.Rect(wWindow - maxdist - gutter*3 -40, gutter, maxdist+gutter*2 +40, FLOOR+30), 0, 5)   # '+5's added in later to account for graph labels
                                                                                                                                # should have made a surface for the rect but I di
                                                                                                                                # -dn't think that far ahead
    pygame.draw.rect(win, divider_color, pygame.Rect(wWindow - maxdist - gutter*3 -40, gutter, maxdist+gutter*2 +40, FLOOR+30), 1, 5) 

    # graph itself
    # rows
    for i in range(round((FLOOR-gutter)/STEP)):
        if i % 5 == 0:
            pygame.draw.line(win, medium_gray, (wWindow - gutter*2 - maxdist, gutter*2 + i*STEP), (wWindow - gutter*2, gutter*2 + i*STEP), 1)
            if i == 0:
                ylabel = font1.render(f'{'0':>3}', True, black)
                ylabelRect = ylabel.get_rect()
                ylabelRect.center = (wWindow - gutter*2 - maxdist -15, FLOOR+8) # lowering zero label to origin
            else: 
                ylabel = font1.render(f'{i*10:>3}', True, black)
                ylabelRect = ylabel.get_rect()
                ylabelRect.center = (wWindow - gutter*2 - maxdist -15, FLOOR - i*STEP)
            win.blit(ylabel, ylabelRect)
        else:
            pygame.draw.line(win, light_gray, (wWindow - gutter*2 - maxdist, gutter*2 + i*STEP), (wWindow - gutter*2, gutter*2 + i*STEP), 1)
    # columns
    for i in range(round(420*1.5/STEP)):
        if i == 0:
            pygame.draw.line(win, dark_gray, (wWindow - gutter*2 - maxdist + i*STEP, FLOOR), (wWindow - gutter*2 - maxdist + i*STEP, gutter*2), 1)
        elif i % 5 == 0:
            pygame.draw.line(win, medium_gray, (wWindow - gutter*2 - maxdist + i*STEP, FLOOR), (wWindow - gutter*2 - maxdist + i*STEP, gutter*2), 1)
            xlabel = font1.render(f'{i*10}', True, black)
            xlabelRect = xlabel.get_rect()
            xlabelRect.center = (wWindow - gutter*2 - maxdist + i*STEP, FLOOR + 8)
            win.blit(xlabel, xlabelRect)
        else:
            pygame.draw.line(win, light_gray, (wWindow - gutter*2 - maxdist + i*STEP, FLOOR), (wWindow - gutter*2 - maxdist + i*STEP, gutter*2), 1)
    pygame.draw.line(win, dark_gray, (wWindow - gutter * 2 - maxdist, FLOOR-1), (wWindow - gutter*2 +1, FLOOR-1), 2)

    xAxisLabel = font1.render('distance (cm)', True, black)
    yAxisLabel = font1.render('height (cm)', True, black)
    yAxisLabel = pygame.transform.rotate(yAxisLabel, 90)

    xAxisLabel_Rect = xAxisLabel.get_rect()
    yAxisLabel_Rect = yAxisLabel.get_rect()

    xAxisLabel_Rect.center = (wWindow - gutter*3 - maxdist//2, FLOOR + 30)
    yAxisLabel_Rect.center = (wWindow - gutter*3 - maxdist - 20, (FLOOR + gutter*3)//2)

    win.blit(xAxisLabel, xAxisLabel_Rect)
    win.blit(yAxisLabel, yAxisLabel_Rect)

    # goal
    pygame.draw.rect(win, red, pygame.Rect(wWindow-gutter*2-goal_width+3, FLOOR - goal_height, goal_width, goal_height))
    pygame.draw.line(win, red, (wWindow-gutter*2-1, FLOOR-2), (wWindow-gutter*2-1, FLOOR - goal_backboard), 4)

    # moving objects
    artifact.draw(win)
    robot.draw(win)
    shooter.draw(win)

    #pygame.display.flip() 
    pygame.display.update() 

# main loop
pygame.init()

clock = pygame.time.Clock()
run = True
framerate = 60

held = False
launch = False
time = 0
vinitial = 200
launchAngle = math.radians(45) 

while run:
    clock.tick(framerate)

    for event in pygame.event.get():

        # quit
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            
            if event.key == pygame.K_SPACE:
                if not launch:
                    launch = True
                    x = artifact.x
                    y = artifact.y
        
    # moving robot
    if event.type == pygame.KEYDOWN:
        key_pressed_is = pygame.key.get_pressed()
        if key_pressed_is[pygame.K_LEFT]:
            robot.x -= CM
        if key_pressed_is[pygame.K_RIGHT]:
            robot.x += CM
        if robot.x < wWindow - maxdist -gutter*2 +1:
            robot.x = wWindow-maxdist-gutter*2 +1

    # changing angle of chute
        if launchAngle < 0:
            launchAngle = 0
        if launchAngle > math.pi/2:
            launchAngle = 90

    if launch:
        time += 0.01
        shot = ball.trajectory(x, y, vinitial, launchAngle, time)
        artifact.x = shot[0]
        artifact.y = shot[1]
        if artifact.y < FLOOR - artifact.radius + 1:
            if artifact.x <= wWindow - gutter - artifact.radius + 1:
                time += 0.05
                shot = ball.trajectory(x, y, vinitial, launchAngle, time)
                artifact.x = shot[0]
                artifact.y = shot[1]
            else: 
                time += 0.05
                vinitial *= -1
                shot = ball.trajectory(x, y, vinitial, launchAngle, time)
                artifact.x = shot[0]
                artifact.y = shot[1]
        else:
            launch = False
            time = 0
            offset = 0
            artifact.y = FLOOR - artifact.radius
            print('landed')


                
    drawWindow()

pygame.quit()