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
