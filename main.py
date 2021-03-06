# import sys
# if sys.version_info < (3, 5):
#     raise RuntimeError("This package requres Python 3.5+")

import random
import concurrent.futures

from draw import plot

import approximation
import bpp
import optimization
import vns
import files
import results
import utils

import logs


random.seed(0)

if __name__ == "__main__":

    if utils.ask_yes_or_no("Do you want to run the small test optimization?"):
        logs.config('DEBUG')

        print("The file ./images/result.png will be updated for each algorithm.")

        n_items = int(input("Enter the test instance size (default=30): ") or 0) or 30
        bin_size = max(10, n_items // 3)
        test_instance = bpp.BPInstance(
            bin_size, [int(bin_size*random.random()*0.6)+1
                       for _ in range(n_items)])

        print(test_instance)

        print("")
        print("APPROXIMATION")
        print("Testing approximation algorithms...")
        for algorithm in (
            approximation.NullAlgorithm,
            approximation.NextFitAlgorithm,
            approximation.FirstFitAlgorithm,
            # approximation.FirstFitDecreasingAlgorithm,
        ):
            alg = algorithm(test_instance)
            sol = alg.solve()
            # sol.print_stats()
            print("")
            print(algorithm.__name__)
            print(f"{len(sol.bins)=}, {test_instance.lower_bound=}")
            plot(sol)
            utils.ask_continue()

        print("")
        print("OPTIMIZATION")
        input("Running VNS on last approximation algorithm...")
        explorer = optimization.BPSolutionExplorer(test_instance, sol)
        k_max = 20

        t_max = 10

        for algorithm, strategy in (
            (vns.ReducedVNS, None),
            (vns.BasicVNS, vns.LocalSearchStrategy.BEST),
            (vns.BasicVNS, vns.LocalSearchStrategy.FIRST),
        ):
            alg = algorithm(explorer, k_max, t_max, strategy)
            alg.solve()
            sol = alg.explorer.solution

            plot(sol)
            print(algorithm.__name__)
            print(f"{len(sol.bins)=}, {test_instance.lower_bound=}")

            utils.ask_continue()

    if utils.ask_yes_or_no("Run the full Falkenauer optimization? (this may take hours)"):
        logs.config('INFO')
        K_MAX = (
            10,
            20,
            50,
        )

        t_max = 60

        def process_instance(instance):
            logbook = []
            ins = bpp.BPInstance.from_reader(instance)
            aprox = approximation.FirstFitAlgorithm(ins).solve()
            explorer = optimization.BPSolutionExplorer(ins, aprox)
            for algorithm, strategy in (
                (vns.ReducedVNS, None),
                (vns.BasicVNS, vns.LocalSearchStrategy.BEST),
                (vns.BasicVNS, vns.LocalSearchStrategy.FIRST),
            ):
                for k_max in K_MAX:
                    # plot(aprox)
                    # utils.ask_continue()
                    alg = algorithm(explorer, k_max, t_max, strategy)
                    alg.solve()

                    experiment = results.Experiment.from_algorithm(alg)
                    logs.logger.info(experiment)
                    logbook.append(experiment)
                    # logs.logger.info(f"{len(results.logbook)}")
            return logbook

        # Multiprocessing for faster execution
        with concurrent.futures.ProcessPoolExecutor() as executor:
            files = files.Instances.falkenauer()
            for experiments in executor.map(process_instance, files):
                results.logbook.extend(experiments)
                logs.logger.success(f"Total experiments={len(results.logbook)}")
                results.save_logbook(results.falkenauer_file)
