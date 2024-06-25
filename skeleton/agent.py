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
        self.bump = dict()  # loc: direction
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
        """TODO: Returns all possible adjacent rooms to 'room' that aren't known to be walls."""
        pass

    def record_percepts(self, sensed_percepts, current_location):
        """TODO: Update the percepts in agent's KB with the percepts sensed in the current 
        location, and update safe_rooms, visited_rooms, and possible_rooms accordingly."""
        pass

    def room_could_be_pit(self, query_room):
        """TODO: Return True if the query_room could be a pit given KB, False otherwise."""
        pass

    def room_could_be_wampa(self, query_room):
        """TODO: Return True if the query_room could be a wampa given KB, False otherwise."""
        pass

    def enumerate_possible_worlds(self):
        """TODO: Return all possible combinations of pit and wampa locations consistent with the rules."""
        pass

    def find_subset_of_worlds_consistent_with_KB(self, possible_worlds):
        """TODO: Return all possible worlds consistent with KB."""
        pass

    def query_set_of_worlds(self, query_feature, room, worlds):
        """TODO: Where query_feature can be "pit" or "wampa", filter the set of worlds 
        to those in which query feature is true in given room."""
        pass

    def inference_algorithm(self):
        """TODO: Infer wall locations given bump percept, Luke's location given gasp percept,
        whether the Wampa is alive given scream percept, and infer Wampa location and whether 
        a room is safe to move to using by following the backward-chaining resolution algorithm:
        1. Enumerate possible worlds
        2. Find subset of possible worlds consistent with KB
        3. For each adjacent room, filter possible worlds and consistent worlds to those consistent with query (e.g. "wampa in adj_room?")
        4. If set of consistent worlds with query is subset of possible worlds with query, the query is entailed by the KB
        5. Update KB.wampa, and KB.safe_rooms accordigly
        """
        pass
        