from src.StrategyEvolution import run_ga
import cProfile
from src.FixedAuctions import *
import copy

def profile():
    cProfile.run('res = run_ga(generations=100)')


auction = fixed_auctions['first_price']
run_ga(auction, generations=20)
print ("       \\infty & %10d\\\\" %int(round(auction.get_allocative_efficiency()[0])))

auction = fixed_auctions['second_price']
run_ga(auction, generations=20)
print ("       \\infty & %10d\\\\" %int(round(auction.get_allocative_efficiency()[0])))

auction = fixed_auctions['realistic1']
#print(auction)
_total, max_utility = auction.get_allocative_efficiency()
auction_history = []
for max_bid in [math.inf, 250, 200, 100, 50, 25, 10, 1, 0.01, 0.0000001]:
    auction.max_bid = max_bid
    run_ga(auction=auction, generations=30, start_range=auction.max_bid)
    if max_bid == math.inf:
        print ("       \\infty & %10d\\\\" %int(round(auction.get_allocative_efficiency()[0])))
    else:
        print("%10d &\t%10d\\\\" % (int(round(max_bid)), int(round(auction.get_allocative_efficiency()[0]))))
    auction_history.append(copy.deepcopy(auction))
pass
