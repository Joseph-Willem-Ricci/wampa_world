from utils import flatten, get_direction
from itertools import combinations

# KNOWLEDGE BASE
class KB:
    def __init__(self, agent):
        self.safe_rooms = {agent.loc}  # set of rooms (x, y) that are known to be safe
        self.visited_rooms = {agent.loc}  # set of rooms (x, y) that have been visited
        self.possible_rooms = {agent.loc}  # set of rooms (x, y) that might be possible to visit
        self.stench = set()  # set of rooms (x, y) where stench has been perceived
        self.breeze = set()  # set of rooms (x, y) where breeze has been perceived
        self.bump = dict()  # loc: direction where bump has been perceived
        self.gasp = False  # True if gasp has been perceived
        self.scream = False  # True if scream has been perceived
        self.walls = set()  # set of rooms (x, y) that are known to be walls (if bump in (0, 0), left, then (-1, 0) is a wall)
        self.pits = set()  # set of rooms (x, y) that are known to be pits
        self.wampa = None  # room (x, y) that is known to be the Wampa
        self.luke = None  # room (x, y) that is known to be Luke
        

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
        Use this function to update KB.possible_rooms."""
        x, y = room
        deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return ((x+dx, y+dy) for dx, dy in deltas if (x+dx, y+dy))

    def record_percepts(self, sensed_percepts, current_location):
        """Update the percepts in agent's KB with the percepts sensed in the current location, 
        and update safe_rooms, visited_rooms, and possible_rooms accordingly."""
        self.loc = current_location
        present_percepts = set(p for p in sensed_percepts if p)
        percept_to_process = {
            "stench": lambda: self.KB.stench.add(self.loc),
            "breeze": lambda: self.KB.breeze.add(self.loc),
            "bump": lambda: self.KB.bump.update({self.loc: get_direction(self.degrees)}),
            "gasp": lambda: setattr(self.KB, "gasp", True),
            "scream": lambda: setattr(self.KB, "scream", True)
        }
        for percept in present_percepts:
            percept_to_process[percept]()
        
        self.KB.safe_rooms.add(self.loc)
        self.KB.visited_rooms.add(self.loc)
        self.KB.possible_rooms.update(self.adjacent_rooms(self.loc))
    
    def room_could_be_pit(self, room):
        """Return True if the room could be a pit given KB, False otherwise."""
        if room == tuple():  # It is possible that there are no pits (i.e. if room is an empty tuple)
            return not self.KB.breeze  # if no breeze has been perceived yet
        
        return all(room in self.KB.breeze or room not in self.KB.visited_rooms
                   for room in self.adjacent_rooms(room))
    
    def room_could_be_wampa(self, room):
        """Return True if the room could be a wampa given KB, False otherwise."""
        if room == tuple():  # It is possible that there is no Wampa (i.e. if room is an empty tuple)
            return not self.KB.stench  # if no stench has been perceived yet

        return all(room in self.KB.stench or room not in self.KB.visited_rooms
                   for room in self.adjacent_rooms(room))

    def enumerate_possible_worlds(self):
        """Return all possible combinations of pit and wampa locations consistent with the rules.
        First, subtract the set of rooms that cannot have a pit or wampa from the set of possible 
        rooms to yield the set of rooms that could have a pit or wampa.

        Then use itertools.combinations to return the set of possible worlds, where possible_worlds
        is a set of tuples (pit_rooms, wampa_room), pit_rooms is a tuple of possible pit rooms
        and wampa_room is a tuple representing a possible wampa room.

        You may find the utils.flatten(tup) method useful here for flattening wampa_room into a tuple."""

        rooms_cannot_be_pit_or_wampa = self.KB.walls | self.KB.safe_rooms
        rooms_could_be_pit_or_wampa = self.KB.possible_rooms - rooms_cannot_be_pit_or_wampa

        return set(
            (pit_rooms, flatten(wampa_room))
            for num_pits in range(len(rooms_could_be_pit_or_wampa) + 1)
            for num_wampas in range(2)
            for pit_rooms in combinations(rooms_could_be_pit_or_wampa, num_pits)
            for wampa_room in combinations(rooms_could_be_pit_or_wampa, num_wampas)
            if wampa_room not in pit_rooms or wampa_room == ()
        )

    def find_model_of_KB(self, possible_worlds):
        """Return the subset of all possible worlds consistent with KB.
        possible_worlds is a set of tuples (pit_rooms, wampa_room),
        pit_rooms is a set of tuples of possible pit rooms,
        and wampa_room is a tuple representing a possible wampa room."""

        return {(p, w) for p, w in possible_worlds if
                self.room_could_be_wampa(w) and all(self.room_could_be_pit(room) for room in p)}


    def query_set_of_worlds(self, query, room, worlds):
        """Where query can be "pit_in_room", "wampa_in_room", "no_pit_in_room" or "no_wampa_in_room",
        filter the set of worlds to those which contain the query in the given room."""
        query_to_filter = {
            "pit_in_room": lambda world: room in world[0],
            "wampa_in_room": lambda world: room == world[1],
            "no_pit_in_room": lambda world: room not in world[0],
            "no_wampa_in_room": lambda world: room != world[1]
        }
        return {world for world in worlds if query_to_filter[query](world)}

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
        3. For each adjacent room and each query, find the model of the query (i.e. "pit in adj_room?", "no wampa in adj_room?", etc.)
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
        pit_in_room = set()
        wampa_in_room = set()
        no_pit_in_room = set()
        no_wampa_in_room = set()
        queries_to_inferences = {"pit_in_room": pit_in_room, "wampa_in_room": wampa_in_room,
                   "no_pit_in_room": no_pit_in_room, "no_wampa_in_room": no_wampa_in_room}

        # enumerate possible worlds and find the model of the KB
        possible_worlds = self.enumerate_possible_worlds()
        model_of_KB = self.find_model_of_KB(possible_worlds)
        
        # for each query in each adj. room, find the model of the query and check if query is entailed by KB
        for adj_room in self.adjacent_rooms(self.loc):
            for query, inferences in queries_to_inferences.items():
                model_of_query = self.query_set_of_worlds(query, adj_room, possible_worlds)
                if model_of_KB.issubset(model_of_query):
                    inferences.add(adj_room)

        # update KB.safe_rooms, KB.wampa and KB.pits based on new information inferred
        safe_adjacent_rooms = no_pit_in_room.intersection(no_wampa_in_room)
        self.KB.safe_rooms.update(safe_adjacent_rooms)
        self.KB.wampa = wampa_in_room.pop() if len(wampa_in_room) == 1 else None
        self.KB.pits.update(pit_in_room)
        