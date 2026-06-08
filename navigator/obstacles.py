from pygame import Rect
from navigator.node import Node

class ObstacleRect (Rect):

    def __init__(self, *args):
        super().__init__(*args)

    def collidepoint(self, node : Node | tuple | list) -> bool:
        if (isinstance(node, Node)):
            point = node.point
        elif (isinstance(node, (tuple, list))):
            point = node
        else:
            raise TypeError(f"In {self.collidepoint}, argument node is of typle {type(node)}")
        return super().collidepoint(point)

    def __hash__(self):
        return (self.topleft + self.size).__hash__()

    def move(self, new_loc):
        self.topleft = new_loc
        return
    
    def __str__(self):
        return f"{self.x}, {self.y}, {self.w}, {self.h}"

class ObstacleCircle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def collidepoint(self, node : Node) -> bool:
        x, y = node.point
        cx, cy = self.center
        if ((((cx - x)*(cx - x)) + ((cy - y)*(cy - y))) <= (self.radius*self.radius)):
            return True
        return False
        
    def __hash__(self):
        return hash((self.center, self.radius))

    def move(self, new_loc):
        self.center = new_loc
        return

    def __str__(self):
        return f"{self.center}, {self.radius}"
