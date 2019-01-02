from scipy.stats import uniform

import matplotlib.pyplot as plt
import numpy as np

#import random
#from datetime import datetime
#random.seed(datetime.now())  # So that we have truly random numbers.

class Auction:
    """Class that can simulate and auction."""

    def __init__(self, max_tokens=100, players=None, courses=None, clearing_function=None):
        if courses is None:
            courses = [Course() for i in range(3)]
        if players is None:
            players = [Player() for i in range(10)]
        self.max_tokens = max_tokens
        self.courses = courses
        self.players = players
        if clearing_function is None:
            self.clearing_function = default_clearing_function
        else:
            self.clearing_function = clearing_function

    def run_auction(self):
        """returns the allocations of courses to players."""
        all_bids = []
        for p in self.players:
            #  Draw a random utility for each course.
            utilities = [c.popularity_distribution() for c in self.courses]
            num_players = len(self.players)
            bids = p.strategy(self.max_tokens, num_players, utilities, self.courses)
            all_bids.append(bids)
        return self.clearing_function(all_bids, self.courses)


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


def _default_strategy(max_tokens, _num_players, utilities, courses):
    """The "all-in" strategy."""
    assert(len(utilities) == len(courses))
    bids = [0] * len(courses)
    idx_of_max = utilities.index(max(utilities))
    bids[idx_of_max] = max_tokens
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
#  This function intializes the plot with empty data.
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
    plt.xlabel(r'Iteration number ($t$)')
    plt.ylabel(r'Population fraction $x_i$')
    plt.title(r'Evolution of population fraction')

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