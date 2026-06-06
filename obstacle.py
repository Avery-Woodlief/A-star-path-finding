from pygame import Rect
from node import *

class Obstacle (Rect):

    def __init__(self, *args):
        super().__init__(*args)

    def collidepoint(self, node : Node):
        point = node.point
        return super().collidepoint(point)

    def __hash__(self):
        return (self.topleft + self.size).__hash__()

    def move(self, new_loc):
        self.topleft = new_loc
        return
    
    def __str__(self):
        return f"{self.x}, {self.y}, {self.w}, {self.h}"
