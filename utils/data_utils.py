from pathlib import Path


def parse_input(fin: Path) -> dict[int, dict[str, set[int]]]:
    guards: dict[int, dict[str, set[int]]] = {}
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
            guards[idx] = {"prefs": set(prefs), "forbiddens": set(forbiddens)}
            idx += 1
    return guards


def save_output(fout: Path, shifts: list[list[int]]) -> None:
    with open(file=fout, encoding="utf-8", mode="w") as f:
        for s in shifts:
            line = " ".join([str(x + 1) for x in s]) + "\n"
            f.write(line)
