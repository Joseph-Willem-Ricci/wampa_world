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
        self.pits = set()
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
        """Returns a set of tuples representing all possible adjacent rooms to 'room'
        that aren't known to be walls."""
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
    
    def room_could_be_pit(self, room):
        """Return True if the room could be a pit given KB, False otherwise.
        It is possible that there is no Wampa (i.e. if room is an empty tuple)
        if no stench has been percieved yet."""
        if room == tuple():
            return not self.KB.breeze
        
        adj_rooms = self.adjacent_rooms(room)
        return adj_rooms and \
            all(adj_room in self.KB.breeze or adj_room not in self.KB.visited_rooms for adj_room in adj_rooms)
    
    def room_could_be_wampa(self, room):
        """Return True if the room could be a wampa given KB, False otherwise.
        It is possible that there is no Wampa (i.e. if room is an empty tuple)
        if no stench has been percieved yet."""
        if room == tuple():
            return not self.KB.stench

        adj_rooms = self.adjacent_rooms(room)
        return adj_rooms and \
            all(adj_room in self.KB.stench or adj_room not in self.KB.visited_rooms for adj_room in adj_rooms)

    def enumerate_possible_worlds(self):
        """Return all possible combinations of pit and wampa locations consistent with the rules.
        First, subtract the set of rooms that cannot have a pit or wampa from the set of possible rooms.
        Then use itertools.combinations to return the set of possible worlds, where
        possible_worlds is (pit_rooms, wampa_room), pit_rooms is a set of tuples of possible pit rooms
        and wampa_room is a tuple representing a possible wampa room.
        You may find the utils.flatten(tup) method useful here."""

        rooms_cannot_be_pit_or_wampa = self.KB.walls | self.KB.safe_rooms
        rooms_could_be_pit_or_wampa = self.KB.possible_rooms - rooms_cannot_be_pit_or_wampa

        return set(
            (pit_rooms, flatten(wampa_room))
            for num_pits in range(len(rooms_could_be_pit_or_wampa) + 1)
            for num_wampas in range(2)
            for pit_rooms in combinations(rooms_could_be_pit_or_wampa, num_pits)
            for wampa_room in combinations(rooms_could_be_pit_or_wampa, num_wampas)
            if flatten(wampa_room) not in pit_rooms or flatten(wampa_room) == ()
        )

    def find_model_of_KB(self, possible_worlds):
        """Return the set of all possible worlds consistent with KB.
        worlds is a tuple (pit_rooms, wampa_room), pit_rooms is a set of tuples of possible pit rooms
        and wampa_room is a tuple representing a possible wampa room."""
        consistent_worlds = set(
            world for world in possible_worlds if self.room_could_be_wampa(world[1])
            and ((all(self.room_could_be_pit(room) for room in world[0]) and world[0])  # if world[0] is not empty and all rooms in world[0] could be pits
                 or (not world[0] and self.room_could_be_pit(tuple())))  # or if world[0] is empty and no breeeze has been perceived yet
        )
        return consistent_worlds


    def query_set_of_worlds(self, query_feature, room, worlds):
        """Where query_feature can be "pit" or "wampa", filter the set of worlds 
        to those in which contain the query feature in the given room."""
        if query_feature == "pit_in_room":
            return {world for world in worlds if room in world[0]}
        if query_feature == "wampa_in_room":
            return {world for world in worlds if room == world[1]}
        if query_feature == "no_pit_in_room":
            return {world for world in worlds if room not in world[0]}
        if query_feature == "no_wampa_in_room":
            return {world for world in worlds if room != world[1]}

    def infer_wall_locations(self):
        """If a bump is perceived, infer wall locations along the entire known length of the room."""
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
        """If there is no breeze or stench, infer that the adjacent rooms are safe.
        Infer wall locations given bump percept, Luke's location given gasp percept,
        and whether the Wampa is alive given scream percept.
        Infer whether each adjacent room could be a pit or could be a Wampa by
        following the backward-chaining resolution algorithm:
        1. Enumerate possible worlds
        2. Find the model of the KB, i.e. the subset of possible worlds consistent with the KB
        3. For each adjacent room, find the model of the query (i.e. "pit in adj_room?", "no wampa in adj_room?", etc.)
        4. If the model of the KB is a subset of the model of the query, the query is entailed by the KB
        5. Update KB.pits, KB.wampa, and KB.safe_rooms based on any new information inferred.
        """

        # infer that adjacent rooms are safe if there is no breeze or stench
        if self.loc not in self.KB.breeze | self.KB.stench:
            self.KB.safe_rooms.update(set(self.adjacent_rooms(self.loc))) 

        # make inferences based on bump, gasp and scream percepts
        self.infer_wall_locations()
        if self.KB.gasp:
            self.KB.luke = self.loc
        if self.KB.scream:
            self.KB.wampa = None
            self.KB.stench.clear()
        
        # initialize our four queries and sets to store rooms where the query is true
        queries = {"pit_in_room": pit_in_room, "wampa_in_room": wampa_in_room,
                   "no_pit_in_room": no_pit_in_room, "no_wampa_in_room": no_wampa_in_room}
        pit_in_room = set()
        wampa_in_room = set()
        no_pit_in_room = set()
        no_wampa_in_room = set()

        # enumerate possible worlds and find the model of the KB
        possible_worlds = self.enumerate_possible_worlds()
        model_of_KB = self.find_model_of_KB(possible_worlds)
        
        # for each query in each adj. room, find the model of the query and check if query is entailed by KB
        for adj_room in self.adjacent_rooms(self.loc):
            for query, kb_set in queries.items():
                model_of_query = self.query_set_of_worlds(query, adj_room, possible_worlds)
                if model_of_KB.issubset(model_of_query):
                    kb_set.add(adj_room)

        # update KB.safe_rooms, KB.wampa and KB.pits based on new information inferred
        safe_adjacet_rooms = no_pit_in_room.intersection(no_wampa_in_room)
        self.KB.safe_rooms.update(safe_adjacet_rooms)
        self.KB.wampa = wampa_in_room.pop() if len(wampa_in_room) == 1 else None
        self.KB.pits.update(pit_in_room)
        