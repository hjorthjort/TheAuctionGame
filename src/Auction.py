import scipy as sp

class Auction:
    """Class that can simulate and auction."""

    def __init__(self, maxTokens=100, players=[], courses=[], clearingFunction=None):
        self.maxTokens = maxTokens
        self.courses = courses
        self.players = players
        self.clearingFunction = clearingFunction


class Player:

    def __init__(self, strategy=None):
        if strategy is None:
            self.strategy = _defaultStrategy
        else:
            self.strategy = strategy


class Course:

    def __init__(self, maxSeats=1, popularityDistribution=None):
        self.maxSeats = maxSeats
        if popularityDistribution is None:
            self.popularityDistribution = uniformDistribution
        else:
            self.popularityDistribution = popularityDistribution


### Useful default functions.

def _defaultStrategy(maxTokens, numPlayers, utilities, courses):
    """The "all-in" strategy."""
    assert(len(utilities) == len(courses))
    assert(len(utilities) == len(courses))
    bids = [0] * len(courses)
    idxOfMax = utilities.index(max(utilities))
    bids[idxOfMax] = maxTokens
    return bids

def uniformDistribution(min, max):
    def dist():
        min + sp.stats.uniform() * (max - min)
    return dist

