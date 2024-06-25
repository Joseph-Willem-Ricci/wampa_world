from utils import flatten, get_direction
from itertools import combinations

# KNOWLEDGE BASE
class KB:
    def __init__(self, agent):
        self.safe_rooms = {agent.loc}
        self.visited_rooms = {agent.loc}
        self.possible_rooms = {agent.loc}
        self.stench = set()
        self.breeze = set()
        self.bump = {}  # loc: direction
        self.gasp = False
        self.scream = False
        self.walls = set()
        self.wampa = None
        self.luke = None
        

# AGENT
class Agent:
    def __init__(self, world):
        self.world = world
        self.loc = (0,0)
        self.score = 0
        self.degrees = 0
        self.blaster = True
        self.has_luke = False
        self.percepts = ['stench', 'breeze', 'gasp', 'bump', 'scream']
        self.orientation_to_delta = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0)
        }
        self.KB = KB(self)

    def turn_left(self):
        self.degrees -= 90

    def turn_right(self):
        self.degrees += 90

    def adjacent_rooms(self, room):
        """Returns all possible adjacent rooms to 'room' that aren't known to be walls."""
        x, y = room
        deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return ((x+dx, y+dy) for dx, dy in deltas if (x+dx, y+dy) not in self.KB.walls)

    def record_percepts(self, sensed_percepts, current_location):
        """Update the percepts in agent's KB with the percepts sensed in the current location, 
        and update safe_rooms, visited_rooms, and possible_rooms accordingly."""
        self.loc = current_location
        percept_to_process = {
            "stench": lambda: self.KB.stench.add(self.loc),
            "breeze": lambda: self.KB.breeze.add(self.loc),
            "bump": lambda: self.KB.bump.update({self.loc: get_direction(self.degrees)}),
            "gasp": lambda: setattr(self.KB, "gasp", True),
            "scream": lambda: setattr(self.KB, "scream", True)
        }
        for percept in self.percepts:
            if percept in sensed_percepts:
                percept_to_process[percept]()
        
        self.KB.safe_rooms.add(self.loc)
        self.KB.visited_rooms.add(self.loc)
        self.KB.possible_rooms.update(self.adjacent_rooms(self.loc))

    def room_could_be_pit(self, query_room):
        """Return True if the query_room could be a pit given KB, False otherwise."""
        if query_room == tuple():  # it is possible that no rooms have pits if no breeze has been perceived yet
            return not self.KB.breeze

        return all(adj_room in self.KB.breeze or adj_room not in self.KB.visited_rooms for
                   adj_room in self.adjacent_rooms(query_room))

    def room_could_be_wampa(self, query_room):
        """Return True if the query_room could be a wampa given KB, False otherwise."""
        if query_room == tuple():  # it is possible that no rooms have wampa if no stench has been perceived yet
            return not self.KB.stench

        return all(adj_room in self.KB.stench or adj_room not in self.KB.visited_rooms for
                   adj_room in self.adjacent_rooms(query_room))

    def enumerate_possible_worlds(self):
        """Return all possible combinations of pit and wampa locations consistent with the rules."""
        rooms_could_be_pit_or_wampa = [
            room for room in self.KB.possible_rooms
            if room not in self.KB.walls
            and room not in self.KB.stench
            and room not in self.KB.breeze
            and room not in self.KB.safe_rooms
        ]

        possible_worlds = set(
            (pit_rooms, flatten(wampa_room))
            for num_pits in range(len(rooms_could_be_pit_or_wampa) + 1)
            for num_wampas in range(2)
            for pit_rooms in combinations(rooms_could_be_pit_or_wampa, num_pits)
            for wampa_room in combinations(rooms_could_be_pit_or_wampa, num_wampas)
            if flatten(wampa_room) not in pit_rooms or flatten(wampa_room) == ()
        )

        return possible_worlds

    def find_subset_of_worlds_consistent_with_KB(self, possible_worlds):
        """Return all possible worlds consistent with KB."""
        consistent_worlds = set(
            world for world in possible_worlds if self.room_could_be_wampa(world[1]) 
            and all(self.room_could_be_pit(room) for room in world[0])
        )
        return consistent_worlds

    def query_set_of_worlds(self, query_feature, room, worlds):
        """Where query_feature can be "pit" or "wampa", filter the set of worlds 
        to those in which query feature is true in given room."""
        if query_feature == "pit":
            return {world for world in worlds if room in world[0]}
        if query_feature == "wampa":
            return {world for world in worlds if room == world[1]}

    def infer_wall_locations(self):
        """If a bump is perceived, infer wall locations along the entire length of the room."""
        min_x = min(self.KB.possible_rooms, key=lambda x: x[0])[0]
        max_x = max(self.KB.possible_rooms, key=lambda x: x[0])[0]
        min_y = min(self.KB.possible_rooms, key=lambda x: x[1])[1]
        max_y = max(self.KB.possible_rooms, key=lambda x: x[1])[1]
        for room, orientation in self.KB.bump.items():
            if orientation == "up":
                for x in range(min_x, max_x + 1, 1):
                    self.KB.walls.add((x, room[1] + 1))
            elif orientation == "down":
                for x in range(min_x, max_x + 1, 1):
                    self.KB.walls.add((x, room[1] - 1))
            elif orientation == "left":
                for y in range(min_y, max_y + 1, 1):
                    self.KB.walls.add((room[0] - 1, y))
            elif orientation == "right":
                for y in range(min_y, max_y + 1, 1):
                    self.KB.walls.add((room[0] + 1, y))

    def inference_algorithm(self):
        """Infer wall locations given bump percept, Luke's location given gasp percept,
        whether the Wampa is alive given scream percept, and infer Wampa location and whether 
        a room is safe to move to using by following the backward-chaining resolution algorithm:
        1. Enumerate possible worlds
        2. Find subset of possible worlds consistent with KB
        3. For each adjacent room, filter possible worlds and consistent worlds to those consistent with query (e.g. "wampa in adj_room?")
        4. If set of consistent worlds with query is subset of possible worlds with query, the query is entailed by the KB
        5. Update KB.wampa, and KB.safe_rooms accordigly
        """

        if self.loc not in self.KB.breeze | self.KB.stench and "breeze":
            self.KB.safe_rooms.update(set(self.adjacent_rooms(self.loc))) 

        self.infer_wall_locations()
        if self.KB.gasp:
            self.KB.luke = self.loc
        if self.KB.scream:
            self.KB.wampa = None
            self.KB.stench.clear()

        could_be_pit = set()
        could_be_wampa = set()
        queries = {"pit": could_be_pit, "wampa": could_be_wampa}

        possible_worlds = self.enumerate_possible_worlds()
        worlds_consistent_with_KB = self.find_subset_of_worlds_consistent_with_KB(possible_worlds)
        
        for adj_room in self.adjacent_rooms(self.loc):
            for query, kb_set in queries.items():
                possible_worlds_with_query = self.query_set_of_worlds(query, adj_room, possible_worlds)
                consistent_worlds_with_query = self.query_set_of_worlds(query, adj_room, worlds_consistent_with_KB)
                if consistent_worlds_with_query and \
                  consistent_worlds_with_query.issubset(possible_worlds_with_query):
                    kb_set.add(adj_room)
            if adj_room not in could_be_pit | could_be_wampa:
                self.KB.safe_rooms.add(adj_room)

        self.KB.wampa = could_be_wampa.pop() if len(could_be_wampa) == 1 else None
        