from src.StrategyEvolution import run_ga
import cProfile
from src.FixedAuctions import *

def profile():
    cProfile.run('res = run_ga(generations=100)')


auction = fixed_auctions['realistic1']
print(auction)
run_ga(auction=auction, start_range=auction.max_bid)
print(auction)
pass

