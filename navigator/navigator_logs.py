from navigator.navigator import dist, nint, Navigator

class NavigatorLog:

    def __init__(self, nav: Navigator):
        self.focused_nav = nav
        self.string = ""
        self.step_counter = 0
        if (self.focused_nav):
            self.prev_dist = dist(self.focused_nav.current, self.focused_nav.target)
            self.curr_dist = dist(self.focused_nav.current, self.focused_nav.target)
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
        self.step_counter = 0
        self.prev_dist = dist(self.focused_nav.current, self.focused_nav.target)
        self.curr_dist = dist(self.focused_nav.current, self.focused_nav.target)
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
            self.focused_nav.current,
            self.focused_nav.target
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
                self.focused_nav.current,
                self.focused_nav.target
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
