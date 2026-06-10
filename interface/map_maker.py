from navigator.obstacles import *
from interface.ui_elements import *
import json
import pygame
from pathlib import Path
import math
import os
import re
#import exceptions

pygame.init()
nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function





class MapMaker:
    
    def __init__(self, screen_width, screen_height):
        
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        self.obstacles_ = {}
        #self.load_in_a_map(input("mapname> "))
        self.color_pool = {
                0 : "white",
                1 : "red",
                2 : "green",
                3 : "blue",
                4 : "black"          
             }
        self.colors = {
            "white" : pygame.Color(255, 255, 255),
            "red" : pygame.Color(255, 0, 0),
            "green" : pygame.Color(0, 255, 0),
            "blue" : pygame.Color(0, 0, 255),
            "black" : pygame.Color(0, 0, 0)
        }

        self.fonts = {
                "small": pygame.font.Font(None, 12),
                "medium": pygame.font.Font(None, 24),
                "large": pygame.font.Font(None, 36)
            }

        self.screen.fill(self.colors["white"])
        
        self.running = False
        self.start_menu_running = True
        self.began_drag = False
        self.end_drag = False
        self.start = None
        
        # rect params

        self.width = None
        self.height = None

        # circle params

        self.radius = None
        self.center = None


        self.more_control = False
        self.edit_began_drag = False
        self.edit_end_drag = False
        self.edit_dragging = False
        self.edit_pos = None
        self.edit_width = None
        self.edit_height = None
        self.focused_obj = None
        self.dx = None
        self.dy = None
        self.skip_map = False
        self.selected_shape_type = "ObstacleRect"
        self.loadded_in_map = ""
        self.loaded_in_a_map = False
        self.complete_exit = False


    def display_text(self, msg, font_key, pos):
        text_surface = self.fonts[font_key].render(msg, True, (0, 0, 0, 255))
        self.screen.blit(text_surface, pos)


    def collect_text_input_yes_no(self, prompts : list) -> str:

        no_button = SimpleButton((0, 0, 50, 50), "No", bg_color=(255, 0, 0, 100))
        yes_button = SimpleButton((0, 0, 50, 50), "Yes", bg_color=(0, 255, 0, 100))

        len_last_prompt = 0        

        for prompt in prompts:
            self.display_text(*prompt)
            len_last_prompt = len(prompt[0])


        R=True
        collected_text = ""
        len_last_prompt = 0
        while (R):
            self.screen.fill(self.colors["white"])
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
                self.display_text(*prompt)
            #self.display_text(collected_text, "large", (, 50))
            yes_button.draw("large")
            yes_button.put_in(self.screen, ((len_last_prompt)*12 + 400, 50))
            no_button.draw("large")
            no_button.put_in(self.screen, (400 + ((len_last_prompt)*12) + yes_button.width + 50, 50))
            pygame.display.flip()

    def run_start_menu(self) -> None: # TODO

        drop_down = DropDownList(text="Load in a map", rel_parent_loc=(0,0), bg_color_open=pygame.Color(0, 0, 0, 10), bg_color_closed=(0, 0, 0, 0))
        new_map_button = SimpleButton((0, 0, 400, 50), "Create new map")
        
        map_files = [re.sub(r"\b.json\b", "", re.sub(r"\bmaps/\b", "", str(map_))) for map_ in Path("maps/").iterdir() if map_.is_file()]
        items = [DropDownItem(text=f"{map_}", parent=drop_down) for map_ in map_files]
        #items = [DropDownItem(text=f"item {i}", parent=drop_down) for i in range(3)]
        drop_down.init_children_shapes(drop_down.drop_menu_width, 30)
        drop_down.children[0].height=50
        #drop_down.close()
        while (self.start_menu_running):
            self.screen.fill(self.colors["white"])
            self.display_text("Press 'q' or 'Esc' to quit the program", "medium", (0, self.screen.get_height()-150))
            new_map_button.put_in(self.screen, (self.screen.get_width()-400, 0))
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
                                self.running = True
                                self.start_menu_running = False
                                return
                            if (drop_down.is_open):
                                if (event.button in [2, 4, 5]): # 4 - up, 5 - down
                                    if (event.button == 5):
                                        drop_down.scroll_down(self.screen)
                                        break
                                    elif (event.button == 4):
                                        drop_down.scroll_up(self.screen)
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
                                        overwrite_previous_map_version_response = self.collect_text_input_yes_no(prompts)
                                        if (overwrite_previous_map_version_response == "N" or
                                            overwrite_previous_map_version_response == "NO"):
                                            self.running = True
                                            self.start_menu_running = False
                                            return
                                        self.running = True
                                        self.start_menu_running = False
                                        self.load_in_a_map(child.text)
                                        self.loadded_in_map = child.text
                                        self.loaded_in_a_map = True
                                        
                            if (drop_down.drop_down_button.collidepoint(mouse_pos)):
                                drop_down.is_open = not drop_down.is_open
                if (event.type == pygame.KEYDOWN):
                    if ((event.key == pygame.K_q) or (event.key == pygame.K_ESCAPE)):
                        self.complete_exit = True
                        self.running = False
                        self.start_menu_running = False
                    
                if (event.type == pygame.QUIT):
                    self.complete_exit = True
                    self.running = False
                    self.start_menu_running = False

            if (drop_down.is_open):
                drop_down.open()
            else:
                drop_down.close()
            
            self.screen.blit(drop_down.overlay, (drop_down.parent_screen_x, drop_down.parent_screen_y))
            pygame.display.flip()
        return

    def load_in_rect(self, instances : dict) -> None:
        for rect, color in instances.items():
            a1 = re.findall(r"\d+", rect)
            a1_map = map(int, a1)
            rect_args = []
            for i in a1_map:
                rect_args.append(i)
            topleft = (rect_args[0], rect_args[1])
            size = (rect_args[2], rect_args[3])
            a2 = re.findall(r"\d+", color)
            a2_map = map(int, a2)
            color_args = []
            for i in a2_map:
                color_args.append(i)
            self.obstacles_[ObstacleRect(topleft, size)] = pygame.Color(tuple(color_args))
        return

    def load_in_circle(self, instances : dict) -> None:
        for circle, color in instances.items():
            a1 = re.findall(r"\d+", circle)
            a1_map = map(int, a1)
            circle_args = []
            for i in a1_map:
                circle_args.append(i)
            center = (circle_args[0], circle_args[1])
            radius = circle_args[2]
            a2 = re.findall(r"\d+", color)
            a2_map = map(int, a2)
            color_args = []
            for i in a2_map:
                color_args.append(i)
            self.obstacles_[ObstacleCircle(center, radius)] = pygame.Color(tuple(color_args))
        return

    def parse_loaded_in_obstacles(self, loaded_in_objs) -> None:
        for obstacle_type, instances in loaded_in_objs.items():
            if (obstacle_type == "Rect"):
                self.load_in_rect(instances)
            elif (obstacle_type == "Circle"):
                self.load_in_circle(instances)
        return

    def load_in_a_map(self, map_name : str) -> None:
        print(os.getcwd())
        with open(f"maps/{map_name}.json", "r") as file:
            loaded_in_obstacles = json.load(file)
        file.close()
        self.parse_loaded_in_obstacles(loaded_in_obstacles)
        
        return

    def dragging_check(self, event):
        if (self.began_drag and not self.end_drag):
            #print("dragging")
            if (event.type == pygame.MOUSEMOTION):
                if (self.selected_shape_type == "ObstacleRect"):
                    self.width = abs(self.start[0] - event.pos[0])
                    self.height = abs(self.start[1] - event.pos[1])
                    overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 1))  # clears overlay to transparent
                    self.screen.blit(overlay, (min(self.start[0], event.pos[0]),min(self.start[1], event.pos[1])))
                elif (self.selected_shape_type == "ObstacleCircle"):
                    self.radius = math.dist(self.center, event.pos)
                    overlay = pygame.Surface((self.radius * 2 + 10, self.radius * 2 + 10), pygame.SRCALPHA)
                    #overlay.fill((0, 0, 0, 1))  # clears overlay to transparent
                    pygame.draw.circle(overlay, (0, 0, 0, 1), (self.radius, self.radius), self.radius)
                    self.screen.blit(overlay, (self.center[0] - self.radius, self.center[1] - self.radius))
                    
        elif (self.edit_began_drag and not self.edit_end_drag):
            #print("edit dragging")
            self.edit_dragging = True
            self.screen.fill(self.colors["white"])
            try:
                try:
                    self.obstacles_.pop(self.focused_obj)
                except (KeyError):
                    pass
                mouse_pos = event.pos
               
                self.edit_pos = (mouse_pos[0] - self.dx, mouse_pos[1] - self.dy)
                self.focused_obj.move(self.edit_pos)
                self.obstacles_[self.focused_obj] = self.colors["blue"]
            except(AttributeError):
                raise AttributeError
        else:
            self.screen.fill(self.colors["white"])
            #print("")

    def handle_rect_in_mouse_event(self, event):
        #print(self.obstacles_)
        for obj in self.obstacles_:
            if (not isinstance(obj, ObstacleRect)):
                continue
            mouse_pos = event.pos
            if (pygame.Rect(obj).collidepoint(mouse_pos)):
                if (not self.edit_began_drag):
                    self.edit_end_drag = False
                    self.edit_began_drag = True
                    self.focused_obj = obj
                    self.obstacles_.pop(obj)
                    self.edit_width = self.focused_obj.width
                    self.edit_height = self.focused_obj.height
                    self.dx = mouse_pos[0] - self.focused_obj.x
                    self.dy = mouse_pos[1] - self.focused_obj.y
                    break

    def handle_circle_in_mouse_event(self, event):
        for obj in self.obstacles_:
            if (not isinstance(obj, ObstacleCircle)):
                continue
            mouse_pos = event.pos
            if (obj.collidepoint(mouse_pos)):
                if (not self.edit_began_drag):
                    self.edit_end_drag = False
                    self.edit_began_drag = True
                    self.focused_obj = obj
                    self.obstacles_.pop(obj)
                    #self.edit_width = self.focused_obj.width
                    #self.edit_height = self.focused_obj.height
                    self.dx = mouse_pos[0] - self.focused_obj.center[0]
                    self.dy = mouse_pos[1] - self.focused_obj.center[1]
                    break
        return

    def make_new_rect_obj(self, event):
        self.width = abs(self.start[0] - event.pos[0])
        self.height = abs(self.start[1] - event.pos[1])
        size = (self.width, self.height)
        
        new_rect = ObstacleRect((min(self.start[0], event.pos[0]),min(self.start[1], event.pos[1])), size)
        self.obstacles_[new_rect] = self.colors["black"]
        return

    def make_new_circle_obj(self, event):
        self.radius = math.dist(self.start, event.pos)
        self.center = self.start
        new_circle = ObstacleCircle(self.center, self.radius)
        self.obstacles_[new_circle] = self.colors["black"]
        return

    def handle_mouse_event(self, event):
        if (event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]):
            #print("mouse moving")
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == 1 and self.more_control):
                    print("began edit dragging")
                    if (self.selected_shape_type == "ObstacleRect"):
                        self.handle_rect_in_mouse_event(event)
                    elif (self.selected_shape_type == "ObstacleCircle"):
                        self.handle_circle_in_mouse_event(event)
                        
                        
                if (event.button == 3):
                    if (not self.began_drag):
                        print("began dragging")
                        self.end_drag = False
                        self.began_drag = True
                        self.start = event.pos
                        self.center = self.start
        elif event.type == pygame.MOUSEBUTTONUP:
            if (self.edit_began_drag):
                self.edit_began_drag = False
                self.edit_end_drag = True
                self.obstacles_[self.focused_obj] = self.colors["black"]

            if (self.began_drag):
                self.began_drag = False
                self.end_drag = True
                if (self.selected_shape_type == "ObstacleRect"):
                    self.make_new_rect_obj(event)
                elif (self.selected_shape_type == "ObstacleCircle"):    
                    self.make_new_circle_obj(event)

    def handle_key_event(self, event):
        if (event.type in [pygame.KEYDOWN, pygame.KEYUP]):
        
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_z and event.mod & pygame.KMOD_LCTRL):
                    try:
                        popped_key = list(self.obstacles_.keys()).pop()
                        self.obstacles_.pop(popped_key)
                    except (IndexError, KeyError):
                        pass
                elif (event.key == pygame.K_1):
                    print("Rectangle type selected")
                    self.selected_shape_type = "ObstacleRect"
                elif (event.key == pygame.K_2):
                    print("Circle type selected")
                    self.selected_shape_type = "ObstacleCircle"
                elif (event.key == pygame.K_e and event.mod & pygame.KMOD_LSHIFT):
                    self.more_control = not self.more_control
                
                elif (event.key == pygame.K_DELETE and (not (self.focused_obj == None))):
                    try:
                        self.obstacles_.pop(self.focused_obj)
                        self.focused_obj = None
                    except (KeyError):
                        pass
            if (event.key == pygame.K_ESCAPE):
                self.running = False

    def running_loop(self):
        self.run_start_menu()

        while (self.running):
            #print(self.selected_shape_type)
            for event in pygame.event.get():
                if (event.type == pygame.WINDOWLEAVE):
                    print("No come back!")
                try:
                    self.dragging_check(event)
                except (AttributeError):
                    continue
                self.handle_mouse_event(event)
                self.handle_key_event(event)
                if (event.type == pygame.QUIT):
                    self.running = False
                
                for obj in self.obstacles_.keys():
                    if (isinstance(obj, ObstacleRect)):
                        pygame.draw.rect(self.screen, self.obstacles_[obj], obj)
                    elif (isinstance(obj, ObstacleCircle)):
                        pygame.draw.circle(self.screen, self.obstacles_[obj], obj.center, obj.radius)
                pygame.display.flip()

        return

