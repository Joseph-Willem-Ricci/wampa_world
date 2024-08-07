from random import shuffle
from visualize_world import visualize_world
from utils import fit_grid, get_direction, is_facing_wampa, check_blaster_hits
from scenarios import *
from agent import Agent

# ENVIRONMENT
class WampaWorld:
    def __init__(self, worldInit):
        self.gridsize = worldInit['grid']
        self.wampa = worldInit['wampa']
        self.pits = worldInit['pits']
        self.luke = worldInit['luke']
        self.wampaAlive = True

        #populate grid with breezes
        breeze = []
        for pit in worldInit['pits']:
            breeze += fit_grid(worldInit['grid'], pit)

        #prepopulate grid with percepts
        stench=fit_grid(worldInit['grid'], self.wampa)
        self.grid = [[set() for y in range(worldInit['grid'][1])] for x in range(worldInit['grid'][0])]
        for x in range(1,worldInit['grid'][0]+1):
            for y in range(1,worldInit['grid'][1]+1):
                percepts = [None, None, None, None, None]
                if [x,y] in stench: percepts[0] = "stench"
                if [x,y] in breeze: percepts[1] = "breeze"
                self.grid[x-1][y-1] = percepts
        self.grid[self.luke[0]-1][self.luke[1]-1][2] = "gasp"

        self.agent = Agent(self)

    def get_percepts(self):
        x,y = self.agent.loc
        return self.grid[x][y]

    def take_action(self, action):
        x,y = self.agent.loc
        self.agent.score-=1

        #R2 moves forward from whatever direction he's facing
        if action == "forward":
            moved = True
            orientation = get_direction(self.agent.degrees)
            if orientation == "up":
                if y < len(self.grid[0])-1:
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
                if x < len(self.grid)-1:
                    self.agent.loc = (x + 1, y)
                else:
                    moved = False
            if (self.get_location() == self.wampa and self.wampaAlive) or self.get_location() in self.pits:
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
                check_blaster_hits(self)
                print("Blaster bolt was shot")
            print("No blaster bolts available")

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
            if self.agent.has_luke and self.agent.loc == (0,0):
                self.agent.score += 1000
                print("Congrats! R2 has saved Luke! +1000 points!")
                print("Your final score is: ", self.agent.score)
                quit()
            else:
                print("Climb requirements are not met yet")

        else:
            raise ValueError("R2-D2 can only move Forward, turn Left, turn Right, Shoot, Grab, or Climb.")
    
    def get_location(self):
        x,y = self.agent.loc
        return [x+1, y+1]
    
    def get_blaster(self):
        return self.agent.blaster
    

# DEFINE R2D2's POSSIBLE ACTIONS
def all_safe_next_actions(w):
    """Define R2D2's possible safe actions based on the current state of the world."""
    actions = ['left', 'right']
    x, y = w.agent.loc
    dx, dy = w.agent.orientation_to_delta[get_direction(w.agent.degrees)]
    forward_room = (x+dx, y+dy)
    if forward_room in w.agent.KB.safe_rooms and forward_room not in w.agent.KB.walls:
        actions.append('forward')
    if w.agent.blaster and is_facing_wampa(w.agent):
        actions.append('shoot')
    if w.agent.has_luke and w.agent.loc == (0, 0):
        actions.append('climb')
    if w.agent.KB.luke == w.agent.loc and not w.agent.has_luke:
        actions.append('grab')

    return actions

def choose_next_action(w):
    """Choose next action from all safe next actions. You can prioritize some based on state."""
    actions = all_safe_next_actions(w)
    if 'climb' in actions:
        return 'climb'
    elif 'grab' in actions:
        return 'grab'
    elif 'shoot' in actions:
        return 'shoot'
    x, y = w.agent.loc
    dx, dy = w.agent.orientation_to_delta[get_direction(w.agent.degrees)]
    forward_room = (x+dx, y+dy)
    if 'forward' in actions and (forward_room not in w.agent.KB.visited_rooms or \
         (w.agent.has_luke and (dx == -1 or dy == -1))):
        return 'forward'
    else:
        shuffle(actions)
        return actions.pop()

# RUN THE GAME
w = WampaWorld(S4)
while True:
    visualize_world(w, w.agent.loc, get_direction(w.agent.degrees))
    percepts = w.get_percepts()
    w.agent.record_percepts(percepts, w.agent.loc)
    w.agent.inference_algorithm()
    action = choose_next_action(w)
    w.take_action(action)
