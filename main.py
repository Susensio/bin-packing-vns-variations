import random
import concurrent.futures

from draw import plot

import aproximation
import bpp
import optimization
import vns
import files
import results

import logs
logs.config('INFO')

random.seed(0)

# test_instance = bpp.BPInstance(10, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7])
# test_instance = bpp.BPInstance(10, [1, 5, 2, 8, 6, 2, 3, 4, 5, 8, 1, 1, 2, 3])
# test_instance = bpp.BPInstance.from_reader(files.ins)

# bin_size = 500
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

    K_MAX = (
        # 5,
        10,
        # 20,
        # 50,
    )

    t_max = 1

    # instances = list(files.Instances.easy())[:3]
    def process_instance(instance):
        logbook = []
        ins = bpp.BPInstance.from_reader(instance)
        aprox = aproximation.FirstFitAlgorithm(ins).solve()
        explorer = optimization.BPSolutionExplorer(ins, aprox)
        for algorithm, strategy in (
            # (vns.ReducedVNS, None),
            # (vns.BasicVNS, vns.LocalSearchStrategy.BEST),
            (vns.BasicVNS, vns.LocalSearchStrategy.FIRST),
        ):
            for k_max in K_MAX:
                # plot(aprox)
                # input("Press enter to continue...")
                alg = algorithm(explorer, k_max, t_max, strategy)
                alg.solve()

                experiment = results.Experiment.from_algorithm(alg)
                logs.logger.info(experiment)
                logbook.append(experiment)
                logs.logger.info(f"{len(results.logbook)=}")
        return logbook

    with concurrent.futures.ProcessPoolExecutor() as executor:
        files = files.Instances.falkenauer()
        for experiments in executor.map(process_instance, files):
            results.logbook.extend(experiments)
            logs.logger.warning(f"{len(results.logbook)}")
            results.save_logbook(results.falkenauer_file)

    # for instance in files.Instances.hard28():
    #     ins = bpp.BPInstance.from_reader(instance)
    #     aprox = aproximation.FirstFitAlgorithm(ins).solve()
    #     explorer = optimization.BPSolutionExplorer(ins, aprox)
    #     for algorithm, strategy in (
    #         # (vns.ReducedVNS, None),
    #         (vns.BasicVNS, vns.LocalSearchStrategy.BEST),
    #         (vns.BasicVNS, vns.LocalSearchStrategy.FIRST),
    #     ):
    #         for k_max in K_MAX:
    #             plot(aprox)
    #             # input("Press enter to continue...")
    #             alg = algorithm(explorer, k_max, t_max, strategy)
    #             alg.solve()
    #             sol = alg.explorer.solution
    #             # experiment = results.Experiment(
    #             #     str(files.ins.path.parent),
    #             #     files.ins.path.name,
    #             #     ins.lower_bound,
    #             #     algorithm.__name__,
    #             #     strategy.name,
    #             #     k_max,
    #             #     t_max,
    #             #     alg.elapsed_time,
    #             #     len(sol.bins),
    #             #     alg.explorer.is_optimum,
    #             # )
    #             experiment = results.Experiment.from_algorithm(alg)
    #             logs.logger.info(experiment)
    #             results.logbook.append(experiment)
    #             logs.logger.info(f"{len(results.logbook)=}")

    # k_max = 20

    # # # input("Press enter to continue...")
    # alg = aproximation.FirstFitAlgorithm(test_instance)
    # sol = alg.solve()
    # plot(sol)
    # # input("Press enter to continue...")

    # ex = optimization.BPSolutionExplorer(test_instance, sol)

    # mh = vns.BasicVNS(ex, k_max, t_max, vns.LocalSearchStrategy.BEST)
    # sol2 = mh.solve()
    # logs.logger.info(f"{mh.elapsed_time=}")
    # results.logbook.append(results.Experiment(files.ins, test_instance.lower_bound,
    # k_max, t_max, 0, len(sol.bins))
    # # input("Press enter to continue...")
    # plot(sol2)

    # # input("Press enter to continue...")
    # mh=vns.BasicVNS(ex, k_max, t_max, vns.LocalSearchStrategy.FIRST)
    # sol2=mh.solve()
    # # input("Press enter to continue...")
    # plot(sol2)

    # for instance in
