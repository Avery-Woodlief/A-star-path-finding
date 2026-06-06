from obstacle import Obstacle
import json
import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 800))

obstacles = {}



color_pool = {
                0 : "white",
                1 : "red",
                2 : "green",
                3 : "blue",
                4 : "black"          
             }

colors = {
            "white" : pygame.Color(255, 255, 255),
            "red" : pygame.Color(255, 0, 0),
            "green" : pygame.Color(0, 255, 0),
            "blue" : pygame.Color(0, 0, 255),
            "black" : pygame.Color(0, 0, 0)
        }




running = True
began_drag = False
end_drag = False
start = None
width = None
height = None

screen.fill(colors["white"])


more_control = False


edit_began_drag = False
edit_end_drag = False


edit_dragging = False
edit_pos = None

edit_width = None
edit_height = None

focused_rect = None

#edit_index = -1


#last_drawn_rect = None


dx = None
dy = None

while (running):

    

    for event in pygame.event.get():
        if (event.type == pygame.WINDOWLEAVE):
            print("No come back!")
        if (began_drag and not end_drag):
            print("dragging")
            if (event.type == pygame.MOUSEMOTION):
                width = abs(start[0] - event.pos[0])
                height = abs(start[1] - event.pos[1])
                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 1))  # clears overlay to transparent
                screen.blit(overlay, (min(start[0], event.pos[0]),min(start[1], event.pos[1])))
        elif (edit_began_drag and not edit_end_drag):
            print("edit dragging")
            edit_dragging = True
            screen.fill(colors["white"])
            try:
                try:
                    obstacles.pop(focused_rect)
                except (KeyError):
                    pass
                mouse_pos = event.pos
               
                #edit_pos = (mouse_pos[0] - focused_rect.w//2, mouse_pos[1] - focused_rect.h//2)
                edit_pos = (mouse_pos[0] - dx, mouse_pos[1] - dy)
                focused_rect.move(edit_pos)
                obstacles[focused_rect] = colors["blue"]
                #last_drawn_rect = focused_rect
            except(AttributeError):
                continue
            
            
        else:
            screen.fill(colors["white"])
        if (event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]):
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == 1 and more_control):
                    #edit_index = 0
                    #i = 0
                    for obj in obstacles:
                        mouse_pos = event.pos
                        if (pygame.Rect(obj).collidepoint(mouse_pos)):
                            if (not edit_began_drag):
                                edit_end_drag = False
                                edit_began_drag = True
                                focused_rect = obj
                                #obstacles[obj] = colors["blue"]
                                obstacles.pop(obj)
                                edit_width = focused_rect.width
                                edit_height = focused_rect.height
                                dx = mouse_pos[0] - focused_rect.x
                                dy = mouse_pos[1] - focused_rect.y
                                break
                        
                        
                if (event.button == 3):
                    if (not began_drag):
                        end_drag = False
                        began_drag = True
                        start = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if (edit_began_drag):
                edit_began_drag = False
                edit_end_drag = True
                #obstacles.pop(edit_index)
                #obstacles.insert(edit_index, Obstacle(event.pos,(edit_width, edit_height)))
                obstacles[focused_rect] = colors["black"]
                #edit_index = -1
            if (began_drag):
                began_drag = False
                end_drag = True
                width = abs(start[0] - event.pos[0])
                height = abs(start[1] - event.pos[1])
                size = (width, height)
                
                #obstacles.append()
                new_rect = Obstacle((min(start[0], event.pos[0]),min(start[1], event.pos[1])), size)
                obstacles[new_rect] = colors["black"]
                #last_drawn_rect = new_rect
        if (event.type in [pygame.KEYDOWN, pygame.KEYUP]):
        
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_z and event.mod & pygame.KMOD_LCTRL):
                    try:
                        #obstacles.pop(last_drawn_rect)
                        popped_key = list(obstacles.keys()).pop()
                        obstacles.pop(popped_key)
                    except (IndexError, KeyError):
                        pass
                elif (event.key == pygame.K_e and event.mod & pygame.KMOD_LSHIFT):
                    more_control = not more_control
                elif (event.key == pygame.K_DELETE and (not (focused_rect == None))):
                    try:
                        obstacles.pop(focused_rect)
                        focused_rect = None
                    except (KeyError):
                        pass
            if (event.key == pygame.K_ESCAPE):
                running = False
            
        elif (event.type == pygame.QUIT):
            running = False
    
    for obj in obstacles.keys():
        pygame.draw.rect(screen, obstacles[obj], obj)
    
    pygame.display.flip()


file_ = {}


for obj, color in obstacles.items():
    file_[f"{obj}"] = f"{color}"


file_name = input("name your map: ")

with open(f"{file_name}.json", "w") as file:
    json.dump(file_, file, indent=4)

pygame.quit()
