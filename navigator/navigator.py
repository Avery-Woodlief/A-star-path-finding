from exceptions.navigator_errors import *
from navigator.obstacles import *
from navigator.node import Node
from itertools import product
from math import floor, ceil, sqrt
import math
from pygame import Rect
from random import randint, choice
import os
#from itertools import combinations
import pygame





def dist(nodeA : Node, nodeB : Node) -> float:
    return math.dist(nodeA.point, nodeB.point)

nint = lambda x: (floor(x + 0.5) + ceil((2*x - 1)/4) - floor((2*x - 1)/4) - 1) # nearest integer function



def line_intersection_circle_x(circle_center, line_slope, search_radius):

    '''
    This function returns the solutions for x after plugging
        y = s_2_ + m*(x - s_1_) into
        (x - h)^2 + (y - k)^2 = r^2
    '''

    h, k = circle_center

    m = line_slope
    r = search_radius

    first_part = ((h) + (k)*(m)) + (((m)**2)*(h)) - ((m)*(k))
    sqrt_part = sqrt((-((h)**2)*((m)**2)) + (2*(h)*(k)*(m)) + (2*(h)*((m)**2)*(h)) - (2*(h)*(m)*(k)) - ((k)**2) - (2*(k)*(m)*(h)) + (2*(k)*(k)) + (((m)**2)*((r)**2)) - (((m)**2)*((h)**2)) + (2*(m)*(h)*(k)) + ((r)**2) - ((k)**2))
    divisor_part = (((m)**2) + 1)

    x1 = (first_part - sqrt_part)/divisor_part
    x2 = (first_part + sqrt_part)/divisor_part

    return [x1, x2]


def get_points_from_solved_x(line_slope, x_sols, circle_center):
    '''
    Returns points of intersection between circle - with center 'circle_center' - and 
    line with slope 'line_slope'. Then rounds to the nearest integer using 'nint'.
    '''
    m = line_slope
    h, k = circle_center
    y1 = nint(int(k) + m * (x_sols[0] - int(h)))
    y2 = nint(int(k) + m * (x_sols[1] - int(h)))
    
    return [(nint(x_sols[0]), y1), (nint(x_sols[1]), y2)]


class BaseNavigationShape:
    '''
    Base Class for 'Navigator' helper classes.
    Note: Class 'Line' does not need the inheritance.
    '''

    def __init__(self):
        self.nodes = []

    def __contains__(self, node : Node) -> bool:
        return node in self.nodes

    def __iter__(self) -> iter:
        return iter(self.nodes)

    def __str__(self) -> str:
        try:
            string = f"{self.nodes[0]}"
        except (IndexError):
            return ""
        for i in range(1, len(self.nodes)):
            string += f", {self.nodes[i]}"
        return string

    def get_integer_points(self):
        pass

class Line:
    '''
    Helper class for 'Navigator' class.
    Makes line segment from 'start_point' to 'end_point'.
    Is able to check collision with other obstacles on map and is used to build segment from center of 'radar' to border of 'radar' using
    the slope of a legal 'Node'.
    Each Node on the border of the radar corresponds to two seperate line segments (opposite directions): one in northern hemisphere of radar
                                                                                                          one in southern hemisphere of radar
    '''

    def __init__(self, start_point, end_point):
        self.start = start_point
        self.end = end_point

    def colliderect(self, rect : Rect) -> bool:
        return bool(rect.clipline(self.start, self.end))

    def collidecircle(self, circle : ObstacleCircle) -> bool:
        return bool(circle.clipline(self.start, self.end))


