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
defaultroom = pygame.image.load("defaultroom.png")
defaultroom = pygame.transform.scale(defaultroom, (400,600))


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
task_texts = []
selected_task_index = None

# Animation variables
card_animations = {}  # Store animation data for each card
animation_speed = 0.15  # Animation speed factor

# Hover effects
hovered_card = None
hovered_newtask = False

# Functions
def createnewcard():
    global numcards
    numcards += 1
    taskcards.append(numcards)
    task_texts.append("Enter Task Title...")
    
    # Initialize animation for new card
    card_animations[numcards] = {
        'y_offset': -125,  # Start above screen
        'alpha': 0,        # Start fully transparent
        'target_y': 50 + ((numcards - 1) * 140) - scrollY
    }

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
            else:
                selected_task_index = None  

                for idx, i in enumerate(taskcards):
                    yoffset = 50 + ((i - 1) * 140) - scrollY
                    if i == 1:
                        yoffset = 50 - scrollY

                    card_rect = pygame.Rect(20, yoffset, 400, 125)
                    if card_rect.collidepoint(event.pos):
                        selected_task_index = idx
                        break
        elif event.type == pygame.KEYDOWN:
            if selected_task_index is not None:
                if event.key == pygame.K_BACKSPACE:
                    task_texts[selected_task_index] = task_texts[selected_task_index][:-1]
                elif event.key == pygame.K_RETURN:
                    selected_task_index = None
                else:
                    if task_texts[selected_task_index] == "Enter Task Title...":
                        task_texts[selected_task_index] = ""
                    task_texts[selected_task_index] += event.unicode
        elif event.type == pygame.MOUSEWHEEL:
            scrollY += event.y * -30

            # clamp scrolling - create a scrollable viewport
            scroll_area_start = 50  # Cards start here
            scroll_area_height = 400  # Available height for scrolling (leaves space for button)
            maxscroll = max(0, (len(taskcards) * 140) - scroll_area_height)
            scrollY = max(0, min(scrollY, maxscroll))

    # Update hover states
    mouse_pos = pygame.mouse.get_pos()
    hovered_newtask = newtask.collidepoint(mouse_pos)
    
    hovered_card = None
    for idx, i in enumerate(taskcards):
        yoffset = 50 + ((i - 1) * 140) - scrollY  # Cards start at Y=50
        if i == 1:
            yoffset = 50 - scrollY

        card_rect = pygame.Rect(20, yoffset, 400, 125)
        if card_rect.collidepoint(mouse_pos):
            hovered_card = i
            break

    # container for tasks, etc
    #pygame.draw.rect(screen, brown, (475, 0, 325, 600), width=0, border_radius=0)
    screen.blit(defaultroom, (475, 0))
    screen.blit(taskboardcrop, (0, 0)) 

    # border between room and taskboard
    pygame.draw.rect(screen, brown, (475, 0, 3, 600), width=0, border_radius=0)

    # Update animations
    for card_id in card_animations:
        anim = card_animations[card_id]
        target_y = 50 + ((card_id - 1) * 140) - scrollY  # Cards start at Y=50
        
        # Animate position
        if abs(anim['y_offset'] - target_y) > 1:
            anim['y_offset'] += (target_y - anim['y_offset']) * animation_speed
        else:
            anim['y_offset'] = target_y
            
        # Animate alpha (fade in)
        if anim['alpha'] < 255:
            anim['alpha'] += 15
        else:
            anim['alpha'] = 255

    # create task button
    button_color = orange if hovered_newtask else darkorange
    pygame.draw.rect(screen, button_color, newtask, width=0, border_radius=6)
    pygame.draw.rect(screen, black, newtask, width=2, border_radius=6)
    text_surface = bodyfont.render("+", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center = newtask.center)

    screen.blit(text_surface, text_rect)

    # Set clipping rectangle for scroll viewport
    scroll_clip = pygame.Rect(0, 50, 475, 400)  # Clip to scroll area
    screen.set_clip(scroll_clip)

    for i in taskcards:
        # animations if available
        if i in card_animations:
            yoffset = card_animations[i]['y_offset']
            alpha = card_animations[i]['alpha']
        else:
            yoffset = 50 + ((i - 1) * 140) - scrollY  # Cards start at Y=50
            if i == 1:
                yoffset = 50 - scrollY
            alpha = 255

        # Create card surface with transparency
        card_surface = pygame.Surface((400, 125), pygame.SRCALPHA)
        
        # Add shadow effect for hovered cards
        if i == hovered_card:
            shadow_surface = pygame.Surface((400, 125), pygame.SRCALPHA)
            shadow_color = (*black, 50)  # Semi-transparent shadow
            pygame.draw.rect(shadow_surface, shadow_color, (4, 4, 400, 125), width=0, border_radius=12)
            screen.blit(shadow_surface, (16, yoffset - 4))
        
        # Draw card background with alpha
        card_color = (*darkorange, alpha)
        pygame.draw.rect(card_surface, card_color, (0, 0, 400, 125), width=0, border_radius=12)
        pygame.draw.rect(card_surface, (*black, alpha), (0, 0, 400, 125), width=3, border_radius=12)
        
        # Blit card to screen
        screen.blit(card_surface, (20, yoffset))

        idx = i - 1
        task_title = task_texts[idx]
        is_selected = (selected_task_index == idx)

        # placeholder text
        if not task_title or task_title == "Enter Task Title...":
            if is_selected:
                task_title = "|"  
            else:
                task_title = "Enter Task Title..."  
            color = (120, 80, 40)  # lighter brown for placeholder
        else:
            if is_selected:
                task_title += "|"  
            color = (0, 0, 0)

        # Render text with alpha
        text_surface = subheaderfont.render(task_title, True, color)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(topleft=(40, yoffset + 20))
        screen.blit(text_surface, text_rect)

    # Remove clipping rectangle
    screen.set_clip(None)

    # scroll bar
    total_height = len(taskcards) * 140
    view_height = 400  # Match the scroll viewport height
    scrollbar_x = 440
    scrollbar_y = 50  # Start at same Y as cards
    scrollbar_width = 8
    scrollbar_height = 400  # Match the scroll viewport height

    if total_height > view_height:
        pygame.draw.rect(screen, scrollbg, (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        thumb_height = max(40, scrollbar_height * (view_height / total_height))
        scroll_ratio = scrollY / (total_height - view_height)
        thumb_y = scrollbar_y + scroll_ratio * (scrollbar_height - thumb_height)
        pygame.draw.rect(screen, scrollmain, (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=3)
    

    pygame.display.flip() # continuously update

pygame.quit()
sys.exit()