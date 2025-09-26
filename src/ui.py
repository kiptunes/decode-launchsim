import pygame, sys
#import pygame_textinput

pygame.init()
pygame.font.init()

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (245, 245, 245)

BUTTON_NONE = (190, 190, 190)
BUTTON_HOVER = (120, 120, 120)
font1 = pygame.font.SysFont('dejavusansmono', 10)
font2 = pygame.font.SysFont('dejavusansmono', 12)

class button:
    def __init__(self, x, y, surfcolor, label = ''):
        self.x = x
        self.y = y
        self.label = label
        self.surfcolor = surfcolor
        self.clicked = False
        
    def draw(self, surface):
        self.surface = surface
        pos = pygame.mouse.get_pos()
        label = font1.render(self.label, True, BLACK)
        self.label_rect = label.get_rect()
        self.label_rect.center = (self.x+(self.label_rect[2]+6*2)//2, self.y+18/2)
        self.butSurf = pygame.Surface((self.label_rect[2]+6*2, 18))
        self.butRect = self.butSurf.get_rect()
        self.butRect.topleft = (self.x, self.y)
        butSurf = self.butSurf

        if self.butRect.collidepoint(pos):
            butSurf.fill(self.surfcolor)
            surface.blit(self.butSurf, (self.x, self.y))
            pygame.draw.rect(surface, BUTTON_HOVER, self.butRect, 0, 3)
            surface.blit(label, self.label_rect)
        else:
            butSurf.fill(self.surfcolor)
            surface.blit(self.butSurf, (self.x, self.y))
            pygame.draw.rect(surface, BUTTON_NONE, self.butRect, 0, 3)
            surface.blit(label, self.label_rect)
    
    def clicked():
        if self.clicked is True:
            return True
        else:
            return False


class checkbox:
    def __init__(self, surface, x, y, caption="", font_color=BLACK, checked=False):
        self.surface = surface
        self.x = x
        self.y = y
        self.caption = caption
        self.font_color = font_color
        
        self.checkbox_rect = pygame.Rect(self.x, self.y, 12, 12)

        self.checked = False

    def _draw_caption(self):
        self.font_surf = font2.render(self.caption, True, BLACK)
        w, h = font2.size(self.caption)
        self.font_pos = (self.x + 8 + 10, self.y -1)
        self.surface.blit(self.font_surf, self.font_pos)

    def _draw_checkbox(self):
        if self.is_checked():
            pygame.draw.rect(self.surface, GRAY, self.checkbox_rect)
            pygame.draw.rect(self.surface, BLACK, self.checkbox_rect, 1)
        elif not self.is_checked():
            pygame.draw.rect(self.surface, WHITE, self.checkbox_rect)
            pygame.draw.rect(self.surface, BLACK, self.checkbox_rect, 1)
        self._draw_caption()

    def update_checkbox(self):
        pos = pygame.mouse.get_pos()
        if self.checkbox_rect.collidepoint(pos):
            if not self.checked:
                self.checked = True
            else:
                self.checked = False

    def is_checked(self):
        if self.checked is True:
            return True
        else:
            return False

class textLabel:
    def __init__(self, x, y, win, text='', font=font2, color=BLACK):
        self.x = x
        self.y = y
        self.win = win
        self.font = font
        self.color = color
        self.text = self.font.render(text, True, self.color)
        self.text_rect = self.text.get_rect()
        self.text_rect.topleft = (self.x, self.y)

    def draw(self):
        self.win.blit(self.text, self.text_rect)


class textbox:
    pass

# class textbox:
#     def __init__(self, surface, x, y, length, height, text =''):
#         self.surface = surface
#         self.x = x
#         self.y = y
#         self.length = length
#         self.height = height
#         self.text = text
#         self.input_rect = pygame.Rect(self.x, self.y, self.length, self.height)

#         self.is_active = False

#     def draw(self, surface):
#         self.surface = surface
#         pygame.draw.rect(self.surface, WHITE, self.input_rect)
#         text_surface = font1.render(self.text, True, BLACK)
#         surface.blit(text_surface, (self.input_rect.x+5, self.input_rect.y+5))
#         #self.input_rect.w = max(100, 20)
    

#     def text_update(self):
#         while self.is_active:
#             clock.tick(framerate)
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.is_active = False
#                 if event.type == pygame.KEYDOWN:
#                     if event.key == pygame.K_ESCAPE:
#                         self.is_active = False
                
#                 if event.type == pygame.KEYDOWN:
#                     if event.key == pygame.K_BACKSPACE:
#                         self.draw()
#                     elif event.key == pygame.K_RETURN:
#                         print('hit enter')
#                         self.is_active = False
#                     elif event.key == pygame.K_ESCAPE:
                #         self.is_active = False
                # elif event.type == pygame.MOUSEBUTTONDOWN:
                #     if not self.input_rect.collidepoint(pygame.mouse.get_pos()):
                #         print('clicked off textbox')
                #         self.is_active = False
                # elif event.type == pygame.QUIT:
                #     self.is_active = False
                # elif event.type == pygame.KEYDOWN:
                #     self.text += event.unicode
                #     self.draw()
                

    


