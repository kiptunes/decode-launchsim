# pip install pygame
# pip install pygame-textinput 

import pygame, sys, math
from ui import *
import copy
#import pygame_textinput

CM = 1.5
vinitial = 600 # <- edit this to be velocity in cm/s
vinitial *= CM # <-- converting to pixels

wWindow, hWindow = 960, 540
bg_color = (100, 100, 100)
gutter = 20

clock = pygame.time.Clock()
framerate = 60

FLOOR = 340
STEP = 10 * CM  # 10 pixels per 0.1 meter
DRAW_MESSAGE = pygame.USEREVENT + 0
CLEAR_MESSAGE = pygame.USEREVENT + 1

landed = False
flipped = False
goalScored = False
backboard_hit = False
launch = False
hit_left = False
time = 0
g = -9.8 *100*CM# px/s^2
# 9.8 m/s^2 = (9.8*100) cm/s^2 
COR = 0.6 # coefficient of restitution
vinitial = 600 * CM # px/s
launchAngle = 45 
trajecVis = False
liveUpdate = True

minipos = 'VALID'

# window setup
win = pygame.display.set_mode((wWindow, hWindow))
pygame.display.set_caption('DECODE Launch Simulator')
pygame.font.init()
pygame.font.get_init()
font1 = pygame.font.SysFont('dejavusansmono', 10)
font2 = pygame.font.SysFont('dejavusansmono', 12)

white, black, light_gray, medium_gray, gray, dark_gray = (255, 255, 255), (0, 0, 0), (220, 220, 220), (200, 200, 200), (150, 150, 150), (120, 120, 120)
red, pink, red_gray, green_gray = (60, 0, 0), (250, 210, 220), (142,95,97), (109,150,103)
teamRed, teamBlue = (220, 60, 60), (60, 60, 220)
purple, green = (160, 40, 200), (80, 200, 100)
divider_color = (50, 50, 50)
blue, dark_blue = (150, 200, 200), (120, 160, 200)

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


class ball(object):
    def __init__(self, x, y, radius, color, win):
        self.x = x 
        self.y = y
        self.radius = radius
        self.color = color
        

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
    
    @staticmethod
    def trajectory(xinitial, yinitial, vinitial, angle, time, win):
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
            if not flipped and not hit_left:
                angle = math.radians(angle)
                xvel = vinitial * math.cos(angle)
                yivel = vinitial * math.sin(angle)
                yfvel = -(vinitial*math.sin(angle) + g*time)
                curang = math.atan(yfvel/xvel)    

                xdist = xvel * time
                ydist = (yivel * time) + ((g * (time)**2)/2)

                newx = round(xdist + xinitial)
                newy = round(yinitial - ydist)
            elif hit_left and flipped:
                x_prev = artifact.x
                angle = math.radians(angle)
                xvel = (vinitial * math.cos(angle))*COR
                yivel = vinitial * math.sin(angle)
                yfvel = (yivel*time + (g * (time)**2)/2)
                curang = math.atan(yfvel/xvel)    

                xdist = xvel * 0.015
                ydist = ((yivel * time) + ((g * (time)**2)/2))
                newx = round(x_prev + xdist)
                newy = round(yinitial - ydist)
            elif hit_left:
                x_prev = artifact.x
                angle = math.radians(angle)
                xvel = (vinitial * math.cos(angle))*(-1)*COR
                yivel = vinitial * math.sin(angle)
                yfvel = (yivel*time + (g * (time)**2)/2)
                curang = math.atan(yfvel/xvel)    

                xdist = xvel * 0.015
                ydist = ((yivel * time) + ((g * (time)**2)/2))
                newx = round(x_prev + xdist)
                newy = round(yinitial - ydist)
                print(newx, xdist)
            else:
                x_prev = artifact.x
                angle = math.radians(angle)
                xvel = (vinitial * math.cos(angle))*(-1)*COR
                yivel = vinitial * math.sin(angle)
                yfvel = (yivel*time + (g * (time)**2)/2)
                curang = math.atan(yfvel/xvel)    

                xdist = xvel * 0.015
                ydist = ((yivel * time) + ((g * (time)**2)/2))
                # xdist = 2
                newx = round(x_prev + xdist)
                newy = round(yinitial - ydist)
            return(newx, newy, xvel, yfvel, curang)
            


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

    def draw_chute(self, win, angle):
        ang = math.radians(angle)
        r = shooter.radius -1
        l = 30
        pointA = (shooter.x-r*math.sin(ang), shooter.y-r*math.cos(ang))
        pointB = (shooter.x + r*math.sin(ang), shooter.y + r*math.cos(ang))
        pointC = (pointB[0] + l*math.cos(ang), pointB[1] - l*math.sin(ang))
        pointD = (pointA[0] + l*math.cos(ang), pointA[1] - l*math.sin(ang))
        pygame.draw.polygon(win, dark_blue, (pointA, pointB, pointC, pointD))
        pygame.draw.circle(win, blue, (shooter.x, shooter.y), shooter.x-self.x)
        pygame.draw.rect(win, self.color, (self.x, self.y, self.length, self.width))
        pygame.draw.circle(win, dark_blue, (shooter.x, shooter.y), 5)