class Circle (BaseNavigationShape):
    '''
    'Circle (BaseNavigationShape)' is used as a radar tool for 'Navigator'.
    '''

    def __init__(self, center, radius):
        super().__init__()
        self.center = center
        self.radius = radius
        self.get_integer_border_points()


    def collidepoint(self, point):
        x, y = self.center
        p1, p2 = point
        if (p1-x)**2 + (p2-y)**2 <= (self.radius)**2:
            return True
        return False

    def on_border(self, point):
        cx, cy = self.center
        x, y = point
        if (((cx - x)**2 + (cy - y)**2) == (self.radius)**2):
            return True
        return False

    def get_integer_border_points(self):
        cx, cy = self.center
        for x in range(cx - self.radius, cx + self.radius + 1):
            for y in range(cy - self.radius, cy + self.radius + 1):
                point = (x, y)
                if self.on_border(point):
                    self.nodes.append(Node(point))

    def get_integer_points(self):

        cx, cy = self.center
        for x in range(cx - self.radius, cx + self.radius + 1):
            for y in range(cy - self.radius, cy + self.radius + 1):
                point = (x, y)
                if (self.collidepoint(point)):
                    #print(point)
                    self.nodes.append(Node(point))
        return

    def __getitem__(self, index):
        return self.nodes[index]

    def __len__(self):
        return len(self.nodes)

    def __str__(self):
        return f"{self.center} : {self.radius}"

