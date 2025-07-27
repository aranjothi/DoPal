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
taskboardbackground = pygame.image.load("taskbackground.png")
taskboardbackground = pygame.transform.scale(taskboardbackground, (800,800))
crop_rect = pygame.Rect(0, 0, 475, 800)
taskboardcrop = taskboardbackground.subsurface(crop_rect)


# Color Palette
orange = (226, 140, 48)
darkorange = (230, 160, 48)
white = (255, 255, 255)
black = (0, 0, 0)
brown = (94, 59, 22)
scrollbg = (200, 115, 50)
scrollmain = (94, 59, 22)


# Fonts
subheaderfont = pygame.font.SysFont('marker felt', 28)  # None = default font, 36 = font size
bodyfont = pygame.font.SysFont(None, 24)

# Create initialized buttons
newtask = pygame.Rect(20, 10, 75, 30)
taskcard = pygame.Rect(20, 50, 400, 125)

# Other initializing stuff
running = True

global numcards, lastcardY, lasttextY, scrollY

lastcardY = 50
lasttextY = 80

numcards = 0

scrollY = 0

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
        elif event.type == pygame.MOUSEWHEEL:
            scrollY += event.y * -30

            # clamp scrolling
            maxscroll = max(0, (len(taskcards) - 4) * 140)
            scrollY = max(0, min(scrollY, maxscroll))

    # container for tasks, etc
    #pygame.draw.rect(screen, brown, (-20, -10, 525, 750), width=0, border_radius=12)

    screen.blit(taskboardcrop, (0, 0)) 


    # create task button
    pygame.draw.rect(screen, darkorange, newtask, width=0, border_radius=6)
    pygame.draw.rect(screen, black, newtask, width=2, border_radius=6)
    text_surface = bodyfont.render("+", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center = newtask.center)

    screen.blit(text_surface, text_rect)

    for i in taskcards:
        yoffset = 50 + ((i - 1) * 140) - scrollY
        if i == 1:
            yoffset = 50 - scrollY

        # no drawing if card off screen
        if yoffset + 140 < 0 or yoffset > height:
            continue

        pygame.draw.rect(screen, darkorange, (20, yoffset, 400, 125), width=0, border_radius=12)
        pygame.draw.rect(screen, black, (20, yoffset, 400, 125), width=3, border_radius=12)

        text_surface = subheaderfont.render("Task", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(60, yoffset + 30))
        screen.blit(text_surface, text_rect)


    # scroll bar
    total_height = len(taskcards) * 140
    view_height = 4 * 140
    scrollbar_x = 440
    scrollbar_y = 50
    scrollbar_width = 8
    scrollbar_height = 500

    if total_height > view_height:
        pygame.draw.rect(screen, scrollbg, (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        thumb_height = max(40, scrollbar_height * (view_height / total_height))
        scroll_ratio = scrollY / (total_height - view_height)
        thumb_y = scrollbar_y + scroll_ratio * (scrollbar_height - thumb_height)
        pygame.draw.rect(screen, scrollmain, (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=3)
    

    pygame.display.flip() # continuously update

pygame.quit()
sys.exit()