from navigator.obstacles import *
from exceptions.ui_errors import *
import json
import pygame
from pathlib import Path
import math
import os
import re
#import exceptions

pygame.init()
nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function


class SimpleButton(pygame.Rect):

    def __init__(self, args, text, bg_color=(0, 0, 255, 100)):
        super().__init__(*args)
        self.text = text
        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.fonts = {
                "small": pygame.font.Font(None, 12),
                "medium": pygame.font.Font(None, 24),
                "large": pygame.font.Font(None, 36)
            }
        self.bg_color = bg_color
        self.loc_rel_parent = None
        #self.draw("medium")

    def put_in(self, parent_screen, loc_rel_parent):
        self.loc_rel_parent = loc_rel_parent
        parent_screen.blit(self.overlay, loc_rel_parent)
        
    def draw(self, font_type):
        self.overlay.fill(self.bg_color)
        pygame.draw.rect(self.overlay, (0, 0, 0), self, width=2)
        self.text_surface = self.fonts[font_type].render(self.text, True, (0, 0, 0))
        self.overlay.blit(self.text_surface, (self.width//4, self.height//4))
        
    def collidepoint(self, point):
        dx, dy = self.loc_rel_parent
        return super().collidepoint((point[0] - dx, point[1] - dy))

class DropDownList:pass

class DropDownItem(pygame.Rect):

    


    def __init__(self, img = None, text = None, parent = None, id_ = None, bg_color = pygame.Color(255, 0, 0, 100)):
        self.z_index = 0
        if (img):
            if (isinstance(img, str)):
                if (Path(img).exists() and 
                    ((img[img.index('.'):] == ".png") or (img[img.index('.'):] == ".jpg") or (img[img.index('.'):] == ".jpeg"))):
                    self.img = pygame.image.load(img)
        if (not text):
            self.text = ""
        else:
            self.text = text
        self.fonts = {
                "small": pygame.font.Font(None, 12),
                "medium": pygame.font.Font(None, 24),
                "large": pygame.font.Font(None, 36)
            }
        #if (isinstance(parent, DropDownList)):
            #print(type(parent))
        if ((parent == None) or (not isinstance(parent, DropDownList))):
            raise NoParentContainerFound
        else:
            self.parent = parent
            self.parent.add(self)
        self.bg_color = bg_color
        self.id = id_
        
    def __hash__(self):
        return (self.topleft + self.size).__hash__()

    def create_shape(self, args):
        super().__init__(*args)
    

    def draw_text(self, font_type):
        if (font_type not in list(self.fonts.keys())):
            return
        self.text_surface = self.fonts[font_type].render(self.text, True, (0, 0, 0))
        self.parent.overlay.blit(self.text_surface, (self.x, self.y))


    def get_dominating_z(self):
        hits = []
        for child in self.parent.children:
            if (child == self):
                continue
            if (child.colliderect(self)):
                hits.append(child)
        if (len(hits) > 0):
            return max([child.z_index for child in hits])
        return self.z_index

    def collidepoint(self, point):
        point_rel = (point[0] - self.parent.parent_screen_x, point[1] - self.parent.parent_screen_y)
            
        return super().collidepoint(point_rel)

    def __str__(self):
        return f"{self.x}, {self.y}, {self.w}, {self.h}"

class DropDownList(pygame.Rect):
    def __init__(self, img = None, text = None, rel_parent_loc = (50, 50), size = (400, 400),
                 drop_button_bg_color=pygame.Color(0, 255, 0, 100), bg_color_open=(0, 0, 0, 100), bg_color_closed=(0, 0, 0, 100)):
        if (img):
            if (isinstance(img, str)):
                if (Path(img).exists() and 
                    ((img[img.index('.'):] == ".png") or (img[img.index('.'):] == ".jpg") or (img[img.index('.'):] == ".jpeg"))):
                    self.img = pygame.image.load(img)
        if (not text):
            self.text = ""
        else:
            self.text = text
        
        self.children = []
        self.child_height = 0
        self.size = size
        self.drop_menu_width = self.size[0]
        self.drop_menu_height = self.size[1]
        self.drop_down_button = DropDownItem(text="Load in a map", parent=self, id_=1, bg_color=drop_button_bg_color)
        self.drop_down_button.z_index = 1
        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.bounding_box = pygame.Rect(0, 0, self.drop_menu_width, self.drop_menu_height)
        self.bg_color_open = bg_color_open
        self.bg_color_closed = bg_color_closed
        self.overlay.fill(self.bg_color_closed)
        self.is_open = False
        
        self.parent_screen_x, self.parent_screen_y = rel_parent_loc
        self.removed_children = 1 # used for scrolling down
        

    def check_children_instances(self):
        if (isinstance(self.children, list)):
            for child in self.children:
                if (not isinstance(child, DropDownItem)):
                    raise BadDropDownItemTypeError
        return

    def add(self, child):
        self.children.append(child)
        
        self.check_children_instances()

    def update_screen(self, screen):
        screen.blit(self.overlay, (self.parent_screen_x, self.parent_screen_y))

    def init_children_shapes(self, width, height):
        if (len(self.children) == 0):
            return
        self.child_height = height
        for child in self.children:
            child.create_shape([0, 0 + (self.children.index(child)*height) + (self.children.index(child)*10), width, height])
            child.index = self.children.index(child)

    def open(self):
        if (len(self.children) == 0):
            return
        #self.overlay.fill((0, 0, 0, 100))
        self.overlay.fill(self.bg_color_open)
        for child in self.children:
            if (child.id == 1):
                continue
            else:
                pygame.draw.rect(self.overlay, child.bg_color, child)
                child.draw_text("medium")

        pygame.draw.rect(self.overlay, self.children[0].bg_color, self.children[0])
        self.children[0].draw_text("large")
            
    def close(self):
        self.overlay.fill(self.bg_color_closed)
        pygame.draw.rect(self.overlay, self.drop_down_button.bg_color, self.drop_down_button)
        self.drop_down_button.draw_text("large")

    def collidepoint(self, point):
        point_rel = (point[0] - self.parent_screen_x, point[1] - self.parent_screen_y)
        return self.bounding_box.collidepoint(point_rel)

    def scroll_down(self,parent_screen):
        
        if (self.children[-1].y <= (self.children[0].height)):
            return
        for child in self.children:
            if (child.id == 1):
                continue
            child.y -= (self.child_height)
        self.close()
        self.open()
        self.update_screen(parent_screen)
        #self.removed_children += 1

    def scroll_up(self,parent_screen):
        
        if (self.children[1].y >= (self.children[0].height)):
            return
        for child in self.children:
            if (child.id == 1):
                continue
            child.y += (self.child_height)
        self.close()
        self.open()
        self.update_screen(parent_screen)
        #self.removed_children += 1


class MapMaker:
    
    def __init__(self, screen_width, screen_height):
        
        self.screen = pygame.display.set_mode((screen_width, screen_height))
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


    def display_text(self, msg, font_key, pos):
        text_surface = self.fonts[font_key].render(msg, True, (0, 0, 0, 255))
        self.screen.blit(text_surface, pos)


    def collect_text_input(self, prompts : list) -> str:

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
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if no_button.collidepoint(mouse_pos):
                            bg = no_button.bg_color
                            r, g, b, a = bg
                            no_button.bg_color = (r, g, b, (2*a % 255)+1)
                            return "NO"

                        if yes_button.collidepoint(mouse_pos):
                            bg = yes_button.bg_color
                            r, g, b, a = bg
                            yes_button.bg_color = (r, g, b, (2*a % 255)+1)
                            return "YES"
                        

            pygame.time.Clock().tick(5)
                        
            for prompt in prompts:
                self.display_text(*prompt)
            #self.display_text(collected_text, "large", (, 50))
            yes_button.draw("large")
            yes_button.put_in(self.screen, ((len_last_prompt)*12 + 400, 50))
            no_button.draw("large")
            no_button.put_in(self.screen, (400 + ((len_last_prompt)*12) + yes_button.width + 50, 50))
            pygame.display.flip()

    def run_start_menu(self) -> None: # TODO

        drop_down = DropDownList(rel_parent_loc=(0,0), bg_color_open=pygame.Color(0, 0, 0, 10), bg_color_closed=(0, 0, 0, 0))
        map_files = [map_ for map_ in Path("maps/").iterdir() if map_.is_file()]
        items = [DropDownItem(text=f"{map_}", parent=drop_down) for map_ in map_files]
        #items = [DropDownItem(text=f"item {i}", parent=drop_down) for i in range(3)]
        drop_down.init_children_shapes(drop_down.drop_menu_width, 25)
        
        #drop_down.close()
        while (self.start_menu_running):
            self.screen.fill(self.colors["white"])
            for event in pygame.event.get():
                if (event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL]):
                        
                        if (event.type == pygame.MOUSEBUTTONDOWN):
                            mouse_pos = event.pos
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
                                        overwrite_previous_map_version_response = self.collect_text_input(prompts)
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
                    if (event.key == pygame.K_q):
                        self.running = True
                        self.start_menu_running = False
                    elif (event.key == pygame.K_o):
                        drop_down.open()
                    elif (event.key == pygame.K_c):
                        drop_down.close()
                    
                if (event.type == pygame.QUIT):
                    self.running = True
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
        with open(f"{map_name}", "r") as file:
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

        pygame.quit()

game_map = MapMaker(1000, 800)


game_map.running_loop()
file_ = {"Rect":{}, "Circle":{}}


for obj, color in game_map.obstacles_.items():
    if isinstance(obj, ObstacleRect):
        file_["Rect"][f"{obj}"] = f"{color}"
    elif isinstance(obj, ObstacleCircle):
        obj.radius = nint(obj.radius)
        file_["Circle"][f"{obj}"] = f"{color}"

file_name = ""
if (game_map.loaded_in_a_map):
    file_name = game_map.loadded_in_map
    with open(f"{file_name}", "w") as file:
        json.dump(file_, file, indent=4)
else:
    file_name = input("name your map: ")
    with open(f"maps/{file_name}.json", "w") as file:
        json.dump(file_, file, indent=4)
