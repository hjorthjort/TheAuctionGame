from typing import Dict, List, Tuple, Callable
import random
import math
from scipy.stats import uniform

import matplotlib.pyplot as plt
import numpy as np

#import random
#from datetime import datetime
#random.seed(datetime.now())  # So that we have truly random numbers.


class Auction:
    """Class that can simulate and auction."""

    def __init__(self, max_bid: float=100, players=None, courses=None, clearing_function=None):
        if courses is None:
            courses = [Course() for _i in range(3)]
        if players is None:
            players = [Player() for _i in range(2)]
        self.max_bid = max_bid
        self.courses = courses
        self.players = players
        if clearing_function is None:
            self.clearing_function = first_price_clearing_function
        else:
            self.clearing_function = clearing_function

    def with_players(self, players):
        self.players = players

    def run_auction(self):
        """returns the allocations of courses to players."""
        all_bids = list(map(lambda p: p.strategy(self.courses), self.players))
        return self.clearing_function(all_bids)

    def get_allocative_efficiency(self):
        all_utilities = list(map(lambda p: p.utilities, self.players))
        max_utility = 0
        total_utility = 0
        for _i in range(1000):

            res = self.run_auction()
            optimal_res = second_price_clearing_function(all_utilities)
            for i in range(len(res)):
                _pay, course = res[i]
                _pay, optimal_course = optimal_res[i]
                if course is not None:
                    total_utility += self.players[i].utilities[course]
                if optimal_course is not None:
                    max_utility += self.players[i].utilities[optimal_course]
        return total_utility/1000, max_utility/1000

    def __repr__(self):
        res = self.run_auction()
        total_utility, max_utility = self.get_allocative_efficiency()
        players_repr = ""
        for i in range(len(self.players)):
            pay, course = res[i]
            p = self.players[i]
            bids = p.strategy(self.courses)
            players_repr += "Player: " + str(i) + "\n"
            players_repr += "Utilities: " + str(p.utilities.values()) + "\n"
            players_repr += "Bids: " + str(bids.values()) + "\n"
            players_repr += "Gets: " + str(course) + " for " + str(pay) + "\n"
        return str(self.run_auction()) + "\nPlayers:\n" + players_repr + "\nTotal uitility: " + str(total_utility) + " out of max " + str(max_utility)


class Course:
    def __init__(self, capacity=1, popularity_distribution=None, name="Unnamed course"):
        self.capacity = capacity
        if popularity_distribution is None:
            self.popularity_distribution = uniform_distribution(0, 1000)
        else:
            self.popularity_distribution = popularity_distribution
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{" + self.name + ", id: " + str(id(self)) + ", capacity: " + str(self.capacity) + "}"


Strategy = Callable[[List[Course]], Dict[Course, float]]


class InfiniteDict(dict):
    def __init__(self, default_item):
        super().__init__()
        self.default_item = default_item

    def __getitem__(self, key):
        if key is None:
            return self.default_item
        return super().__getitem__(key)

    def __missing__(self, _key):
        return self.default_item


class Player:
    def __init__(self, strategy: Strategy = None, utilities: Dict[Course, float]=None):
        if strategy is None:
            self.strategy = _default_strategy
        else:
            self.strategy = strategy
        if utilities is None:
            self.utilities = InfiniteDict(0)
        else:
            self.utilities = utilities

#  Useful default functions.
"""
The bids in sent to the clearing function are in a list, each index representing the bids of the player with that index.
 Input: List of Dict from Course to Bid.
 Output: List of tuples: the payment and the course. Indexed according to the bids index.

Example: Player0 bids 10 for course1, 5 for course 2.
         Player1 bids 7 for course1, 11 for course 2.
Input: [{course1: 10, course2: 5},
        {course1: 7,  course2: 11}]
Output: [(10, course1), (11, course2)]  -- This would be a first-price assignment.
"""


def first_price_clearing_function(bids: List[Dict[Course, float]]) -> List[Tuple[float, Course]]:
    """First-price auction: highest overall bid gets assigned a course, pay that price."""
    assignments: List[Tuple[float, Course]] = [None] * len(bids)
    bids_flattened = []
    capacities = {}
    for player_idx in range(len(bids)):
        bids_of_player = bids[player_idx]
        for course, bid in bids_of_player.items():
            bids_flattened.append((player_idx, course, bid))
            capacities[course] = course.capacity
    random.shuffle(bids_flattened)  # The sorting is usually in place, so make sure we don't give the players an ordering
    bids_flattened.sort(key=lambda item: item[2], reverse=True)  # Sort on bid, descending.
    assigned_players = set()
    for player, course, bid in bids_flattened:
        if player not in assigned_players\
                and capacities[course] > 0:
            assignments[player] = (bid, course)
            assigned_players.add(player)
            capacities[course] -= 1
    return assignments


