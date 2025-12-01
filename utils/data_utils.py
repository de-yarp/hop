from pathlib import Path


def parse_input(fin: Path) -> dict[int, dict[str, list[int]]]:
    guards: dict[int, dict[str, list[int]]] = {}
    with fin.open(mode="r", encoding="utf-8") as f:
        idx = 1

        for line in f:
            prefs = []
            forbiddens = []
            line = line.strip()
            tokens = line.split(" ")

            for t in tokens:
                if t.startswith("E"):
                    forbiddens.append(int(t[1:]))
                    continue
                prefs.append(int(t))
            guards[idx] = {"prefs": prefs, "forbiddens": forbiddens}
            idx += 1
    return guards
