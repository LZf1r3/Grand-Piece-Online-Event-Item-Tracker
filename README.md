# GPO Cupid Dungeon Tracker

A small desktop app that keeps track of your loot while farming the Cupid Dungeon in Grand Piece Online. It sits on top of the game window, you click a button each time something drops, and it tells you how much of the set you still need.

Written in Python with Tkinter.

## Why I made it

The event has 35 items and the rarest ones drop about 0.3% of the time, which works out to roughly 333 runs each on average. Keeping count in your head doesn't work over a session that long, and alt-tabbing to a notes file every few minutes is worse.

This stays pinned over the game, takes one click per drop, and saves after every single click so nothing is lost if it closes.

## What it does

- Counts your total runs
- Counts how many of each of the 35 items you've got
- Shows the drop rate next to every item
- Tells you what percentage of the set you've completed
- Names the three rarest items you're still missing and roughly how many runs each should take
- Keeps a separate list of fruits from MVP rewards
- Stays on top of other windows so you don't have to alt-tab
- Saves everything automatically

## How to use it

Run the program and a window opens. The controls are:

| Button | What it does |
| --- | --- |
| `+1 Run` | Adds one to your run counter |
| `−` next to it | Takes one off, in case you miscount |
| `+ Fruit` | Asks you to type a fruit name and adds it to the fruit list |
| `fruits` | Shows the full list of fruits you've logged |
| `on top` | Turns the always-on-top setting on or off |
| `reset` | Clears everything, after asking you to confirm |

Each item has its own row with a `+` and `−` button and a count. Items you've received turn gold, and ones you still need stay white, so you can see what's left at a glance.

At the bottom there's a summary that updates as you go:

```
12 / 35 items                                    34%
Rarest missing: Cupid's All-Seeing Eye (~333 runs),
Prestige Cupid's Chakrum (~333 runs), Mythic Chest (~333 runs)
Fruits logged: 4
```

## The item list

The 35 items are split into five groups, shown in this order:

| Group | Items | Drop rates |
| --- | --- | --- |
| Common | 10 | 5% to 15% |
| Guards | 4 | 1% to 25% |
| Leo | 4 | 3% to 5% |
| Cupid Queen | 12 | 0.3% to 5% |
| Blessed Queen | 5 | 0.3% |

The drop rates are community estimates, not official numbers from the developers. They're used for the display and for the "runs remaining" estimate, so if better numbers come out you can just edit them.

To change a rate or add an item, edit the `ITEMS` list near the top of the file:

```python
ITEMS = [
    ("Cupid's Mask", 0.15, "Common"),
    #  name          rate   group
]
```

If you add a new group, add its name to the `GROUPS` list too, in the order you want it displayed.

## How the "runs remaining" estimate works

For each item you're missing, the program calculates `1 / drop_rate`. An item with a 0.3% rate gives `1 / 0.003`, or about 333 runs. It sorts the missing items by that number and shows the three highest.

This is an average, not a guarantee. Every run is independent, so going 400 runs without a 0.3% drop is unlucky but completely normal — it happens about 30% of the time.

## How saving works

Everything is written to a file called `cupid_save.json`, stored in the same folder as the program:

```json
{
  "runs": 147,
  "counts": { "Cupid's Mask": 22, "Wings of Leo": 6 },
  "fruits": ["Light", "Magma"],
  "on_top": true
}
```

It saves every time you click anything, and again when you close the window. If the file is missing or damaged the program just starts fresh instead of crashing.

To back up your progress or move it to another computer, copy that one file.

## Running it

```bash
python tracker.py
```

You need Python 3 with Tkinter. On Windows and Mac, Tkinter comes with the normal Python installer. On Ubuntu or Debian you may need to install it:

```bash
sudo apt install python3-tk
```

Nothing else to install — the program only uses `json`, `os` and `tkinter`, which all come with Python.

## How the code is organised

Everything is in one file.

- `ITEMS` — the 35 items with their drop rates and groups
- `GROUPS` — the order the groups are displayed in
- `SAVE_FILE` — where the save file goes
- The colour constants at the top (`BG`, `CARD`, `PINK`, `GOLD`) control the theme
- `Tracker` — the whole app, as one class:
  - `build_top()`, `build_list()`, `build_bottom()` — build the three parts of the window
  - `make_row()` — builds one item row
  - `add_run()` and `add_item()` — handle the `+` and `−` buttons
  - `refresh_row()` — turns an item gold once you have one
  - `update_totals()` — recalculates the completion percentage and the rarest-missing text
  - `load()` and `save()` — read and write the JSON file

The item list scrolls, which is why there's a canvas inside `build_list()` rather than just a plain frame — Tkinter frames don't scroll on their own.

## Notes

This was built for the 2026 Cupid Dungeon. Drop tables change between events, so the item list would need updating for a future one.

It's an unofficial fan tool, not connected to Grand Piece Online or Roblox in any way.