def second_price_clearing_function(bids: List[Dict[Course, float]]) -> List[Tuple[float, Course]]:
    assigned_courses: List[Course] = [None] * len(bids)
    bids_flattened = []
    capacities = {}
    for player_idx in range(len(bids)):
        bids_of_player = bids[player_idx]
        for course, bid in bids_of_player.items():
            bids_flattened.append((player_idx, course, bid))
            capacities[course] = course.capacity
    random.shuffle(bids_flattened)  # The sorting is usually in place, so make sure we don't give the players an ordering.
    bids_flattened.sort(key=lambda item: item[2], reverse=True)  # Sort on bid, descending.

    payments: Dict[Course, float] = InfiniteDict(None)
    assigned_players = set()
    for player, course, bid in bids_flattened:
        if player not in assigned_players:
            if capacities[course] > 0:
                assigned_courses[player] = course
                assigned_players.add(player)
                capacities[course] -= 1
            elif payments[course] is None:
                payments[course] = bid

    assignments = []
    for player_idx in range(len(assigned_courses)):
        course = assigned_courses[player_idx]
        if payments[course] is None:
            price = 0.0
        else:
            price = payments[course]

        assignments.append((price, course))
    return assignments


def _default_strategy(courses: List[Course]) -> Dict[Course, float]:
    """Bid 0 on everything"""
    return dict(zip(courses, [.0] * len(courses)))


def uniform_distribution(range_min, range_max):
    def dist():
        return range_min + uniform.rvs() * (range_max - range_min)
    return dist




    # assign bid to course


# # # Plotting functions.

#  This function just initializes a figure with a given number of line plots.
#  It outputs a list where list[0] is the figure and list[1] is a list with
#  line plot objects. This is important as update_plot takes this list and
#  will update the plot data with new data being inputted.
#  This function initializes the plot with empty data.
#  It takes as INPUT the number of strategies you want to plot.
def init_plot_population(number_of_strat):
    strategy_population = [None] * number_of_strat
    for i in range(0, number_of_strat):
        strategy_population[i] = np.array([])

    # Sources for plotting:
    #       http://www.randalolson.com/2014/06/28/how-to-make
    #       -beautiful-data-visualizations-in-python-with-matplotlib/
    # The following are the "Tableau 20" colors as RGB. Check
    #       https://public.tableau.com/profile/chris.gerrard#!/
    #       vizhome/TableauColors/ColorPaletteswithRGBValues
    # to see which color is which.
    tableau20 = (
        [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
         (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
         (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
         (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
         (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
    # Scale the RGB values to the [0, 1] range, which is the format matplotlib
    # accepts.
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    fig = plt.figure(figsize=(10, 7.5))

    # See
    #  https://matplotlib.org/gallery/style_sheets/style_sheets_reference.html
    # for different style types.
    plt.style.use('seaborn-talk')

    # If LaTeX gives you problems disable these labels.
   # plt.xlabel(r'Iteration number ($t$)')
   # plt.ylabel(r'Population fraction $x_i$')
   # plt.title(r'Evolution of population fraction')

    plot_list = []
    for i in range(0, number_of_strat):
        line, = plt.plot(strategy_population[i], color=tableau20[i % 20])
        plot_list.append(line)

    plt.show()
    # plt.savefig("graph.png", bbox_inches="tight")

    return fig, plot_list


#  What this will do is update the plot with the new data.
#  New data is expected in the form of a numpy array where
#       new_data[i]=x_i,
#  x_i being the population fraction of population i at the current time.
#  Note: don't input the previous values, just the present population values.
#  The plot should have been run before with init_plot_population().
#  plot_output is the output of init_plot_population().
#  Code inspired by the example from the following link:
#  https://stackoverflow.com/questions/4098131/
#  how-to-update-a-plot-in-matplotlib/4098938#4098938
def update_plot(plot_output, time, new_data):
    plot_line_list = plot_output[1]
    nr_strat = len(plot_line_list)

    for strat in range(0, nr_strat):
        plot_line_list[strat].set_ydata(
            np.append(plot_line_list[strat].get_ydata(),
                      new_data[strat]))
        plot_line_list[strat].set_xdata(
            np.append(plot_line_list[strat].get_xdata(),
                      time))  # Increase the time
    ax = plt.gca()
    ax.relim()
    ax.autoscale_view()
    fig = plot_output[0]
    fig.canvas.draw()
    fig.canvas.flush_events()


# Now I will test the functions by generating data and plotting it.
'''
time = np.arange(0.1, 20, 0.1)
plot_output = init_plot_population(3)  # plot_output[0] is the figure
# plot_output[1] is a list of line
# objects from which to pull the
# x and y data from
new_data = [None] * 3
for t in time:
    # Generate points to add to the plot:
    new_data[0] = np.exp(-t)
    new_data[1] = np.sin(t)
    new_data[2] = np.log(t)

    # Update the plot:
    update_plot(plot_output, t, new_data)
'''

