import pygame
import sys

# Setup
pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("DoPal")

# Images
# taskboard = pygame.image.load("taskboard.png")
# taskboard = pygame.transform.scale(taskboard, (250,250))
# taskboard = pygame.transform.rotate(taskboard, 5)

# Color Palette
orange = (226, 140, 48)
darkorange = (230, 160, 48)
white = (255, 255, 255)
black = (0, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 36)  # None = default font, 36 = font size

running = True

# Game Loop
while running:

    screen.fill(orange)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # task boards
    pygame.draw.rect(screen, darkorange, (200, 0, 400, 150), width=0, border_radius=12) # (x, y, w, h)

    pygame.draw.rect(screen, black, (200, 0, 400, 150), width=3, border_radius=12) # (x, y, w, h)

    text_surface = font.render("Task", True, (0, 0, 0))  # text, antialias, color

    text_rect = text_surface.get_rect(center=(200 + 150 // 2, 0 + 150 // 2))

    screen.blit(text_surface, text_rect)



    

    pygame.display.flip() # continuously update

pygame.quit()
sys.exit()