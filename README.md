# HOP – Assignment 2, Úloha 1 (rozpis služieb)

---

## 1. Cieľ projektu

Repozitár obsahuje riešenie úlohy č. 1 z predmetu **Heuristické optimalizačné procesy (HOP)** na FEI TUKE.

Cieľom je pre daný vstup:

- naplánovať služby pre **112 dní**,
- každý deň:
  - 1 × denná služba,
  - 2 × nočná služba,
- splniť dané **hard constraints** (zákazy, max. 1 služba za deň),
- a zlepšiť rozpis podľa týchto **kritérií** (lexikograficky):

1. platnosť rozpisu (žiadne porušenie hard constraints),
2. maximalizácia preferovaných dní (preferencie členov),
3. maximalizácia pokrytia „záhradiek“ (coverage).

---

## 2. Požiadavky

- **Python** 3.12+
- nástroj **`uv`** (na správu prostredia a závislostí)

---

## 3. Inštalácia `uv`

macOS aj Windows:

```bash
pip install uv
```

Overenie inštalácie:

```bash
uv --version
```

Nie je potrebné zakladať `venv` ani ručne inštalovať balíky – všetko rieši `uv` cez `pyproject.toml`.

---

## 4. Štruktúra projektu

```text
.
├── data
│   ├── input
│   │   └── input.txt        # vstupný súbor podľa zadania
│   └── results
│       └── output.txt       # vygenerovaný rozpis služieb (výstup)
│
├── docs
│   └── REPORT.md            # technická dokumentácia
│
├── main.py                  # vstupný bod programu
├── pyproject.toml           # závislosti a konfigurácia pre uv
├── README.md
├── uv.lock
│
├── runners
│   └── run.py               # pomocný skript na spúšťanie / testovanie
│
└── utils
    ├── algo_utils.py        # heuristiky, konštrukcia a optimalizácia rozpisu
    ├── data_utils.py        # parsovanie vstupu, zápis výstupu
    ├── helpers.py           # pomocné funkcie (dni v týždni, validácie, atď.)
    └── print_utils.py       # formátovaný výpis metrik a výsledkov
```

---

## 5. Spustenie projektu

V koreňovom priečinku repozitára (tam, kde je `main.py` a `pyproject.toml`):

```bash
uv run main.py
```

Nástroj `uv` automaticky:

- vytvorí izolované prostredie,
- nainštaluje závislosti z `pyproject.toml`,
- spustí skript `main.py`.

### Vstup a výstup

- Vstup sa očakáva v súbore:

  ```text
  data/input/input.txt
  ```

  v tvare definovanom v zadaní (členovia, ich preferencie a zakázané dni).

- Po úspešnom behu programu sa výsledný rozpis uloží do:

  ```text
  data/results/output.txt
  ```

  Každý riadok reprezentuje jeden deň (1–112) a obsahuje **3 celé čísla** (indexy členov, 1-based):

  ```text
  <guard_day> <guard_night_1> <guard_night_2>
  ```

---

## 6. Stručný popis algoritmu

Riešenie prebieha v niekoľkých krokoch:

1. **Parsovanie vstupu**
   - Vstup sa načíta do štruktúry:
     - `guards[id]["prefs"]` – preferované dni v týždni,
     - `guards[id]["forbiddens"]` – zakázané dni v týždni.
   - Pre každý kalendárny deň (1–112) sa určí deň v týždni a množina dostupných členov.

2. **Konštrukcia počiatočného rozpisu (`init_solution`)**
   - Dni sa zoradia podľa „náročnosti“ (menej dostupných členov → skôr).
   - Pre každý deň sa greedy priraďuje:
     - 1 × denná služba,
     - 2 × nočné služby,
   - s ohľadom na:
     - zakázané dni (hard constraint),
     - maximálne 1 službu na člena a deň (hard constraint),
     - kvóty na počet denných a nočných služieb:
       - denné služby: každý člen má napr. **1 alebo 2**,
       - nočné služby: cieľ napr. **3 alebo 4** na člena.

3. **Lokálna optimalizácia rozpisu**
   - Používa sa jednoduchá 2-opt heuristika „swap v rovnakom slote“:
     - náhodne sa vyberú dva rozdielne dni a jeden slot (day / night1 / night2),
     - v danom slote sa členovia medzi dňami vymenia,
     - nový rozpis sa porovná s pôvodným podľa:
       1. **Platnosť** (hard constraints),
       2. **PrefScore** (podiel služieb v preferovaných dňoch),
       3. **CoverageScore** (pokrytie „záhradiek“),
       4. **Fairness penalty** (rozptyl v celkovom počte služieb).
   - Zmena sa akceptuje len vtedy, ak zlepší vyššie kritériá, pri rovnosti je zavedený malý náhodný tie-break.

4. **Fairness repair pre nočné služby**
   - Po lokálnej optimalizácii sa vykoná krátka opravná fáza:
     - identifikujú sa členovia s príliš malým počtom nočných služieb (napr. 2),
     - a s príliš vysokým počtom nočných služieb (napr. 4),
     - kde je to možné, jedna nočná služba sa presunie z „preťaženého“ člena na „podťaženého“,
     - bez porušenia zakázaných dní a pravidla „max. 1 služba za deň“.

Výsledkom je platný rozpis s dobrým pomerom medzi preferenciami, pokrytím a spravodlivou záťažou.

---

## 7. Metriky a výstupné štatistiky

Pri behu programu sa na konzolu vypíše blok so zhrnutím výsledkov, napríklad:

```text
---------- RESULTS ----------

 • PrefScore: 0.9911 → 0.9970 (+0.601%)
 • CoverageScore: 0.6150 → 0.8942 (+45.403%)
 • Fairness penalty: 2 → 1 (Δ = -1), S_min = 4, S_max = 6
      → 1 dayshifts: 34 guards
      → 2 dayshifts: 39 guards
      → 3 nightshifts: 68 guards
      → 4 nightshifts: 5 guards
   • Time taken: 2.95 s
```

Tu:

- **PrefScore** – podiel všetkých priradení (deň + noc), ktoré spadajú do preferovaných dní členov,
- **CoverageScore** – priemerné pokrytie modelovaných zón na „ulici“,
- **Fairness penalty** – penalizácia za rozdiel v celkovom počte služieb medzi najmenej a najviac zaťaženým členom:
  - `S_min`, `S_max` – minimum a maximum celkových služieb,
  - penalty > 0 znamená, že rozdiel je väčší než 1.

---

## 8. Konfigurovateľné parametre

Základné parametre (počet iterácií lokálnej optimalizácie, seed generátora náhodných čísel a pod.) sú nastavené priamo v `main.py`.

V prípade potreby je možné:

- **zvýšiť `max_iter`** – získať lepšie riešenia za cenu dlhšieho času výpočtu,
- **zmeniť seed RNG** – vygenerovať inú, ale stále deterministickú realizáciu rozpisu.

---
