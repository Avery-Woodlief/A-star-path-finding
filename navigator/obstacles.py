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

    def collidepoint(self, node : Node | tuple) -> bool:
        if (isinstance(node, Node)):
            x, y = node.point
        elif (isinstance(node, tuple)):
            x, y = node
        else:
            raise ValueError(f"node is of type {type(node)}\nWhich is neither of type {type(Node)} nor of type {type(tuple)}\n")
        cx, cy = self.center
        if ((((cx - x)*(cx - x)) + ((cy - y)*(cy - y))) <= (self.radius*self.radius)):
            return True
        return False

    def clipline(self, start, end):
        px, py = start
        qx, qy = end
        cx, cy = self.center

        dx = qx - px
        dy = qy - py

        if dx == 0 and dy == 0:
            return (cx - px)**2 + (cy - py)**2 <= (self.radius)**2

        t = ((cx - px)*dx + (cy - py)*dy) / (dx*dx + dy*dy)

        # clamp to segment
        t = max(0, min(1, t))

        nearest_x = px + t*dx
        nearest_y = py + t*dy

        return ((nearest_x - cx)**2 + (nearest_y - cy)**2) <= (self.radius)**2
        
    def __hash__(self):
        return hash((self.center, self.radius))

    def move(self, new_loc):
        self.center = new_loc
        return

    def __str__(self):
        return f"{self.center[0]}, {self.center[1]}, {self.radius}"
