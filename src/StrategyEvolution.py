from scipy.stats import norm
from typing import Callable
from src.Auction import *
import random
import numpy as np


def run_ga(auction=Auction(), generations=10e3, population_size=100, tournament_prob=0.75, tournament_size=2,
           crossover_prob=0.5, mutation_prob=0.1, elitism_copies=1, creep_factor=0.2, start_range=1):
    """Modifies players strategies to have them perform optimally, but modifies nothing else about the auction."""
    players = auction.players
    populations = [initialize_population(population_size, len(auction.courses), start_range, auction.max_bid) for _p in players]  # One population for each player.
    for i_generation in range(int(generations)):
        print(auction)
        for player_idx in range(len(players)):
            population = populations[player_idx]
            decoded_population = list(map(lambda bids: decode_chromosome(bids), population))
            fitnesses = get_fitnesses(auction, player_idx, decoded_population)
            best_individual_idx = fitnesses.index(max(fitnesses))
            best_individual = population[best_individual_idx]

            # Operators.
            apply_selection(population, fitnesses, tournament_prob, tournament_size)
            apply_crossover(population, crossover_prob)
            apply_mutation(population, mutation_prob, creep_factor, auction.max_bid)
            apply_elitism(population, best_individual, elitism_copies)
            players[player_idx].strategy = decoded_population[best_individual_idx]


def decode_chromosome(bids: List[float]) -> Strategy:  # Returns a bidding strategy.
    def strategy(courses: List[Course]):
        assert(len(courses) == len(bids))
        courses_and_bids = dict(zip(courses, bids))
        return courses_and_bids
    return strategy


def initialize_population(population_size: int, chromosome_length: int, start_range: float, max_bid: float) -> List[List[float]]:
    population = []
    for i in range(population_size):
        population.append([min(max_bid, abs(norm.rvs() * start_range)) for _i in range(chromosome_length)])
    return population


def get_fitnesses(auction: Auction, player_idx: int, strategies: List[Strategy]) -> List[float]:
    fitnesses = [.0] * len(strategies)
    for individual_idx in range(len(strategies)):
        current_strategy = strategies[individual_idx]
        auction.players[player_idx].strategy = current_strategy
        res = auction.run_auction()
        if res[player_idx] is None:
            fitnesses[individual_idx] = 0
            continue
        pay, course = res[player_idx]
        if course is None:
            utility = 0
        else:
            utility = auction.players[player_idx].utilities[course]
        fitness = utility - pay
        fitnesses[individual_idx] = fitness
    return fitnesses


# Operators

def apply_elitism(population, best_individual, num_copies):
    for i in range(num_copies):
        population[i] = best_individual.copy()


def apply_mutation(population: List[List[float]], mutation_probability: float, creep_factor: float, max_bid):
    for chromosome in population:
        for i in range(len(chromosome)):
            if mutation_probability > random.random():
                creep_range = max(1.0, creep_factor * chromosome[i])
                creep = random.random() * creep_range - creep_range / 2
                new_gene = max(0.0, chromosome[i] + creep)
                new_gene = min(max_bid, new_gene)
                chromosome[i] = new_gene


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
