import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

# progress gets saved next to this file
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cupid_save.json")

BG = "#1c1023"
CARD = "#2b1830"
PINK = "#ff5d8f"
GOLD = "#ffd166"
TEXT = "#f5e9ee"
GREY = "#a98ba0"

# (item name, drop rate, group) - rates are community estimates, not official
ITEMS = [
    ("Cupid's Mask", 0.15, "Common"),
    ("Worshipper Cape", 0.05, "Common"),
    ("Wings of Roses", 0.05, "Common"),
    ("Cupid Scarf", 0.05, "Common"),
    ("Love Witch's Hat", 0.05, "Common"),
    ("Love Boppers Headband", 0.05, "Common"),
    ("Love Shades", 0.05, "Common"),
    ("Cupid Heart", 0.05, "Common"),
    ("Dark Root", 0.05, "Common"),
    ("SP Reset", 0.08, "Common"),

    ("Virtuous Cupid Vanguard Outfit", 0.25, "Guards"),
    ("Virtuous Cupid Helmet", 0.15, "Guards"),
    ("Blessed Vanguard Outfit", 0.02, "Guards"),
    ("Cupid Queen Maid Outfit", 0.01, "Guards"),

    ("Wings of Leo", 0.05, "Leo"),
    ("Leo's Outfit", 0.05, "Leo"),
    ("Leo's Blazing Scarf", 0.05, "Leo"),
    ("Leo's Inferno Hagoromo", 0.03, "Leo"),

    ("Cupid's Headband", 0.05, "Cupid Queen"),
    ("Cupid Boat", 0.05, "Cupid Queen"),
    ("Cupid's Chakrum", 0.02, "Cupid Queen"),
    ("Cupid Queen's Wings", 0.01, "Cupid Queen"),
    ("Cupid Wand", 0.01, "Cupid Queen"),
    ("Cupid's Battleaxe", 0.01, "Cupid Queen"),
    ("Cupid's Bow", 0.01, "Cupid Queen"),
    ("Exalted Cupid Queen's Wings", 0.01, "Cupid Queen"),
    ("Cupid Queen's Outfit", 0.005, "Cupid Queen"),
    ("Cupid Queen's Scarf", 0.005, "Cupid Queen"),
    ("Cupid's All-Seeing Eye", 0.003, "Cupid Queen"),
    ("Prestige Cupid's Chakrum", 0.003, "Cupid Queen"),

    ("Mythic Chest", 0.003, "Blessed Queen"),
    ("Blessed Exalted Cupid Queen's Wings", 0.003, "Blessed Queen"),
    ("Blessed Cupid's Bow", 0.003, "Blessed Queen"),
    ("Blessed Exalted Cupid Queen Outfit", 0.003, "Blessed Queen"),
    ("Blessed Cupid Queen's Scarf", 0.003, "Blessed Queen"),
]

GROUPS = ["Common", "Guards", "Leo", "Cupid Queen", "Blessed Queen"]


def pct(rate):
    return ("%.3f" % (rate * 100)).rstrip("0").rstrip(".") + "%"


def button(parent, text, command, bg=PINK, fg="#2a0f1a"):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     activebackground=bg, activeforeground=fg, relief="flat",
                     bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"),
                     padx=10, pady=3)


