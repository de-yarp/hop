import random as r
from copy import deepcopy

from utils.helpers import (
    _day_of_the_week,
    _days_sorted_by_difficulty,
    _dayshift,
    _get_coverage_score,
    _get_fairness_penalty,
    _get_night_count,
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
) -> list[list[int]]:
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

    return shifts_1


def repair_night_fairness(
    shifts: list[list[int]],
    guards: dict[int, dict[str, set[int]]],
) -> list[list[int]]:
    V = len(guards)
    days = len(shifts)
    q_n = (2 * days) // V  # floor ночных смен на человека

    shifts_new = deepcopy(shifts)
    night_count = _get_night_count(shifts_new, V)

    deficit = sum(1 for x in night_count if x < q_n)
    surplus = sum(1 for x in night_count if x > q_n)
    max_passes = min(deficit, surplus)

    for _ in range(max_passes):
        low_guards = {g for g in range(V) if night_count[g] < q_n}
        high_guards = {g for g in range(V) if night_count[g] > q_n}

        if not low_guards or not high_guards:
            break

        improved = False

        for g_low in low_guards:
            idx_g_low = g_low + 1
            forbiddens = guards[idx_g_low]["forbiddens"]
            for idx_d, s in enumerate(shifts_new):
                if g_low in s:
                    continue

                d = idx_d + 1
                weekday = _day_of_the_week(d)
                if weekday in forbiddens:
                    continue

                for slot in (1, 2):
                    g_high = shifts_new[idx_d][slot]

                    if g_high not in high_guards:
                        continue

                    shifts_new[idx_d][slot] = g_low
                    night_count[g_low] += 1
                    night_count[g_high] -= 1

                    improved = True
                    break
                if improved:
                    break
            if improved:
                break
        if not improved:
            break

    return shifts_new
