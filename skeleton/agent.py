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
        "up": (0, 1),  # (dx, dy)
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
        """TODO: Returns a set of tuples representing all possible adjacent rooms to 'room'
        Use this function to update KB.possible_rooms."""
        ...
        pass

    def record_percepts(self, sensed_percepts, current_location):
        """TODO: Update the percepts in agent's KB with the percepts sensed in the current 
        location, and update safe_rooms, visited_rooms, and possible_rooms accordingly."""
        self.loc = current_location
        present_percepts = set(p for p in sensed_percepts if p)
        ...
        pass
        

    def room_could_be_pit(self, room):
        """TODO: Return True if the room could be a pit given KB, False otherwise."""
        if room == tuple():  # It is possible that there are no pits (i.e. if room is an empty tuple)
            return not self.KB.breeze  # if no breeze has been perceived yet
        ...
        pass

    def room_could_be_wampa(self, room):
        """TODO: Return True if the room could be a wampa given KB, False otherwise."""
        if room == tuple():  # It is possible that there is no Wampa (i.e. if room is an empty tuple)
            return not self.KB.stench  # if no stench has been perceived yet
        ...
        pass

    def enumerate_possible_worlds(self):
        """TODO: Return all possible combinations of pit and wampa locations consistent with the rules.
        First, subtract the set of rooms that cannot have a pit or wampa from the set of possible 
        rooms to yield the set of rooms that could have a pit or wampa.

        Then use itertools.combinations to return the set of possible worlds, where possible_worlds
        is a set of tuples (pit_rooms, wampa_room), pit_rooms is a tuple of possible pit rooms
        and wampa_room is a tuple representing a possible wampa room.

        You may find the utils.flatten(tup) method useful here for flattening wampa_room into a tuple."""
        ...
        pass

    def find_model_of_KB(self, possible_worlds):
        """TODO: Return the subset of all possible worlds consistent with KB.
        possible_worlds is a set of tuples (pit_rooms, wampa_room),
        pit_rooms is a set of tuples of possible pit rooms,
        and wampa_room is a tuple representing a possible wampa room."""
        ...
        pass

    def query_set_of_worlds(self, query, room, worlds):
        """Where query can be "pit_in_room", "wampa_in_room", "no_pit_in_room" or "no_wampa_in_room",
        filter the set of worlds to those which contain the query in the given room."""
        ...
        pass

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
        """TODO: If there is no breeze or stench, infer that the adjacent rooms are safe.
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
        ...
        pass
        