map_maker = MapMaker(1000, 750)


map_maker.running_loop()
file_ = {"Rect":{}, "Circle":{}}


for obj, color in map_maker.obstacles_.items():
    if isinstance(obj, ObstacleRect):
        file_["Rect"][f"{obj}"] = f"{color}"
    elif isinstance(obj, ObstacleCircle):
        obj.radius = nint(obj.radius)
        file_["Circle"][f"{obj}"] = f"{color}"

file_name = ""
if (map_maker.loaded_in_a_map):
    file_name = map_maker.loadded_in_map
    with open(f"maps/{file_name}.json", "w") as file:
        json.dump(file_, file, indent=4)
elif (not map_maker.complete_exit):
    run = True
    file_name = ""
    while (run):
        map_maker.screen.fill(map_maker.colors["white"])
        for event in pygame.event.get():
            if event.type == pygame.TEXTINPUT:
                file_name += event.text

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_BACKSPACE:
                    file_name = file_name[:-1]

                elif event.key == pygame.K_RETURN:
                    run=False
        map_maker.display_text("name your map: ", "large", (0, 0))
        map_maker.display_text("Press Enter when finished", "large", (0, 50))
        map_maker.display_text(file_name, "large", (len("name your map: ")*13, 0))
        pygame.display.flip()

    #file_name = input("name your map: ")
    with open(f"maps/{file_name}.json", "w") as file:
        json.dump(file_, file, indent=4)

pygame.quit()