artifact = ball(500, FLOOR - artifact_radius, artifact_radius, purple, win)
robot = rectangle(wWindow-gutter*2-maxdist+1, FLOOR - robot_width/3, robot_width, robot_width/3, blue)
shooter = ball(robot.x + artifact_radius+4, robot.y, artifact_radius + 2, dark_blue, win)

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

        title = font2.render(self.title, True, white)
        title_rect = pygame.Rect(menuRect[0]+6, menuRect[1]+7, menuRect[2]-5, menuRect[3])
        title_surf = pygame.Surface((menuRect[2], 24))
        title_surf.fill(divider_color)

        win.blit(title_surf, (menuRect[0], menuRect[1]))
        win.blit(title, title_rect)
        pygame.draw.rect(win, divider_color,pygame.Rect(menuRect[0], menuRect[1], menuRect[2] +1, menuRect[3]+1), 1)

    def draw_noTitle(self, win):
        menuRect = self.menuRect
        self.menuSurf.fill(self.color)
        win.blit(self.menuSurf, (self.leftx, self.topy))
        menuRect.topleft = (self.leftx, self.topy)
        title = font2.render(self.title, True, white)
        win.blit(title, menuRect)

loadMenu_width = (maxdist+gutter*2 +40) // 3
loadMenu_height = hWindow - (FLOOR + 50 + gutter*2)
currentVars = menu(gutter, field_length+gutter*2+15, field_length, hWindow-field_length-gutter*2-35, gray, 'CURRENT VALUES')
prevVars = menu(field_length+2 +gutter*2, hWindow - gutter - loadMenu_height, loadMenu_width, loadMenu_height, gray, 'LAST LAUNCH')
storedVars = menu(field_length+2 +gutter*3+loadMenu_width, hWindow - gutter - loadMenu_height, loadMenu_width, loadMenu_height, gray, 'STORED LAUNCH')
keysMenu = menu(wWindow - gutter - field_length, hWindow - gutter - loadMenu_height, loadMenu_width, loadMenu_height, bg_color, '')
goalRect = pygame.Rect(wWindow-gutter*2-goal_width+3, FLOOR - goal_height, goal_width, goal_height)

label_miniField = textLabel(gutter, gutter + field_length + 2, win, 'Overhead Preview', False, font2)
label_warning = textLabel(gutter, field_length + gutter + 16, win, f'{'WARNING: Invalid launch ':>34}', False, font1, red)

curValues_list = ['', '', '']
prevValues_list = [6, 45, 365]
storedValues_list = [6, 45, 365]

label_curvar_vi = textLabel(currentVars.leftx + 10, currentVars.topy + 34, win, 'velocity (m/s²): ', True)
label_curvar_angle = textLabel(currentVars.leftx + 10, label_curvar_vi.y+20, win, 'angle (degrees): ', True)
label_curvar_xdist = textLabel(currentVars.leftx+10, label_curvar_angle.y +20, win, 'cm from goal: ', True)

textbox_vi = textbox(label_curvar_vi.text_rect.right, label_curvar_vi.text_rect.top, win, str(vinitial/100/CM))
textbox_ang = textbox(label_curvar_angle.text_rect.right, label_curvar_angle.text_rect.top, win, str(launchAngle))
textbox_dist = textbox(label_curvar_xdist.text_rect.right, label_curvar_xdist.text_rect.top, win, '365')

