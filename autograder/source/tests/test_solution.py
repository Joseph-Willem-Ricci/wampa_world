# import itertools
import os.path
import unittest
# import mock
# import timeout_decorator
from gradescope_utils.autograder_utils.decorators import weight, visibility, tags
from agent import Agent
from wampa_world import WampaWorld, run_game
from scenarios import *

def relpath(*args):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, *args)

class TestSolution(unittest.TestCase):

    # TEST RECORD PERCEPTS #
    # @timeout_decorator.timeout(12)
    def test_record_percepts_stench(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(['stench', 'breeze', 'gasp', 'bump', 'scream'], (9, 9))
        self.assertEqual(w.agent.KB.stench, {(9, 9)}, msg = "Expected KB.stench to have room with stench in it after stench is perceived")

    # @timeout_decorator.timeout(12)
    def test_record_percepts_breeze(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(['stench', 'breeze', 'gasp', 'bump', 'scream'], (9, 9))
        self.assertEqual(w.agent.KB.breeze, {(9, 9)}, msg = "Expected KB.breeze to have room with breeze in it after breeze is perceived")

    # @timeout_decorator.timeout(12)
    def test_record_percepts_gasp(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(['stench', 'breeze', 'gasp', 'bump', 'scream'], (9, 9))
        self.assertEqual(w.agent.KB.gasp, True, msg = "Expected KB.gasp to be True after gasp is perceived")

    # @timeout_decorator.timeout(12)
    def test_record_percepts_bump(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(['stench', 'breeze', 'gasp', 'bump', 'scream'], (9, 9))
        self.assertEqual(w.agent.KB.bump, {(9, 9): "up"}, msg = "Expected KB.bump to have room with bump in it after bump is perceived")

    # @timeout_decorator.timeout(12)
    def test_record_percepts_scream(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(['stench', 'breeze', 'gasp', 'bump', 'scream'], (9, 9))
        self.assertEqual(w.agent.KB.scream, True, msg = "Expected KB.scream to be True after scream is perceived")


    # TEST ENUMERATE POSSIBLE WORLDS #
    # @timeout_decorator.timeout(12)
    def test_enumerate_possible_worlds_1(self):
        w = WampaWorld(S1)
        student_possible_worlds = w.agent.enumerate_possible_worlds()
        self.assertEqual(student_possible_worlds, {((), ())}, msg = "Expected possible worlds from initial position on S1 to be {(), ()} as shown in README.")

    # @timeout_decorator.timeout(12)
    def test_enumerate_possible_worlds_2(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.inference_algorithm()
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_possible_worlds = w.agent.enumerate_possible_worlds()
        solution_possible_worlds = {
            ((), ()),
            ((), (-1, 1)),
            ((), (0, 2)),
            ((), (1, 1)),
            (((-1, 1),), ()),
            (((-1, 1),), (0, 2)),
            (((-1, 1),), (1, 1)),
            (((-1, 1), (0, 2)), ()),
            (((-1, 1), (0, 2)), (1, 1)),
            (((-1, 1), (1, 1)), ()),
            (((-1, 1), (1, 1)), (0, 2)),
            (((-1, 1), (1, 1), (0, 2)), ()),
            (((0, 2),), ()),
            (((0, 2),), (-1, 1)),
            (((0, 2),), (1, 1)),
            (((1, 1),), ()),
            (((1, 1),), (-1, 1)),
            (((1, 1),), (0, 2)),
            (((1, 1), (0, 2)), ()),
            (((1, 1), (0, 2)), (-1, 1))
        }
        self.assertEqual(student_possible_worlds, solution_possible_worlds, msg = "Expected possible worlds after 'forward' from initial position on S1 to be as shown in README.")

     # @timeout_decorator.timeout(12)
    def test_enumerate_possible_worlds_3(self):
        """Tests the same situation as described in the previous test case
        and in the README, after visiting (0, 0), (1, 0) and (0, 1) on S1,
        except with bumps having been perceived in {(0, 1), "left"} and {(1, 0), "down"}
        so """
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("left")
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.infer_wall_locations()
        w.take_action("left")
        w.take_action("forward")
        w.take_action("left")
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("right")
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.infer_wall_locations()
        student_possible_worlds = w.agent.enumerate_possible_worlds()
        is_any_room_negative = False
        for _, w in student_possible_worlds:
            if w:
                x, y = w
                if x < 0 or y < 0:
                    is_any_room_negative = True
        self.assertFalse(is_any_room_negative, msg = "Expected no possible worlds with negative room coordinates after visiting (0, 0), (1, 0) and (0, 1) on S1 with bumps perceived down and left.")


    # TEST CONSISTENCY CHECKS #
    # @timeout_decorator.timeout(12)
    def test_pit_room_is_consistent_with_KB_1(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.loc = (1, 0)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_check = w.agent.pit_room_is_consistent_with_KB((2, 0))
        self.assertEqual(student_check, True, msg = "On S1, after visiting (0, 0), (1, 0) and (0, 1), expected pit_room_is_consistent_with_KB((2, 0)) to be True.")

    # @timeout_decorator.timeout(12)
    def test_pit_room_is_consistent_with_KB_2(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.loc = (1, 0)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_check = w.agent.pit_room_is_consistent_with_KB((1, 1))
        self.assertEqual(student_check, False, msg = "On S1, after visiting (0, 0), (1, 0) and (0, 1), expected pit_room_is_consistent_with_KB((1, 1)) to be False.")

    # @timeout_decorator.timeout(12)
    def test_wampa_room_is_consistent_with_KB_1(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.loc = (1, 0)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_check = w.agent.wampa_room_is_consistent_with_KB((0, 2))
        self.assertEqual(student_check, True, msg = "On S1, after visiting (0, 0), (1, 0) and (0, 1), expected wampa_room_is_consistent_with_KB((0, 2)) to be True.")

    # @timeout_decorator.timeout(12)
    def test_wampa_room_is_consistent_with_KB_2(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.loc = (1, 0)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_check = w.agent.wampa_room_is_consistent_with_KB((1, 1))
        self.assertEqual(student_check, False, msg = "On S1, after visiting (0, 0), (1, 0) and (0, 1), expected wampa_room_is_consistent_with_KB((1, 1)) to be False.")

    
    # TEST MODEL OF KB #
    # @timeout_decorator.timeout(12)
    def test_model_of_KB_1(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_possible_worlds = w.agent.enumerate_possible_worlds()
        student_model_of_KB = w.agent.find_model_of_KB(student_possible_worlds)
        solution_model_of_KB = {
            ((), (-1, 1)),
            ((), (0, 2)),
            ((), (1, 1))
        }
        self.assertEqual(student_model_of_KB, solution_model_of_KB, msg = "Expected model of KB after 'forward' from initial position on S1 to be as shown in README.")

    # @timeout_decorator.timeout(12)
    def test_model_of_KB_2(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.loc = (1, 0)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_possible_worlds = w.agent.enumerate_possible_worlds()
        student_model_of_KB = w.agent.find_model_of_KB(student_possible_worlds)
        solution_model_of_KB = {
            (((1, -1),), (-1, 1)),
            (((1, -1),), (0, 2)),
            (((2, 0),), (-1, 1)),
            (((2, 0),), (0, 2)),
            (((2, 0), (1, -1)), (-1, 1)),
            (((2, 0), (1, -1)), (0, 2))
        }
        self.assertEqual(student_model_of_KB, solution_model_of_KB, msg = "Expected model of KB after visiting (0, 0), (1, 0) and (0, 1) on S1 with no bumps to be as shown in README.")

    # @timeout_decorator.timeout(12)
    def test_model_of_KB_3(self):
        """Tests the same situation as described in the previous test case
        and in the README, after visiting (0, 0), (1, 0) and (0, 1) on S1,
        except with bumps having been perceived in {(0, 1), "left"} and {(1, 0), "down"}
        so """
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("left")
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.infer_wall_locations()
        w.take_action("left")
        w.take_action("forward")
        w.take_action("left")
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("right")
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.agent.infer_wall_locations()
        student_possible_worlds = w.agent.enumerate_possible_worlds()
        student_model_of_KB = w.agent.find_model_of_KB(student_possible_worlds)
        solution_model_of_KB = {
            (((2, 0),), (0, 2))
        }
        self.assertEqual(student_model_of_KB, solution_model_of_KB, msg = "Expected model of KB after visiting (0, 0), (1, 0) and (0, 1) on S1 with bumps perceived down and left to be {(((2, 0),), (0, 2))}.")


    # TEST MODEL OF QUERY #
    # @timeout_decorator.timeout(12)
    def test_model_of_query_1(self):
        w = WampaWorld(S1)
        a = Agent(w)
        possible_worlds = {
            ((), ()),
            ((), (-1, 1)),
            ((), (0, 2)),
            ((), (1, 1)),
            (((-1, 1),), ()),
            (((-1, 1),), (0, 2)),
            (((-1, 1),), (1, 1)),
            (((-1, 1), (0, 2)), ()),
            (((-1, 1), (0, 2)), (1, 1)),
            (((-1, 1), (1, 1)), ()),
            (((-1, 1), (1, 1)), (0, 2)),
            (((-1, 1), (1, 1), (0, 2)), ()),
            (((0, 2),), ()),
            (((0, 2),), (-1, 1)),
            (((0, 2),), (1, 1)),
            (((1, 1),), ()),
            (((1, 1),), (-1, 1)),
            (((1, 1),), (0, 2)),
            (((1, 1), (0, 2)), ()),
            (((1, 1), (0, 2)), (-1, 1))
        }
        solution_model_of_query = {
            ((), (0, 2)),
            (((-1, 1),), (0, 2)),
            (((-1, 1), (1, 1)), (0, 2)),
            (((1, 1),), (0, 2))
        }
        student_model_of_query = a.find_model_of_query("wampa_in_room", (0, 2), possible_worlds)
        self.assertEqual(student_model_of_query, solution_model_of_query, msg = "Expected model of query 'wampa_in_room', (0, 2) the state in S1 as shown in README to be as shown in README.")

    # @timeout_decorator.timeout(12)
    def test_model_of_query_2(self):
        w = WampaWorld(S1)
        a = Agent(w)
        possible_worlds = {
            ((), ()),
            ((), (-1, 1)),
            ((), (0, 2)),
            ((), (1, 1)),
            (((-1, 1),), ()),
            (((-1, 1),), (0, 2)),
            (((-1, 1),), (1, 1)),
            (((-1, 1), (0, 2)), ()),
            (((-1, 1), (0, 2)), (1, 1)),
            (((-1, 1), (1, 1)), ()),
            (((-1, 1), (1, 1)), (0, 2)),
            (((-1, 1), (1, 1), (0, 2)), ()),
            (((0, 2),), ()),
            (((0, 2),), (-1, 1)),
            (((0, 2),), (1, 1)),
            (((1, 1),), ()),
            (((1, 1),), (-1, 1)),
            (((1, 1),), (0, 2)),
            (((1, 1), (0, 2)), ()),
            (((1, 1), (0, 2)), (-1, 1))
        }
        student_model_of_query = a.find_model_of_query("no_wampa_in_room", (0, 2), possible_worlds)
        model_of_query_contains_0_2 = any([True for model in student_model_of_query if (0, 2) in model[1]])
        self.assertFalse(model_of_query_contains_0_2, msg = "Expected model of query 'no_wampa_in_room', (0, 2) in the state on S1 shown in the README not to include (0, 2) as a Wampa Room.")

    # @timeout_decorator.timeout(12)
    def test_model_of_query_3(self):
        w = WampaWorld(S1)
        a = Agent(w)
        possible_worlds = {
            ((), ()),
            ((), (-1, 1)),
            ((), (0, 2)),
            ((), (1, 1)),
            (((-1, 1),), ()),
            (((-1, 1),), (0, 2)),
            (((-1, 1),), (1, 1)),
            (((-1, 1), (0, 2)), ()),
            (((-1, 1), (0, 2)), (1, 1)),
            (((-1, 1), (1, 1)), ()),
            (((-1, 1), (1, 1)), (0, 2)),
            (((-1, 1), (1, 1), (0, 2)), ()),
            (((0, 2),), ()),
            (((0, 2),), (-1, 1)),
            (((0, 2),), (1, 1)),
            (((1, 1),), ()),
            (((1, 1),), (-1, 1)),
            (((1, 1),), (0, 2)),
            (((1, 1), (0, 2)), ()),
            (((1, 1), (0, 2)), (-1, 1))
        }
        solution_model_of_query = {
            (((-1, 1), (0, 2)), ()),
            (((-1, 1), (0, 2)), (1, 1)),
            (((-1, 1), (1, 1), (0, 2)), ()),
            (((0, 2),), ()),
            (((0, 2),), (-1, 1)),
            (((0, 2),), (1, 1)),
            (((1, 1), (0, 2)), ()),
            (((1, 1), (0, 2)), (-1, 1))
        }
        student_model_of_query = a.find_model_of_query("pit_in_room", (0, 2), possible_worlds)
        self.assertEqual(student_model_of_query, solution_model_of_query, msg = "Expected all worlds in model of query 'pit_in_room', (0, 2) in step 1 on S1 as shown in the README to include (0, 2) as a pit room")

    # @timeout_decorator.timeout(12)
    def test_model_of_query_4(self):
        w = WampaWorld(S1)
        a = Agent(w)
        possible_worlds = {
            ((), ()),
            ((), (-1, 1)),
            ((), (0, 2)),
            ((), (1, 1)),
            (((-1, 1),), ()),
            (((-1, 1),), (0, 2)),
            (((-1, 1),), (1, 1)),
            (((-1, 1), (0, 2)), ()),
            (((-1, 1), (0, 2)), (1, 1)),
            (((-1, 1), (1, 1)), ()),
            (((-1, 1), (1, 1)), (0, 2)),
            (((-1, 1), (1, 1), (0, 2)), ()),
            (((0, 2),), ()),
            (((0, 2),), (-1, 1)),
            (((0, 2),), (1, 1)),
            (((1, 1),), ()),
            (((1, 1),), (-1, 1)),
            (((1, 1),), (0, 2)),
            (((1, 1), (0, 2)), ()),
            (((1, 1), (0, 2)), (-1, 1))
        }
        solution_model_of_query = {
            ((), ()),
            ((), (-1, 1)),
            ((), (0, 2)),
            ((), (1, 1)),
            (((-1, 1),), ()),
            (((-1, 1),), (0, 2)),
            (((-1, 1),), (1, 1)),
            (((-1, 1), (1, 1)), ()),
            (((-1, 1), (1, 1)), (0, 2)),
            (((1, 1),), ()),
            (((1, 1),), (-1, 1)),
            (((1, 1),), (0, 2))
        }
        student_model_of_query = a.find_model_of_query("no_pit_in_room", (0, 2), possible_worlds)
        self.assertEqual(student_model_of_query, solution_model_of_query)


    # TEST ALL SAFE NEXT ACTIONS #
    def test_all_safe_next_actions(self):
        w = WampaWorld(S1)
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        w.take_action("forward")
        w.agent.record_percepts(w.get_percepts(), w.agent.loc)
        student_actions = w.agent.all_safe_next_actions()
        forward_in_student_actions = True if "forward" in student_actions else False
        self.assertFalse(forward_in_student_actions, msg = "Expected 'forward' not to be in safe actions after 'forward' from initial position on S1.")


    # TEST FULL SOLUTIONS #
    def test_run_game_1(self):
        score, has_luke, loc = run_game(S1)
        self.assertGreater(score, 0, msg = "Expected score to be greater than 0 after running game on S1.")
        self.assertTrue(has_luke, msg = "Expected R2D2 to have luke after running game on S1.")
        self.assertEqual(loc, (0, 0), msg = "Expected R2D2 to be in room (0, 0) after running game on S1.")

    def test_run_game_2(self):
        score, has_luke, loc = run_game(S2)
        self.assertGreater(score, 0, msg = "Expected score to be greater than 0 after running game on S2.")
        self.assertTrue(has_luke, msg = "Expected R2D2 to have luke after running game on S2.")
        self.assertEqual(loc, (0, 0), msg = "Expected R2D2 to be in room (0, 0) after running game on S2.")

    def test_run_game_3(self):
        score, has_luke, loc = run_game(S3)
        self.assertGreater(score, 0, msg = "Expected score to be greater than 0 after running game on S3.")
        self.assertTrue(has_luke, msg = "Expected R2D2 to have luke after running game on S3.")
        self.assertEqual(loc, (0, 0), msg = "Expected R2D2 to be in room (0, 0) after running game on S3.")
    
    def test_run_game_4(self):
        score, has_luke, loc = run_game(S4)
        self.assertGreater(score, 0, msg = "Expected score to be greater than 0 after running game on S4.")
        self.assertTrue(has_luke, msg = "Expected R2D2 to have luke after running game on S4.")
        self.assertEqual(loc, (0, 0), msg = "Expected R2D2 to be in room (0, 0) after running game on S4.")
    
    def test_run_game_5(self):
        score, has_luke, loc = run_game(S5)
        self.assertGreater(score, 0, msg = "Expected score to be greater than 0 after running game on S5.")
        self.assertTrue(has_luke, msg = "Expected R2D2 to have luke after running game on S5.")
        self.assertEqual(loc, (0, 0), msg = "Expected R2D2 to be in room (0, 0) after running game on S5.")
    
    def test_run_game_6(self):
        score, has_luke, loc = run_game(S6)
        self.assertGreater(score, 0, msg = "Expected score to be greater than 0 after running game on S6.")
        self.assertTrue(has_luke, msg = "Expected R2D2 to have luke after running game on S6.")
        self.assertEqual(loc, (0, 0), msg = "Expected R2D2 to be in room (0, 0) after running game on S6.")
    


if __name__ == '__main__':
    unittest.main()