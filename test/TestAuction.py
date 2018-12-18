import unittest
from src.Auction import *


class TestAuction(unittest.TestCase):

    def test_run_simple(self):
        auction = Auction()  # Default implementation.
        res = auction.run_auction()  # Just make sure nothing fails.
        print(res)  # TODO: Remove

