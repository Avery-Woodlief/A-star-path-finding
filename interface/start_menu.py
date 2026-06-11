from interface.ui_elements import *
import re
from pathlib import Path
import pygame

def display_text(parent, msg, font_key, pos):
    text_surface = parent.fonts[font_key].render(msg, True, (0, 0, 0, 255))
    parent.screen.blit(text_surface, pos)

def collect_text_input_yes_no(parent, prompts : list) -> str:

    no_button = SimpleButton((0, 0, 50, 50), "No", bg_color=(255, 0, 0, 100))
    yes_button = SimpleButton((0, 0, 50, 50), "Yes", bg_color=(0, 255, 0, 100))

    len_last_prompt = 0        

    for prompt in prompts:
        display_text(parent, *prompt)
        len_last_prompt = len(prompt[0])


    R=True
    collected_text = ""
    len_last_prompt = 0
    while (R):
        parent.screen.fill(parent.colors["white"])
        for event in pygame.event.get():
            if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                mouse_pos = event.pos
                hit_button_color = None
                grabbed_button = None
                if event.type == pygame.MOUSEBUTTONDOWN:
                        if (no_button.collidepoint(mouse_pos)):
                            return "NO"
                            hit_button_color = no_button.bg_color
                            grabbed_button = no_button    
                        elif (yes_button.collidepoint(mouse_pos)):
                            return "YES"
                            hit_button_color = yes_button.bg_color
                            grabbed_button = yes_button
                elif event.type == pygame.MOUSEMOTION:
                        if (no_button.collidepoint(mouse_pos)):
                            hit_button_color = no_button.bg_color
                            grabbed_button = no_button
                        else:
                            no_button.bg_color = (255, 0, 0, 100)
                        if (yes_button.collidepoint(mouse_pos)):
                            hit_button_color = yes_button.bg_color
                            grabbed_button = yes_button
                        else:
                            yes_button.bg_color = (0, 255, 0, 100)

                        if (hit_button_color != None and grabbed_button != None):
                            r, g, b, a = hit_button_color
                            grabbed_button.bg_color = (r, g, b, (2*a % 256) + 1)
                            hit_button_color = None
                    
                    
                    

        pygame.time.Clock().tick(60)
                    
        for prompt in prompts:
            display_text(parent, *prompt)
        yes_button.draw("large")
        yes_button.put_in(parent.screen, ((len_last_prompt)*12 + 400, 50))
        no_button.draw("large")
        no_button.put_in(parent.screen, (400 + ((len_last_prompt)*12) + yes_button.width + 50, 50))
        pygame.display.flip()
    return

def run_start_menu(parent) -> None:

    drop_down = DropDownList(text="Load in a map", rel_parent_loc=(0,0), bg_color_open=pygame.Color(0, 0, 0, 10), bg_color_closed=(0, 0, 0, 0))
    new_map_button = SimpleButton((0, 0, 400, 50), "Create new map")
    map_files = [
                re.sub(r"\b.json\b", "", re.sub(fr"\bmaps{parent.file_nav_char}\b", "", str(map_))) for map_ in Path(f"maps{parent.file_nav_char}").iterdir() if map_.is_file()
                ]
    items = [DropDownItem(text=f"{map_}", parent=drop_down) for map_ in map_files]
    #items = [DropDownItem(text=f"item {i}", parent=drop_down) for i in range(3)]
    drop_down.init_children_shapes(drop_down.drop_menu_width, 30)
    drop_down.children[0].height=50
    #drop_down.close()
    while (parent.start_menu_running):
        parent.screen.fill(parent.colors["white"])
        display_text(parent, "Press 'q' or 'Esc' to quit the program", "medium", (0, parent.screen.get_height()-150))
        new_map_button.put_in(parent.screen, (parent.screen.get_width()-400, 0))
        new_map_button.draw("large")
        for event in pygame.event.get():
            if (event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL]):
                    mouse_pos = event.pos                        
                    if (event.type == pygame.MOUSEMOTION):
                        for child in drop_down.children:
                                if (child.collidepoint(mouse_pos) and child.id != 1):
                                    if (child.colliderect(drop_down.drop_down_button)):
                                        break
                                    child.bg_color = (255, 0, 0, 50)
                                elif (not child.collidepoint(mouse_pos) and child.id != 1):
                                    child.bg_color = (255, 0, 0, 100)
                        if (new_map_button.collidepoint(mouse_pos)):
                            new_map_button.bg_color = (0, 0, 255, 50)
                        else:
                            new_map_button.bg_color = (0, 0, 255, 100)

                        if (drop_down.drop_down_button.collidepoint(mouse_pos)):
                            drop_down.drop_down_button.bg_color = (0, 255, 0, 50)
                        else:
                            drop_down.drop_down_button.bg_color = (0, 255, 0, 100)
                    if (event.type == pygame.MOUSEBUTTONDOWN):
                        mouse_pos = event.pos
                        if (new_map_button.collidepoint(mouse_pos)):
                            parent.running = True
                            parent.start_menu_running = False
                            return
                        if (drop_down.is_open):
                            if (event.button in [2, 4, 5]): # 4 - up, 5 - down
                                if (event.button == 5):
                                    drop_down.scroll_down(parent.screen)
                                    break
                                elif (event.button == 4):
                                    drop_down.scroll_up(parent.screen)
                                    break
                                continue
                            for child in drop_down.children:
                                if (child.collidepoint(mouse_pos) and child.id != 1):
                                    if (child.colliderect(drop_down.drop_down_button)):
                                        break

                                    prompts = [
                                                ["Loading in a map will overwrite the previous save once the changes are made","large",(0, 0)],
                                                ["Would you like to continue? ","large",(0, 50)]
                                              ]
                                    pygame.display.flip()
                                    overwrite_previous_map_version_response = collect_text_input_yes_no(parent, prompts)
                                    if (overwrite_previous_map_version_response == "N" or
                                        overwrite_previous_map_version_response == "NO"):
                                        parent.running = True
                                        parent.start_menu_running = False
                                        return
                                    parent.running = True
                                    parent.start_menu_running = False
                                    parent.load_in_a_map(child.text)
                                    parent.loadded_in_map = child.text
                                    parent.loaded_in_a_map = True
                                    
                        if (drop_down.drop_down_button.collidepoint(mouse_pos)):
                            drop_down.is_open = not drop_down.is_open
            if (event.type == pygame.KEYDOWN):
                if ((event.key == pygame.K_q) or (event.key == pygame.K_ESCAPE)):
                    parent.complete_exit = True
                    parent.running = False
                    parent.start_menu_running = False
                
            if (event.type == pygame.QUIT):
                parent.complete_exit = True
                parent.running = False
                parent.start_menu_running = False

        if (drop_down.is_open):
            drop_down.open()
        else:
            drop_down.close()
        
        parent.screen.blit(drop_down.overlay, (drop_down.parent_screen_x, drop_down.parent_screen_y))
        pygame.display.flip()
    return
