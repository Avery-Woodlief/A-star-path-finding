from navigator.obstacle import Obstacle
from navigator.node import Node
from itertools import product
from math import floor, sqrt, dist


class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.nodes = []
        self.get_integer_points()
        #print(self.nodes, self.center, self.radius)

    def collidepoint(self, point):
        x, y = self.center
        p1, p2 = point
        if (p1-x)**2 + (p2-y)**2 <= (self.radius)**2:
            return True
        return False

    def __contains__(self, node : Node) -> bool:
        return node in self.nodes

    def __iter__(self) -> iter:
        return iter(self.nodes)

    def __str__(self):
        try:
            string = f"{self.nodes[0]}"
        except (IndexError):
            return ""
        for i in range(1, len(self.nodes)):
            string += f", {self.nodes[i]}"
        return string

    def get_integer_points(self):
        #for point in product(range(-(self.radius**2), ((self.radius + 1)**2)), repeat=2):
            #print(point)
        cx, cy = self.center
        for x in range(cx - self.radius, cx + self.radius + 1):
            for y in range(cy - self.radius, cy + self.radius + 1):
                point = (x, y)
                if (self.collidepoint(point)):
                    #print(point)
                    self.nodes.append(Node(point))
        return

class Navigator:

    def __init__(self, start : Node | tuple | list, target : Node | tuple | list, obstacles = None):

        self.start = None
        self.target = None
        if (obstacles != None):
            if (not isinstance(obstacles, (list, tuple))):
                raise TypeError(f" obstacles type is {type(obstacles)}\n\tNeither tuple nor list")
            else:
                if (len(obstacles) > 0):
                    for obstacle in obstacles:
                        if (not isinstance(obstacle, Obstacle)):
                            raise TypeError(f"bad obstacle type in nonempty {type(obstacles)}\n\tExpected: {type(Obstacle)}\n\tFound: {type(obstacle)}")
                else: # if empty list or empty tuple then set to None
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
        self.search_radius = 15
        self.radar = Circle(self.current.point, self.search_radius)
        self.tolerance = 100
        self.path = [self.start]
        
        self.step_count = 0

    def get_neighbors_of_node(self, node, stride):
        saved = self.current
        self.current = node
        neighbors = self.get_neighbors_of_current(stride)
        self.current = saved
        return neighbors

    def get_neighbors_of_current(self, stride):
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

    def optimize_costs(self, nodes):
        f_costs = {self.current.calc(node, self.target) : node for node in nodes}
        try:
            min_f_cost = min(f_costs.keys())
        except (ValueError):
            return
        next = f_costs[min_f_cost]
        self.path.append(next)
        self.current = next


    def obstacle_free(self, stride):
        nodes = self.get_neighbors_of_current(stride)
        self.optimize_costs(nodes)

    def node_collides(self, node : Node | tuple | list) -> bool:
        for obstacle in self.obstacles:
            if (obstacle.collidepoint(node)):
                #print("collision")
                return True
        return False

    def update_radar(self, stride):
        center_x = None
        center_y = None
        current_x = self.current.point[0]
        current_y = self.current.point[1]
        target_x = self.target.point[0]
        target_y = self.target.point[1]
        if (current_x < target_x):
            center_x = current_x + stride
        elif (current_x > target_x):
            center_x = current_x - stride
        
        if (current_y < target_y):
            center_y = current_y + stride
        elif (current_y > target_y):
            center_y = current_y - stride
        
        
        if ((center_x != None) and (center_y != None)):
            self.radar = Circle((center_x, center_y), self.search_radius)
        return

    def careful_step(self, stride):
        #print("careful!")
        #nodes = self.get_neighbors_of_current(stride)
        if (self.step_count % 3 == 0):
            self.update_radar(stride) # direct neighbors of self.current are in radar now
        allowed_nodes = []
        #print(self.radar)
        print(f"stide = {stride}")
        for node in self.radar:
            
            #neighbors = self.get_neighbors_of_node(self.current, stride)
                
            collide = self.node_collides(node)
            
                
            if ((not collide) and not (node in self.path)):
                allowed_nodes.append(node)
        
        self.optimize_costs(allowed_nodes)
        return

    def step(self):
        self.step_count += 1
        if (not self.obstacles):
            self.obstacle_free(stride = 1)
            return
        else:
            print(dist(self.current.point, self.target.point))
            if (dist(self.current.point, self.target.point) > self.tolerance):
                print("impatient")
                self.careful_step(stride = 10)
            else:
                self.careful_step(stride = 1)
            
            return

    def __str__(self):
        string = f"{self.start}"
        for node in self.path:
            if (node == self.start):
                continue
            string += f", {node}"

        return string




