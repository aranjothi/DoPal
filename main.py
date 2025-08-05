import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import sys
import time
import math
import sqlite3

#print(pygame.font.get_fonts())


# setup
pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("DoPal")

# images
board = pygame.image.load("board.png")
board = pygame.transform.smoothscale(board, (275,200))
button = pygame.image.load("button.png")
button = pygame.transform.smoothscale(button, (250,175))
heart = pygame.image.load("healthheart.png")
heart = pygame.transform.smoothscale(heart, (45,32.5))
collar = pygame.image.load("collar.png")
collar = pygame.transform.smoothscale(collar, (32.5,32.5))
exp = pygame.image.load("exp.png")
exp = pygame.transform.smoothscale(exp, (45,32.5))
taskboardbackground = pygame.image.load("taskbackground.png")
taskboardbackground = pygame.transform.smoothscale(taskboardbackground, (800,800))
crop_rect = pygame.Rect(0, 0, 475, 800)
taskboardcrop = taskboardbackground.subsurface(crop_rect)
defaultroom = pygame.image.load("defaultroom.png")
defaultroom = pygame.transform.smoothscale(defaultroom, (400,600))
trash_icon = pygame.image.load("defaulttrash.png")
trash_icon = pygame.transform.smoothscale(trash_icon, (20, 25))
defaulttreat = pygame.image.load("defaulttreat.png")
defaulttreat = pygame.transform.smoothscale(defaulttreat, (60, 60))
check_icon = pygame.image.load("defaultcheck.png")
check_icon = pygame.transform.smoothscale(check_icon, (23.5, 25))
dog = pygame.image.load("defaultdoghappy.png")
dog = pygame.transform.smoothscale(dog, (250, 250))


# color palette
orange = (226, 140, 48)
darkorange = (230, 160, 48)
white = (255, 255, 255)
black = (0, 0, 0)
brown = (94, 59, 22)
scrollbg = (200, 115, 50)
scrollmain = (94, 59, 22)
taskcard_color = (212, 139, 59)  # #d48b3b


# fonts
headerfont = pygame.font.SysFont('marker felt', 34)
subheaderfont = pygame.font.SysFont('marker felt', 28)  
bodyfont = pygame.font.SysFont(None, 24)
descfont = pygame.font.SysFont('marker felt', 18)
levelfont = pygame.font.SysFont('marker felt', 14)
namefont = pygame.font.SysFont('marker felt', 20)

# create initialized buttons
newtask = pygame.Rect(20, 10, 75, 30)
taskcard = pygame.Rect(20, 50, 400, 125)

# other initializing stuff
running = True

global numcards, lastcardY, lasttextY, scrollY

lastcardY = 50
lasttextY = 80

numcards = 0
numtreats = 0

scrollY = 0

# health bar variables
dog_health = 100
dog_max_health = 100
health_bar_width = 120
health_bar_height = 10
health_decrease_rate = 1  # hp per 5 seconds
last_health_update = time.time()

# experience system variables
player_exp = 0
player_level = 0
exp_to_next_level = 50
exp_bar_width = 120
exp_bar_height = 10

# experience bar animation variables
displayed_exp = 0  # the experience value shown in the bar
exp_animation_speed = 0.1  # how fast the bar fills up

# dog name variables
dog_name = "Rufus"
selected_name_box = False
name_cursor_position = 0
name_cursor_blink_time = 0

# name box backspace repeat tracking
name_backspace_repeat_time = 0

# treat dragging variables
dragging_treat = False
dragged_treat_pos = (0, 0)
dragged_treat_alpha = 255
dragged_treat_scale = 1.0
treat_click_pos = (0, 0)
treat_vanishing = False
dragged_treat_zindex = 10000

taskcards = []
task_texts = []
task_descriptions = []
selected_task_index = None
selected_textbox_index = None
selected_description_index = None
cursor_position = 0
selection_start = 0
cursor_blink_time = 0

