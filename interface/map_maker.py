from navigator.obstacles import *
from interface.ui_elements import *
from interface.start_menu import run_start_menu, collect_text_input_yes_no, display_text
import json
import pygame
from pathlib import Path
import platform
import math
import os
import re
#import exceptions
pygame.init()
pygame.font.init()

nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function





class MapMaker:
    
    def __init__(self, screen_width, screen_height):
        
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        self.obstacles_ = {}
        
        self.colors = pygame.color.THECOLORS
        self.font_names = pygame.font.get_fonts()
        self.fonts = {}
        for name in self.font_names:
            try:
                self.fonts[name] = {
                                    "small": pygame.font.Font(pygame.font.match_font(name), 12),
                                    "medium": pygame.font.Font(pygame.font.match_font(name), 24),
                                    "large": pygame.font.Font(pygame.font.match_font(name), 36)
                                   }
            except (FileNotFoundError):
                self.fonts.pop(name)
                continue

        #print(self.fonts)


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
        self.operating_system = platform.system()
        self.file_nav_char =""
        if (self.operating_system.upper() == "WINDOWS"):
            self.file_nav_char = "\\"
        else:
            self.file_nav_char = "/"
        self.dx = None
        self.dy = None
        self.skip_map = False
        self.selected_shape_type = "ObstacleRect"
        self.loadded_in_map = ""
        self.loaded_in_a_map = False
        self.complete_exit = False

        self.easy_draw = False
        self.saved_obj = None
        self.filled_circle = False
        run_start_menu(self)


    


    

    

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
        #print(os.getcwd())
        with open(f"maps{self.file_nav_char}{map_name}.json", "r") as file:
            loaded_in_obstacles = json.load(file)
        file.close()
        self.parse_loaded_in_obstacles(loaded_in_obstacles)
        
        return

    def dragging_check(self, event):
        if (self.began_drag and not self.end_drag and not self.easy_draw):
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
                    
        elif (self.edit_began_drag and not self.edit_end_drag and not self.easy_draw):
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
        elif (self.began_drag and self.easy_draw):
            self.obstacles_[ObstacleRect((event.pos[0], event.pos[1], 50, 50))] = self.colors["black"]
            
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

    def draw_circle_using_rects(self, center, radius):
        cx, cy = center

        w = 5
        h = 5
        increment = math.floor((360)/(2*math.pi*radius/w))
        

        for d in range(0, 360, increment):
            angle = math.radians(d)

            x = nint(cx + radius * math.cos(angle))
            y = nint(cy + radius * math.sin(angle))

            new_rect = ObstacleRect((x, y), (w, h))
            self.obstacles_[new_rect] = self.colors["black"]


    def make_new_circle_obj(self, event):
        self.radius = math.dist(self.start, event.pos)
        self.center = self.start
        self.draw_circle_using_rects(self.center, self.radius)
        return

    def make_new_circle_obj_filled(self, event):
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
                print("ending drag")
                self.began_drag = False
                self.end_drag = True
                if (not self.easy_draw):
                    if (self.selected_shape_type == "ObstacleRect"):
                        self.make_new_rect_obj(event)
                    elif (self.selected_shape_type == "ObstacleCircle"):
                        if (not self.filled_circle):
                            self.make_new_circle_obj(event)
                        else:
                            self.make_new_circle_obj_filled(event)

          

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
                elif (event.key == pygame.K_SPACE):
                    self.easy_draw = not self.easy_draw
                    self.saved_obj = self.focused_obj
                elif (event.key == pygame.K_f and event.mod & pygame.KMOD_LCTRL):
                    self.filled_circle = not self.filled_circle
                    print(f"filled circle: {self.filled_circle}")
                elif (event.key == pygame.K_DELETE and (not (self.focused_obj == None))):
                    try:
                        self.obstacles_.pop(self.focused_obj)
                        self.focused_obj = None
                    except (KeyError):
                        pass
            if (event.key == pygame.K_ESCAPE):
                self.running = False

    def running_loop(self):
        #self.run_start_menu()

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
    with open(f"maps{map_maker.file_nav_char}{file_name}.json", "w") as file:
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
        prompt_width = display_text(map_maker,"name your map: ", "large", (0, 0)).get_width()
        display_text(map_maker, "Press Enter when finished", "large", (0, 50))
        display_text(map_maker, file_name, "large", (prompt_width + 10, 0))
        pygame.display.flip()

    #file_name = input("name your map: ")
    with open(f"maps{map_maker.file_nav_char}{file_name}.json", "w") as file:
        json.dump(file_, file, indent=4)

pygame.quit()
