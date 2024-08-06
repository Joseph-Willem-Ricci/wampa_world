from math import modf

def flatten(tup):
    if len(tup) == 1:
        return tup[0]
    return tup

def get_direction(degrees):
    fraction = (degrees % 360) / 360
    orientation = None
    match fraction:
        case 0:
            orientation = "up"
        case 0.25:
            orientation = "right"
        case 0.5:
            orientation = "down"
        case 0.75:
            orientation = "left"
    return orientation

def is_facing_wampa(agent):
    if agent.KB.wampa is None:
        return False
    x, y = agent.loc
    wx, wy = agent.KB.wampa
    direction = get_direction(agent.degrees)
    return (direction == "up" and wx == x and wy > y) or \
            (direction == "down" and wx == x and wy < y) or \
            (direction == "left" and wx < x and wy == y) or \
            (direction == "right" and wx > x and wy == y)
  
def fit_grid(grid, item):
    grid_x, grid_y = grid
    x, y = item
    loc = []

    if x < grid_x:
        loc += [[x+1,y]]
    if x > 1:
        loc += [[x-1,y]]
    if y < grid_y:
        loc += [[x,y+1]]
    if y > 1:
        loc += [[x,y-1]]

    return loc

def check_blaster_hits(world):
    #DO NOT CALL OR YOU WILL LOSE 5 POINTS ON THE ASSIGNMENT
    direction = get_direction(world.agent.degrees)
    x, y = world.agent.loc
    x+=1
    y+=1
    hit = False
    if (direction == "up" and world.wampa[1] > y and world.wampa[0] == x) or \
        (direction == "down" and world.wampa[1] < y and world.wampa[0] == x) or \
        (direction == "left" and world.wampa[0] < x and world.wampa[1] == y) or \
        (direction == "right" and world.wampa[0] > x and world.wampa[1] == y):
        hit = True
        world.wampaAlive = False
        world.wampa = None
    if hit:
        for x in range(len(world.grid)):
            for y in range(len(world.grid[0])):
                world.grid[x][y][4]="scream"
                world.grid[x][y][0]=None