#from int32.int32 import *
from math import dist

class Node: pass

class NodeHelper:

    @classmethod
    def calculate_h_cost(cls, func):
        def check_type(cls, value):
            if (not isinstance(value, (Node, list, tuple))):
                raise TypeError
            value_point = None
            if (isinstance(value, Node)):
                value_point = value.point
            elif (isinstance(value, (list, tuple))):
                value_point = tuple(value)
            elif (value_point == None):
                return ValueError("need next point to be of not NoneType")
            cls.H_cost = dist(cls.point, value_point)
            return dist(cls.point, value_point)
        return check_type

    @classmethod
    def calculate_g_cost(cls, func):
        def check_type(cls, value):
            if (not isinstance(value, (Node, list, tuple))):
                raise TypeError
            value_point = None
            if (isinstance(value, Node)):
                value_point = value.point
            elif (isinstance(value, (list, tuple))):
                value_point = tuple(value)
            elif (value_point == None):
                return ValueError("need next point to be of not NoneType")
            cls.G_cost = dist(cls.point, value_point)
            return dist(cls.point, value_point)
        return check_type

class Node (NodeHelper):

    def __init__(self, point : tuple | list):
        #self.point = Int32(point)
        self.point = point
        self.G_cost = -1.0
        self.H_cost = -1.0
        self.F_cost = -1.0

    @NodeHelper.calculate_h_cost
    def calc_H_cost(self, target : Node | list | tuple) -> float:
        pass
    
    @NodeHelper.calculate_g_cost
    def calc_G_cost(self, next : Node | list | tuple) -> float:
        pass
         
    def calc(self, next : Node | list | tuple, target : Node | list | tuple) -> float:
        self.calc_G_cost(next)
        
        self.F_cost = self.G_cost + next.calc_H_cost(target)
        return self.F_cost

    def __eq__(self, other : Node) -> bool:
        if (self.point[0] == other.point[0] and
            self.point[1] == other.point[1]):
            return True
        return False

    def __str__(self):
        return f"{self.point}"

    def __getitem__(self, index):
        return self.point[index % len(self.point)]

    def __hash__(self):
        return (self.point[0], self.point[1]).__hash__()
