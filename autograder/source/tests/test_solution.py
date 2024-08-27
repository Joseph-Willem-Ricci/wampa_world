import itertools
import os.path
import unittest
import mock
import timeout_decorator
from gradescope_utils.autograder_utils.decorators import weight, visibility, tags
from agent import Agent
from wampa_world import WampaWorld
from scenarios import *

def relpath(*args):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, *args)

class TestSolution(unittest.TestCase):

    @timeout_decorator.timeout(12)
    def test_record_percepts(self):
        w = WampaWorld(S6)
        a = Agent(w)
        a.record_percepts(['stench', 'breeze', 'gasp', 'bump', 'scream'], (9, 9))
        self.assertEqual(a.KB.stench, set(9, 9), msg = "Expected KB.stench to have room with stench in it after stench is perceived")
        self.assertEqual(a.KB.breeze, set(9, 9), msg = "Expected KB.breeze to have room with breeze in it after breeze is perceived")
        self.assertEqual(a.KB.gasp, True, msg = "Expected KB.gasp to be True after gasp is perceived")
        self.assertEqual(a.KB.scream, True, msg = "Expected KB.scream to be True after scream is perceived")
        self.assertEqual(a.KB.bump, {(9, 9): "up"}, msg = "Expected KB.bump to have room with bump in it after bump is perceived")

    @timeout_decorator.timeout(12)
    def test_enumerate_possible_worlds(self):
        w = WampaWorld(S1)
        a = Agent(w)