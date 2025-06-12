import tkinter as tk
from tkinter import ttk, messagebox


# --- Scoreboard Data Model ---
class Scoreboard:
    def __init__(self):
        self.players = []
        self.results = {}  # player: [wins, losses, ties, games]

    def add_player(self, name):
        if name and name not in self.players:
            self.players.append(name)
            self.results[name] = [0, 0, 0, 0]

    def record_match(self, p1, p2, result):  # result: 'p1', 'p2', 'tie'
        if p1 not in self.players or p2 not in self.players:
            return
        # Update stats
        if result == 'p1':
            self.results[p1][0] += 1  # win
            self.results[p2][1] += 1  # loss
        elif result == 'p2':
            self.results[p2][0] += 1
            self.results[p1][1] += 1
        else:
            self.results[p1][2] += 1
            self.results[p2][2] += 1
        self.results[p1][3] += 1
        self.results[p2][3] += 1

    def leaderboard(self):
        board = []
        for p in self.players:
            w, l, t, g = self.results[p]
            wr = (w / g * 100) if g else 0
            board.append((p, w, l, t, g, wr))
        # Sort: by wins desc, ties desc, then name
        board.sort(key=lambda x: (-x[1], -x[3], x[0].lower()))
        return board


# --- Main App ---
class ScoreboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scoreboard Tracker — Playful Leaderboard")
        self.geometry("880x700")
        self['bg'] = '#f9fafb'
        self.scoreboard = Scoreboard()
        self._ttk_styles()
        self._layout_main()

    def _ttk_styles(self):
        style = ttk.Style()
        # Font - ALL TEXT SET TO BLACK FOR VISIBILITY
        style.configure("Headline.TLabel", font=("Poppins", 40, "bold"), background="#f9fafb", foreground="#000000")
        style.configure("Body.TLabel", font=("Poppins", 15), background="#f9fafb", foreground="#000000")
        style.configure("Card.TFrame", background="#fff", borderwidth=0, relief="flat")
        style.configure("TButton", font=("Poppins", 12, "bold"), background="#262626", foreground="#000000", borderwidth=0,
                        padding=8)  # Changed foreground to black
        style.map("TButton",
                  background=[('active', '#0d9488')],
                  foreground=[('active', '#000000')])  # Changed active foreground to black
        style.configure("MiniCard.TFrame", background="#f3f4f6", borderwidth=0, relief="flat")
        style.configure("Leaderboard.TLabel", font=("Poppins", 14, "bold"), background="#fff", foreground="#000000")
        # All table text set to black
        style.configure("TableWin.TLabel", foreground='#000000', background="#fff", font=("Poppins", 13, 'bold'))
        style.configure("TableLoss.TLabel", foreground='#000000', background="#fff", font=("Poppins", 13))
        style.configure("TableTie.TLabel", foreground='#000000', background="#fff", font=("Poppins", 13))
        style.configure("TableCell.TLabel", background="#fff", font=("Poppins", 13), foreground="#000000")

    def _layout_main(self):
        # -- Header section (sticky style) --
        header = ttk.Frame(self, style="Card.TFrame")
        header.place(relx=0.5, y=0, anchor="n", width=900)
        ttk.Label(header, text="Playful Scoreboard", style="Headline.TLabel").pack(pady=(34, 4))
        # Removed the following line to eliminate the extra text
        # ttk.Label(header, text="Track who beats who. Instantly. Clean look. Friendly feel ✨",
        #           style="Body.TLabel").pack()

        # -- Card container, centered --
        main_card = tk.Frame(self, bg="#fff", highlightthickness=0)
        main_card.place(relx=0.5, rely=0.48, anchor="center", width=720, height=530)
        main_card.config(borderwidth=0, highlightbackground="#e5e7eb")

        # -- Add Player UI --
        self.player_name = tk.StringVar()
        add_frame = tk.Frame(main_card, bg="#fff")
        add_frame.pack(pady=(22, 8), anchor="w")
        entry = ttk.Entry(add_frame, textvariable=self.player_name, font=("Poppins", 13), width=18)
        entry.pack(side="left", padx=(0, 4))
        entry.bind("<Return>", lambda e: self._add_player())
        apbtn = ttk.Button(add_frame, text="Add Player", style="TButton", command=self._add_player)
        apbtn.pack(side="left", padx=(10, 0))

        # -- Current Players as nice chips/badges --
        self.players_list_frame = tk.Frame(main_card, bg="#fff")
        self.players_list_frame.pack(anchor="w", pady=(0, 14))
        self._refresh_players_list()

        ttk.Separator(main_card, orient='horizontal').pack(fill="x", pady=4, padx=6)

        # -- Matchup Card: who vs who? --
        mcard = ttk.Frame(main_card, style="MiniCard.TFrame", padding=22)
        mcard.pack(fill="x", padx=8, pady=(2, 13))

        ttk.Label(mcard, text="Record a Match", style="Leaderboard.TLabel").grid(row=0, column=0, columnspan=6,
                                                                                 sticky="w")
        ttk.Label(mcard, text="Who played who?", background="#f3f4f6", font=("Poppins", 13), foreground="#000000").grid(row=1, column=0,
                                                                                                  padx=(2, 2), pady=4)
        self.match_p1 = tk.StringVar()
        self.match_p2 = tk.StringVar()
        self.p1_menu = ttk.Combobox(mcard, textvariable=self.match_p1, font=("Poppins", 13), state="readonly", width=12,
                                    postcommand=self._update_match_menus)
        self.p2_menu = ttk.Combobox(mcard, textvariable=self.match_p2, font=("Poppins", 13), state="readonly", width=12,
                                    postcommand=self._update_match_menus)
        self.p1_menu.grid(row=1, column=1, padx=(3, 10))
        ttk.Label(mcard, text="vs", background="#f3f4f6", font=("Poppins", 13, "bold"), foreground="#000000").grid(row=1, column=2)
        self.p2_menu.grid(row=1, column=3, padx=(10, 3))

        # Result buttons: P1 wins, P2 wins, or Tie
        self._winner_var = tk.StringVar(value="p1")
        rb1 = ttk.Radiobutton(mcard, text="🥇 P1 Wins", variable=self._winner_var, value="p1")
        rb2 = ttk.Radiobutton(mcard, text="🥇 P2 Wins", variable=self._winner_var, value="p2")
        rb3 = ttk.Radiobutton(mcard, text="🤝 Tie", variable=self._winner_var, value="tie")
        rb1.grid(row=2, column=1)
        rb2.grid(row=2, column=3)
        rb3.grid(row=2, column=4, padx=(18, 0))
        rbtn = ttk.Button(mcard, text="Record Result", style="TButton", command=self._record_match)
        rbtn.grid(row=2, column=5, padx=(22, 0), pady=4, sticky="e")

        # -- Leaderboard (modern table) --
        lb_card = ttk.Frame(main_card, style="MiniCard.TFrame", padding=24)
        lb_card.pack(pady=(14, 0), fill="both", expand=True)
        self.lb_container = lb_card
        self._refresh_leaderboard()

    def _add_player(self):
        name = self.player_name.get().strip()
        if not name:
            messagebox.showwarning("No name", "Enter a player name.")
            return
        if name in self.scoreboard.players:
            messagebox.showerror("Duplicate", "Player already exists!")
            return
        if len(name) > 18:
            messagebox.showerror("Too long", "Max 18 character names.")
            return
        self.scoreboard.add_player(name)
        self.player_name.set("")
        self._refresh_players_list()
        self._update_match_menus()
        self._refresh_leaderboard()

    def _refresh_players_list(self):
        for chip in self.players_list_frame.winfo_children():
            chip.destroy()
        players = self.scoreboard.players
        if not players:
            l = ttk.Label(self.players_list_frame, text="No players yet.", style="Body.TLabel")
            l.pack(side="left", padx=(2, 0))
            return
        for p in players:
            chip = tk.Label(self.players_list_frame, text=p,
                            font=("Poppins", 12, "bold"), bg="#e0e7ef", fg="#000000",  # Changed to black
                            padx=16, pady=6, bd=0, relief="ridge")
            chip.pack(side="left", padx=4, pady=3)

    def _update_match_menus(self):
        options = self.scoreboard.players[:]
        self.p1_menu['values'] = options
        self.p2_menu['values'] = options
        # Defaults: auto-select two different players if available
        if not getattr(self, 'match_p1', None): return
        if not self.match_p1.get() and options:
            self.match_p1.set(options[0])
        if (not self.match_p2.get() or self.match_p2.get() == self.match_p1.get()) and len(options) > 1:
            self.match_p2.set(next((o for o in options if o != self.match_p1.get()), options[0]))

    def _record_match(self):
        p1 = self.match_p1.get()
        p2 = self.match_p2.get()
        if not p1 or not p2 or p1 == p2:
            messagebox.showwarning("Invalid", "Pick two DIFFERENT players to record a match.")
            return
        result = self._winner_var.get()
        self.scoreboard.record_match(p1, p2, result)
        self._refresh_leaderboard()

    def _refresh_leaderboard(self):
        for w in self.lb_container.winfo_children():
            w.destroy()
        ttk.Label(self.lb_container, text="Leaderboard", style="Leaderboard.TLabel").grid(row=0, column=0,
                                                                                         columnspan=10, sticky="w",
                                                                                         pady=(2, 10))
        columns = ['#', 'Player', 'Wins', 'Losses', 'Ties', 'Games', 'Win %']
        style_cols = [
            "Leaderboard.TLabel", "Leaderboard.TLabel", "TableWin.TLabel", "TableLoss.TLabel", "TableTie.TLabel",
            "TableCell.TLabel", "TableCell.TLabel"
        ]
        for c, text in enumerate(columns):
            ttk.Label(self.lb_container, text=text, style=style_cols[c], anchor="center").grid(row=1, column=c,
                                                                                              sticky="nsew", padx=8,
                                                                                              pady=0)
        lb = self.scoreboard.leaderboard()
        for idx, (p, w, l, t, g, wr) in enumerate(lb, 1):
            tk.Label(self.lb_container, text=f"{idx}", font=("Poppins", 13, "bold"), bg="#fff", fg="#000000").grid(
                row=idx + 1, column=0)
            tk.Label(self.lb_container, text=p, font=("Poppins", 13, "bold"), bg="#fff", fg="#000000").grid(row=idx + 1,
                                                                                                           column=1)
            tk.Label(self.lb_container, text=w, font=("Poppins", 13, "bold"), bg="#fff", fg="#16a34a").grid(row=idx + 1,
                                                                                                           column=2)  # Green for wins
            tk.Label(self.lb_container, text=l, font=("Poppins", 13), bg="#fff", fg="#dc2626").grid(row=idx + 1,
                                                                                                   column=3)  # Red for losses
            tk.Label(self.lb_container, text=t, font=("Poppins", 13), bg="#fff", fg="#0ea5e9").grid(row=idx + 1,
                                                                                                   column=4)  # Blue for ties
            tk.Label(self.lb_container, text=g, font=("Poppins", 13), bg="#fff", fg="#000000").grid(row=idx + 1,
                                                                                                   column=5)
            tk.Label(self.lb_container, text=f"{wr:.1f}%", font=("Poppins", 13), bg="#fff", fg="#000000").grid(
                row=idx + 1, column=6)


if __name__ == "__main__":
    ScoreboardApp().mainloop()