class Navigator:

    def __init__(self, start : Node | tuple | list, target : Node | tuple | list, obstacles = None):

        self.start = None
        self.target = None
        if (obstacles != None):
            if (not isinstance(obstacles, dict)):
                raise TypeError(f" obstacles type is {type(obstacles)}\n\tNot a dict")
            else:
                if (len(obstacles["Rect"].keys()) > 0):
                    for rect in obstacles["Rect"]:
                        if (not isinstance(rect, ObstacleRect)):
                            raise TypeError(f"bad obstacle rect type in nonempty {type(obstacles)}\n\tExpected: {type(ObstacleRect)}\n\tFound: {type(rect)}")        
                else: # if empty dict then set to None
                    obstacles = None
        self.obstacles = obstacles
        
        
        if (isinstance(start, Node)):
            self.start = start
        elif (isinstance(start, (tuple, list))):
            self.start = Node(start)
        else:
            raise TypeError(f"start is of type {type(start)}\n\tNeither tuple, list, nor Node")

        if (isinstance(target, Node)):
            self.target = target
        elif (isinstance(target, (tuple, list))):
            self.target = Node(target)
        else:
            raise ValueError

        self.current = self.start                                                   
        self.search_radius = 50                                                                                                     
        self.exploration_radius = 30                                               
        self.greedy_radius = 50                                                     
        self.center_x, self.center_y = self.current.point                           
                  
        self.tolerance = 10                                                         
        self.is_stuck = False                                                       
        self.initial_dist = dist(self.current, self.target)             
        self.curr_dist_to_target = dist(self.current, self.target)      
        self.prev_dist_to_target = dist(self.current, self.target)      

        self.movement = self.curr_dist_to_target - self.prev_dist_to_target
        self.rolling_total_movements = self.movement
        self.rolling_movement_average = self.rolling_total_movements/1
        
        self.recent_improvements = []              
        '''
        The variable self.recent_improvements stores at most 'self.stuck_window' values.
        Each of the said values in this list is the distance between self.current and self.target.
        The distances vary because self.current varies whenever Navigator traverses to a node.
        '''                                 
        self.min_window_improvement = 50
        '''
        The variable self.min_window_improvement is lower bound of sum(self.recent_improvements).
        Used as part of condition with identifyiing if Navigator is stuck and goes into a loop of wanting to use greedy
        algorithm but cannot actually traverse to the cheapest node (because an obstacle is in the way.)
        '''
        self.stuck_window = 5                                                 
        self.progress = 0                                                           
        self.dist_moved = 0                                                         
        self.stuck_counter = 0                                                      
        self.dist_improvement = 0                                                   
        self.stuck_limit = 2  
        self.current_stride = 0
        self.radar = Circle((self.start[0], self.start[1]), self.search_radius)
        #self.update_radar()
        '''
        The goal of using a radar is to be able to build lines from current node to border of the radar, in the direction
        of nodes on the border of the circle that is radar.
        Then checks if any of those lines collide with obstacles on the map. Saves computation as opposed to doing nodes inside the radar.
        '''
        #self.update_radar()        
        self.escaping = False                                                      
        self.path = [self.start]                                                   
        #self.nodes_that_made_navigator_stuck = []
        #self.areas_seen = {} # areas of previous radars to not go to the same legal node more than one time               
        #self.areas_memory = []
        self.visited_areas = []
        self.visited_areas_memory_capacity = 32
        self.expand_factor = 1.05
        self.compress_factor = 0.95
        self.search_radius_upper_bound = 100
        self.search_radius_lower_bound = 10
        # FOR DRAWING ONLY

        self.next_point_for_drawing = self.current     

        #
                            
        self.step_count = 1                                                      

    def get_neighbors_of_node(self, node, stride):
        '''returns adjacent and diagonal neighbors of specified node with a stride of 'stride'.'''
        saved = self.current
        self.current = node
        neighbors = self.get_neighbors_of_current(stride)
        self.current = saved
        return neighbors

    def get_neighbors_of_current(self, stride):
        '''returns adjacent and diagonal neighbors of current node (the node the Navigator is currently traversed on) with a stride of 'stride'.'''
        x, y = self.current.point
        up      = Node((x, y - stride))
        down    = Node((x, y + stride))
        left    = Node((x - stride, y))
        right   = Node((x + stride, y))
        main_diag_up = Node((x - stride, y - stride))
        main_diag_down = Node((x + stride, y + stride))
        oppisite_diag_up = Node((x + stride, y - stride))
        oppisite_diag_down = Node((x - stride, y + stride))
        nodes = [
                    up, 
                    down, 
                    left, 
                    right,
                    main_diag_up,
                    main_diag_down,
                    oppisite_diag_up,
                    oppisite_diag_down,
                ]
        return nodes


    def in_visited_area(self, node):
        # Here center is of type Node
        for center, radius in self.visited_areas:
            if dist(node, center) <= radius:
                return True

        return False
    
    def update_movement(self, next):
        '''
        stores information relating to the relative movement of 'Navigator' and updates the current 'Node', then puts the next Node in path variable.
        Note:   if self.dist_improvement < 0, then doing worse than before
                if self.dist_improvement > 0, then now doing better
        '''
        self.prev_dist_to_target = self.curr_dist_to_target

        self.dist_moved = dist(self.current, next)
        
        

        self.path.append(next)
        self.current = next

        if (len(self.visited_areas) > self.visited_areas_memory_capacity):
            self.visited_areas.remove(self.visited_areas[0])
        self.visited_areas.append((self.current, nint(self.search_radius/4)))

        self.curr_dist_to_target = dist(self.current, self.target)
        self.dist_improvement = self.prev_dist_to_target - self.curr_dist_to_target
        
        self.movement = abs(self.dist_improvement)
        


    def optimize_costs(self, nodes):
        '''
        Cost is calculate as a sum of two different expenses.
        The first expense is the distance between the current node and the node to traverse to.
        The second expense is the distance between the node to traverse to and the target node which 'Navigator' is searching for.
        The optimized cost is the minimum of these sums between all the nodes in 'nodes'.
        '''
        f_costs = {self.current.calc(node, self.target) : node for node in nodes}
        try:
            min_f_cost = min(f_costs.keys())
        except (ValueError):
            return
        next = f_costs[min_f_cost]
          
        self.update_movement(next)
       
        return


    def obstacle_free(self, stride):
        '''
        No obstacles in map so just needs to the direct neighbors (adjacent and diagonal).
        '''
        nodes = self.get_neighbors_of_current(stride)
        self.optimize_costs(nodes)

    def node_collides(self, node : Node | tuple | list) -> bool:
        '''
        returns True if the specified node of 'Node' type collides with an obstacle on the map.
        returns False otherwise.
        '''
        for obstacle in self.obstacles["Rect"]:
            if (obstacle.collidepoint(node)):
                return True
        for obstacle in self.obstacles["Circle"]:
            if (obstacle.collidepoint(node)):
                return True
        return False

    def line_collides(self, line : Line) -> bool:
        '''
        returns True if the specified line of 'Line' type collides with an obstacle on the map.
        returns False otherwise.
        '''
        for obstacle in self.obstacles["Rect"]:
            if (line.colliderect(obstacle)):
                return True
        for obstacle in self.obstacles["Circle"]:
            if (line.collidecircle(obstacle)):
                return True
        return False


    def update_radar(self):
        '''
        changes radar to a circle of center self.current and using radius of self.search_radius.
        '''
        #print("UPDATING RADAR")
        current_x = self.current.point[0]
        current_y = self.current.point[1]
        target_x = self.target.point[0]
        target_y = self.target.point[1]
        
        if (current_x < target_x):
            self.center_x = current_x + self.current_stride
        elif (current_x > target_x):
            self.center_x = current_x - self.current_stride
        
        if (current_y < target_y):
            self.center_y = current_y + self.current_stride
        elif (current_y > target_y):
            self.center_y = current_y - self.current_stride
        
        
        if ((self.center_x != None) and (self.center_y != None)):
            #print(f"SEARCH RADIUS: {self.search_radius}")
            self.radar = Circle((self.center_x, self.center_y), self.search_radius)
        
        return

    def is_legal_southern_node(self, node):
        '''
        Checks if node in the direction of the southern hemisphere is legal for traversal.
        '''
        line_southern_hem = Line(self.current.point, node.point)
        southern_hem_collide = self.line_collides(line_southern_hem)

        

        if ((not southern_hem_collide) 
            and not (node in self.path)):
            #and not (node in self.nodes_that_made_navigator_stuck)):
            return True
        return False

    def is_legal_northern_node(self, node):
        '''
        Checks if node in the direction of the northern hemisphere is legal for traversal.
        '''
        line_northern_hem = Line(self.current.point, node.point)
        northern_hem_collide = self.line_collides(line_northern_hem)


        if ((not northern_hem_collide) 
            and not (node in self.path)):
            #and not (node in self.nodes_that_made_navigator_stuck)):
            return True
        return False


    def change_radius(self):


        for node in self.radar:
            line_northern_hem = Line(self.current.point, node.point)
            northern_hem_collide = self.line_collides(line_northern_hem)
            line_southern_hem = Line(self.current.point, node.point)
            southern_hem_collide = self.line_collides(line_southern_hem)

            if (northern_hem_collide):
                self.search_radius = nint(self.search_radius * self.compress_factor)
            else:
                self.search_radius = nint(self.search_radius * self.expand_factor)
                

            if (southern_hem_collide):
                self.search_radius = nint(self.search_radius * self.compress_factor)
            else:
                self.search_radius = nint(self.search_radius * self.expand_factor)


            while (self.search_radius >= self.search_radius_upper_bound):
                self.search_radius = nint(self.search_radius * self.compress_factor)

            while (self.search_radius <= self.search_radius_lower_bound):
                self.search_radius = nint(self.search_radius * self.expand_factor)
            
        return

    def get_legal_nodes(self, query_visited = False):
        allowed_nodes = []
        for node in self.radar:
           
            #if self.in_seen_area(node) and (node != self.current):
            #    print("!")
            #    continue
            if (query_visited):
                if (self.in_visited_area(node)):
                    continue
            
            if (not (node[0] == self.current[0])):
                line_slope = (node[1] - self.current[1])/(node[0] - self.current[0])

                x_sols = line_intersection_circle_x(self.current.point, line_slope, self.search_radius)
                end_points = get_points_from_solved_x(line_slope, x_sols, self.current.point)

                southern_hem_node = Node(end_points[0])
                northern_hem_node = Node(end_points[1])
                
                if self.is_legal_southern_node(southern_hem_node):
                    allowed_nodes.append(southern_hem_node)

                if self.is_legal_northern_node(northern_hem_node):
                    allowed_nodes.append(northern_hem_node)
        self.change_radius()
        return allowed_nodes

    def find_f_cost_optimized_unexplored_node(self):
        nodes = self.get_legal_nodes(query_visited=True)
        if (len(nodes) > 0):
            self.optimize_costs(nodes)
        else:
            saved_search_radius = self.search_radius
            
            while (len(nodes) == 0):
                self.search_radius = nint(self.search_radius * self.expand_factor)
                self.update_radar()
                nodes = self.get_legal_nodes(query_visited=True)

            #self.search_radius = saved_search_radius
            self.optimize_costs(nodes)
        return

    def careful_step(self):

        '''
        Uses greedy algorithm to traverse to node with minimum 'F_cost' cost - see 'Node.py'.
        This cannot be used all the time because sometimes minimum cost is directly through a obstacle so must then change state to explore.
        '''
        
        allowed_nodes = self.get_legal_nodes(query_visited=True)
        
        self.next_point_for_drawing = self.current
        

        if (len(allowed_nodes) > 0):
            self.optimize_costs(allowed_nodes)
        else:
            self.find_f_cost_optimized_unexplored_node()
            while (self.search_radius > self.search_radius_upper_bound):
                self.search_radius = nint(self.search_radius * self.compress_factor)
        
        return
        

    def find_random_unexplored_node(self):
        
        
        nodes = self.get_legal_nodes(query_visited=True)
        if (len(nodes) > 0):
            return choice(nodes)
        else:
            saved_search_radius = self.search_radius
            
            while (len(nodes) == 0):
                self.search_radius = nint(self.search_radius * self.expand_factor)
                self.update_radar()
                nodes = self.get_legal_nodes(query_visited=True)

            #self.search_radius = saved_search_radius
            return choice(nodes)


    def explore(self):
        '''
        Used when greedy algorithm fails.
        Randomly picks a node from a list of legal nodes.
        '''
        allowed_nodes = self.get_legal_nodes(query_visited=True)
            
           
            
            

        #next = allowed_nodes[randint(0, len(allowed_nodes)-1)]
        unvisited_nodes = [node for node in allowed_nodes if not self.in_visited_area(node)]

        if len(unvisited_nodes) > 0:
            next = choice(unvisited_nodes)
        else:
            
            next = self.find_random_unexplored_node()
            while (self.search_radius > self.search_radius_upper_bound):
                self.search_radius = nint(self.search_radius * self.compress_factor)

        #next = choice(allowed_nodes)
        self.update_movement(next)
        return

    def step(self):
        '''
        Iteration of each node traversal (not recursive).
        '''

        # FOR NAVIGATOR LOG

        try:
            self.progress = ((self.initial_dist - self.dist_moved) / self.initial_dist) * 100
        except ZeroDivisionError:
            self.progress = "NA"

        #
        previous_position = self.current
        if not self.obstacles:
            self.obstacle_free(stride=1)
        else:
            if self.is_stuck:
                #self.search_radius = self.exploration_radius
                
                self.escaping = True
                self.current_stride = 1
                self.explore()

            elif dist(self.current, self.target) > self.tolerance:
                #self.search_radius = self.greedy_radius
                self.current_stride = 1
                self.careful_step()
            else:
                #self.search_radius = self.greedy_radius
                self.current_stride = 1
                self.careful_step()
        current_position = self.current

        did_not_move = False

        if (previous_position == current_position):
            print("did not move this step")
            self.is_stuck = True
            did_not_move = True
            self.stuck_counter = 0
        
        # update stuck state after movement happens
        self.recent_improvements.append(self.dist_improvement)

        if len(self.recent_improvements) > self.stuck_window:
            # discard oldest improvement to get a new one in
            self.recent_improvements.pop(0)

        if len(self.recent_improvements) == self.stuck_window:
            total_improvement = sum(self.recent_improvements)

            if total_improvement < self.min_window_improvement:
                                    
                self.update_stuck_status()
            elif (not did_not_move):
                self.is_stuck = False
                self.escaping = False
                
        prev_rolling_movement_average = self.rolling_movement_average
        self.step_count += 1
        self.rolling_total_movements += self.movement
        self.rolling_movement_average = self.rolling_total_movements/self.step_count
        #self.areas_seen[Node(self.radar.center)] = self.search_radius//4
        #self.areas_memory.append(Circle(self.radar.center, self.search_radius//4))
        self.update_radar()
        return

    def update_stuck_status(self) -> None:
        '''
        If allowance of times Navigator has fallen below lower bound of sum(self.recent_improvements) self.stuck_limit times,
        then the Navigator identifies itself as being stuck and changes from greedy algorithm to exploration.
        Otherwise increases (by 1) the number of times it has fallen below the lower bound.
        '''
        if (self.stuck_counter >= self.stuck_limit):
            self.is_stuck = True
            #self.nodes_that_made_navigator_stuck.append(self.current)
            
            #self.update_radar()
            self.stuck_counter = 0
        else:
            self.stuck_counter += 1
        

    def __str__(self):
        '''
        Converts the path of Navigator to a string which is list of CSV of tuples which are points that the Navigator has traversed to.
        '''
        string = f"{self.start}"
        for node in self.path:
            if (node == self.start):
                continue
            string += f", {node}"

        return string
