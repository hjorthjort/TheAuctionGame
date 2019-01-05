from src.StrategyEvolution import run_ga
import cProfile
from src.FixedAuctions import *

def profile():
    cProfile.run('res = run_ga(generations=100)')


auction = fixed_auctions['second_price']
print(auction)
run_ga(auction=auction)
print(auction)
pass

