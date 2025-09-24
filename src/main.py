#
#  sorry 
#
import pygame, sys, math
from ui import *
#import pygame_textinput


wWindow, hWindow = 960, 540
bg_color = (120, 120, 120)
gutter = 20

clock = pygame.time.Clock()
framerate = 60

held = False
launch = False
time = 0
vinitial = 200
launchAngle = math.radians(45) 

minipos = 'VALID'
# window setup
win = pygame.display.set_mode((wWindow, hWindow))
pygame.display.set_caption('DECODE Launch Simulator')
pygame.font.init()
pygame.font.get_init()
font1 = pygame.font.SysFont('dejavusansmono', 10)

white, black, light_gray, medium_gray, gray, dark_gray = (245, 245, 245), (0, 0, 0), (220, 220, 220), (200, 200, 200), (150, 150, 150), (120, 120, 120)
red, pink = (200, 80, 80), (250, 210, 220)
teamRed, teamBlue = (220, 60, 60), (60, 60, 220)
purple, green = (160, 40, 200), (80, 200, 100)
divider_color = (50, 50, 50)
blue, dark_blue = (150, 200, 200), (120, 160, 200)

FLOOR = 340
CM = 1.5
STEP = 10 * CM  # 10 pixels per 0.1 meter

miniMulti = 0.56
field_length = math.floor(144 * 2.54 *miniMulti) # 144" to cm to mini
field_surf = pygame.Surface((field_length, field_length))
field_rect = field_surf.get_rect()
tile = field_length/6
tile_diagonal = math.sqrt(2*tile**2)
tunnel_width = 15.6 * miniMulti

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

artifact = ball(500, FLOOR - artifact_radius, artifact_radius, purple)
robot = rectangle(wWindow-gutter*2-maxdist+1, FLOOR - robot_width/3, robot_width, robot_width/3, blue)
shooter = ball(robot.x + artifact_radius+4, robot.y, artifact_radius + 2, dark_blue)

class menu(object):
    def __init__(self, leftx, topy, width, height, color, title):
        self.leftx = leftx
        self.topy = topy
        self.width = width
        self.height = height
        self.color = color
        self.title = title
        self.menuSurf = pygame.Surface((width, height))
        self.menuRect = self.menuSurf.get_rect()
    
    def draw(self, win):
        menuRect = self.menuRect
        self.menuSurf.fill(self.color)
        win.blit(self.menuSurf, (self.leftx, self.topy))
        menuRect.topleft = (self.leftx, self.topy)

        title = font1.render(self.title, True, white)
        title_rect = pygame.Rect(menuRect[0]+6, menuRect[1]+5, menuRect[2]-5, menuRect[3])
        title_surf = pygame.Surface((menuRect[2], 24))
        title_surf.fill(divider_color)

        win.blit(title_surf, (menuRect[0], menuRect[1]))
        win.blit(title, title_rect)
        pygame.draw.rect(win, divider_color,pygame.Rect(menuRect[0], menuRect[1], menuRect[2] +1, menuRect[3]+1), 1)

loadMenu_width = (maxdist+gutter*2 +40) // 3
loadMenu_height = hWindow - (FLOOR + 50 + gutter*2)
currentVars = menu(gutter, field_length+gutter*2+15, field_length, hWindow-field_length-gutter*2-35, gray, 'CURRENT VALUES')
prevVars = menu(field_length+2 +gutter*2, hWindow - gutter - loadMenu_height, loadMenu_width, loadMenu_height, gray, 'LAST LAUNCH')
storedVars = menu(field_length+2 +gutter*3+loadMenu_width, hWindow - gutter - loadMenu_height, loadMenu_width, loadMenu_height, gray, 'STORED LAUNCH')

checkbox1 = checkbox(win, currentVars.leftx + 8, currentVars.topy + 40, 'Show trajectory')
# viTextbox = textbox(win, currentVars.leftx + 8, currentVars.topy + 50, field_length-16, 20, str(vinitial))
#textinput = pygame_textinput.

def drawMenus():
    currentVars.draw(win)
    prevVars.draw(win)
    storedVars.draw(win)
    checkbox1._draw_checkbox()

    #win.blit(textinput.surface, (10, 10))

def drawField():
    field_surf.fill(white)
    win.blit(field_surf, (gutter, gutter))
    field_rect.topleft= (gutter, gutter)
    # launch zones
    pygame.draw.polygon(win, pink, (field_rect.topleft, field_rect.topright, field_rect.center))
    pygame.draw.polygon(win, pink, ((field_rect.bottomleft[0] + tile*2, field_rect.bottomleft[1]), (field_rect.bottomright[0] - tile*2, field_rect.bottomright[1]), (field_rect.centerx, field_rect.centery+ tile*2)))
    # goals
    pygame.draw.polygon(win, teamRed, (field_rect.topleft, (field_rect.topleft[0] + tile, field_rect.topleft[1]), (field_rect.topleft[0]+tunnel_width, field_rect.topleft[1]+tile), (field_rect.topleft[0], field_rect.topleft[1]+tile)))
    pygame.draw.polygon(win, teamBlue, (field_rect.topright, (field_rect.topright[0] - tile, field_rect.topright[1]), (field_rect.topright[0]-tunnel_width, field_rect.topright[1]+tile), (field_rect.topright[0], field_rect.topright[1]+tile)))
    pygame.draw.rect(win, divider_color,pygame.Rect(field_rect[0], field_rect[1], field_rect[2] +1, field_rect[3]+1), 1)

