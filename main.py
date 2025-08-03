import pygame
import sys
import time

#print(pygame.font.get_fonts())

# Setup
pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("DoPal")

# Images
board = pygame.image.load("board.png")
board = pygame.transform.scale(board, (250,175))
board = pygame.transform.rotate(board, 5)
taskboardbackground = pygame.image.load("taskbackground.png")
taskboardbackground = pygame.transform.scale(taskboardbackground, (800,800))
crop_rect = pygame.Rect(0, 0, 475, 800)
taskboardcrop = taskboardbackground.subsurface(crop_rect)
defaultroom = pygame.image.load("defaultroom.png")
defaultroom = pygame.transform.scale(defaultroom, (400,600))
trash_icon = pygame.image.load("defaulttrash.png")
trash_icon = pygame.transform.scale(trash_icon, (20, 25))
defaulttreat = pygame.image.load("defaulttreat.png")
defaulttreat = pygame.transform.scale(defaulttreat, (60, 60))
check_icon = pygame.image.load("defaultcheck.png")
check_icon = pygame.transform.scale(check_icon, (23.5, 25))
dog = pygame.image.load("defaultdog.png")
dog = pygame.transform.scale(dog, (200, 300))


# Color Palette
orange = (226, 140, 48)
darkorange = (230, 160, 48)
white = (255, 255, 255)
black = (0, 0, 0)
brown = (94, 59, 22)
scrollbg = (200, 115, 50)
scrollmain = (94, 59, 22)


# Fonts
headerfont = pygame.font.SysFont('marker felt', 34)
subheaderfont = pygame.font.SysFont('marker felt', 28)  
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
numtreats = 0

scrollY = 0

taskcards = []
task_texts = []
selected_task_index = None
selected_textbox_index = None
cursor_position = 0
selection_start = 0
cursor_blink_time = 0

# Key repeat tracking
backspace_repeat_time = 0
backspace_initial_delay = 60
backspace_repeat_delay = 30

# Animation variables
card_animations = {}
animation_speed = 0.15

# Hover effects
hovered_card = None
hovered_newtask = False

# Cursor blink tracking
previous_selected_textbox = None
frame_counter = 0
cursor_blink_start = time.time()

def createnewcard():
    global numcards
    numcards += 1
    taskcards.append(numcards)
    task_texts.append("Task Title...")
    
    card_animations[numcards] = {
        'y_offset': -125,
        'alpha': 0,
        'target_y': 50 + ((numcards - 1) * 140) - scrollY
    }

    return

def delete_task_card(card_index):
    global numcards, taskcards, task_texts
    
    if 0 <= card_index < len(taskcards):
        del taskcards[card_index]
        del task_texts[card_index]
        
        taskcards = list(range(1, len(taskcards) + 1))
        
        for card_id in list(card_animations.keys()):
            if card_id > len(taskcards):
                del card_animations[card_id]
        
        numcards = len(taskcards)
        
        global selected_task_index
        if selected_task_index == card_index:
            selected_task_index = None
        elif selected_task_index is not None and selected_task_index > card_index:
            selected_task_index -= 1
            
        global selected_textbox_index
        if selected_textbox_index == card_index:
            selected_textbox_index = None
            cursor_position = 0
        elif selected_textbox_index is not None and selected_textbox_index > card_index:
            selected_textbox_index -= 1

