from random import shuffle
from visualize_world import visualize_world
from utils import get_direction
from scenarios import *
from agent import Agent
from time import sleep

def fit_grid(grid, item):
    """Used for calculating breeze and stench locationsbased on pit and wampa
    locations."""
    grid_x, grid_y = grid
    x, y = item
    loc = []

    if x < grid_x - 1:
        loc += [[x+1, y]]
    if x > 0:
        loc += [[x-1, y]]
    if y < grid_y - 1:
        loc += [[x, y+1]]
    if y > 0:
        loc += [[x, y-1]]

    return loc

# ENVIRONMENT
class WampaWorld:
    def __init__(self, worldInit):
        self.gridsize = worldInit['grid']
        self.X = self.gridsize[0]
        self.Y = self.gridsize[1]
        self.wampa = worldInit['wampa']
        self.pits = worldInit['pits']
        self.luke = worldInit['luke']
        self.wampaAlive = True

        # calculate breeze and stench locations
        breeze = []
        for pit in self.pits:
            breeze += fit_grid(self.gridsize, pit)
        stench = fit_grid(self.gridsize, self.wampa)

        # prepopulate grid with percepts
        self.grid = [
            [
                [
                    "stench" if [x, y] in stench else None,
                    "breeze" if [x, y] in breeze else None,
                    None,  # "gasp" index
                    None,  # "bump" index
                    None   # "scream" index
                ]
                for y in range(self.Y)
            ]
            for x in range(self.X)
        ]

        # set "gasp" percept at Luke's location
        self.grid[self.luke[0]][self.luke[1]][2] = "gasp"
        self.agent = Agent(self)

    def get_percepts(self):
        x, y = self.agent.loc
        return self.grid[x][y]

    def take_action(self, action):
        x, y = self.agent.loc
        self.agent.score -= 1

        #R2 moves forward from whatever direction he's facing
        if action == "forward":
            moved = True
            orientation = get_direction(self.agent.degrees)
            if orientation == "up":
                if y < len(self.grid[0]) - 1:
                    self.agent.loc = (x, y + 1)
                else:
                    moved = False
            elif orientation == "down":
                if y > 0:
                    self.agent.loc = (x, y - 1)
                else:
                    moved = False
            elif orientation == "left":
                if x > 0:
                    self.agent.loc = (x - 1, y)
                else:
                    moved = False
            elif orientation == "right":
                if x < len(self.grid) - 1:
                    self.agent.loc = (x + 1, y)
                else:
                    moved = False
            if (self.get_location() == self.wampa and self.wampaAlive) or \
                self.get_location() in self.pits:
                self.agent.score -= 1000
                print("R2-D2 has been crushed, -1000 points")
                print("Your final score is: ", self.agent.score)
                quit()
            if moved == False:
                percepts = self.get_percepts()
                percepts[3] = "bump"
            else:
                percepts = self.get_percepts()
                percepts[3] = None  # reset bump = None if no bump

        #R2 turns left
        elif action == "left":
            self.agent.turn_left()
            percepts = self.get_percepts()
            percepts[3] = None  # cannot experience a bump upon a turn

        #R2 turns right
        elif action == "right":
            self.agent.turn_right()
            percepts = self.get_percepts()
            percepts[3] = None  # cannot experience a bump upon a turn

        #R2 fires his blaster
        elif action == "shoot":
            blaster = self.get_blaster()
            if blaster:
                self.agent.blaster = False
                if self.is_facing_wampa():
                    self.wampaAlive = False
                    self.wampa = None
                    for x in range(self.gridsize[0]):
                        for y in range(self.gridsize[1]):
                            self.grid[x][y][4] = "scream"  # scream everywhere
                            self.grid[x][y][0] = None  # stench is gone
                print("Blaster bolt was shot")
            print("No more blaster bolts available")

        #R2 grabs Luke
        elif action == "grab":
            if self.get_location() == self.luke and not self.agent.has_luke:
                self.agent.has_luke = True
                self.luke = None
                print("R2-D2 has picked up Luke")
            elif self.agent.has_luke:
                print("R2 already has Luke")
            else:
                print("R2 cannot pick up Luke here")

        #R2 climbs out
        elif action == "climb":
            if self.agent.has_luke and self.agent.loc == (0, 0):
                self.agent.score += 1000
                print("Congrats! R2 has saved Luke! +1000 points!")
                print("Your final score is: ", self.agent.score)
                quit()
            else:
                print("Climb requirements are not met yet")

        else:
            raise ValueError("R2-D2 can only move Forward, turn Left, turn \
                             Right, Shoot, Grab, or Climb.")
    
    def get_location(self):
        x, y = self.agent.loc
        return [x, y]
    
    def get_blaster(self):
        return self.agent.blaster
    
    def is_facing_wampa(self):
        """You may wish to use this in all_safe_next_actions"""
        if self.agent.KB.wampa is None:
            return False
        x, y = self.agent.loc
        wx, wy = self.wampa
        direction = get_direction(self.agent.degrees)
        return (direction == "up" and wx == x and wy > y) or \
                (direction == "down" and wx == x and wy < y) or \
                (direction == "left" and wx < x and wy == y) or \
                (direction == "right" and wx > x and wy == y)

# DEFINE R2D2's POSSIBLE ACTIONS
def all_safe_next_actions(w):
    """Define R2D2's valid and safe next actions based on his current location
    and knowledge of the environment."""
    actions = ['left', 'right']
    x, y = w.agent.loc
    dx, dy = w.agent.orientation_to_delta[get_direction(w.agent.degrees)]
    forward_room = (x+dx, y+dy)
    if forward_room in w.agent.KB.safe_rooms and \
        forward_room not in w.agent.KB.walls:
        actions.append('forward')
    if w.agent.blaster and w.is_facing_wampa():
        actions.append('shoot')
    if w.agent.has_luke and w.agent.loc == (0, 0):
        actions.append('climb')
    if w.agent.KB.luke == w.agent.loc and not w.agent.has_luke:
        actions.append('grab')

    return actions

def choose_next_action(w):
    """Choose next action from all safe next actions. You may want to
    prioritizesome actions based on current state. For example, if R2D2
    knows Luke's location and is in the same room as Luke, you may want
    to prioritize 'grab' over all other actions. Similarly, if R2D2 has
    Luke, you may want to prioritize moving toward the exit. You can
    implement this as basically (randomly choosing between safe actions)
    or as sophisticated (optimizing exploration of unvisited states,
    finding shortest paths, etc.) as you like."""
    actions = all_safe_next_actions(w)
    if 'climb' in actions:
        return 'climb'
    elif 'grab' in actions:
        return 'grab'
    elif 'shoot' in actions:
        w.agent.KB.safe_rooms.add(w.agent.KB.wampa)  # if shot, room safe
        return 'shoot'
    x, y = w.agent.loc
    dx, dy = w.agent.orientation_to_delta[get_direction(w.agent.degrees)]
    forward_room = (x+dx, y+dy)
    if 'forward' in actions and \
        (forward_room not in w.agent.KB.visited_rooms or
         (w.agent.has_luke and (dx == -1 or dy == -1))):
        return 'forward'
    else:
        shuffle(actions)
        return actions.pop()

# RUN THE GAME
w = WampaWorld(S1)
while True:
    visualize_world(w, w.agent.loc, get_direction(w.agent.degrees))
    percepts = w.get_percepts()
    w.agent.record_percepts(percepts, w.agent.loc)
    w.agent.inference_algorithm()
    action = choose_next_action(w)
    w.take_action(action)
    # sleep(.25)
