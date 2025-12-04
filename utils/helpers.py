def get_quota(guards: dict[int, dict[str, set[int]]], days: int) -> dict[str, int]:
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


def init_guards_quantity_per_weekday(
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


def days_sorted_by_difficulty(
    guards: dict[int, dict[str, set[int]]], days: int
) -> list[tuple[int, int, int]]:
    quantity_per_weekday = init_guards_quantity_per_weekday(guards)
    available: list[tuple[int, int, int]] = []

    for idx in range(1, days + 1):
        day = day_of_the_week(idx)
        free_guards = quantity_per_weekday[day]
        row = (idx, day, free_guards)
        available.append(row)

    available.sort(reverse=False, key=lambda x: x[2])
    return available


def day_of_the_week(idx: int) -> int:
    day = idx % 7
    day = 7 if day == 0 else day
    return day


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
        d = day_of_the_week(idx_d + 1)
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
            d = day_of_the_week(idx_d + 1)
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
