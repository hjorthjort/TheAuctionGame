import unittest
import random
from src.StrategyEvolution import *


class TestAuction(unittest.TestCase):
    def test_run_ga(self):
        run_ga(generations=40, population_size=10)

    def test_unzip(self):
        l = [(random.random(), random.random()) for _i in range(100)]
        l1, l2 = unzip(l)
        self.assertListEqual(l, list(zip(l1, l2)))

    def test_crossover(self):
        population = initialize_population(100)
        total_length = sum([len(chromosome) for chromosome in population])
        apply_crossover(population, 0.7)
        self.assertEqual(total_length, sum(len(chromosome) for chromosome in population))

    def test_decode_chromosome(self):
        chromosome = [3, -1, 1]
        player = decode_chromosome(chromosome)
        courses = [Course(), Course(), Course(), Course()]
        utilities = [0, 1, -1, 3]
        course_uts =  dict(zip(courses, utilities))
        expected_bids_unnormalized = [3, 3-1+1, 3+1+1, 3-3+9]
        expected_bids = dict(zip(courses, map(lambda x: x * 10, expected_bids_unnormalized)))
        total = sum(expected_bids.values())
        bids = player.strategy(total, 0, course_uts)
        self.assertEqual(total, sum(bids.values()),)
        self.assertDictEqual(expected_bids, bids)

