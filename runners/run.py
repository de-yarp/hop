import random as r
from pathlib import Path
from time import perf_counter

from utils.algo_utils import (
    get_quotas_and_days_sorted,
    init_solution,
    optimize_schedule,
    repair_night_fairness,
)
from utils.data_utils import parse_input, save_output
from utils.helpers import (
    _get_coverage_score,
    _get_fairness_penalty,
    _get_pref_score,
    _is_schedule_valid,
)
from utils.print_utils import print_result


def run_optimization(
    input_file_name: str, output_file_name: str, days: int, max_iter: int, seed: int
) -> None:
    t1 = perf_counter()

    # parameters
    fin = Path("data") / "input" / input_file_name
    fout = Path("data") / "results" / output_file_name
    rng = r.Random(seed)

    # preparation
    guards = parse_input(fin)
    quotas, available = get_quotas_and_days_sorted(guards, days)
    shifts_1 = init_solution(guards, available, quotas)

    # initial score
    pref_score_1 = _get_pref_score(shifts_1, guards)
    cov_score_1 = _get_coverage_score(shifts_1, guards)
    penalty_1 = _get_fairness_penalty(shifts_1, guards)

    # optimization
    shifts_2 = optimize_schedule(shifts_1, guards, rng, max_iter)
    shifts_2 = repair_night_fairness(shifts_2, guards)
    assert _is_schedule_valid(shifts_2, guards)

    # final score
    pref_score_2 = _get_pref_score(shifts_2, guards)
    cov_score_2 = _get_coverage_score(shifts_2, guards)
    penalty_2 = _get_fairness_penalty(shifts_2, guards)

    # save results to ./data/results/
    save_output(fout, shifts_2)

    t2 = perf_counter()
    t_d = t2 - t1

    # results
    print_result(
        guards,
        shifts_1,
        shifts_2,
        t_d,
        pref_score_1,
        pref_score_2,
        cov_score_1,
        cov_score_2,
        penalty_1,
        penalty_2,
    )

    # print(_is_schedule_valid(shifts_2, guards))
