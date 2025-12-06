from utils.helpers import _get_total_shift_count


def _fairness_penalty_and_min_max(
    shifts: list[list[int]], guards: dict[int, dict[str, set[int]]]
) -> tuple[int, int, int]:
    total_count = _get_total_shift_count(shifts, guards)

    min_count = min(total_count)
    max_count = max(total_count)

    fairness_penalty = max(0, max_count - min_count - 1)

    return fairness_penalty, min_count, max_count


def print_result(
    guards: dict[int, dict[str, set[int]]],
    shifts_1: list[list[int]],
    shifts_2: list[list[int]],
    t_d: float,
    pref1: float,
    pref2: float,
    cov1: float,
    cov2: float,
    pen1: int,
    pen2: int,
) -> None:
    pref_perc = round((pref2 - pref1) / (pref1 / 100), 3)
    cov_perc = round((cov2 - cov1) / (cov1 / 100), 3)
    pen_delta = pen2 - pen1
    _, min_count_1, max_count_1 = _fairness_penalty_and_min_max(shifts_1, guards)
    _, min_count_2, max_count_2 = _fairness_penalty_and_min_max(shifts_2, guards)

    # inital schedule
    print(f"initial schedule:\n\n{shifts_1}\n")
    print(f"preference score: {pref1}")
    print(f"coverage score: {cov1}")
    print(f"fairness penalty: {pen1}")

    print("\n\n\n")

    # optimized schedule
    print(f"optimized schedule:\n\n{shifts_2}\n")
    print(f"preference score: {pref2}")
    print(f"coverage score: {cov2}")
    print(f"fairness penalty: {pen2}")

    print("\n\n\n")

    # results
    print("\n---------- RESULTS ----------\n")
    print(f"Preference score improved {pref_perc}%")
    print(f"Coverage score improved {cov_perc}%")
    print("\nFairness penalty (max total-shift gap above 1):")
    print(
        f"initial: S_min = {min_count_1}, S_max = {max_count_1}, penalty = {max_count_1 - min_count_1}"
    )
    print(
        f"final: S_min = {min_count_2}, S_max = {max_count_2}, penalty = {max_count_2 - min_count_2}"
    )
    print(f"Δ penalty = {pen_delta}")
    print(f"\nTime taken: {t_d:.4f} s")