# key repeat tracking
backspace_repeat_time = 0
backspace_initial_delay = 50
backspace_repeat_delay = 10

# animation variables
card_animations = {}
animation_speed = 0.15

# hover effects
hovered_card = None
hovered_newtask = False

# cursor blink tracking
previous_selected_textbox = None
frame_counter = 0
cursor_blink_start = time.time()

# new task cooldown variables
new_task_cooldown = 0
new_task_cooldown_duration = 5  # seconds
new_task_cooldown_start = 0

def createnewcard():
    global numcards, new_task_cooldown, new_task_cooldown_start
    numcards += 1
    taskcards.append(numcards)
    task_texts.append("Task Title...")
    task_descriptions.append("Task Description...")
    
    # start cooldown timer with actual time
    new_task_cooldown_start = time.time()
    new_task_cooldown = new_task_cooldown_duration
    
    card_animations[numcards] = {
        'y_offset': -125,
        'alpha': 0,
        'target_y': 50 + ((numcards - 1) * 140) - scrollY
    }

    return

# function to further help with retaining image quality when scaling
def smoothscaleprogressive(image, size):

    current_size = image.get_size()
    target_width, target_height = size

    if current_size[0] > target_width * 2 or current_size[1] > target_height * 2:
        intermediate_width = max(target_width, current_size[0] // 2)
        intermediate_height = max(target_height, current_size[1] // 2)
        
        intermediate = pygame.transform.smoothscale(image, (intermediate_width, intermediate_height))
        
        return pygame.transform.smoothscale(intermediate, size)
    else:
        return pygame.transform.smoothscale(image, size)

def delete_task_card(card_index):
    global numcards, taskcards, task_texts
    
    if 0 <= card_index < len(taskcards):
        del taskcards[card_index]
        del task_texts[card_index]
        del task_descriptions[card_index]
        
        taskcards = list(range(1, len(taskcards) + 1))
        
        for card_id in list(card_animations.keys()):
            if card_id > len(taskcards):
                del card_animations[card_id]
        
        numcards = len(taskcards)
        
        global selected_task_index, selected_textbox_index, selected_description_index
        if selected_task_index == card_index:
            selected_task_index = None
        elif selected_task_index is not None and selected_task_index > card_index:
            selected_task_index -= 1
            
        if selected_textbox_index == card_index:
            selected_textbox_index = None
            cursor_position = 0
        elif selected_textbox_index is not None and selected_textbox_index > card_index:
            selected_textbox_index -= 1
            
        if selected_description_index == card_index:
            selected_description_index = None
            cursor_position = 0
        elif selected_description_index is not None and selected_description_index > card_index:
            selected_description_index -= 1

def complete_task_card(card_index):
    global numcards, taskcards, task_texts, numtreats
    
    if 0 <= card_index < len(taskcards):
        numtreats += 1
        
        del taskcards[card_index]
        del task_texts[card_index]
        del task_descriptions[card_index]
        
        taskcards = list(range(1, len(taskcards) + 1))
        
        for card_id in list(card_animations.keys()):
            if card_id > len(taskcards):
                del card_animations[card_id]
        
        numcards = len(taskcards)
        
        global selected_task_index, selected_textbox_index, selected_description_index
        if selected_task_index == card_index:
            selected_task_index = None
        elif selected_task_index is not None and selected_task_index > card_index:
            selected_task_index -= 1
            
        if selected_textbox_index == card_index:
            selected_textbox_index = None
            cursor_position = 0
        elif selected_textbox_index is not None and selected_textbox_index > card_index:
            selected_textbox_index -= 1
            
        if selected_description_index == card_index:
            selected_description_index = None
            cursor_position = 0
        elif selected_description_index is not None and selected_description_index > card_index:
            selected_description_index -= 1
        
        save_game_data()  # auto-save when completing tasks

def clip_text_to_width(text, font, max_width):
    if font.size(text)[0] <= max_width:
        return text
    
    # Start with the full text and work backwards
    for i in range(len(text), 0, -1):
        clipped_text = text[:i] + "..."
        if font.size(clipped_text)[0] <= max_width:
            return clipped_text
    
    # If even one character is too wide, return "..."
    return "..."

def gain_experience(amount):
    global player_exp, player_level, exp_to_next_level
    
    player_exp += amount
    
    # check for level up
    while player_exp >= exp_to_next_level:
        player_exp -= exp_to_next_level
        player_level += 1
        exp_to_next_level *= 2  # double the experience required for next level

def save_game_data():
    try:
        conn = sqlite3.connect('dopal.db')
        cursor = conn.cursor()
        
        # clear existing data
        cursor.execute('DELETE FROM game_state')
        cursor.execute('DELETE FROM tasks')
        
        # save game state
        cursor.execute('''
            INSERT INTO game_state VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1, numcards, numtreats, dog_health, player_exp, 
              player_level, exp_to_next_level, dog_name, scrollY))
        
        # save tasks
        for i, (task_id, title, desc) in enumerate(zip(taskcards, task_texts, task_descriptions)):
            cursor.execute('''
                INSERT INTO tasks VALUES (?, ?, ?, ?)
            ''', (i+1, task_id, title, desc))
        
        conn.commit()
        conn.close()
        print("game data saved successfully!")
    except Exception as e:
        print(f"error saving game data: {e}")

def create_database():
    try:
        conn = sqlite3.connect('dopal.db')
        cursor = conn.cursor()
        
        # create game_state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY,
                numcards INTEGER,
                numtreats INTEGER,
                dog_health INTEGER,
                player_exp INTEGER,
                player_level INTEGER,
                exp_to_next_level INTEGER,
                dog_name TEXT,
                scroll_y INTEGER
            )
        ''')
        
        # create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_id INTEGER,
                title TEXT,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("database created successfully!")
    except Exception as e:
        print(f"error creating database: {e}")

def load_game_data():
    global taskcards, task_texts, task_descriptions, numcards, numtreats
    global dog_health, player_exp, player_level, exp_to_next_level, dog_name, scrollY
    
    try:
        conn = sqlite3.connect('dopal.db')
        cursor = conn.cursor()
        
        # load game state
        cursor.execute('SELECT * FROM game_state WHERE id = 1')
        row = cursor.fetchone()
        if row:
            numcards = row[1]
            numtreats = row[2]
            dog_health = row[3]
            player_exp = row[4]
            player_level = row[5]
            exp_to_next_level = row[6]
            dog_name = row[7]
            scrollY = row[8]
        
        # load tasks
        cursor.execute('SELECT task_id, title, description FROM tasks ORDER BY id')
        tasks = cursor.fetchall()
        
        taskcards = [task[0] for task in tasks]
        task_texts = [task[1] for task in tasks]
        task_descriptions = [task[2] for task in tasks]
        
        conn.close()
        print("game data loaded successfully!")
        
    except Exception as e:
        print(f"error loading game data: {e}")
        # start with default values if loading fails

# Game Loop
create_database() 
load_game_data() 

while running:

    screen.fill(orange)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game_data()  # save before closing
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if newtask.collidepoint(event.pos) and new_task_cooldown <= 0:
                createnewcard()
            else:
                # check if clicking on treat
                treat_rect = pygame.Rect(735, 10, 60, 60)
                if treat_rect.collidepoint(event.pos) and numtreats > 0:
                    dragging_treat = True
                    treat_click_pos = event.pos
                    dragged_treat_pos = event.pos
                    treat_vanishing = False
                    dragged_treat_alpha = 255
                    dragged_treat_scale = 1.0
                else:
                    # check if clicking on name box
                    name_box_rect = pygame.Rect(collar_x + 45, collar_y, 100, 25)
                    if name_box_rect.collidepoint(event.pos):
                        selected_name_box = True
                        name_cursor_position = len(dog_name)
                        selected_textbox_index = None  # deselect task textbox
                        selected_description_index = None  # deselect description textbox
                        cursor_position = 0
                    else:
                        selected_name_box = False
                        name_cursor_position = 0
                    
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
                            selected_description_index = None  # deselect description textbox
                            selected_name_box = False  # deselect name box
                            cursor_position = len(task_texts[idx])
                            textbox_clicked = True
                            break
                        
                        description_rect = pygame.Rect(20, yoffset + 65, 285, 24)
                        if description_rect.collidepoint(event.pos):
                            selected_task_index = idx
                            selected_description_index = idx
                            selected_textbox_index = None  # deselect title textbox
                            selected_name_box = False  # deselect name box
                            cursor_position = len(task_descriptions[idx])
                            textbox_clicked = True
                            break
                    
                    if not trash_clicked and not check_clicked and not textbox_clicked:
                        selected_task_index = None
                        selected_textbox_index = None
                        selected_description_index = None
                        cursor_position = 0

                        for idx, i in enumerate(taskcards):
                            yoffset = 50 + ((i - 1) * 140) - scrollY
                            if i == 1:
                                yoffset = 50 - scrollY

                            card_rect = pygame.Rect(20, yoffset, 400, 125)
                            if card_rect.collidepoint(event.pos):
                                if not textbox_rect.collidepoint(event.pos) and not description_rect.collidepoint(event.pos):
                                    selected_task_index = idx
                                    selected_textbox_index = None
                                    selected_description_index = None
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
            elif selected_description_index is not None:
                if event.key == pygame.K_BACKSPACE:
                    if task_descriptions[selected_description_index] == "Task Description...":
                        task_descriptions[selected_description_index] = ""
                        cursor_position = 0
                    elif cursor_position > 0:
                        task_descriptions[selected_description_index] = (
                            task_descriptions[selected_description_index][:cursor_position - 1] + 
                            task_descriptions[selected_description_index][cursor_position:]
                        )
                        cursor_position -= 1
                        backspace_repeat_time = 0
                elif event.key == pygame.K_RETURN:
                    selected_description_index = None
                    cursor_position = 0
                elif event.key == pygame.K_LEFT:
                    cursor_position = max(0, cursor_position - 1)
                elif event.key == pygame.K_RIGHT:
                    cursor_position = min(len(task_descriptions[selected_description_index]), cursor_position + 3)
                else:
                    if task_descriptions[selected_description_index] == "Task Description...":
                        task_descriptions[selected_description_index] = ""
                        cursor_position = 0
                    
                    task_descriptions[selected_description_index] = (
                        task_descriptions[selected_description_index][:cursor_position] + 
                        event.unicode + 
                        task_descriptions[selected_description_index][cursor_position:]
                    )
                    cursor_position += 1
            elif selected_name_box:
                if event.key == pygame.K_BACKSPACE:
                    if name_cursor_position > 0:
                        dog_name = dog_name[:name_cursor_position - 1] + dog_name[name_cursor_position:]
                        name_cursor_position -= 1
                        name_backspace_repeat_time = 0
                elif event.key == pygame.K_RETURN:
                    selected_name_box = False
                    name_cursor_position = 0
                elif event.key == pygame.K_LEFT:
                    name_cursor_position = max(0, name_cursor_position - 1)
                elif event.key == pygame.K_RIGHT:
                    name_cursor_position = min(len(dog_name), name_cursor_position + 1)
                else:
                    dog_name = dog_name[:name_cursor_position] + event.unicode + dog_name[name_cursor_position:]
                    name_cursor_position += 1
        elif event.type == pygame.MOUSEMOTION:
            if dragging_treat:
                dragged_treat_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging_treat:
                # Check if treat is dropped on dog
                dog_rect = pygame.Rect(510, 340, 250, 250)  # Approximate dog area
                if dog_rect.collidepoint(event.pos):
                    # feed the dog
                    dog_health = min(dog_max_health, dog_health + 20)
                    numtreats -= 1
                    
                    # gain random experience (30-60)
                    import random
                    exp_gained = random.randint(30, 60)
                    gain_experience(exp_gained)
                    
                    save_game_data()  # auto-save when feeding dog
                else:
                    # Start vanishing animation
                    treat_vanishing = True
                dragging_treat = False
        elif event.type == pygame.MOUSEWHEEL:
            scrollY += event.y * -30

            scroll_area_start = 50
            scroll_area_height = 400
            maxscroll = max(0, (len(taskcards) * 140) - scroll_area_height)
            scrollY = max(0, min(scrollY, maxscroll))

    # only check mouse position for hover effects, not for selection
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
    
    # Name box backspace repeat
    if selected_name_box:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            name_backspace_repeat_time += 1
            if name_backspace_repeat_time > backspace_initial_delay:
                if (name_backspace_repeat_time - backspace_initial_delay) % backspace_repeat_delay == 0:
                    if name_cursor_position > 0:
                        dog_name = dog_name[:name_cursor_position - 1] + dog_name[name_cursor_position:]
                        name_cursor_position -= 1
        else:
            name_backspace_repeat_time = 0
    
    # Description textbox backspace repeat
    if selected_description_index is not None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            backspace_repeat_time += 1
            if backspace_repeat_time > backspace_initial_delay:
                if (backspace_repeat_time - backspace_initial_delay) % backspace_repeat_delay == 0:
                    if cursor_position > 0:
                        task_descriptions[selected_description_index] = (
                            task_descriptions[selected_description_index][:cursor_position - 1] + 
                            task_descriptions[selected_description_index][cursor_position:]
                        )
                        cursor_position -= 1
        else:
            backspace_repeat_time = 0
    
    frame_counter += 1

    # update health bar
    current_time = time.time()
    if current_time - last_health_update >= 180.0:  # every 3 minutes
        dog_health = max(0, dog_health - health_decrease_rate)
        last_health_update = current_time

    # update dog animation
    # dog_vertical_offset = dog_bounce_range * math.sin(frame_counter * 0.01)

    # update treat vanishing animation
    if treat_vanishing:
        dragged_treat_alpha = max(0, dragged_treat_alpha - 15)
        dragged_treat_scale = max(0.1, dragged_treat_scale - 0.05)
        if dragged_treat_alpha <= 0:
            treat_vanishing = False

    # update experience bar animation
    if displayed_exp < player_exp:
        displayed_exp += (player_exp - displayed_exp) * exp_animation_speed
        if displayed_exp > player_exp - 0.1:  # close enough to snap to final value
            displayed_exp = player_exp

    # update new task cooldown
    if new_task_cooldown > 0:
        current_time = time.time()
        elapsed_time = current_time - new_task_cooldown_start
        new_task_cooldown = max(0, new_task_cooldown_duration - elapsed_time)
        if new_task_cooldown <= 0:
            new_task_cooldown = 0

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

    button_color = taskcard_color if hovered_newtask else taskcard_color
    pygame.draw.rect(screen, button_color, newtask, width=0, border_radius=6)
    pygame.draw.rect(screen, black, newtask, width=2, border_radius=6)
    
    # Show countdown or + button
    if new_task_cooldown > 0:
        text_surface = bodyfont.render("...", True, (0, 0, 0))
    else:
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
        
        card_color = (*taskcard_color, alpha)
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
        # Clip text to fit within textbox width (285 - 10 for padding)
        clipped_task_title = clip_text_to_width(task_title, subheaderfont, 275)
        text_surface = subheaderfont.render(clipped_task_title, True, color)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(topleft=(45, yoffset + 22.5))
        
        if is_selected:
            # Draw background with border radius - same as description textbox
            textbox_bg_rounded = pygame.Surface((285, 35), pygame.SRCALPHA)
            pygame.draw.rect(textbox_bg_rounded, (255, 255, 255, 100), (0, 0, 285, 35), border_radius=4)
            screen.blit(textbox_bg_rounded, (40, yoffset + 20))
            pygame.draw.rect(screen, (*black, alpha), (40, yoffset + 20, 285, 35), width=2, border_radius=4)
        
        screen.blit(text_surface, text_rect)

        # Task description
        task_description = task_descriptions[idx]
        is_description_selected = (selected_description_index == idx)

        if not task_description or task_description == "Task Description...":
            if is_description_selected:
                task_description = "|"  
            else:
                task_description = "Task Description..."  
            desc_color = (120, 80, 40)
        else:
            if is_description_selected:
                current_time = time.time()
                if int(current_time * 2) % 2 == 0:
                    task_description = (
                        task_description[:cursor_position] + 
                        "|" + 
                        task_description[cursor_position:]
                    )
            desc_color = (0, 0, 0)

        # Clip description text to fit within textbox width (285 - 10 for padding)
        clipped_task_description = clip_text_to_width(task_description, descfont, 275)
        desc_surface = descfont.render(clipped_task_description, True, desc_color)
        desc_surface.set_alpha(alpha)
        desc_rect = desc_surface.get_rect(topleft=(45, yoffset + 67.5))
        
        if is_description_selected:
            desc_textbox_bg_rounded = pygame.Surface((285, 24), pygame.SRCALPHA)
            pygame.draw.rect(desc_textbox_bg_rounded, (255, 255, 255, 100), (0, 0, 285, 24), border_radius=4)
            screen.blit(desc_textbox_bg_rounded, (40, yoffset + 65))
            pygame.draw.rect(screen, (*black, alpha), (40, yoffset + 65, 285, 24), width=2, border_radius=4)
        
        screen.blit(desc_surface, desc_rect)

        trash_x = 380  
        trash_y = yoffset + 21  
        screen.blit(trash_icon, (trash_x, trash_y))

        check_x = 345
        check_y = yoffset + 22
        screen.blit(check_icon, (check_x, check_y))

    screen.set_clip(None)

    # dog stuff
    screen.blit(dog, (510, 340))
    screen.blit(board, (460, -10))

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
    
    # two buttons side by side below the scrollbox
    button1_x = 0
    button1_y = 440  # below the scroll area
    button2_x = 220
    button2_y = 440
    screen.blit(button, (button1_x, button1_y))
    screen.blit(button, (button2_x, button2_y))
    
    # shop text on button1
    shop_text = subheaderfont.render("Store", True, black)
    shop_text_rect = shop_text.get_rect(center=(button1_x + 125, button1_y + 87.5))  # center of 250x175 button
    screen.blit(shop_text, shop_text_rect)
    
    # inventory text on button2
    inventory_text = subheaderfont.render("Customize", True, black)
    inventory_text_rect = inventory_text.get_rect(center=(button2_x + 125, button2_y + 87.5))  # center of 250x175 button
    screen.blit(inventory_text, inventory_text_rect)

    # render health bar and heart with z-index 9999
    health_bar_x = 555
    health_bar_y = 85  # on the board
    
    # health bar background - using app's brown color
    pygame.draw.rect(screen, brown, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), border_radius=3)
    
    # health bar border - using app's brown color
    pygame.draw.rect(screen, brown, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), width=2, border_radius=3)
    
    # health bar fill - always orange
    health_percentage = dog_health / dog_max_health
    health_fill_width = int(health_bar_width * health_percentage)
    
    # always use orange color
    health_color = orange
    
    if health_fill_width > 0:
        pygame.draw.rect(screen, health_color, (health_bar_x + 2, health_bar_y + 2, health_fill_width - 4, health_bar_height - 4), border_radius=2)
    
    # heart icon next to health bar
    heart_x = health_bar_x - 45  # position heart to the left of health bar
    heart_y = health_bar_y - 10   # align with health bar
    screen.blit(heart, (heart_x, heart_y))
    
    # collar icon above heart
    collar_x = heart_x + 7  # same x position as heart
    collar_y = heart_y - 40  # 40 pixels above heart
    screen.blit(collar, (collar_x, collar_y))
    
    # name box next to collar
    name_box_x = collar_x + 40
    name_box_y = collar_y + 1
    name_box_width = 115
    name_box_height = 30
    
    # name box background
    if selected_name_box:
        # draw background with border radius - same as description textbox
        name_box_bg_rounded = pygame.Surface((name_box_width, name_box_height), pygame.SRCALPHA)
        pygame.draw.rect(name_box_bg_rounded, (255, 255, 255, 100), (0, 0, name_box_width, name_box_height), border_radius=4)
        screen.blit(name_box_bg_rounded, (name_box_x, name_box_y))
        pygame.draw.rect(screen, black, (name_box_x, name_box_y, name_box_width, name_box_height), width=2, border_radius=4)
    
    # name text with cursor
    name_display = dog_name
    if selected_name_box:
        current_time = time.time()
        if int(current_time * 2) % 2 == 0:
            name_display = name_display[:name_cursor_position] + "|" + name_display[name_cursor_position:]
    
    # clip name text to fit within name box width (100 - 10 for padding)
    clipped_name_display = clip_text_to_width(name_display, namefont, 90)
    name_text = namefont.render(clipped_name_display, True, black)
    screen.blit(name_text, (name_box_x + 5, name_box_y + 5))
    
    # exp icon under heart
    exp_x = heart_x  # same x position as heart
    exp_y = heart_y + 40  # 40 pixels below heart
    screen.blit(exp, (exp_x, exp_y))
    
    # experience bar next to exp icon
    exp_bar_x = exp_x + 45  # position exp bar to the right of exp icon
    exp_bar_y = exp_y + 10  # align with exp icon
    
    # experience bar background - using app's brown color
    pygame.draw.rect(screen, brown, (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height), border_radius=3)
    
    # experience bar border - using app's brown color
    pygame.draw.rect(screen, brown, (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height), width=2, border_radius=3)
    
    # experience bar fill - always orange
    exp_percentage = displayed_exp / exp_to_next_level
    exp_fill_width = int(exp_bar_width * exp_percentage)
    
    # always use orange color
    exp_color = orange
    
    if exp_fill_width > 0:
        pygame.draw.rect(screen, exp_color, (exp_bar_x + 2, exp_bar_y + 2, exp_fill_width - 4, exp_bar_height - 4), border_radius=2)
    
    # level text below experience bar
    level_text = levelfont.render(f"Lvl. {player_level}", True, black)
    level_text_x = exp_bar_x + (exp_bar_width // 2) - (level_text.get_width() // 2)  # center the text
    level_text_y = exp_bar_y + exp_bar_height + 5  # 5 pixels below the bar
    screen.blit(level_text, (level_text_x, level_text_y))

    # render dragged treat on top of everything (z-index 10000)
    if dragging_treat or treat_vanishing:
        # create a scaled and alpha-modified version of the treat
        treat_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        treat_surface.set_alpha(dragged_treat_alpha)
        
        # scale the treat
        scaled_size = (int(60 * dragged_treat_scale), int(60 * dragged_treat_scale))
        scaled_treat = pygame.transform.smoothscale(defaulttreat, scaled_size)
        
        # calculate position to center the scaled treat
        treat_x = dragged_treat_pos[0] - scaled_size[0] // 2
        treat_y = dragged_treat_pos[1] - scaled_size[1] // 2
        
        screen.blit(scaled_treat, (treat_x, treat_y))

    pygame.display.flip()

pygame.quit()
sys.exit()