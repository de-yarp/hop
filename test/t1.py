from pathlib import Path

from utils.data_utils import parse_input

p = Path("data") / "input" / "input.txt"
g = parse_input(p)
print(g)
