from scipy.stats import norm
from src.Auction import *
import random

INITIAL_POLY_DEGREE = 2
INITIAL_POLY_COEFFICEINT_STD = 3


def run_ga(auction=Auction(), generations=10e3, population_size=100, tournament_prob=0.75, tournament_size=2, elitism_copies=1):
    population = initialize_population(population_size)
    for i_generation in range(int(generations)):
        decoded_population = list(map(lambda coeff: decode_chromosome(coeff), population))
        auction.with_players(decoded_population)
        best_individual, fitnesses = get_fitnesses(auction)
        population = apply_selection(population, fitnesses, tournament_prob, tournament_size)
    return population


def decode_chromosome(coefficients: List[float]) -> Player:
    """A chromosome is a list of real numbers, representing coefficients of a polynomial. This function turns it into a
    strategy. It takes the utility of a course, evaluates the polynomial at that point, and assigns that as a bid, in
    the end normalizing all bids so that they add up to the max bid. """
    def evaluate_poly_at(x: float) -> float:
        total = 0
        for i in range(len(coefficients)):
            total += coefficients[i] * (x ** i)
        return total

    def strategy(max_tokens: int, _num_players: int, utilities: Dict[Course, float]):
        courses, uts = unzip(list(utilities.items()))
        courses = list(courses)  # They are turned into tuples by unzip for some reason.
        uts = list(uts)
        bids = uts.copy()
        for i in range(len(uts)):
            bids[i] = evaluate_poly_at(uts[i])
        normalizing_factor = max_tokens / sum(bids)
        bids = list(map(lambda x: x * normalizing_factor, bids))
        return dict(zip(courses, bids))
    return Player(strategy=strategy)


def initialize_population(population_size: int) -> List[List[float]]:
    population = []
    for i in range(population_size):
        population.append([norm.rvs(loc=0, scale=INITIAL_POLY_COEFFICEINT_STD) for _i in range(INITIAL_POLY_DEGREE + 1)])
    return population


def get_fitnesses(auction):
    best_fitness = -math.inf
    best_individual = -1
    res, all_utilities = auction.run_auction()
    fitnesses = [0] * len(res)
    for individual_idx in range(len(res)):
        if res[individual_idx] is None:
            continue
        pay, course = res[individual_idx]
        utilities = all_utilities[individual_idx]
        fitness = utilities[course] - pay
        fitnesses[individual_idx] = fitness
        if best_fitness < fitness:
            best_fitness = fitness
            best_individual = individual_idx
    return best_individual, fitnesses


def apply_selection(population, fitnesses, tournament_prob, tournament_size):
    new_population = [None] * len(population)
    for individual_idx in range(len(population)):
        # Pick contestants.
        contestants = [None] * tournament_size
        for contestant_idx in range(tournament_size):
            r = random.choice(range(len(population)))
            contestants[contestant_idx] = (fitnesses[r], population[r])
        # Sort them.
        contestants.sort(key=lambda x: x[0], reverse=True)  # Sort on fitness, high to low.
        # Play them off against each other.
        tourn_idx = 0
        while random.random() > tournament_prob and tourn_idx < tournament_size - 1:
            tourn_idx += 1
        # Add winner to population.
        _winner_fitness, winner = contestants[tourn_idx]
        new_population[individual_idx] = winner
        # End single tournament.
    # End population creation.
    return new_population


def unzip(l):
    return zip(*l)
