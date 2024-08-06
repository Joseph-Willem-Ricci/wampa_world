# Wampa World

Wampa World logic-based agent homework was developed by Joseph Willem Ricci upon the original Jupyter Notebook by Lara Martin.

# Gameplay

R2D2 begins at the bottom-left location (0, 0) and must navigate the rectangular grid of unknown size. R2 can navigate left, right or forward. R2D2's goal is to rescue Luke by navigating to the room that contains Luke, "grab"ing him, and navigating back to (0, 0) to "climb" out of the cave.

Along the way, R2D2 must avoid pits which he can fall into, and must avoid the Wampa, which can destroy him. In any adjacent room to a pit, R2D2 can percieve a "breeze". In any adjacent room to a Wampa, R2D2 can percieve a "stench". There can be [0, m*n - 2] pits, and there can be [0, 1] Wampas. Each room can have 0 or 1 features from ['luke', 'pit', 'wall', 'wampa'].

R2D2 is also carrying a blaster with one shot, and can "shoot" the Wampa with a shot in its direction. If the Wampa is killed by the shot, R2D2 percieves a "scream".

A "gasp" from Luke can be percieved by R2D2 if they are both in the same room.

Finally, if R2D2 moves "forward" into a wall, R2D2 percieves a "bump". For this assignment, assume that R2 knows that the world is rectangular.

Percepts: `['stench', 'breeze', 'gasp', 'bump', 'scream']`, where at some location, R2's percepts might look like `[None, 'breeze', None, 'bump', None]`

Actions: `'left', 'right', 'forward', 'grab', 'climb', 'shoot'`

# File Structure

## agent.py

Contains R2D2's constructor including initial knowledge base class, KB. Familiarize yourself with the knowledge base, as the agent class will be using it for logical inference.

### TODOs:

`adjacent_rooms(self, room):`
- Returns a set of tuples representing all possible adjacent rooms to 'room' that aren't known to be walls.

`record_percepts(self, sensed_percepts, current_location):`
- Update the percepts in agent's KB with the percepts sensed in the current location, and update safe_rooms, visited_rooms, and possible_rooms accordingly.

`room_could_be_pit(self, room)`
- Given the rules of the game, return True if the room could be a pit given KB, False otherwise.

`room_could_be_wampa(self, room)`
- Given the rules of the game, return True if the room could be a wampa given KB, False otherwise.

`enumerate_possible_worlds(self)`
- Return all possible combinations of pit and wampa locations consistent with the rules.

`find_model_of_KB(self, possible_worlds)`
- Return the subset of all possible worlds consistent with KB.

`query_set_of_worlds(self, query_feature, room, worlds)`
- Where query can be "pit_in_room", "wampa_in_room", "no_pit_in_room" or "no_wampa_in_room", filter the set of worlds to those which contain the query in the given room.

`inference_algorithm(self):`
- If there is no breeze or stench, infer that the adjacent rooms are safe. Infer wall locations given bump percept, Luke's location given gasp percept, and whether the Wampa is alive given scream percept.
- Infer whether each adjacent room could be a pit or could be a Wampa by following the backward-chaining resolution algorithm:
1. Enumerate possible worlds
2. Find the model of the KB, i.e. the subset of possible worlds consistent with the KB
3. For each adjacent room and each query, find the model of the query (i.e. "pit in adj_room?", "no wampa in adj_room?", etc.)
4. If the model of the KB is a subset of the model of the query, the query is entailed by the KB
5. Update KB.pits, KB.wampa, and KB.safe_rooms based on any new information inferred.

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