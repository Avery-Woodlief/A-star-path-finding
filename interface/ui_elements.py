from exceptions.ui_errors import *
import pygame

class SimpleButton(pygame.Rect):

    def __init__(self, args, text, bg_color=(0, 0, 255, 100), id_=None, parent=None):
        super().__init__(*args)
        self.z_index = 0
        self.text = text
        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.fonts = {
                "small": pygame.font.Font(None, 12),
                "medium": pygame.font.Font(None, 24),
                "large": pygame.font.Font(None, 36)
            }
        self.bg_color = bg_color
        self.loc_rel_parent = None
        self.id = id_
        self.parent = parent
        if (self.parent != None):
            self.parent.add(self)
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
                 drop_button_bg_color=pygame.Color(0, 255, 0, 100), bg_color_open=(0, 0, 0, 100), bg_color_closed=(0, 0, 0, 100),
                 drop_button_rect_args=(0, 0, 400, 50)):
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
        #self.drop_down_button = DropDownItem(text=text, parent=self, id_=1, bg_color=drop_button_bg_color)
        self.drop_down_button = SimpleButton(drop_button_rect_args, text=text, bg_color=drop_button_bg_color, id_=1, parent=self)
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
                if (not isinstance(child, (SimpleButton, DropDownItem))):
                    raise BadDropDownItemTypeError
        return

    def add(self, child):
        child.index = len(self.children)
        self.children.append(child)
        
        self.check_children_instances()

    def update_screen(self, screen):
        
        screen.blit(self.overlay, (self.parent_screen_x, self.parent_screen_y))

    def init_children_shapes(self, width, height):
        if (len(self.children) == 0):
            return
        self.child_height = height
        for child in self.children:
            
            if (child.id == 1):
                child.put_in(self.overlay, (0, 0))
            else:
                child.create_shape([0, 0 + (self.children.index(child)*height) + (self.children.index(child)*10), width, height])
            #child.index = self.children.index(child)

    def open(self):
        if (len(self.children) == 0):
            return
        #self.overlay.fill((0, 0, 0, 100))
        self.overlay.fill(self.bg_color_open)
        for child in self.children:
            if (child.id == 1):
                continue
            pygame.draw.rect(self.overlay, child.bg_color, child)
            pygame.draw.rect(self.overlay, (0, 0, 0), child, width=2)
            child.draw_text("medium")

        #pygame.draw.rect(self.overlay, self.children[0].bg_color, self.children[0], width=2)
        self.drop_down_button.put_in(self.overlay, (0, 0))
        self.drop_down_button.draw("large")
            
    def close(self):
        self.overlay.fill(self.bg_color_closed)
        #pygame.draw.rect(self.overlay, (0, 0, 0), self.drop_down_button, width=2)
        self.drop_down_button.put_in(self.overlay, (0, 0))
        self.drop_down_button.draw("large")

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
