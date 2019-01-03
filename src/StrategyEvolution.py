from scipy.stats import norm
from src.Auction import *
import random

INITIAL_POLY_DEGREE = 2
INITIAL_POLY_COEFFICEINT_STD = 0.1


def run_ga(auction=Auction(), generations=10e3, population_size=100, tournament_prob=0.75, tournament_size=2,
           crossover_probability=0.5, mutation_probability=0.1, insertion_probability=0.05, elitism_copies=0):
    population = initialize_population(population_size)
    for i_generation in range(int(generations)):
        decoded_population = list(map(lambda coeff: decode_chromosome(coeff), population))
        auction.with_players(decoded_population)
        best_individual_idx, fitnesses = get_fitnesses(auction)
        best_individual = population[best_individual_idx]

        # Operators.
        apply_selection(population, fitnesses, tournament_prob, tournament_size)
        apply_crossover(population, crossover_probability)
        apply_mutation(population, mutation_probability, insertion_probability)
        apply_elitism(population, best_individual, elitism_copies)
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


def new_coefficient():
    return norm.rvs(loc=0, scale=INITIAL_POLY_COEFFICEINT_STD)


def initialize_population(population_size: int) -> List[List[float]]:
    population = []
    for i in range(population_size):
        population.append([new_coefficient() for _i in range(INITIAL_POLY_DEGREE + 1)])
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


# Operators

def apply_elitism(population, best_individual, num_copies):
    for i in range(num_copies):
        population[i] = best_individual.copy()


def apply_mutation(population: List[List[float]], mutation_probability: float, extension_probability: float):
    for chromosome in population:
        for i in range(len(chromosome)):
            if mutation_probability > random.random():
                chromosome[i] = new_coefficient()
        if extension_probability > random.random():
            # Coinflip: Extend or remove?
            if 0.5 > random.random():
                chromosome.append(new_coefficient())
            else:
                remove_idx = random.choice(range(len(chromosome)))
                chromosome[remove_idx] = 0


def apply_crossover(population: List[List[float]], crossover_probability: float):
    assert(len(population) % 2 == 0)
    for i in range(0, len(population), 2):
        if crossover_probability > random.random():
            ind1, ind2 = population[i], population[i+1]
            max_slicepoint = min(len(ind1), len(ind2))
            slicepoint = random.choice(range(max_slicepoint))
            new_ind1 = ind1[:slicepoint] + ind2[slicepoint:]
            new_ind2 = ind2[:slicepoint] + ind1[slicepoint:]
            population[i] = new_ind1
            population[i+1] = new_ind2

def apply_selection(population: List[List[float]], fitnesses: List[float], tournament_prob: float, tournament_size: int):
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
    for i in range(len(new_population)):
        population[i] = new_population[i]


def unzip(l):
    return zip(*l)
