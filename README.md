# HPMon

Derive accurate HP values of monsters from damage taken and their HP%.

## Current limitations

Currently does **not** work properly if:

* The mob has a regen or uses a regen move.
* The mob has a DoT on it.
* The fight does not start at 100% mob HP.

## Visualizing data

1. Install Python 3.

2. Install matplotlib:

```
pip install matplotlib
```

3. Run plot from the root of the repository:

```
python tools/plot.py
```
