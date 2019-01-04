from src.StrategyEvolution import run_ga
import cProfile
from src.FixedAuctions import *

def profile():
    cProfile.run('res = run_ga(generations=100)')


fixed_auctions['second_price'].players
