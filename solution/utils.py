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