class Tracker:
    def __init__(self, root):
        self.root = root
        self.runs = 0
        self.counts = {}   # item name -> how many I got
        self.fruits = []   # fruit names from MVP rewards
        self.labels = {}   # item name -> count label, so I can update it later
        self.on_top = tk.BooleanVar(value=True)

        self.load()

        root.title("GPO Cupid Dungeon Tracker")
        root.configure(bg=BG)
        root.geometry("430x680")
        root.minsize(380, 460)
        root.attributes("-topmost", self.on_top.get())
        root.protocol("WM_DELETE_WINDOW", self.close)

        self.build_top()
        self.build_list()
        self.build_bottom()
        self.update_totals()

    # ---------- layout ----------
    def build_top(self):
        bar = tk.Frame(self.root, bg=CARD)
        bar.pack(fill="x", padx=12, pady=12)

        left = tk.Frame(bar, bg=CARD)
        left.pack(side="left", padx=10, pady=8)
        tk.Label(left, text="TOTAL RUNS", bg=CARD, fg=GREY,
                 font=("Segoe UI", 8)).pack(anchor="w")
        self.runs_label = tk.Label(left, text=str(self.runs), bg=CARD, fg=PINK,
                                   font=("Segoe UI", 22, "bold"))
        self.runs_label.pack(anchor="w")

        right = tk.Frame(bar, bg=CARD)
        right.pack(side="right", padx=10, pady=8)
        row = tk.Frame(right, bg=CARD)
        row.pack(anchor="e")
        button(row, "-", lambda: self.add_run(-1), bg="#38203f", fg=TEXT).pack(side="left", padx=3)
        button(row, "+1 Run", lambda: self.add_run(1)).pack(side="left", padx=3)
        button(row, "+ Fruit", self.log_fruit, bg=GOLD).pack(side="left", padx=3)

        row2 = tk.Frame(right, bg=CARD)
        row2.pack(anchor="e", pady=(6, 0))
        tk.Checkbutton(row2, text="on top", variable=self.on_top, command=self.toggle_top,
                       bg=CARD, fg=GREY, selectcolor="#38203f", activebackground=CARD,
                       activeforeground=TEXT, font=("Segoe UI", 8), bd=0,
                       highlightthickness=0).pack(side="left")
        button(row2, "fruits", self.show_fruits, bg="#38203f", fg=TEXT).pack(side="left", padx=4)
        button(row2, "reset", self.reset, bg="#38203f", fg=TEXT).pack(side="left")

    def build_list(self):
        # canvas + inner frame so the item list can scroll
        holder = tk.Frame(self.root, bg=BG)
        holder.pack(fill="both", expand=True, padx=12)

        self.canvas = tk.Canvas(holder, bg=BG, highlightthickness=0)
        bar = tk.Scrollbar(holder, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=BG)

        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.window, width=e.width))
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self.scroll)
        self.canvas.bind_all("<Button-4>", self.scroll)
        self.canvas.bind_all("<Button-5>", self.scroll)

        for group in GROUPS:
            tk.Label(self.inner, text=group.upper(), bg=BG, fg=PINK,
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(10, 2))
            for name, rate, g in ITEMS:
                if g == group:
                    self.make_row(name, rate)

    def make_row(self, name, rate):
        row = tk.Frame(self.inner, bg=CARD)
        row.pack(fill="x", pady=2)

        title = tk.Label(row, text=name, bg=CARD, fg=TEXT, anchor="w",
                         font=("Segoe UI", 10, "bold"))
        title.pack(side="left", padx=10, pady=6)
        tk.Label(row, text=pct(rate), bg=CARD, fg=GREY,
                 font=("Segoe UI", 8)).pack(side="left")

        button(row, "+", lambda: self.add_item(name, 1)).pack(side="right", padx=(0, 8))
        button(row, "-", lambda: self.add_item(name, -1), bg="#38203f", fg=TEXT).pack(side="right", padx=4)
        count = tk.Label(row, text="0", bg=CARD, fg=TEXT, width=3,
                         font=("Consolas", 11, "bold"))
        count.pack(side="right")

        self.labels[name] = (count, title)
        self.refresh_row(name)

    def build_bottom(self):
        box = tk.Frame(self.root, bg=CARD)
        box.pack(fill="x", padx=12, pady=12)

        top = tk.Frame(box, bg=CARD)
        top.pack(fill="x", padx=12, pady=(10, 4))
        self.done_label = tk.Label(top, text="", bg=CARD, fg=TEXT,
                                   font=("Segoe UI", 10, "bold"))
        self.done_label.pack(side="left")
        self.pct_label = tk.Label(top, text="", bg=CARD, fg=GOLD,
                                  font=("Segoe UI", 10, "bold"))
        self.pct_label.pack(side="right")

        self.estimate_label = tk.Label(box, text="", bg=CARD, fg=GREY, justify="left",
                                       anchor="w", wraplength=370, font=("Segoe UI", 9))
        self.estimate_label.pack(fill="x", padx=12, pady=(0, 10))

    # ---------- actions ----------
    def scroll(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(-event.delta // 120, "units")

    def add_run(self, n):
        self.runs = max(0, self.runs + n)
        self.runs_label.configure(text=str(self.runs))
        self.save()

    def add_item(self, name, n):
        self.counts[name] = max(0, self.counts.get(name, 0) + n)
        self.refresh_row(name)
        self.update_totals()
        self.save()

    def refresh_row(self, name):
        count, title = self.labels[name]
        got = self.counts.get(name, 0)
        color = GOLD if got > 0 else TEXT
        count.configure(text=str(got), fg=color)
        title.configure(fg=color)

    def log_fruit(self):
        name = simpledialog.askstring("Log fruit", "Which fruit did you get?", parent=self.root)
        if name and name.strip():
            self.fruits.append(name.strip())
            self.update_totals()
            self.save()

    def show_fruits(self):
        if not self.fruits:
            messagebox.showinfo("Fruits", "No fruits logged yet.", parent=self.root)
            return
        text = "\n".join("%d. %s" % (i + 1, f) for i, f in enumerate(self.fruits))
        messagebox.showinfo("Fruits (%d)" % len(self.fruits), text, parent=self.root)

    def toggle_top(self):
        self.root.attributes("-topmost", self.on_top.get())
        self.save()

    def reset(self):
        if messagebox.askyesno("Reset", "Clear runs, items and the fruit log?", parent=self.root):
            self.runs = 0
            self.counts = {}
            self.fruits = []
            self.runs_label.configure(text="0")
            for name in self.labels:
                self.refresh_row(name)
            self.update_totals()
            self.save()

    def update_totals(self):
        done = [name for name, rate, g in ITEMS if self.counts.get(name, 0) > 0]
        self.done_label.configure(text="%d / %d items" % (len(done), len(ITEMS)))
        self.pct_label.configure(text="%d%%" % (100 * len(done) / len(ITEMS)))

        missing = [(1 / rate, name) for name, rate, g in ITEMS if self.counts.get(name, 0) == 0]
        if not missing:
            text = "Full set done. %d fruits logged." % len(self.fruits)
        else:
            missing.sort(reverse=True)
            worst = ", ".join("%s (~%.0f runs)" % (n, r) for r, n in missing[:3])
            text = "Rarest missing: %s\nFruits logged: %d" % (worst, len(self.fruits))
        self.estimate_label.configure(text=text)

    # ---------- saving ----------
    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        self.runs = data.get("runs", 0)
        self.counts = data.get("counts", {})
        self.fruits = data.get("fruits", [])
        self.on_top.set(data.get("on_top", True))

    def save(self):
        data = {"runs": self.runs, "counts": self.counts,
                "fruits": self.fruits, "on_top": self.on_top.get()}
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def close(self):
        self.save()
        self.root.destroy()


root = tk.Tk()
Tracker(root)
root.mainloop()