warningText = font1.render('WARNING: INVALID LAUNCH', True, red)
warningText_rect = warningText.get_rect()
warningText_rect.center = (field_rect.centerx+15, field_rect.bottom + 40)


def updatePos(distance):
    distance = (wWindow-gutter*2+3)-(robot.x+robot_width) # the variable is called 'xdist' but the axis from overhead is defined along a diagonal
    distanceMini = distance*miniMulti
    if distanceMini <= math.sqrt(2*(tile*3)**2):
        validpos = True
        minix = distanceMini*math.cos(math.pi/4) + field_rect.left # setting theta to 45 degrees or pi/4 radians because the diagonal is along a 45/45/90 triangle made with the tiles
        miniy = distanceMini*math.sin(math.pi/4) + field_rect.top
    elif distanceMini >= math.sqrt((tile*3)**2+(tile*5)**2) and distanceMini < math.sqrt((tile*3)**2+(tile*6)**2): # topmost point of smaller launch zone is a point on a 3x5 tile rectangle
        validpos = True
        minix = field_rect.centerx
        miniy = distanceMini*math.sin(math.acos((field_rect.centerx -field_rect.left)/distanceMini)) + field_rect.top
    elif distanceMini >= math.sqrt((tile*3)**2+(tile*6)**2) and distanceMini < math.sqrt(((tile*4)**2+(tile*6)**2)):
            validpos = True
            minix = distanceMini*math.cos(math.asin((field_length)/distanceMini)) + field_rect.left
            miniy = field_rect.bottom
    elif distanceMini >= math.sqrt(((tile*4)**2+(tile*6)**2)) and distanceMini < math.sqrt((2*(tile*6)**2)):
            validpos = False
            minix = math.sqrt(distanceMini**2 - field_length**2) + field_rect.left
            miniy = field_rect.bottom
    elif distanceMini >= math.sqrt((2*(tile*6)**2)):
            validpos = False
            minix = field_rect.bottomright[0]
            miniy = field_rect.bottomleft[1]
    else:
        validpos = False
        minix = field_rect.centerx
        miniy = distanceMini*math.sin(math.acos((field_rect.centerx -field_rect.left)/distanceMini)) + field_rect.top
        
    return (minix, miniy, validpos, distance)

def drawGraph():
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

# update window
def drawWindow():
    win.fill(bg_color)
    # graph area
    pygame.draw.rect(win, white, pygame.Rect(wWindow - maxdist - gutter*3 -40, gutter, maxdist+gutter*2 +40, FLOOR+30), 0, 5)   # '+#'s added in later to account for graph labels
                                                                                                                                # should have made a surface for the rect but I di
                                                                                                                                # -dn't think that far ahead
    pygame.draw.rect(win, divider_color, pygame.Rect(wWindow - maxdist - gutter*3 -40, gutter, maxdist+gutter*2 +40, FLOOR+30), 1, 5) 

    drawField()
    drawGraph()
    minipos = updatePos(robot.x)
    pygame.draw.circle(win, dark_blue, (minipos[0], minipos[1]), 4)
    if minipos[2] == False:
        win.blit(warningText, warningText_rect)
    # goal
    pygame.draw.rect(win, teamRed, pygame.Rect(wWindow-gutter*2-goal_width+3, FLOOR - goal_height, goal_width, goal_height))
    pygame.draw.line(win, teamRed, (wWindow-gutter*2-1, FLOOR-2), (wWindow-gutter*2-1, FLOOR - goal_backboard), 4)

    # moving objects
    artifact.draw(win)
    robot.draw(win)
    shooter.draw(win)

    #menus
    drawMenus()
    
    #pygame.display.flip() 
    pygame.display.update() 

run = True
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
                print(updatePos(robot.x)[3])
                if not launch:
                    launch = True
                    x = artifact.x
                    y = artifact.y
    
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            checkbox1.update_checkbox()

    # if event.type == pygame.MOUSEBUTTONDOWN and viTextbox.input_rect.collidepoint(pygame.mouse.get_pos()):
    #     if event.button == 1:
    #         if not viTextbox.is_active:
    #             viTextbox.text =''
    #             viTextbox.is_active = True
    #             print('hit')
    #             viTextbox.text_update()
                


    # moving robot
    if event.type == pygame.KEYDOWN:
        key_pressed_is = pygame.key.get_pressed()
        if key_pressed_is[pygame.K_LEFT]:
            robot.x -= CM
            if robot.x < wWindow - maxdist -gutter*2 +1:
                robot.x = wWindow-maxdist-gutter*2 +1
        if key_pressed_is[pygame.K_RIGHT]:
            robot.x += CM
            if robot.x +robot_width > wWindow-gutter*2-goal_width+.2:
                robot.x = wWindow-gutter*2-goal_width+3 - robot_width

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
        if artifact.y <= FLOOR - artifact.radius:
            if artifact.x <= wWindow - gutter - artifact.radius:
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
