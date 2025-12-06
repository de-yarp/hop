import random as r
from copy import deepcopy

from utils.helpers import (
    _days_sorted_by_difficulty,
    _dayshift,
    _get_coverage_score,
    _get_fairness_penalty,
    _get_pref_score,
    _get_quota,
    _is_new_schedule_better,
    _nightshift,
    _swap,
)


def get_quotas_and_days_sorted(
    guards: dict[int, dict[str, set[int]]], days: int
) -> tuple[dict[str, int], list[tuple[int, int, int]]]:
    quotas = _get_quota(guards, days)
    available = _days_sorted_by_difficulty(guards, days)

    return quotas, available


def init_solution(
    guards: dict[int, dict[str, set[int]]],
    available: list[tuple[int, int, int]],
    quotas: dict[str, int],
) -> list[list[int]]:
    V = len(guards)

    day_count = [0] * V
    night_count = [0] * V
    extra_day_used, extra_night_used = 0, 0

    shifts = [[-1, -1, -1] for _ in range(len(available))]

    unavailable_day_guards = set()
    unavailable_night_guards = set()

    # dayshift
    day_count, extra_day_used, shifts, unavailable_day_guards = _dayshift(
        guards,
        available,
        quotas,
        day_count,
        shifts,
        extra_day_used,
        unavailable_day_guards,
    )

    # nightshift 1
    night_count, extra_night_used, shifts, unavailable_night_guards = _nightshift(
        guards,
        available,
        quotas,
        day_count,
        night_count,
        shifts,
        extra_night_used,
        unavailable_night_guards,
        nightshift_num=1,
    )

    # nightshift 2
    night_count, extra_night_used, shifts, unavailable_night_guards = _nightshift(
        guards,
        available,
        quotas,
        day_count,
        night_count,
        shifts,
        extra_night_used,
        unavailable_night_guards,
        nightshift_num=2,
    )

    # print(f"day_count: {day_count}\n")
    # print(f"night_count: {night_count}\n")
    # print(f"extra_day_used: {extra_day_used}\n")
    # print(f"extra_night_used: {extra_night_used}\n")
    # print(f"unavailable_day_guards: {unavailable_day_guards}\n")
    # print(f"unavailable_night_guards: {unavailable_night_guards}")
    return shifts


def optimize_schedule(
    shifts: list[list[int]],
    guards: dict[int, dict[str, set[int]]],
    rng: r.Random,
    max_iter: int,
) -> tuple[list[list[int]], float, float, int]:
    shifts_1 = deepcopy(shifts)
    pref_score_1 = _get_pref_score(shifts_1, guards)
    cov_score_1 = _get_coverage_score(shifts_1, guards)
    penalty_1 = _get_fairness_penalty(shifts_1, guards)

    for _ in range(max_iter):
        shifts_2 = _swap(shifts_1, rng)
        better, pref2, cov2, pen2 = _is_new_schedule_better(
            guards, rng, shifts_2, pref_score_1, cov_score_1, penalty_1
        )
        if better:
            shifts_1 = shifts_2
            pref_score_1 = pref2
            cov_score_1 = cov2
            penalty_1 = pen2

    return (shifts_1, pref_score_1, cov_score_1, penalty_1)
