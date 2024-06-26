# Wampa World

Wampa World logic-based agent homework was developed by Joseph Willem Ricci upon the original Jupyter Notebook by Lara Martin.

# Gameplay

R2D2 begins at the bottom-left location (0, 0) and must navigate the rectangular grid of unknown size. R2 can navigate left, right or forward. R2D2's goal is to rescue Luke by navigating to the room that contains Luke, "grab"ing him, and navigating back to (0, 0) to "climb" out of the cave.

Along the way, R2D2 must avoid pits which he can fall into, and must avoid the Wampa, which can destroy him. In any adjacent room to a pit, R2D2 can percieve a "breeze". In any adjacent room to a Wampa, R2D2 can percieve a "stench". There can be [0, m*n - 2] pits, and there can be [0, 1] Wampas.

R2D2 is also carrying a blaster with one shot, and can "shoot" the Wampa with a shot in its direction. If the Wampa is killed by the shot, R2D2 percieves a "scream".

A "gasp" from Luke can be percieved by R2D2, but only if they are both in the same room.

Finally, if R2D2 moves "forward" into a wall, R2D2 percieves a "bump". For this assignment, assume that R2 knows that the world is rectangular.

Percepts: stench, breeze, gasp, bump, scream

Actions: left, right, forward, grab, climb, shoot

# File Structure

## agent.py

Contains R2D2's constructor including initial knowledge base class, KB. Familiarize yourself with the knowledge base, as the agent class will be using it for logical inference.

### TODOs:

`adjacent_rooms(self, room):`
- Returns all possible adjacent rooms to 'room' that aren't known to be walls.

`record_percepts(self, sensed_percepts, current_location):`
- For each sensed percept, update the respective percept in the knowledge base
- Given R2's current location, update safe_rooms, visited_rooms and possible_rooms. (possible_rooms represents adjacent rooms to current location, regardless of whether it is safe or possible to move there.)

`room_could_be_pit(self, query_room)`
- Given the rules of the game, return True if the query_room could be a pit given KB, False otherwise.

`room_could_be_wampa(self, query_room)`
- Given the rules of the game, return True if the query_room could be a wampa given KB, False otherwise.

`enumerate_possible_worlds(self)`
- Return all possible combinations of pit and wampa locations consistent with the rules.
- Define a list of rooms from self.KB.possible_rooms that could be a pit or wampa.
- Use itertools combinations to return a set of all possible_worlds of (pit_rooms, wampa_room)

`find_model_of_KB(self, possible_worlds)`
- Given all possible_worlds, return the subset of possible worlds that is consistent with the KB (e.g. whether it is possible that each pit_room in pit_rooms could be a pit, etc.)

`query_set_of_worlds(self, query_feature, room, worlds)`
- Where query_feature can be "pit" or "wampa", filter the set of worlds to those in which query feature is true in given room.

`inference_algorithm(self):`
- This is where R2D2's logical decision making takes place.
- Infer wall locations given bump percept.
- Infer Luke's location given gasp percept.
- Infer whether the Wampa is alive given the scream percept.
- Infer Wampa location and whether a room is safe to move to using by following the backward-chaining resolution algorithm:
1. Enumerate possible worlds
2. Find subset of possible worlds consistent with KB
3. For each adjacent room, filter possible worlds and consistent worlds to those consistent with query (e.g. "wampa in adj_room?")
4. If set of consistent worlds filtered by query is subset of possible worlds filtered by query, the query is entailed by the KB
5. Update KB.wampa and KB.safe_rooms accordingly

## scenarios.py

Contains five scenarios, S1, S2, S3, S4 and S5 to test your program with. Feel free to write your own!

## utils.py

Contains miscellaneous helper and utility functions for various parts of the code. You may want to utilize `flatten(tup)`, `get_direction(degrees)`, and `is_facing_wampa(agent)`.

## visualize_world.py

Is called during gameplay to visualize the current state of the world.

## wampa_world.py

Contains the WampaWorld class which defines gameplay, the main gameplay loop, and

### TODOs:

`all_safe_next_actions(w)`
- Define R2D2's possible safe actions based on the current state of the world.

`choose_next_action(w)`
- Choose next action from all safe next actions. You can prioritize some based on state.