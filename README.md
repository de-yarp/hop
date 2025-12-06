# README — Jednoduché spustenie projektu (macOS + Windows)

---

## 1. Požiadavky
- Python **3.12+**
- `uv` (inštalácia cez `pip`)

---

## 2. Inštalácia `uv`
macOS aj Windows:

```bash
pip install uv
```

Overenie:
```bash
uv --version
```

---

## 3. Spustenie projektu
V koreňovom priečinku (tam, kde je `main.py` a `pyproject.toml`):

```bash
uv run main.py
```

`uv` automaticky:
- vytvorí izolované prostredie,
- nainštaluje závislosti z `pyproject.toml`,
- spustí skript.

Nie je potrebné vytvárať `venv` ani manuálne inštalovať balíky.

---

## 4. Štruktúra projektu
```
.
├── data
│   ├── input
│   │   └── input.txt
│   └── results
│       └── output.txt
│
├── docs
│   └── REPORT.md (...to be finished)
│
├── main.py
├── pyproject.toml
├── README.md
├── uv.lock
│
├── runners
│   └── run.py
│
└── utils
    ├── algo_utils.py
    ├── data_utils.py
    ├── helpers.py
    └── print_utils.py
```

---
