import random

from draw import plot

import aproximation
import bpp
import optimization
import vns
import files

import logs
logs.config('TRACE')


# test_instance = bpp.BPInstance(10, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7])
# test_instance = bpp.BPInstance(10, [1, 5, 2, 8, 6, 2, 3, 4, 5, 8, 1, 1, 2, 3])
test_instance = bpp.BPInstance.from_reader(files.ins)
# random.seed(0)
# bin_size = 100
# test_instance = bpp.BPInstance(
#     bin_size, [int(bin_size*random.random()*0.5)+1
#                for _ in range(int(bin_size*3))])

if __name__ == "__main__":

    #     test_instance = BPInstance(
    #         10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5])

    #     for Algorithm in (
    #         NextFitAlgorithm,
    #         FirstFitAlgorithm,
    #         FirstFitDecreasingAlgorithm,
    #     ):
    #         alg = Algorithm(test_instance)
    #         sol = alg.solve()
    #         sol.print_stats()
    #         plot(sol)
    k_max = 15
    t_max = 60

    input("Press enter to continue...")
    alg = aproximation.NextFitAlgorithm(test_instance)
    sol = alg.solve()
    plot(sol)
    input("Press enter to continue...")

    ex = optimization.BPSolutionExplorer(sol)

    mh = vns.BasicVNS(ex, k_max, t_max, strategy=vns.LocalSearchStrategy.BEST)
    sol2 = mh.solve()
    # input("Press enter to continue...")
    plot(sol2)

    input("Press enter to continue...")
    mh = vns.BasicVNS(ex, k_max, t_max, strategy=vns.LocalSearchStrategy.FIRST)
    sol2 = mh.solve()
    # input("Press enter to continue...")
    plot(sol2)

    input("Press enter to continue...")
    mh = vns.ReducedVNS(ex, k_max, t_max)
    sol2 = mh.solve()
    # input("Press enter to continue...")
    plot(sol2)

    # plot(ex.solution)
    # ex.print_stats()
    # ex2 = ex.improve()
    # plot(ex2.solution)
    # ex2.print_stats()

    # for m in sol.possible_moves():
    #     print(m)

    # moves = sol.possible_moves()
    # m = random.choice(moves)

    # plot(sol)
    # print(m)
    # m.apply_to_solution(sol)
    # plot(sol)
