from obstacle import Obstacle, Node




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
        self.path = [self.start]

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

    def node_collides(self, node : Node) -> bool:
        for obstacle in self.obstacles:
            if (obstacle.collidepoint(node)):
                #print("collision")
                return True
        return False

    def careful_step(self, stride):
        #print("careful!")
        nodes = self.get_neighbors_of_current(stride)
        allowed_nodes = []
        for node in nodes:
            
            #neighbors = self.get_neighbors_of_node(self.current, stride)
                
            collide = self.node_collides(node)
            
                
            if ((not collide) and not (node in self.path)):
                allowed_nodes.append(node)
        
        self.optimize_costs(allowed_nodes)

    def step(self, stride = 1):
        if (not self.obstacles):
            self.obstacle_free(stride)
            return
        else:
            self.careful_step(stride)
            return

    def __str__(self):
        string = f"{self.start}"
        for node in self.path:
            if (node == self.start):
                continue
            string += f", {node}"

        return string