label_stvar_vi = textLabel(storedVars.leftx + 10, storedVars.topy + 28, win, 'velocity (m/s²): ')
label_stvar_angle = textLabel(storedVars.leftx + 10, label_stvar_vi.y+20, win, 'angle (degrees): ')
label_stvar_xdist = textLabel(storedVars.leftx+10, label_stvar_angle.y +20, win, 'cm from goal: ')

label_prvar_vi = textLabel(prevVars.leftx + 10, prevVars.topy + 28, win, 'velocity (m/s²): ')
label_prvar_angle = textLabel(prevVars.leftx + 10, label_prvar_vi.y+20, win, 'angle (degrees): ')
label_prvar_xdist = textLabel(prevVars.leftx+10, label_prvar_angle.y +20, win, 'cm from goal: ')

label_keys_updown = textLabel(keysMenu.leftx+5, keysMenu.topy+5, win, f'UP/DOWN{'change angle':>21}')
label_keys_rightleft = textLabel(keysMenu.leftx+5, label_keys_updown.y+20, win, f'LEFT/RIGHT{'change position':>18}')
label_keys_space = textLabel(keysMenu.leftx+5, label_keys_rightleft.y+20, win, f'SPACE{'launch':>23}')
label_keys_goal = textLabel(keysMenu.leftx+5, label_keys_space.y+40, win, f'{'Nice shot! :-)':28}')

checkbox_showtrajec = checkbox(win, currentVars.leftx + 10, label_curvar_xdist.y + 98, 'Show trajectory')
checkbox_showvec = checkbox(win, currentVars.leftx + 10, checkbox_showtrajec.y +20, 'Show vectors')
checkbox_liveup = checkbox(win, currentVars.leftx + 10, checkbox_showvec.y +20, 'Live update', black, True)

button_storeValues = button(currentVars.leftx+10, checkbox_liveup.y+24, currentVars.color, 'STORE')
button_fromGraph = button(currentVars.leftx +95, checkbox_liveup.y +24, currentVars.color, 'LOAD FROM GRAPH')
button_loadStored = button(wWindow - loadMenu_width-gutter*2+1, prevVars.topy+3, divider_color, 'LOAD')
button_loadPrev = button(wWindow - loadMenu_width*2-gutter*3+1, prevVars.topy+3, divider_color, 'LOAD')

def prevValues(vinitial, launchAngle):
    u = vinitial/CM/100
    ang = launchAngle
    xv = round(u*math.cos(ang))
    yv = round(u*math.sin(ang))
    distance = round(prevValues_list[2]/CM)
    return [u, ang, distance]

def storeValues(vinitial, launchAngle):
    u = vinitial/CM/100
    ang = launchAngle
    xv = round(u*math.cos(ang))
    yv = round(u*math.sin(ang))
    distance = round(storedValues_list[2]/CM)
    return [u, ang, distance]

def curValues(vinitial, launchAngle):
    u = vinitial/CM/100
    ang = launchAngle
    xv = round(u*math.cos(ang))
    yv = round(u*math.sin(ang))
    distance = round(curValues_list[2]/CM)
    return [u, ang, distance]

