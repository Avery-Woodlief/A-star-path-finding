from navigator.obstacles import *
import json
import pygame

pygame.init()

class MapMaker:
    
    def __init__(self, screen_width, screen_height):
        
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.obstacles_ = {}
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

        self.screen.fill(self.colors["white"])

        self.running = True
        self.began_drag = False
        self.end_drag = False
        self.start = None
        self.width = None
        self.height = None
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

    def dragging_check(self, event):
        if (self.began_drag and not self.end_drag):
            #print("dragging")
            if (event.type == pygame.MOUSEMOTION):
                self.width = abs(self.start[0] - event.pos[0])
                self.height = abs(self.start[1] - event.pos[1])
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 1))  # clears overlay to transparent
                self.screen.blit(overlay, (min(self.start[0], event.pos[0]),min(self.start[1], event.pos[1])))
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

    def handle_mouse_event(self, event):
        if (event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]):
            print("mouse moving")
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == 1 and self.more_control):
                    print("began edit dragging")
                    for obj in self.obstacles_:
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
                        
                        
                if (event.button == 3):
                    if (not self.began_drag):
                        print("began dragging")
                        self.end_drag = False
                        self.began_drag = True
                        self.start = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if (self.edit_began_drag):
                self.edit_began_drag = False
                self.edit_end_drag = True
                self.obstacles_[self.focused_obj] = self.colors["black"]

            if (self.began_drag):
                self.began_drag = False
                self.end_drag = True
                self.width = abs(self.start[0] - event.pos[0])
                self.height = abs(self.start[1] - event.pos[1])
                size = (self.width, self.height)
                
                new_rect = ObstacleRect((min(self.start[0], event.pos[0]),min(self.start[1], event.pos[1])), size)
                self.obstacles_[new_rect] = self.colors["black"]

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
                    print("pressed 1")
                elif (event.key == pygame.K_2):
                    print("pressed 2")
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
        while (self.running):
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
                    pygame.draw.rect(self.screen, self.obstacles_[obj], obj)
                pygame.display.flip()

        pygame.quit()

game_map = MapMaker(1000, 800)
game_map.running_loop()
file_ = {"Rect":{}}


for obj, color in game_map.obstacles_.items():
    file_["Rect"][f"{obj}"] = f"{color}"

file_name = input("name your map: ")



with open(f"maps/{file_name}.json", "w") as file:
    json.dump(file_, file, indent=4)
