from src.StrategyEvolution import run_ga
import cProfile

cProfile.run('res = run_ga(generations=100)')