def drawMenus():
    currentVars.draw(win)
    prevVars.draw(win)
    storedVars.draw(win)
    
    label_miniField.draw()

    if textbox_vi.enter:
        print(textbox_vi.visualizer.value)
        curvel = float(textbox_vi.visualizer.value)*CM*100
        global vinitial 
        global launchAngle
        vinitial = curvel
        label_curvar_vi.drawValue(textbox_vi.visualizer.value)

    if button_fromGraph.clicked and not checkbox_liveup.is_checked():
        label_curvar_vi.drawValue(curValues_list[0])
        label_curvar_angle.drawValue(curValues_list[1])
        label_curvar_xdist.drawValue(curValues_list[2])
    elif button_loadPrev.clicked:
        global launchAngle
        vinitial = int(prevValues_list[0])*CM*100
        launchAngle = int(prevValues_list[1])
        robot.x = -(int(prevValues_list[2])*CM +robot_width - (wWindow-gutter*2+3))
        label_curvar_vi.drawValue(prevValues_list[0])
        label_curvar_angle.drawValue(prevValues_list[1])
        label_curvar_xdist.drawValue(prevValues_list[2])
        button_loadPrev.clicked = False
    elif button_loadStored.clicked:
        vinitial = int(storedValues_list[0])*CM*100
        launchAngle = int(storedValues_list[1])
        robot.x = -(int(storedValues_list[2])*CM +robot_width - (wWindow-gutter*2+3))
        label_curvar_vi.drawValue(storedValues_list[0])
        label_curvar_angle.drawValue(storedValues_list[1])
        label_curvar_xdist.drawValue(storedValues_list[2])
        button_loadStored.clicked = False
    elif checkbox_liveup.is_checked():
        curvel = vinitial/CM/100
        distpx = (wWindow-gutter*2+3)-(robot.x+robot_width)
        curdist = round(distpx/CM)
        label_curvar_vi.drawValue(curvel)
        label_curvar_angle.drawValue(launchAngle)
        label_curvar_xdist.drawValue(curdist)
    else:
        label_curvar_vi.draw()
        label_curvar_angle.draw()
        label_curvar_xdist.draw()

    if button_storeValues.clicked:
        label_stvar_vi.drawValue(storedValues_list[0])
        label_stvar_angle.drawValue(storedValues_list[1])
        label_stvar_xdist.drawValue(storedValues_list[2])
    else: 
        label_stvar_vi.draw()
        label_stvar_angle.draw()
        label_stvar_xdist.draw()
        
    if landed:
        label_prvar_vi.drawValue(prevValues_list[0])
        label_prvar_angle.drawValue(prevValues_list[1])
        label_prvar_xdist.drawValue(prevValues_list[2])
    else:
        label_prvar_vi.draw()
        label_prvar_angle.draw()
        label_prvar_xdist.draw()

    label_keys_updown.draw()
    label_keys_rightleft.draw()
    label_keys_space.draw()
    if goalScored:
        pygame.draw.rect(win, green_gray, label_keys_goal.text_rect)
        label_keys_goal.draw()
    
    checkbox_liveup._draw_checkbox()
    if checkbox_liveup.is_checked():
        pass
    checkbox_showtrajec._draw_checkbox()
    if trajecVis:
        x = shooter.x
        y = shooter.y
        u = vinitial
        l = 3
        ang = math.radians(launchAngle)
        xv = round(u*math.cos(ang))
        yv = round(u*math.sin(ang))
        distance = round((u**2*math.sin(2*ang))/(-g) +artifact_radius)
        t = ((yv+math.sqrt(yv**2+2*(-g)*(robot.width))))/(-g)
        for i in range(100):
            if i < 10 or i % 2 != 0:
                continue
            elif i == 10:
                ti = t*float(f'0.0{i}')
                ti_prev = t*float(f'0.0{i-1}')
                x_prev = x + xv*(ti_prev)
                y_prev = y - yv*(ti_prev) - (g*(ti_prev)**2)/2
                x_new = x + xv*(ti)
                y_new = y - yv*(ti) - (g*(ti)**2)/2
                pygame.draw.line(win, dark_gray, (x_prev, y_prev), (x_new, y_new))
            else: 
                ti = t*float(f'0.{i}')
                ti_prev = t*float(f'0.{i-1}')
                x_prev = x + xv*(ti_prev)
                y_prev = y - yv*(ti_prev) - (g*(ti_prev)**2)/2
                x_new = x + xv*(ti)
                y_new = y - yv*(ti) - (g*(ti)**2)/2
                if x_new > wWindow -gutter*2 or x_new < wWindow -gutter*2 - maxdist:
                    continue
                else:
                    pygame.draw.line(win, dark_gray, (x_prev, y_prev), (x_new, y_new))

    checkbox_showvec._draw_checkbox()

    button_storeValues.draw(win)
    button_fromGraph.draw(win)
    button_loadPrev.draw(win)
    button_loadStored.draw(win)

    textbox_vi.draw()
    textbox_ang.draw()
    textbox_dist.draw()


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
        pygame.draw.rect(win, red_gray, label_warning.text_rect)
        label_warning.draw()

    # moving objects
    artifact.draw(win)
    robot.draw(win)
    shooter.draw(win)
    robot.draw_chute(win, launchAngle)

    # goal
    pygame.draw.rect(win, teamRed, goalRect)
    pygame.draw.line(win, teamRed, (wWindow-gutter*2-1, FLOOR-2), (wWindow-gutter*2-1, FLOOR - goal_backboard), 4)

    if launch:
        if checkbox_showvec.is_checked():
            x = shot[0]
            y = shot[1]
            xvel = shot[2]/5
            yvel = shot [3]/5
            pygame.draw.line(win, dark_gray, (x, y), (x+xvel//CM, y))
            if xvel > 0:
                pygame.draw.line(win, dark_gray, (x+xvel//CM, y), (x+xvel//CM -5, y + 3))
                pygame.draw.line(win, dark_gray, (x+xvel//CM, y), (x+xvel//CM -5, y - 3))
            else:
                pygame.draw.line(win, dark_gray, (x+xvel//CM, y), (x+xvel//CM +5, y + 3))
                pygame.draw.line(win, dark_gray, (x+xvel//CM, y), (x+xvel//CM +5, y - 3))

            pygame.draw.line(win, dark_gray, (x, y), (x, y+ yvel//CM))
            if yvel > 0:
                pygame.draw.line(win, dark_gray, (x, y+ yvel//CM), (x +3, y+ yvel//CM - 5))
                pygame.draw.line(win, dark_gray, (x, y+ yvel//CM), (x -3, y+ yvel//CM - 5))
            else:         
                pygame.draw.line(win, dark_gray, (x, y+ yvel//CM), (x +3, y+ yvel//CM + 5))
                pygame.draw.line(win, dark_gray, (x, y+ yvel//CM), (x -3, y+ yvel//CM + 5))

            pygame.draw.line(win, dark_gray, (x, y), (x +xvel//CM, y+yvel//CM))

    #menus
    drawMenus()
    pygame.display.update() 

run = True
while run:
    clock.tick(framerate)
    drawWindow()
    
    events = pygame.event.get()
    
    textbox_vi.visualizer.update(events)

    key_pressed_is = pygame.key.get_pressed()
    if key_pressed_is[pygame.K_LEFT]:
        robot.x -= CM
        if robot.x < wWindow - maxdist -gutter*2 +1:
            robot.x = wWindow-maxdist-gutter*2 +1
    if key_pressed_is[pygame.K_RIGHT]:
        robot.x += CM
        if robot.x +robot_width > wWindow-gutter*2-goal_width+.2:
            robot.x = wWindow-gutter*2-goal_width+3 - robot_width
    if key_pressed_is[pygame.K_UP]:
        launchAngle += 1
        if launchAngle > 180:
            launchAngle = 180
    if key_pressed_is[pygame.K_DOWN]:
        launchAngle -= 1
        if launchAngle < 1:
            launchAngle = 1
    
    for event in events:
        # quit
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            
            if event.key == pygame.K_SPACE:
                if not launch:
                    launch = True
                    artifact.x = shooter.x
                    artifact.y = shooter.y
                    x = artifact.x
                    y = artifact.y
            
            # curvel = vinitial/CM/100
            # distpx = (wWindow-gutter*2+3)-(robot.x+robot_width)
            # curdist = round(distpx/CM)
            # textbox_vi.update(event, curvel)
            # textbox_ang.update(event, launchAngle)
            # textbox_dist.update(event, curdist)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                checkbox_liveup.update_checkbox()
                if not checkbox_liveup.is_checked():
                    liveUpdate = False
                button_fromGraph.clicked = False
                checkbox_showtrajec.update_checkbox()
                if checkbox_showtrajec.is_checked():
                    if not trajecVis:
                        trajecVis = True
                        linex = shooter.x
                        liney = shooter.y
                else:
                    trajecVis = False
                checkbox_showvec.update_checkbox()

                if button_storeValues.butRect.collidepoint(pygame.mouse.get_pos()):
                    button_storeValues.clicked = True
                    storedValues_list[2] = (wWindow-gutter*2+3)-(robot.x+robot_width)
                    storedValues_list = storeValues(vinitial, launchAngle)
                
                if button_fromGraph.butRect.collidepoint(pygame.mouse.get_pos()):
                    button_fromGraph.clicked = True
                    curValues_list[2] = (wWindow-gutter*2+3)-(robot.x+robot_width)
                    curValues_list = curValues(vinitial, launchAngle)
                
                if button_loadPrev.butRect.collidepoint(pygame.mouse.get_pos()):
                    button_loadPrev.clicked = True

                if button_loadStored.butRect.collidepoint(pygame.mouse.get_pos()):
                    button_loadStored.clicked = True

                # if label_curvar_vi.textbox_rect.collidepoint(pygame.mouse.get_pos()):
                #     textbox_vi.state = 'HIGHLIGHTED'
                #     textbox_ang.state = 'DEFAULT'
                #     textbox_dist.state = 'DEFAULT'
                # if label_curvar_angle.textbox_rect.collidepoint(pygame.mouse.get_pos()):
                #     textbox_ang.state = 'HIGHLIGHTED'
                #     textbox_vi.state = 'DEFAULT'
                #     textbox_dist.state = 'DEFAULT'
                # if label_curvar_xdist.textbox_rect.collidepoint(pygame.mouse.get_pos()):
                #     textbox_dist.state = 'HIGHLIGHTED'
                #     textbox_vi.state = 'DEFAULT'
                #     textbox_ang.state = 'DEFAULT'
                

        if event.type == DRAW_MESSAGE:
            goalScored = True
        if event.type == CLEAR_MESSAGE:
            goalScored = False
            pygame.time.set_timer(DRAW_MESSAGE, 0)
            pygame.time.set_timer(CLEAR_MESSAGE, 0)

    if launch:
        landed = False
        prevValues_list[2] = (wWindow-gutter*2+3)-(robot.x+robot_width)
        if artifact.y < FLOOR - artifact.radius+1:
            time += 0.015
            if artifact.x - artifact_radius < wWindow - maxdist - 37:
                # hit left wall
                hit_left = True
                shot = ball.trajectory(x, y, vinitial, launchAngle, time,win)
                artifact.x = shot[0]
                artifact.y = shot[1]
            elif artifact.x+artifact_radius > wWindow - gutter-18 and artifact.y + artifact_radius <= FLOOR - goal_backboard:
                # hit right wall
                flipped = True
                shot = ball.trajectory(x, y, vinitial, launchAngle, time,win)
                artifact.x = shot[0]
                artifact.y = shot[1]
            elif not backboard_hit and artifact.x+artifact_radius > wWindow - gutter-23 and artifact.y + artifact_radius+2 <= FLOOR - goal_height+30 and artifact.y + artifact.radius > FLOOR - goal_backboard:
                # hit backboard
                flipped = True
                backboard_hit = True
                shot = ball.trajectory(x, y, vinitial, launchAngle, time,win)
                artifact.x = shot[0]
                artifact.y = shot[1]
            elif backboard_hit and artifact.x <= goalRect.left + artifact_radius:
                # hit backboard and returning
                hit_left = True
                shot = ball.trajectory(x, y, vinitial, launchAngle, time,win)
                artifact.x = shot[0]
                artifact.y = shot[1]
            elif artifact.y - artifact_radius < -100:
                # hit 'ceiling'
                artifact.y = FLOOR - artifact.radius
                flipped = False
                hit_left = False
                backboard_hit = False
                launch = False
                time = 0
            elif not backboard_hit and goalRect.collidepoint(artifact.x + artifact_radius, artifact.y+artifact_radius-2) and artifact.x + artifact_radius < wWindow - gutter - goal_width:
                # goal hit from side
                flipped = True
                shot = ball.trajectory(x, y, vinitial, launchAngle, time,win)
                artifact.x = shot[0]
                artifact.y = shot[1]
            elif goalRect.collidepoint(artifact.x+2, artifact.y-artifact_radius-10) and artifact.x + artifact_radius >= wWindow - gutter - goal_width:
                # goal scored
                pygame.time.set_timer(DRAW_MESSAGE, 199)
                pygame.time.set_timer(CLEAR_MESSAGE, 1000)
                artifact.y = FLOOR - artifact.radius
                launch = False
                hit_left = False
                backboard_hit = False
                flipped = False
                time = 0
                landed = True
                prevValues_list = prevValues(vinitial, launchAngle)
            else:
                shot = ball.trajectory(x, y, vinitial, launchAngle, time,win)
                artifact.x = shot[0]
                artifact.y = shot[1]
        else:
            prevValues_list = prevValues(vinitial, launchAngle)
            landed = True
            launch = False
            time = 0
            flipped = False
            hit_left = False
            backboard_hit = False
            artifact.y = FLOOR - artifact.radius

pygame.quit()
