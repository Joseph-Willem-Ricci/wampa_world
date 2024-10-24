from random import shuffle
from itertools import combinations as comb
from utils import flatten, get_direction, is_facing_wampa


# KNOWLEDGE BASE
class KB:
    def __init__(self, agent):
        self.all_rooms = {agent.loc}  # set of rooms that are known to exist
        self.safe_rooms = {agent.loc}  # set of rooms that are known to be safe
        self.visited_rooms = {agent.loc}  # set of visited rooms (x, y)
        self.stench = set()  # set of rooms where stench has been perceived
        self.breeze = set()  # set of rooms where breeze has been perceived
        self.bump = dict()  # {loc: direction} of most recent bump in loc
        self.gasp = False  # True if gasp has been perceived
        self.scream = False  # True if scream has been perceived
        self.walls = set()  # set of rooms (x, y) that are known to be walls
        self.pits = set()  # set of rooms (x, y) that are known to be pits
        self.wampa = None  # room (x, y) that is known to be the Wampa
        self.luke = None  # room (x, y) that is known to be Luke


# AGENT
class Agent:
    def __init__(self, world):
        self.world = world
        self.loc = (0, 0)
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
        """Returns a set of tuples representing all possible adjacent rooms to
        'room' Use this function to update KB.all_rooms."""
        x, y = room
        deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return {(x+dx, y+dy) for dx, dy in deltas if (x+dx, y+dy)}

    def record_percepts(self, sensed_percepts):
        """Update the percepts in agent's KB with the percepts sensed in the
        current location, and update visited_rooms and all_rooms."""
        present_percepts = set(p for p in sensed_percepts if p)
        direction = get_direction(self.degrees)
        percept_to_process = {
            "stench": lambda: self.KB.stench.add(self.loc),
            "breeze": lambda: self.KB.breeze.add(self.loc),
            "bump": lambda: self.KB.bump.update({self.loc: direction}),
            "gasp": lambda: setattr(self.KB, "gasp", True),
            "scream": lambda: setattr(self.KB, "scream", True)
        }
        for percept in present_percepts:
            percept_to_process[percept]()

        self.KB.visited_rooms.add(self.loc)
        self.KB.all_rooms.update(self.adjacent_rooms(self.loc))

    def enumerate_possible_worlds(self):
        """Return the set of all possible worlds, where a possible world is a
        tuple of (pit_rooms, wampa_room), pit_rooms is a tuple of tuples
        representing possible pit rooms, and wampa_room is a tuple representing
        a possible wampa room.

        Since the goal is to combinatorially enumerate all the possible worlds
        (pit and wampa locations) over the set of rooms that could potentially
        have a pit or a wampa, we first want to find that set. To do that,
        subtract the set of rooms that you know cannot have a pit or wampa from
        the set of all rooms. For example, you know that a room with a wall
        cannot have a pit or wampa.

        Then use itertools.combinations to return the set of possible worlds,
        or all combinations of possible pit and wampa locations.

        You may find the utils.flatten(tup) method useful here for flattening
        wampa_room from a tuple of tuples into a tuple.

        The output of this function will be queried to find the model of the
        query, and will be checked for consistency with the KB
        to find the model of the KB."""

        is_not_pit_or_wampa = self.KB.walls | self.KB.safe_rooms
        could_be_pit_or_wampa = self.KB.all_rooms - is_not_pit_or_wampa
        n = len(could_be_pit_or_wampa)
        return set(
            (pit_rooms, flatten(wampa_room))  # return all possible worlds
            for num_pits in range(n + 1)      # with 0 to n pits
            for num_wampas in range(2)        # with 0 or 1 wampas
            for pit_rooms in comb(could_be_pit_or_wampa, num_pits)
            for wampa_room in comb(could_be_pit_or_wampa, num_wampas)
            # if wampa_room != pit_room or wampa_room is empty
            if flatten(wampa_room) not in pit_rooms or wampa_room == ()
        )

    def pit_room_is_consistent_with_KB(self, room):
        """Return True if the room could be a pit given breeze in KB, False
        otherwise. A room could be a pit if all adjacent rooms that have been
        visited have had breeze perceived in them. A room cannot be a pit if
        any adjacent rooms that have been visited have not had breeze perceived
        in them. This will be used to find the model of the KB."""
        if room == tuple():  # It is possible that there are no pits
            return not self.KB.breeze  # if no breeze has been perceived yet

        return all(room in self.KB.breeze or room not in self.KB.visited_rooms
                   for room in self.adjacent_rooms(room))

    def wampa_room_is_consistent_with_KB(self, room):
        """Return True if the room could be a wampa given stench in KB, False
        otherwise. A queried wampa room is consistent with the KB if all
        adjacent rooms that have been visited have had stench perceived in them
        and if all rooms with stench are adjacent to the queried room.
        A room cannot be a wampa if any adjacent rooms that have been visited
        have not had stench perceived in them.
        This will be used to find the model of the KB."""
        if room == tuple():  # It is possible that there is no Wampa
            return not self.KB.stench  # if no stench has been perceived yet

        all_adj_rooms_have_stench = all(r in self.KB.stench or 
                                        r not in self.KB.visited_rooms 
                                        for r in self.adjacent_rooms(room))
        all_stench_is_adjacent = all(stench_room in self.adjacent_rooms(room)
                                     for stench_room in self.KB.stench)
        return all_adj_rooms_have_stench and all_stench_is_adjacent

    def find_model_of_KB(self, possible_worlds):
        """Return the subset of all possible worlds consistent with KB.
        possible_worlds is a set of tuples (pit_rooms, wampa_room),
        pit_rooms is a set of tuples of possible pit rooms,
        and wampa_room is a tuple representing a possible wampa room.
        A world is consistent with the KB if the wampa location is consistent
        and all pit rooms are consistent with the KB."""

        return {(p, w) for p, w in possible_worlds if
                self.wampa_room_is_consistent_with_KB(w) and
                (all(self.pit_room_is_consistent_with_KB(room) for room in p)
                if p else self.pit_room_is_consistent_with_KB(p))}  # empty p

    def find_model_of_query(self, query, room, possible_worlds):
        """Where query can be "pit_in_room", "wampa_in_room", "no_pit_in_room"
        or "no_wampa_in_room", filter the set of worlds
        according to the query and room."""
        query_to_filter = {
            "pit_in_room": lambda world: room in world[0],
            "wampa_in_room": lambda world: room == world[1],
            "no_pit_in_room": lambda world: room not in world[0],
            "no_wampa_in_room": lambda world: room != world[1]
        }
        filter_function = query_to_filter.get(query)
        return set(filter(filter_function, possible_worlds))

    def infer_wall_locations(self):
        """If a bump is perceived, infer wall locations along the entire known
        length of the room."""
        min_x = min(self.KB.all_rooms, key=lambda x: x[0])[0]
        max_x = max(self.KB.all_rooms, key=lambda x: x[0])[0]
        min_y = min(self.KB.all_rooms, key=lambda x: x[1])[1]
        max_y = max(self.KB.all_rooms, key=lambda x: x[1])[1]
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
        """First, make some basic inferences:
        1. If there is no breeze or stench in current location, infer that the
        adjacent rooms are safe.
        2. Infer wall locations given bump percept.
        3. Infer Luke's location given gasp percept.
        4. Infer whether the Wampa is alive given scream percept. Clear stench
        from the KB if Wampa is dead.

        Then, infer whether each adjacent room is safe, pit or wampa by
        following the backward-chaining resolution algorithm:
        1. Enumerate possible worlds.
        2. Find the model of the KB, i.e. the subset of possible worlds
        consistent with the KB.
        3. For each adjacent room and each query, find the model of the query.
        4. If the model of the KB is a subset of the model of the query, the
        query is entailed by the KB.
        5. Update KB.pits, KB.wampa, and KB.safe_rooms based on any newly
        derived knowledge.
        """

        # infer that adjacent rooms are safe if there is no breeze or stench
        if self.loc not in self.KB.breeze | self.KB.stench:
            self.KB.safe_rooms.update(self.adjacent_rooms(self.loc))

        # make inferences based on bump, gasp and scream percepts
        self.infer_wall_locations()
        if self.KB.gasp:
            self.KB.luke = self.loc
        if self.KB.scream:
            self.KB.wampa = None
            self.KB.stench.clear()

        # initialize our four queries and sets to store where the query is true
        pit_in_room = set()
        wampa_in_room = set()
        no_pit_in_room = set()
        no_wampa_in_room = set()
        queries_to_inferences = {"pit_in_room": pit_in_room,
                                 "wampa_in_room": wampa_in_room,
                                 "no_pit_in_room": no_pit_in_room,
                                 "no_wampa_in_room": no_wampa_in_room}

        # enumerate possible worlds and find the model of the KB
        possible_worlds = self.enumerate_possible_worlds()
        model_of_KB = self.find_model_of_KB(possible_worlds)

        # for each query in each adj. room, find the model of the query
        # and check if query is entailed by KB
        for adj_room in self.adjacent_rooms(self.loc):
            for query, inferences in queries_to_inferences.items():
                model_of_query = self.find_model_of_query(query, adj_room,
                                                          possible_worlds)
                if model_of_KB.issubset(model_of_query):
                    inferences.add(adj_room)

        # update KB.safe_rooms, KB.wampa and KB.pits based on new information
        safe_adjacent_rooms = no_pit_in_room.intersection(no_wampa_in_room)
        self.KB.safe_rooms.update(safe_adjacent_rooms)
        self.KB.wampa = wampa_in_room.pop() if wampa_in_room else None
        self.KB.pits.update(pit_in_room)

    def all_safe_next_actions(self):
        """Define R2D2's valid and safe next actions based on his current
        location and knowledge of the environment."""
        actions = ['left', 'right']
        x, y = self.loc
        dx, dy = self.orientation_to_delta[get_direction(self.degrees)]
        forward_room = (x+dx, y+dy)
        if forward_room in self.KB.safe_rooms and \
                forward_room not in self.KB.walls:
            actions.append('forward')
        if self.blaster and is_facing_wampa(self):
            actions.append('shoot')
        if self.has_luke and self.loc == (0, 0):
            actions.append('climb')
        if self.KB.luke == self.loc and not self.has_luke:
            actions.append('grab')

        return actions

    def choose_next_action(self):
        """Choose next action from all safe next actions. You may want to
        prioritizesome actions based on current state. For example, if R2D2
        knows Luke's location and is in the same room as Luke, you may want
        to prioritize 'grab' over all other actions. Similarly, if R2D2 has
        Luke, you may want to prioritize moving toward the exit. You can
        implement this as basically (randomly choosing between safe actions)
        or as sophisticated (optimizing exploration of unvisited states,
        finding shortest paths, etc.) as you like."""
        actions = self.all_safe_next_actions()
        if 'climb' in actions:
            return 'climb'
        elif 'grab' in actions:
            return 'grab'
        elif 'shoot' in actions:
            self.KB.safe_rooms.add(self.KB.wampa)  # if shot, room safe
            return 'shoot'
        x, y = self.loc
        dx, dy = self.orientation_to_delta[get_direction(self.degrees)]
        forward_room = (x+dx, y+dy)
        if 'forward' in actions and \
            (forward_room not in self.KB.visited_rooms or
                (self.has_luke and (dx == -1 or dy == -1))):
            return 'forward'
        else:
            shuffle(actions)
            return actions.pop()


# Approximately how many hours did you spend on this assignment?
feedback_question_1 = 99

# Which aspects of this assignment did you find most challenging?
# Were there any significant stumbling blocks?
feedback_question_2 = """Test"""

# Which aspects of this assignment did you like?
# Is there anything you would have changed?
feedback_question_3 = """Test"""
