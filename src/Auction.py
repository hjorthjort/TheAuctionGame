from typing import Dict, List, Tuple
import math
from scipy.stats import uniform

import matplotlib.pyplot as plt
import numpy as np

import random

class Auction:
    """Class that can simulate an auction."""

    def __init__(self, max_tokens=100, players=None, courses=None, clearing_function=None):
        if courses is None:
            courses = [Course() for _i in range(3)]
        if players is None:
            players = [Player() for _i in range(3)]
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
        return self.clearing_function(all_bids), all_utilities


class Player:

    def __init__(self, strategy=None):
        if strategy is None:
            self.strategy = default_strategy
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
The bids in sent to the clearing function are in a list, each index representing the bids of the player with that index.
 Input: List of Dict from Course to Bid.
 Output: List of tuples: the payment and the course. Indexed according to the bids index.

Example: Player0 bids 10 for course1, 5 for course 2.
         Player1 bids 7 for course1, 11 for course 2.
Input: [{course1: 10, course2: 5},
        {course1: 7,  course2: 11}]
Output: [(10, course1), (11, course2)]  -- This would be a first-price assignment.
"""


def default_clearing_function(bids: List[Dict[Course, float]]) -> List[Tuple[float, Course]]:
    """First-price auction: highest overall bid gets assigned a course, pay that price."""
    assignments = [None] * len(bids)
    bids_flattened = []
    capacities = {}
    for player_idx in range(len(bids)):
        bids_of_player = bids[player_idx]
        for course, bid in bids_of_player.items():
            bids_flattened.append((player_idx, course, bid))
            capacities[course] = course.capacity
    bids_flattened.sort(key=lambda item: item[2], reverse=True)  # Sort on bid, descending.
    assigned_players = set()
    for player, course, bid in bids_flattened:
        if player not in assigned_players\
                and capacities[course] > 0:
            assignments[player] = (bid, course)
            assigned_players.add(player)
            capacities[course] -= 1
    return assignments


def default_strategy(max_tokens: float, _num_players: int, utilities: Dict[Course, float]) -> Dict[Course, float]:
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

def random_strategy(max_tokens: float, _num_players: int,
                      utilities: Dict[Course, float]) -> Dict[Course, float]:
    """
    You bid a value at random, subject to the constraint that it all
    must sum to one.
    """
    bids = {}
    available_money = max_tokens
    for course, utility in utilities.items():
        bids[course] = random.random() * available_money
        available_money -= bids[course]

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


# # # Plotting functions.

#  This function just initializes a figure with a given number of line plots.
#  It outputs a list where list[0] is the figure and list[1] is a list with
#  line plot objects. This is important as update_plot takes this list and
#  will update the plot data with new data being inputted.
#  This function initializes the plot with empty data.
#  It takes as INPUT the number of strategies you want to plot.
def init_plot_population(number_of_strat, names_of_strats):
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
    #  for different style types.
    plt.style.use('seaborn-talk')

    plt.xlabel('Run number')
    plt.ylabel('Win number')
    plt.title('Win count for different strategies after averaging')

    plot_list = []
    for i in range(0, number_of_strat):
        line, = plt.plot(strategy_population[i], color=tableau20[i % 20])
        plot_list.append(line)

    plt.legend(plot_list, names_of_strats)

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

def find_winning_strategy():
    ### Control variables
    number_of_courses = 3
    number_of_players = 3
    number_of_measurements = 5      # Between how many runs do we stop to update
                                    # the plot and measure.
    runs_between_measures = 100    # How many times run the whole process, ie,
                                    # how many times to start over with different
                                    # strategies.
    number_to_average = 200     # How much to average before looking at the highest
                                # utility to determine the winner. I've chosen this
                                # number as it is such that the variance intervals
                                # centered on the mean don't overlap between the
                                # winner and the second in line.

    types_of_strategies  = [default_strategy,
                            random_strategy]
    number_of_strategies = len(types_of_strategies)
    names_of_strategies  = [types_of_strategies[i].__name__
                            for i in range(0, number_of_strategies)]
    '''
    plot_output = init_plot_population(number_of_strategies,
                                       names_of_strategies)
    '''

    win_counter = np.zeros([number_of_strategies,
                            number_of_measurements*runs_between_measures])

    course_list = [Course(name=str(i), capacity=1)
                   for i in range(0, number_of_courses)]

    for i_measure in range(0, number_of_measurements): # start from 1 to avoid having
                                                       # to define some if statements
        for run in range(0, runs_between_measures):
            player_list = [Player(strategy=random.choice(types_of_strategies))
                                    for i in range(0, number_of_players) ]

            utility = np.zeros([number_of_players, number_to_average])
            average_utility = np.zeros(number_of_players)
            sigma_utility   = np.zeros(number_of_players) # For std. deviation

            # In this loop we run the auction several times and record final utilities.
            for i in range(0, number_to_average):
                auction = Auction(players = player_list, courses = course_list)
                outcome = auction.run_auction()
                payments  = outcome[0] # Type List[Dict[Course, float]]
                utilities = outcome[1] # Type List[Tuple[float, Course]]
                for pl_i in range(0, number_of_players):
                    course_won      = payments[pl_i][1]
                    utility[pl_i,i] = ( utilities[pl_i][course_won]
                                       -payments[pl_i][0])
            # Now we average.
            for i in range(0,number_of_players):
                average_utility[i] = np.average(utility[i,:])
                # Using the formula for the standard deviation of the mean or average:
                sigma_utility[i]   = (  np.sqrt(np.var(utility[i,:]))
                                       /np.sqrt(number_to_average)    )

            # Now we find the winner.
            winner_idx = np.argmax(average_utility)
            # The following gets the name of the winning strategy and finds its index.
            winning_strategy_idx = names_of_strategies.index(
                                        player_list[winner_idx].strategy.__name__ )

            aux_idx = i_measure*runs_between_measures + run
            win_counter[:,aux_idx] = win_counter[:,aux_idx-1]
            win_counter[winning_strategy_idx,aux_idx] += 1


        print('Measurement = '+str(i_measure)+'. Average utilities:')
        for i in range(0, number_of_players):
            print('Player',i,
                  '{0: <16}'.format(player_list[i].strategy.__name__), '\t',
                  round(average_utility[i],1), "+-",
                  round(sigma_utility[i]  ,1))
        print('\n')

        #update_plot(plot_output, i_measure, win_counter[i_measure])

    # The winning strategy is the one with most win counts at the wnd:
    final_winning_strategy_idx = np.argmax(win_counter[:,-1])
    print('*******')
    print('And the winner iiiissss .....: ',
                names_of_strategies[final_winning_strategy_idx])
    print('*******')

    x_axis = np.arange(0, number_of_measurements*runs_between_measures, 1)
    for i in range(0, number_of_strategies):
        plt.plot(x_axis, win_counter[i,:], label=names_of_strategies[i])

    # If the plot functions don't work use this, which plots at the end. With the
    # plot functions you plot live.
    plt.xlabel('Run number')
    plt.ylabel('Win count')
    plt.title('Win count for different strategies after averaging')
    plt.legend()
    plt.show()

find_winning_strategy()

