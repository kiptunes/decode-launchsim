import pygame
pygame.init()
pygame.font.init()
font1 = pygame.font.SysFont('dejavusansmono', 10)
text = font1.render('hello', True, (0, 0, 0))
win = pygame.display.set_mode((300, 200))
visible = True
if visible:
    text.set_alpha(100)
    for i in range(100):
        text.set_alpha(100-i)
    visible = False