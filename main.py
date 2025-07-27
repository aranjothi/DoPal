import pygame
import sys

# Print statement stuff for my brain
#print(pygame.font.get_fonts())

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
subheaderfont = pygame.font.SysFont('marker felt', 28)  # None = default font, 36 = font size
bodyfont = pygame.font.SysFont(None, 24)

# Create initialized buttons
newtask = pygame.Rect(20, 15, 75, 30)
taskcard = pygame.Rect(20, 50, 400, 125)

# Other initializing stuff
running = True

global numcards, lastcardY, lasttextY

lastcardY = 50
lasttextY = 80

numcards = 0

taskcards = []

# Functions
def createnewcard():
    global numcards
    numcards += 1
    taskcards.append(numcards)

    return

# Game Loop
while running:

    screen.fill(orange)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if newtask.collidepoint(event.pos):
                createnewcard()
    
    # create task button
    pygame.draw.rect(screen, darkorange, newtask, width=0, border_radius=6)
    pygame.draw.rect(screen, black, newtask, width=2, border_radius=6)
    text_surface = bodyfont.render("+", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center = newtask.center)

    screen.blit(text_surface, text_rect)
    

    # # first task board
    # pygame.draw.rect(screen, darkorange, taskcard, width=0, border_radius=12) # (x, y, w, h)

    # pygame.draw.rect(screen, black, taskcard, width=3, border_radius=12) # (x, y, w, h)

    # text_surface = subheaderfont.render("Task", True, (0, 0, 0))  # text, antialias, color

    # text_rect = text_surface.get_rect(center=(60, 80)) # x + w, y + h, use // 2 for centering

    # screen.blit(text_surface, text_rect)


    for i in taskcards:
        if i == 1:
            pygame.draw.rect(screen, darkorange, (20, 50, 400, 125), width=0, border_radius=12) # (x, y, w, h)

            pygame.draw.rect(screen, black, (20, 50, 400, 125), width=3, border_radius=12) # (x, y, w, h)

            text_surface = subheaderfont.render("Task", True, (0, 0, 0))  # text, antialias, color

            text_rect = text_surface.get_rect(center=(60, 80)) # x + w, y + h, use // 2 for centering

            screen.blit(text_surface, text_rect)
        else:
            pygame.draw.rect(screen, darkorange, (20, 50 + ((i-1)*140), 400, 125), width=0, border_radius=12) # (x, y, w, h)

            pygame.draw.rect(screen, black, (20, 50 + ((i-1)*140), 400, 125), width=3, border_radius=12) # (x, y, w, h)

            text_surface = subheaderfont.render("Task", True, (0, 0, 0))  # text, antialias, color

            text_rect = text_surface.get_rect(center=(60, 80 + ((i-1)*140))) # x + w, y + h, use // 2 for centering

            screen.blit(text_surface, text_rect)

    

    pygame.display.flip() # continuously update

pygame.quit()
sys.exit()