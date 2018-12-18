import scipy as sp


class Auction:
    """Class that can simulate and auction."""

    def __init__(self, max_tokens=100, players=None, courses=None, clearing_function=None):
        if courses is None:
            courses = []
        if players is None:
            players = []
        self.max_tokens = max_tokens
        self.courses = courses
        self.players = players
        self.clearing_function = clearing_function

    def run_auction(self):
        assert(len(self.utilities) == len(self.courses))
        """returns the allocations of courses to players."""
        all_bids = []
        for p in self.players:
            #  draw a random utility for each course.
            utilities = [c.popularitydistribution() for c in self.courses]
            num_players = len(self.players)
            bids = p.strategy(self.max_tokens, num_players, utilities, self.courses)
            all_bids.append(bids)
        return self.clearing_function(self.max_tokens, self.courses)


class Player:

    def __init__(self, strategy=None):
        if strategy is None:
            self.strategy = _default_strategy
        else:
            self.strategy = strategy


class Course:

    def __init__(self, capacity=1, popularity_distribution=None):
        self.capacity = capacity
        if popularity_distribution is None:
            self.popularity_distribution = uniform_distribution
        else:
            self.popularitydistribution = popularity_distribution


#  Useful default functions.
def _default_strategy(max_tokens, num_players, utilities, courses):
    """The "all-in" strategy."""
    assert(len(utilities) == len(courses))
    bids = [0] * len(courses)
    idx_of_max = utilities.index(max(utilities))
    bids[idx_of_max] = max_tokens
    return bids


def uniform_distribution(min, max):
    def dist():
        min + sp.stats.uniform() * (max - min)
    return dist

