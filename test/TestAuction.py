import unittest
from src.Auction import *


class TestAuction(unittest.TestCase):

    def test_auction_correctness(self):
        auction = Auction()  # Default implementation.
        res = auction.run_auction()
        self.assertEqual(len(res), len(auction.players))

        actual_assignments = list(filter(lambda x: x is not None, res))  # All which are not None.
        costs = map(lambda pair: pair[0], actual_assignments)
        self.assertTrue(all(map(lambda x: 0 <= x <= auction.max_tokens, costs)), "Some payments in invalid range")

        total_capacities = sum(map(lambda c: c.capacity, auction.courses))
        total_assigned_students = len(actual_assignments)
        self.assertGreaterEqual(total_capacities, total_assigned_students,  "There are unassigned students and seats "
                                                                     "remaining.")

    def test_run_simple(self):
        auction = Auction()  # Default implementation.
        auction.run_auction()  # Just make sure nothing fails.