def complete_task_card(card_index):
    global numcards, taskcards, task_texts, numtreats
    
    if 0 <= card_index < len(taskcards):
        numtreats += 1
        
        del taskcards[card_index]
        del task_texts[card_index]
        
        taskcards = list(range(1, len(taskcards) + 1))
        
        for card_id in list(card_animations.keys()):
            if card_id > len(taskcards):
                del card_animations[card_id]
        
        numcards = len(taskcards)
        
        global selected_task_index, selected_textbox_index
        if selected_task_index == card_index:
            selected_task_index = None
        elif selected_task_index is not None and selected_task_index > card_index:
            selected_task_index -= 1
            
        if selected_textbox_index == card_index:
            selected_textbox_index = None
            cursor_position = 0
        elif selected_textbox_index is not None and selected_textbox_index > card_index:
            selected_textbox_index -= 1

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
                trash_clicked = False
                check_clicked = False
                textbox_clicked = False
                
                for idx, i in enumerate(taskcards):
                    yoffset = 50 + ((i - 1) * 140) - scrollY
                    if i == 1:
                        yoffset = 50 - scrollY

                    check_rect = pygame.Rect(340, yoffset + 15, 30, 30)
                    if check_rect.collidepoint(event.pos):
                        complete_task_card(idx)
                        check_clicked = True
                        break

                    trash_rect = pygame.Rect(375, yoffset + 15, 30, 30)
                    if trash_rect.collidepoint(event.pos):
                        delete_task_card(idx)
                        trash_clicked = True
                        break
                        
                    textbox_rect = pygame.Rect(20, yoffset + 20, 285, 35)
                    if textbox_rect.collidepoint(event.pos):
                        selected_task_index = idx
                        selected_textbox_index = idx
                        cursor_position = len(task_texts[idx])
                        textbox_clicked = True
                        break
                
                if not trash_clicked and not check_clicked and not textbox_clicked:
                    selected_task_index = None
                    selected_textbox_index = None
                    cursor_position = 0

                    for idx, i in enumerate(taskcards):
                        yoffset = 50 + ((i - 1) * 140) - scrollY
                        if i == 1:
                            yoffset = 50 - scrollY

                        card_rect = pygame.Rect(20, yoffset, 400, 125)
                        if card_rect.collidepoint(event.pos):
                            if not textbox_rect.collidepoint(event.pos):
                                selected_task_index = idx
                                selected_textbox_index = None
                            break
        elif event.type == pygame.KEYDOWN:
            if selected_textbox_index is not None:
                if event.key == pygame.K_BACKSPACE:
                    if task_texts[selected_textbox_index] == "Task Title...":
                        task_texts[selected_textbox_index] = ""
                        cursor_position = 0
                    elif cursor_position > 0:
                        task_texts[selected_textbox_index] = (
                            task_texts[selected_textbox_index][:cursor_position - 1] + 
                            task_texts[selected_textbox_index][cursor_position:]
                        )
                        cursor_position -= 1
                        backspace_repeat_time = 0
                elif event.key == pygame.K_RETURN:
                    selected_textbox_index = None
                    cursor_position = 0
                elif event.key == pygame.K_LEFT:
                    cursor_position = max(0, cursor_position - 1)
                elif event.key == pygame.K_RIGHT:
                    cursor_position = min(len(task_texts[selected_textbox_index]), cursor_position + 3)
                else:
                    if task_texts[selected_textbox_index] == "Task Title...":
                        task_texts[selected_textbox_index] = ""
                        cursor_position = 0
                    
                    task_texts[selected_textbox_index] = (
                        task_texts[selected_textbox_index][:cursor_position] + 
                        event.unicode + 
                        task_texts[selected_textbox_index][cursor_position:]
                    )
                    cursor_position += 1
        elif event.type == pygame.MOUSEWHEEL:
            scrollY += event.y * -30

            scroll_area_start = 50
            scroll_area_height = 400
            maxscroll = max(0, (len(taskcards) * 140) - scroll_area_height)
            scrollY = max(0, min(scrollY, maxscroll))

    mouse_pos = pygame.mouse.get_pos()
    hovered_newtask = newtask.collidepoint(mouse_pos)
    
    hovered_card = None
    for idx, i in enumerate(taskcards):
        yoffset = 50 + ((i - 1) * 140) - scrollY
        if i == 1:
            yoffset = 50 - scrollY

        card_rect = pygame.Rect(20, yoffset, 400, 125)
        if card_rect.collidepoint(mouse_pos):
            hovered_card = i
            break

    if selected_textbox_index is not None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            backspace_repeat_time += 1
            if backspace_repeat_time > backspace_initial_delay:
                if (backspace_repeat_time - backspace_initial_delay) % backspace_repeat_delay == 0:
                    if cursor_position > 0:
                        task_texts[selected_textbox_index] = (
                            task_texts[selected_textbox_index][:cursor_position - 1] + 
                            task_texts[selected_textbox_index][cursor_position:]
                        )
                        cursor_position -= 1
        else:
            backspace_repeat_time = 0
    
    frame_counter += 1

    screen.blit(defaultroom, (475, 0))
    screen.blit(taskboardcrop, (0, 0)) 

    pygame.draw.rect(screen, brown, (475, 0, 3, 600), width=0, border_radius=0)

    for card_id in card_animations:
        anim = card_animations[card_id]
        target_y = 50 + ((card_id - 1) * 140) - scrollY
        
        dynamic_speed = animation_speed / len(taskcards)
        
        if abs(anim['y_offset'] - target_y) > 1:
            anim['y_offset'] += (target_y - anim['y_offset']) * dynamic_speed
        else:
            anim['y_offset'] = target_y
            
        if anim['alpha'] < 255:
            anim['alpha'] += 15
        else:
            anim['alpha'] = 255

    button_color = orange if hovered_newtask else darkorange
    pygame.draw.rect(screen, button_color, newtask, width=0, border_radius=6)
    pygame.draw.rect(screen, black, newtask, width=2, border_radius=6)
    text_surface = bodyfont.render("+", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center = newtask.center)

    screen.blit(text_surface, text_rect)

    numtreatsholder = pygame.Rect(700, 10, 60, 60)
    text_surface = headerfont.render(str(numtreats), True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.right = (numtreatsholder.right - 25)
    text_rect.top = (numtreatsholder.top + 12.5)

    screen.blit(text_surface, text_rect)
    screen.blit(defaulttreat, (735, 10))

    scroll_clip = pygame.Rect(0, 50, 475, 400)
    screen.set_clip(scroll_clip)

    for i in taskcards:
        if i in card_animations:
            yoffset = card_animations[i]['y_offset']
            alpha = card_animations[i]['alpha']
        else:
            yoffset = 50 + ((i - 1) * 140) - scrollY
            if i == 1:
                yoffset = 50 - scrollY
            alpha = 255

        card_surface = pygame.Surface((400, 125), pygame.SRCALPHA)
        
        if i == hovered_card:
            shadow_surface = pygame.Surface((400, 125), pygame.SRCALPHA)
            shadow_color = (*black, 50)
            pygame.draw.rect(shadow_surface, shadow_color, (4, 4, 400, 125), width=0, border_radius=12)
            screen.blit(shadow_surface, (16, yoffset - 4))
        
        card_color = (*darkorange, alpha)
        pygame.draw.rect(card_surface, card_color, (0, 0, 400, 125), width=0, border_radius=12)
        pygame.draw.rect(card_surface, (*black, alpha), (0, 0, 400, 125), width=3, border_radius=12)
        
        screen.blit(card_surface, (20, yoffset))

        idx = i - 1
        task_title = task_texts[idx]
        is_selected = (selected_textbox_index == idx)

        if not task_title or task_title == "Task Title...":
            if is_selected:
                task_title = "|"  
            else:
                task_title = "Task Title..."  
            color = (120, 80, 40)
        else:
            if is_selected:
                current_time = time.time()
                if int(current_time * 2) % 2 == 0:
                    task_title = (
                        task_title[:cursor_position] + 
                        "|" + 
                        task_title[cursor_position:]
                    )
            color = (0, 0, 0)

        # task title
        text_surface = subheaderfont.render(task_title, True, color)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(topleft=(45, yoffset + 22.5))
        
        if is_selected:
            textbox_bg = pygame.Surface((285, 35), pygame.SRCALPHA)
            textbox_bg.fill((255, 255, 255, 100))
            screen.blit(textbox_bg, (40, yoffset + 20))
            pygame.draw.rect(screen, (*black, alpha), (40, yoffset + 20, 285, 35), width=2, border_radius=4)
        
        screen.blit(text_surface, text_rect)

        trash_x = 380  
        trash_y = yoffset + 21  
        screen.blit(trash_icon, (trash_x, trash_y))

        check_x = 345
        check_y = yoffset + 22
        screen.blit(check_icon, (check_x, check_y))

    screen.set_clip(None)

    # dog stuff
    screen.blit(dog, (550, 300))
    screen.blit(board, (465, -10))

    total_height = len(taskcards) * 140
    view_height = 400
    scrollbar_x = 440
    scrollbar_y = 50
    scrollbar_width = 8
    scrollbar_height = 400

    if total_height > view_height:
        pygame.draw.rect(screen, scrollbg, (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        thumb_height = max(40, scrollbar_height * (view_height / total_height))
        scroll_ratio = scrollY / (total_height - view_height)
        thumb_y = scrollbar_y + scroll_ratio * (scrollbar_height - thumb_height)
        pygame.draw.rect(screen, scrollmain, (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=3)
    

    pygame.display.flip()

pygame.quit()
sys.exit()