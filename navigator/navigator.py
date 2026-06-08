from navigator.obstacle import Obstacle
from navigator.node import Node
from itertools import product
from math import floor, ceil, sqrt, dist, pi
from pygame import Rect
from random import randint
from itertools import combinations
#import pygame

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
    m = line_slope
    h, k = circle_center
    y1 = nint(int(k) + m * (x_sols[0] - int(h)))
    y2 = nint(int(k) + m * (x_sols[1] - int(h)))
    
    return [(nint(x_sols[0]), y1), (nint(x_sols[1]), y2)]


class BaseNavigationShape:

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

    def __init__(self, start_point, end_point):
        self.start = start_point
        self.end = end_point

    def colliderect(self, rect : Rect) -> bool:
        return bool(rect.clipline(self.start, self.end))


class Circle (BaseNavigationShape):

    def __init__(self, center, radius):
        super().__init__()
        self.center = center
        self.radius = radius
        self.get_integer_points()
        #print(self.nodes, self.center, self.radius)

    def collidepoint(self, point):
        x, y = self.center
        p1, p2 = point
        if (p1-x)**2 + (p2-y)**2 <= (self.radius)**2:
            return True
        return False

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
        self.search_radius = 50
        self.center_x, self.center_y = self.current.point
        self.radar = Circle(self.current.point, self.search_radius)
        self.tolerance = 10
        self.is_stuck = False
        self.initial_dist = dist(self.current.point, self.target.point)
        self.curr_dist_to_target = dist(self.current.point, self.target.point)
        self.prev_dist_to_target = dist(self.current.point, self.target.point)

        self.movement = self.curr_dist_to_target - self.prev_dist_to_target
        self.recent_improvements = []
        self.stuck_window = 10
        self.min_window_improvement = 100
        self.progress = 0
        self.dist_moved = 0
        self.stuck_counter = 0
        self.dist_improvement = 0
        self.optimizing_attempt_sum = 0
        self.chosen_nodes = []
        self.stuck_limit = 5
        self.escaping = False
        self.path = [self.start]

        #self.radar_surface = pygame.Surface((2*self.search_radius, 2*self.search_radius))
        #self.radar_surface.fill((0, 0, 0))        
        self.next_point_for_drawing = self.current
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

    
    def update_movement(self, next):
        self.prev_dist_to_target = self.curr_dist_to_target

        self.dist_moved = dist(self.current.point, next.point)

        self.path.append(next)
        self.current = next

        self.curr_dist_to_target = dist(self.current.point, self.target.point)

        self.dist_improvement = self.prev_dist_to_target - self.curr_dist_to_target
        self.movement = abs(self.dist_improvement)
        


    def optimize_costs(self, nodes):
        
        f_costs = {self.current.calc(node, self.target) : node for node in nodes}
        try:
            min_f_cost = min(f_costs.keys())
        except (ValueError):
            return
        next = f_costs[min_f_cost]
          
        self.update_movement(next)
       
        return


    def obstacle_free(self, stride):
        nodes = self.get_neighbors_of_current(stride)
        self.optimize_costs(nodes)

    def node_collides(self, node : Node | tuple | list) -> bool:
        for obstacle in self.obstacles:
            if (obstacle.collidepoint(node)):
                return True
        return False

    def line_collides(self, line : Line) -> bool:
        for obstacle in self.obstacles:
            if (line.colliderect(obstacle)):
                return True
        return False

    def update_radar(self, stride):
        #center_x = None
        #center_y = None
        current_x = self.current.point[0]
        current_y = self.current.point[1]
        target_x = self.target.point[0]
        target_y = self.target.point[1]
        if (current_x < target_x):
            self.center_x = current_x + stride
        elif (current_x > target_x):
            self.center_x = current_x - stride
        
        if (current_y < target_y):
            self.center_y = current_y + stride
        elif (current_y > target_y):
            self.center_y = current_y - stride
        
        
        if ((self.center_x != None) and (self.center_y != None)):
            self.radar = Circle((self.center_x, self.center_y), self.search_radius)
        return

    def careful_step(self, stride):
        #nodes = self.get_neighbors_of_current(stride)
        #if (self.step_count % 100 == 0):
            #self.update_radar(stride) # direct neighbors of self.current are in radar now
        self.update_radar(stride)
        allowed_nodes = []
        self.next_point_for_drawing = self.current
        for node in self.radar:
            
            
            
            if (not (node[0] == self.current[0])):
                line_slope = (node[1] - self.current[1])/(node[0] - self.current[0])

                x_sols = line_intersection_circle_x(self.current.point, line_slope, self.search_radius)
                end_points = get_points_from_solved_x(line_slope, x_sols, self.current.point)

                line_southern_hem = Line(self.current.point, end_points[0])
                line_northern_hem = Line(self.current.point, end_points[1])


                southern_hem_collide = self.line_collides(line_southern_hem)
                northern_hem_collide = self.line_collides(line_northern_hem)
                
                

                southern_hem_node = Node(end_points[0])
                nothern_hem_node = Node(end_points[1])

                if ((not southern_hem_collide) and not (southern_hem_node in self.path)):
                    allowed_nodes.append(southern_hem_node)

                if ((not northern_hem_collide) and not (nothern_hem_node in self.path)):
                    allowed_nodes.append(nothern_hem_node)

            '''
            collide = self.node_collides(node) #if node collides then so will the line
            if ((not collide) and not (node in self.path)):
                allowed_nodes.append(node)
            '''
        
        self.optimize_costs(allowed_nodes)
        return


    def explore(self, stride):
        self.update_radar(stride)
        allowed_nodes = []
        self.next_point_for_drawing = self.current
        for node in self.radar:
            
            
            if (node == self.current):
                continue
            if (not (node[0] == self.current[0])):
                line_slope = (node[1] - self.current[1])/(node[0] - self.current[0])

                x_sols = line_intersection_circle_x(self.current.point, line_slope, self.search_radius)
                end_points = get_points_from_solved_x(line_slope, x_sols, self.current.point)

                line_southern_hem = Line(self.current.point, end_points[0])
                line_northern_hem = Line(self.current.point, end_points[1])


                southern_hem_collide = self.line_collides(line_southern_hem)
                northern_hem_collide = self.line_collides(line_northern_hem)
                
                

                southern_hem_node = Node(end_points[0])
                nothern_hem_node = Node(end_points[1])

                if ((not southern_hem_collide) and not (southern_hem_node in self.path)):
                    allowed_nodes.append(southern_hem_node)

                if ((not northern_hem_collide) and not (nothern_hem_node in self.path)):
                    allowed_nodes.append(nothern_hem_node)

        next = allowed_nodes[randint(0, len(allowed_nodes)-1)]
        self.update_movement(next)
        #self.optimize_improvements(allowed_nodes)
        return

    def step(self):
        try:
            self.progress = (self.dist_moved / self.initial_dist) * 100
        except ZeroDivisionError:
            self.progress = "NA"

        if not self.obstacles:
            self.obstacle_free(stride=1)
        else:
            if self.is_stuck:
                #saved_search_radius = self.search_radius
                #self.search_radius = 70
                
                self.escaping = True
                self.explore(stride=10)

                #self.search_radius = saved_search_radius

            elif dist(self.current.point, self.target.point) > self.tolerance:
                self.careful_step(stride=10)
            else:
                self.careful_step(stride=1)
            
        # update stuck state AFTER movement happens
        self.recent_improvements.append(self.dist_improvement)

        if len(self.recent_improvements) > self.stuck_window:
            self.recent_improvements.pop(0)

        if len(self.recent_improvements) == self.stuck_window:
            total_improvement = sum(self.recent_improvements)

            if total_improvement < 0:
                if (self.stuck_counter >= self.stuck_limit):
                    self.is_stuck = True
                    #self.recent_improvements = []
                    self.stuck_counter = 0
                else:
                    self.stuck_counter += 1
            else:
                self.is_stuck = False
                self.escaping = False
                

        self.step_count += 1
        return
        

    def __str__(self):
        string = f"{self.start}"
        for node in self.path:
            if (node == self.start):
                continue
            string += f", {node}"

        return string


