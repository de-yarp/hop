import random as r
from copy import deepcopy
from typing import Literal

EPS = 1e-6


def _get_quota(guards: dict[int, dict[str, set[int]]], days: int) -> dict[str, int]:
    V = len(guards)

    # dayshifts
    r_d = days % V
    q_d = days // V

    # nightshifts
    r_n = (days * 2) % V
    q_n = (days * 2) // V

    quotas = {}
    quotas["q_d"] = q_d
    quotas["r_d"] = r_d
    quotas["q_n"] = q_n
    quotas["r_n"] = r_n

    return quotas


def _init_guards_quantity_per_weekday(
    guards: dict[int, dict[str, set[int]]],
) -> dict[int, int]:
    quantity_per_weekday: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    week = range(1, 8)

    for idx in guards:
        forbiddens = set(guards[idx]["forbiddens"])
        for d in week:
            if d not in forbiddens:
                quantity_per_weekday[d] += 1

    return quantity_per_weekday


def _day_of_the_week(idx: int) -> int:
    day = idx % 7
    day = 7 if day == 0 else day
    return day


def _days_sorted_by_difficulty(
    guards: dict[int, dict[str, set[int]]], days: int
) -> list[tuple[int, int, int]]:
    quantity_per_weekday = _init_guards_quantity_per_weekday(guards)
    available: list[tuple[int, int, int]] = []

    for idx in range(1, days + 1):
        day = _day_of_the_week(idx)
        free_guards = quantity_per_weekday[day]
        row = (idx, day, free_guards)
        available.append(row)

    available.sort(reverse=False, key=lambda x: x[2])
    return available


def _is_pref(guards: dict[int, dict[str, set[int]]], g, weekday: int) -> int:
    if weekday in guards[g]["prefs"]:
        return 1
    return 0


def _is_candidate_better(
    best_idx: int,
    idx_g: int,
    best_pref: int,
    cur_pref: int,
    best_shift_count: int,
    cur_shift_count: int,
) -> bool:
    # compare preferences
    if cur_pref > best_pref:
        return True
    if cur_pref < best_pref:
        return False

    # preferences equal → compare shift_count
    if cur_shift_count < best_shift_count:
        return True
    if cur_shift_count > best_shift_count:
        return False

    # shift_count equal → tie-break by index
    return idx_g < best_idx


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


def _get_zones(guards: dict[int, dict[str, set[int]]]) -> dict[int, set[int]]:
    def mirror(i: int, V: int) -> int:
        return V - i + 1

    V = len(guards)
    zones: dict[int, set[int]] = {}

    for i in guards:
        left = max(1, i - 5)
        right = min(V, i + 5) + 1
        solo_cov = set(range(left, right))
        solo_cov_mir = {mirror(i, V) for i in solo_cov}
        total_cov = solo_cov | solo_cov_mir
        zones[i] = total_cov

    return zones


def _is_schedule_valid(
    shifts: list[list[int]], guards: dict[int, dict[str, set[int]]]
) -> bool:
    V = len(guards)
    days = len(shifts)

    # validate schedule length
    if len(shifts) != days:
        return False

    # validate shifts' completeness
    for idx_d, s in enumerate(shifts):
        if len(s) != 3:
            return False
        if -1 in s:
            return False

        # validate guards' indexes
        for idx_g in s:
            if idx_g < 0 or idx_g >= V:
                return False

        # validate hard constraint 2 (different guard for every shift position)
        g_d_idx, g_n1_idx, g_n2_idx = s
        g_d = g_d_idx + 1
        g_n1 = g_n1_idx + 1
        g_n2 = g_n2_idx + 1
        if g_d == g_n1:
            return False
        if g_d == g_n2:
            return False
        if g_n1 == g_n2:
            return False

        # validate hard_constraint 1 (weekday is not forbidden for a guard)
        d = _day_of_the_week(idx_d + 1)
        for g in (g_d, g_n1, g_n2):
            forbiddens = guards[g]["forbiddens"]
            if d in forbiddens:
                return False
    return True


def _get_pref_score(
    shifts: list[list[int]], guards: dict[int, dict[str, set[int]]]
) -> float:
    days = len(shifts)
    score_raw = 0
    for idx_d, s in enumerate(shifts):
        for idx_g in s:
            g = idx_g + 1
            d = _day_of_the_week(idx_d + 1)
            prefs = guards[g]["prefs"]
            if d in prefs:
                score_raw += 1
    return score_raw / (days * 3)


def _get_coverage_score(
    shifts: list[list[int]], guards: dict[int, dict[str, set[int]]]
) -> float:
    V = len(guards)
    days = len(shifts)
    zones: dict[int, set[int]] = _get_zones(guards)
    score_raw = 0

    for s in shifts:
        total_cov = set()
        for idx_g in s:
            g = idx_g + 1
            solo_cov = zones[g]
            total_cov |= solo_cov
        score_raw += len(total_cov)

    return score_raw / (min(V, 66) * days)


def _get_total_shift_count(
    shifts: list[list[int]], guards: dict[int, dict[str, set[int]]]
) -> list[int]:
    V = len(guards)
    total_count = [0] * V
    for s in shifts:
        for idx_g in s:
            total_count[idx_g] += 1

    return total_count


def _get_fairness_penalty(
    shifts: list[list[int]], guards: dict[int, dict[str, set[int]]]
) -> int:
    total_count = _get_total_shift_count(shifts, guards)

    min_count = min(total_count)
    max_count = max(total_count)

    fairness_penalty = max(0, max_count - min_count - 1)

    return fairness_penalty


def _get_swap_list(days: int, rng: r.Random) -> tuple[int, int, int]:
    d1 = rng.randint(0, days - 1)
    d2 = rng.randint(0, days - 1)
    while d1 == d2:
        d2 = rng.randint(0, days - 1)

    slot = rng.randint(0, 2)

    return (d1, d2, slot)


def _swap(
    shifts: list[list[int]],
    rng: r.Random,
) -> list[list[int]]:
    days = len(shifts)
    d1, d2, slot = _get_swap_list(days, rng)

    shifts_new = deepcopy(shifts)
    shifts_new[d1][slot], shifts_new[d2][slot] = (
        shifts_new[d2][slot],
        shifts_new[d1][slot],
    )

    return shifts_new


def _is_new_schedule_better(
    guards: dict[int, dict[str, set[int]]],
    rng: r.Random,
    shifts_2: list[list[int]],
    pref_score_1: float,
    cov_score_1: float,
    penalty_1: int,
) -> tuple[bool, float, float, int]:
    valid = _is_schedule_valid(shifts_2, guards)

    if not valid:
        return False, pref_score_1, cov_score_1, penalty_1

    pref_score_2 = _get_pref_score(shifts_2, guards)
    cov_score_2 = _get_coverage_score(shifts_2, guards)
    penalty_2 = _get_fairness_penalty(shifts_2, guards)

    t_tuple = (True, pref_score_2, cov_score_2, penalty_2)
    f_tuple = (False, pref_score_2, cov_score_2, penalty_2)

    delta_pref = pref_score_2 - pref_score_1
    if delta_pref > EPS:
        return t_tuple
    if delta_pref < -EPS:
        return f_tuple

    delta_cov = cov_score_2 - cov_score_1
    if delta_cov > EPS:
        return t_tuple
    if delta_cov < -EPS:
        return f_tuple

    if penalty_2 < penalty_1:
        return t_tuple
    if penalty_2 > penalty_1:
        return f_tuple

    if rng.random() <= 0.5:
        return t_tuple

    return f_tuple
