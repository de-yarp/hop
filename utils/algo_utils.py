from random import random as rand
from typing import Literal

from utils.helpers import (
    _get_coverage_score,
    _get_fairness_penalty,
    _get_pref_score,
    _is_candidate_better,
    _is_pref,
    _is_schedule_valid,
)

EPS = 1e-6


def _dayshift(
    guards: dict[int, dict[str, set[int]]],
    available: list[tuple[int, int, int]],
    quotas: dict[str, int],
    day_count: list[int],
    shifts: list[list[int]],
    extra_day_used: int,
    unavailable_day_guards: set[int],
) -> tuple[list[int], int, list[list[int]], set[int]]:
    V = len(guards)

    q_d = quotas["q_d"]
    r_d = quotas["r_d"]

    extra_day_used = 0

    for d, weekday, _ in available:
        idx_d = d - 1
        best_idx: int | None = None
        best_pref: int | None = None
        best_shift_count: int | None = None

        fallback: bool = False

        # dayshift
        for g in guards:
            idx_g = g - 1
            if weekday in guards[g]["forbiddens"]:
                continue
            if idx_g in shifts[idx_d]:
                continue

            cur_pref = _is_pref(guards, g, weekday)
            cur_shift_count = day_count[idx_g]

            if cur_shift_count < q_d or (
                cur_shift_count == q_d and extra_day_used < r_d
            ):
                if best_idx is None:
                    best_idx = idx_g
                    best_pref = cur_pref
                    best_shift_count = cur_shift_count
                    continue

                candidate_is_better = _is_candidate_better(
                    best_idx=best_idx,
                    idx_g=idx_g,
                    best_pref=best_pref,
                    cur_pref=cur_pref,
                    best_shift_count=best_shift_count,
                    cur_shift_count=cur_shift_count,
                )
                if candidate_is_better:
                    best_idx = idx_g
                    best_pref = cur_pref
                    best_shift_count = cur_shift_count
                    continue

        if best_idx is None:
            fallback = True
        else:
            shifts[idx_d][0] = best_idx
            day_count[best_idx] += 1
            if best_shift_count == q_d and extra_day_used < r_d:
                extra_day_used += 1

        # dayshift fallback
        if fallback:
            best_idx = None
            best_pref = None
            best_shift_count = None

            for g in guards:
                idx_g = g - 1
                if idx_g not in unavailable_day_guards:
                    if weekday in guards[g]["forbiddens"]:
                        continue
                    if idx_g in shifts[idx_d]:
                        continue

                    cur_pref = _is_pref(guards, g, weekday)
                    cur_shift_count = day_count[idx_g]

                    if best_idx is None:
                        best_idx = idx_g
                        best_pref = cur_pref
                        best_shift_count = cur_shift_count
                        continue

                    candidate_is_better = _is_candidate_better(
                        best_idx=best_idx,
                        idx_g=idx_g,
                        best_pref=best_pref,
                        cur_pref=cur_pref,
                        best_shift_count=best_shift_count,
                        cur_shift_count=cur_shift_count,
                    )
                    if candidate_is_better:
                        best_idx = idx_g
                        best_pref = cur_pref
                        best_shift_count = cur_shift_count
                        continue

            shifts[idx_d][0] = best_idx
            day_count[best_idx] += 1
            unavailable_day_guards.add(best_idx)

    return (day_count, extra_day_used, shifts, unavailable_day_guards)


def _nightshift(
    guards: dict[int, dict[str, set[int]]],
    available: list[tuple[int, int, int]],
    quotas: dict[str, int],
    day_count: list[int],
    night_count: list[int],
    shifts: list[list[int]],
    extra_night_used: int,
    unavailable_night_guards: set[int],
    nightshift_num: Literal[1, 2],
) -> tuple[list[int], int, list[list[int]], set[int]]:
    q_n = quotas["q_n"]
    r_n = quotas["r_n"]

    for d, weekday, _ in available:
        idx_d = d - 1
        best_idx: int | None = None
        best_pref: int | None = None
        best_shift_count: int | None = None

        fallback: bool = False

        # nightshift
        for g in guards:
            idx_g = g - 1
            if weekday in guards[g]["forbiddens"]:
                continue
            if idx_g in shifts[idx_d]:
                continue

            cur_pref = _is_pref(guards, g, weekday)
            cur_shift_count = night_count[idx_g]

            if cur_shift_count < q_n or (
                cur_shift_count == q_n and extra_night_used < r_n
            ):
                if best_idx is None:
                    best_idx = idx_g
                    best_pref = cur_pref
                    best_shift_count = cur_shift_count
                    continue

                candidate_is_better = _is_candidate_better(
                    best_idx=best_idx,
                    idx_g=idx_g,
                    best_pref=best_pref,
                    cur_pref=cur_pref,
                    best_shift_count=best_shift_count,
                    cur_shift_count=cur_shift_count,
                )
                if candidate_is_better:
                    best_idx = idx_g
                    best_pref = cur_pref
                    best_shift_count = cur_shift_count
                    continue

        if best_idx is None:
            fallback = True
        else:
            shifts[idx_d][nightshift_num] = best_idx
            night_count[best_idx] += 1
            if best_shift_count == q_n and extra_night_used < r_n:
                extra_night_used += 1

        # nightshift fallback
        if fallback:
            best_idx = None
            best_pref = None
            best_shift_count = None
            min_night = None

            for g in guards:
                idx_g = g - 1
                if idx_g not in unavailable_night_guards:
                    if weekday in guards[g]["forbiddens"]:
                        continue
                    if idx_g in shifts[idx_d]:
                        continue

                    cur_night = night_count[idx_g]
                    cur_pref = _is_pref(guards, g, weekday)
                    cur_shift_count = day_count[idx_g] + night_count[idx_g]

                    if min_night is None or cur_night < min_night:
                        min_night = cur_night
                        best_idx = idx_g
                        best_pref = cur_pref
                        best_shift_count = cur_shift_count
                        continue

                    if cur_night > min_night:
                        continue

                    candidate_is_better = _is_candidate_better(
                        best_idx=best_idx,
                        idx_g=idx_g,
                        best_pref=best_pref,
                        cur_pref=cur_pref,
                        best_shift_count=best_shift_count,
                        cur_shift_count=cur_shift_count,
                    )
                    if candidate_is_better:
                        best_idx = idx_g
                        best_pref = cur_pref
                        best_shift_count = cur_shift_count
                        continue

            shifts[idx_d][nightshift_num] = best_idx
            night_count[best_idx] += 1
            unavailable_night_guards.add(best_idx)

    return (night_count, extra_night_used, shifts, unavailable_night_guards)


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


def _is_new_schedule_better(
    guards: dict[int, dict[str, set[int]]],
    shifts_2: list[list[int]],
    pref_score_1: float,
    cov_score_1: float,
    penalty_1: int,
) -> bool:
    valid = _is_schedule_valid(shifts_2, guards)
    if not valid:
        return False

    pref_score_2 = _get_pref_score(shifts_2, guards)
    delta_pref = pref_score_2 - pref_score_1
    if delta_pref > EPS:
        return True
    if delta_pref < -EPS:
        return False

    cov_score_2 = _get_coverage_score(shifts_2, guards)
    delta_cov = cov_score_2 - cov_score_1
    if delta_cov > EPS:
        return True
    if delta_cov < -EPS:
        return False

    penalty_2 = _get_fairness_penalty(shifts_2, guards)
    if penalty_2 < penalty_1:
        return True
    if penalty_2 > penalty_1:
        return False

    if rand() <= 0.5:
        return True

    return False
