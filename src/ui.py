import pygame, sys
#import pygame_textinput

pygame.init()
pygame.font.init()

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (245, 245, 245)

BUTTON_NONE = (180, 180, 180)
BUTTON_HOVER = (130, 130, 130)
font1 = pygame.font.SysFont('dejavusansmono', 10)
font2 = pygame.font.SysFont('dejavusansmono', 12)

class button:
    def __init__(self, x, y, font, label = ''):
        self.x = x
        self.y = y
        self.font = font
        self.label = label
        
    def draw(self, surface):
        self.surface = surface
        pos = pygame.mouse.get_pos()
        label = self.font.render(self.label, True, BLACK)
        self.label_rect = label.get_rect()
        self.label_rect.center = (self.x+(self.label_rect[2]+6*2)//2, self.y+20/2)
        self.butSurf = pygame.Surface((self.label_rect[2]+6*2, 20*1.2))
        self.butRect = self.butSurf.get_rect()
        self.butRect.topleft = (self.x, self.y)
        butSurf = self.butSurf

        if self.butRect.collidepoint(pos):
            butSurf.fill(BUTTON_HOVER)
            surface.blit(butSurf, (self.x, self.y))
            surface.blit(label, self.label_rect)
        else:
            butSurf.fill(BUTTON_NONE)
            surface.blit(self.butSurf, (self.x, self.y))
            surface.blit(label, self.label_rect)


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
        if self.checked:
            pygame.draw.rect(self.surface, GRAY, self.checkbox_rect)
            pygame.draw.rect(self.surface, BLACK, self.checkbox_rect, 1)
        elif not self.checked:
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
                

    


