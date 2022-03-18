from dataclasses import dataclass
from pathlib import Path
import pickle
import pandas as pd
import vns

pickle_file = Path('output.pickle')
excel_file = Path('output.xls')
falkenauer_file = Path('output_falkenauer.xls')


@dataclass
class Experiment:
    folder: str
    instance: str
    items: int
    lower_bound: int
    algorithm: str
    local_search: str
    k_max: int
    t_max: int
    t: float
    bins: int
    optimum: bool

    @classmethod
    def from_algorithm(cls, alg: vns.VNS):
        return cls(
            str(alg.explorer.instance.source.parent),
            alg.explorer.instance.source.name,
            len(alg.explorer.instance.items),
            alg.explorer.instance.lower_bound,
            alg.__class__.__name__,
            getattr(alg.local_strategy, 'name', None),
            alg.k_max,
            alg.t_max,
            alg.timer.elapsed_time,
            len(alg.explorer.solution.bins),
            alg.explorer.is_optimum,
        )


logbook = []


def save_logbook(file=excel_file):
    # with pickle_file.open('wb') as file:
    #     pickle.dump(logbook, file)
    df = pd.DataFrame.from_dict(logbook)
    df.to_excel(file)
