from typing import Dict, List
import math
from scipy.stats import uniform


class Auction:
    """Class that can simulate and auction."""

    def __init__(self, max_tokens=100, players=None, courses=None, clearing_function=None):
        if courses is None:
            courses = [Course() for _i in range(3)]
        if players is None:
            players = [Player() for _i in range(2)]
        self.max_tokens = max_tokens
        self.courses = courses
        self.players = players
        if clearing_function is None:
            self.clearing_function = default_clearing_function
        else:
            self.clearing_function = clearing_function

    def with_players(self, players):
        self.players = players

    def run_auction(self):
        """returns the allocations of courses to players."""
        all_bids = []
        all_utilities = []
        for p in self.players:
            #  Draw a random utility for each course.
            utilities = {c: c.popularity_distribution() for c in self.courses}
            all_utilities.append(utilities)
            num_players = len(self.players)
            bids = p.strategy(self.max_tokens, num_players, utilities)
            all_bids.append(bids)
        return self.clearing_function(all_bids, self.courses), all_utilities


class Player:

    def __init__(self, strategy=None):
        if strategy is None:
            self.strategy = _default_strategy
        else:
            self.strategy = strategy


class Course:

    def __init__(self, capacity=1, popularity_distribution=None, name="Unnamed course"):
        self.capacity = capacity
        if popularity_distribution is None:
            self.popularity_distribution = uniform_distribution(0, 1000)
        else:
            self.popularity_distribution = popularity_distribution
        self.name = name

    def __repr__(self):
        return "{" + self.name + ", id: " + str(id(self)) + ", capacity: " + str(self.capacity) + "}"


#  Useful default functions.
"""
A clearing function returns a list of tuples:
(student_index, course_object)
"""


def default_clearing_function(bids, courses):
    """Just assign courses in the order they come in the array, until they are full."""
    assignments = [0] * len(courses)
    payment = 0  # Same for all.
    student_idx = 0
    course_idx = 0
    ret = [None] * len(bids)
    while student_idx < len(bids) and course_idx < len(courses):
        c = courses[course_idx]
        if assignments[course_idx] < c.capacity:
            assignments[course_idx] += 1
            ret[student_idx] = (payment, c)
            student_idx += 1
        else:
            course_idx += 1
    return ret


def _default_strategy(max_tokens: int, _num_players: int, utilities: List[Dict[Course, float]]):
    """The "all-in" strategy."""
    bids = {}
    max_utility = -math.inf
    most_valued_course = None
    for course, utility in utilities.items():
        if max_utility < utility:
            if most_valued_course is not None:
                bids[most_valued_course] = 0
            bids[course] = max_tokens
            max_utility = utility
            most_valued_course = course
        else:
            bids[course] = 0
    return bids


def uniform_distribution(range_min, range_max):
    def dist():
        return range_min + uniform.rvs() * (range_max - range_min)
    return dist


def applied_clearing_function(bids, courses):
    n_player = len(bids)
    n_courses = len(courses)
    price=[0]*n_courses
    left_capacity=[0]*n_courses
    assignment = [[-1, -1]] * n_player     #1st position: assigned class, 2nd cost of class

    for c in range(n_courses):
        left_capacity[c] = courses[c].capacity

    for i in range(n_player):
        # search for highest bid
        highest_bid_player = -1
        highest_bid_course = -1
        highest_bid_value = -1

        for p in range(n_player):
            if assignment[p][0] is not -1:
                p = p+1
            else:
                for c in range(n_courses):
                    if left_capacity[c] < 0:
                        c = c+1
                    else:
                        if bids[p][c] > highest_bid_value:
                            highest_bid_value = bids[p][c]
                            highest_bid_player = p
                            highest_bid_course = c


        if left_capacity[highest_bid_course] is 0:          # set price if first player cant enter
            price[highest_bid_course] = highest_bid_value
            left_capacity[highest_bid_course] -= 1
        else:                                               # assign player if free spot avaliable
            assignment[highest_bid_player][0] = highest_bid_course
            left_capacity[highest_bid_course] -= 1

    for i in range(n_player):
        assignment[i][1] = price[assignment[i][0]]

    return assignment

    # assign player corresponding to highest bid
    # if player can be assigned: remove all bids of player
    # else: update price (price array)of course and remove all bids for that course





    # assign bid to course


