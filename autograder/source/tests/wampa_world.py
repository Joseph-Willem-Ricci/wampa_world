import sys
from scenarios import *
from agent import Agent
from utils import get_direction, is_facing_wampa

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
        self.game_is_running = True

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
                self.game_is_running = False
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
            if self.agent.blaster:
                self.agent.blaster = False
                if is_facing_wampa(self.agent):
                    self.wampaAlive = False
                    self.wampa = None
                    for x in range(self.gridsize[0]):
                        for y in range(self.gridsize[1]):
                            self.grid[x][y][4] = "scream"  # scream everywhere
                            self.grid[x][y][0] = None  # stench is gone

        #R2 grabs Luke
        elif action == "grab":
            if self.get_location() == self.luke and not self.agent.has_luke:
                self.agent.has_luke = True
                self.luke = None

        #R2 climbs out
        elif action == "climb":
            if self.agent.has_luke and self.agent.loc == (0, 0):
                self.agent.score += 1000
                self.game_is_running = False

        else:
            raise ValueError("R2-D2 can only move Forward, turn Left, turn \
                             Right, Shoot, Grab, or Climb.")
    
    def get_location(self):
        x, y = self.agent.loc
        return [x, y]

# RUN THE GAME
def run_game(scenario):
    w = WampaWorld(scenario)
    while w.game_is_running:
        percepts = w.get_percepts()
        w.agent.record_percepts(percepts, w.agent.loc)
        w.agent.inference_algorithm()
        action = w.agent.choose_next_action()
        w.take_action(action)

    return w.agent.score, w.agent.has_luke, w.agent.loc

def main():
    if len(sys.argv) != 2:
        quit()
    
    scenario_name = sys.argv[1]

    try:
        scenario = eval(scenario_name)
    except KeyError:
        quit()

    run_game(scenario)

if __name__ == "__main__":
    main()