# ============================================================================================================


class NavigatorLog:

    def __init__(self, nav: Navigator):
        self.focused_nav = nav
        self.string = ""
        self.step_counter = 0
        if (self.focused_nav):
            self.prev_dist = dist(self.focused_nav.current.point, self.focused_nav.target.point)
            self.curr_dist = dist(self.focused_nav.current.point, self.focused_nav.target.point)
        self.movement_sums = 0

        self.bits = {
            "WRITE FREE RANGE": True,
            "WRITE NOT FREE RANGE": True,
            "WRITE PATIENCE STATE": True,
            "WRITE IMPATIENCE STATE": True,
            "WRITE STEP COUNTER": True,
            "WRITE STRIDE QUANTITY": True,
            "WRITE DIST DIFF": True,
            "WRITE SEARCH RADIUS":True,
            "WRITE CURRENT POINT": True,
            "WRITE NEXT POINT":True,
            "WRITE STUCK STATUS":True,
            "WRITE PROGRESS STATUS":True
        }

        self.cats = {
            "roll": 30,
            "target dist": 30,
            "movement": 30,
            "step #": 30,
            "state": 30,
            "final roll": 30,
            "search radius":30,
            "current point": 30,
            "next point":30,
            "stuck status":30,
            "progress status":30
        }

        self.chars_occupied = 0

        self.holds = {
            "ALREADY WROTE PATIENCE STATE": False,
            "ALREADY WROTE IMPATIENCE STATE": False
        }

        self.messages = []

    def change_nav(self, new_nav : Navigator) -> None:
        self.focused_nav = new_nav
        self.prev_dist = dist(self.focused_nav.current.point, self.focused_nav.target.point)
        self.curr_dist = dist(self.focused_nav.current.point, self.focused_nav.target.point)
        return

    def update_chars_occupied(self, name):
        self.chars_occupied = self.cats[name]

    def write_progress_status(self) -> None:
        if (self.bits["WRITE PROGRESS STATUS"]):
            self.update_chars_occupied("progress status")
            self.string += (
                f'{"PROGRESS:":<30}'
                f'{f"{self.focused_nav.progress}%":>{self.chars_occupied}}\n'
            )


    def write_stuck_status(self) -> None:
        if (self.bits["WRITE STUCK STATUS"]):
            self.update_chars_occupied("stuck status")
            self.string += (
                f'{"STUCK:":<30}'
                f'{f"{self.focused_nav.is_stuck}":>{self.chars_occupied}}\n'
                f'{"STUCK COUNTER:":<30}'
                f'{f"{self.focused_nav.stuck_counter}":>{self.chars_occupied}}\n'
                f'{"ESCAPING?:":<30}'
                f'{f"{self.focused_nav.escaping}":>{self.chars_occupied}}\n'
            )

            try:
                self.string += f'{f"{self.focused_nav.chosen_nodes[0]}{self.focused_nav.chosen_nodes[1]}":>{self.chars_occupied}}\n'
            except (IndexError):
                pass

    def write_points(self) -> None:
        if (self.bits["WRITE CURRENT POINT"]):
            self.update_chars_occupied("current point")
            self.string += (
                f'{"CURRENT POINT:":<30}'
                f'{f"{self.focused_nav.current}":>{self.chars_occupied}}\n'
            )
        if (self.bits["WRITE NEXT POINT"]):
            self.update_chars_occupied("next point")
            self.string += (
                f'{"NEXT POINT:":<30}'
                f'{f"{self.focused_nav.next_point_for_drawing}":>{self.chars_occupied}}\n'
            )

    def write_patience(self) -> None:
        if (
            self.holds["ALREADY WROTE PATIENCE STATE"]
            or (not self.bits["WRITE PATIENCE STATE"])
        ):
            return

        self.update_chars_occupied("state")
        self.string += f'{"STATE:":<30}{"PATIENT":>{self.chars_occupied}}\n'
        self.holds["ALREADY WROTE PATIENCE STATE"] = True

    def write_impatience(self) -> None:
        if (
            self.holds["ALREADY WROTE IMPATIENCE STATE"]
            or (not self.bits["WRITE IMPATIENCE STATE"])
        ):
            return

        self.update_chars_occupied("state")
        self.string += f'{"STATE:":<30}{"IMPATIENT":>{self.chars_occupied}}\n'
        self.holds["ALREADY WROTE IMPATIENCE STATE"] = True

    def write_range_state(self) -> None:
        if self.focused_nav.obstacles:
            if self.bits["WRITE NOT FREE RANGE"]:
                self.string += f'{"NOT FREE RANGE":<30}\n\n'
                self.bits["WRITE NOT FREE RANGE"] = False
        else:
            if self.bits["WRITE FREE RANGE"]:
                self.string += f'{"FREE RANGE":<30}\n\n'
                self.bits["WRITE FREE RANGE"] = False

    def write_step_counter(self) -> None:
        if self.bits["WRITE STEP COUNTER"]:
            self.update_chars_occupied("step #")
            self.string += (
                f'{"STEP COUNTER:":<30}{self.step_counter:<{self.chars_occupied}}\n'
            )

        self.step_counter += 1

    def write_dist_diff(self) -> None:
        if not self.bits["WRITE DIST DIFF"]:
            return

        target_dist = dist(
            self.focused_nav.current.point,
            self.focused_nav.target.point
        )

        self.update_chars_occupied("target dist")
        self.string += (
            f'{"TARGET DIST:":<30}{target_dist:>{self.chars_occupied}}\n'
        )

        self.prev_dist = self.curr_dist
        self.curr_dist = target_dist

        #diff = abs(self.curr_dist - self.prev_dist)
        diff = self.focused_nav.movement
        self.movement_sums += diff

        self.update_chars_occupied("movement")
        self.string += (
            f'{"MOVEMENT:":<30}{self.focused_nav.dist_moved:>{self.chars_occupied}}\n'
            f'{"DISTANCE IMPROVEMENT:":<30}{self.focused_nav.dist_improvement:>{self.chars_occupied}}\n'
            f'{"RECENT IMPROVEMENTS:":<30}{sum(self.focused_nav.recent_improvements):>{self.chars_occupied}}\n'
        )

        self.update_chars_occupied("roll")

        if self.step_counter == 0:
            self.string += (
                f'{"ROLLING MOVEMENT AVERAGE:":<30}'
                f'{"NA":>{self.chars_occupied}}\n'
            )
        else:
            self.string += (
                f'{"ROLLING MOVEMENT AVERAGE:":<30}'
                f'{(self.movement_sums / self.step_counter):>{self.chars_occupied}}\n'
            )

    def write_search_radius(self):
        self.update_chars_occupied("search radius")
        self.string += (
            f'{"SEARCH RADIUS:":<30}'
            f'{self.focused_nav.search_radius:>{self.chars_occupied}}\n'
        )

    def insert_line_break(self):
        self.string += "\n"

    def write_step_info(self) -> None:
        self.messages.append(self.string)
        self.string = ""
        
        self.write_range_state()
        self.write_search_radius()

        beyond_nav_tolerance = (
            dist(
                self.focused_nav.current.point,
                self.focused_nav.target.point
            )
            > self.focused_nav.tolerance
        )

        self.write_step_counter()
        self.write_dist_diff()
        self.write_progress_status()
        self.write_points()
        self.write_stuck_status()
        if beyond_nav_tolerance:
            self.write_impatience()
        else:
            self.write_patience()

        #self.insert_line_break()
        #self.insert_line_break()

    def print_to_console(self) -> None:
        print(self.messages[-1])
        return

    def upload_info(self) -> None:
        if self.step_counter == 0:
            final_movement_average = "NA"
        else:
            final_movement_average = (
                self.movement_sums / self.step_counter
            )

        self.update_chars_occupied("final roll")
        self.string += (
            f'{"FINAL MOVEMENT AVERAGE:":<30}'
            f'{final_movement_average:>{self.chars_occupied}}\n'
        )

        with open("Navigator_Logs", "w") as file:
            for msg in self.messages:
                file.write(msg)
                file.write("\n\n")

