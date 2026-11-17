import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# Matplotlib is optional. The app still works without it.
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

APP_NAME = "EXPENZ"
DB_FILE = "expenz.db"
BG = "#101512"
PANEL = "#19231d"
PANEL2 = "#202d25"
GREEN = "#35c879"
GREEN_DARK = "#1e8f55"
TEXT = "#f1f5f2"
MUTED = "#a1b0a6"
RED = "#f07171"
BORDER = "#2b3a30"


class ExpenzApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EXPENZ | Personal Finance Manager")
        self.root.geometry("1120x720")
        self.root.minsize(950, 620)
        self.root.configure(bg=BG)

        self.conn = sqlite3.connect(DB_FILE)
        self.create_table()
        self.configure_styles()
        self.build_layout()
        self.show_page("Dashboard")
        self.refresh_all()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                txn_date TEXT NOT NULL,
                note TEXT
            )
        """)
        self.conn.commit()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, foreground=TEXT,
                        fieldbackground=PANEL, rowheight=32, borderwidth=0)
        style.configure("Treeview.Heading", background=PANEL2,
                        foreground=GREEN, font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", GREEN_DARK)],
                  foreground=[("selected", "white")])

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg="#0b100d", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="◆  EXPENZ", bg="#0b100d", fg=GREEN,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=22, pady=(28, 4))
        tk.Label(self.sidebar, text="PERSONAL FINANCE", bg="#0b100d", fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25, pady=(0, 35))

        self.nav_buttons = {}
        for name in ["Dashboard", "Add Transaction", "Transactions", "Reports"]:
            btn = tk.Button(self.sidebar, text="   " + name, anchor="w",
                            command=lambda n=name: self.show_page(n),
                            bg="#0b100d", fg=TEXT, activebackground=PANEL2,
                            activeforeground=GREEN, bd=0, relief="flat",
                            font=("Segoe UI", 10, "bold"), padx=12, pady=14,
                            cursor="hand2")
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[name] = btn

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=18, pady=22)
        tk.Label(self.sidebar, text="Track better.\nSpend smarter.", bg="#0b100d",
                 fg=MUTED, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=25)

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        self.header = tk.Frame(self.main, bg=BG)
        self.header.pack(fill="x", padx=30, pady=(24, 8))
        self.page_title = tk.Label(self.header, text="", bg=BG, fg=TEXT,
                                   font=("Segoe UI", 22, "bold"))
        self.page_title.pack(side="left")
        tk.Label(self.header, text="PERSONAL FINANCE MANAGER", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="right", pady=10)

        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=16)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, page):
        self.current_page = page
        self.page_title.config(text=page)
        for name, btn in self.nav_buttons.items():
            btn.config(bg=PANEL2 if name == page else "#0b100d",
                       fg=GREEN if name == page else TEXT)
        self.clear_content()
        if page == "Dashboard":
            self.build_dashboard()
        elif page == "Add Transaction":
            self.build_add_page()
        elif page == "Transactions":
            self.build_transactions_page()
        elif page == "Reports":
            self.build_reports_page()

    def card(self, parent, title, value, accent=GREEN):
        frame = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER,
                         highlightthickness=1, padx=18, pady=16)
        tk.Label(frame, text=title.upper(), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(frame, text=value, bg=PANEL, fg=accent,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(9, 0))
        return frame

    def totals(self):
        rows = self.conn.execute(
            "SELECT kind, COALESCE(SUM(amount),0) FROM transactions GROUP BY kind"
        ).fetchall()
        income = sum(v for k, v in rows if k == "Income")
        expense = sum(v for k, v in rows if k == "Expense")
        return income, expense, income - expense

    def build_dashboard(self):
        income, expense, balance = self.totals()
        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x", pady=(0, 20))
        for title, value, color in [
            ("Total Balance", f"₹ {balance:,.2f}", GREEN),
            ("Total Income", f"₹ {income:,.2f}", GREEN),
            ("Total Expenses", f"₹ {expense:,.2f}", RED),
        ]:
            c = self.card(cards, title, value, color)
            c.pack(side="left", fill="x", expand=True, padx=(0, 12))

        section = tk.Frame(self.content, bg=PANEL, padx=18, pady=16,
                           highlightbackground=BORDER, highlightthickness=1)
        section.pack(fill="both", expand=True)
        top = tk.Frame(section, bg=PANEL)
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="Recent transactions", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Button(top, text="+ Add transaction", command=lambda: self.show_page("Add Transaction"),
                  bg=GREEN_DARK, fg="white", activebackground=GREEN,
                  bd=0, padx=14, pady=8, cursor="hand2").pack(side="right")
        self.make_tree(section, height=9)
        self.load_tree(limit=8)

    def build_add_page(self):
        box = tk.Frame(self.content, bg=PANEL, padx=26, pady=24,
                       highlightbackground=BORDER, highlightthickness=1)
        box.pack(anchor="nw", fill="x")
        tk.Label(box, text="Record a new transaction", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).grid(row=0, column=0, columnspan=2,
                                                    sticky="w", pady=(0, 20))

        self.kind_var = tk.StringVar(value="Expense")
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Food")
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.note_var = tk.StringVar()

        fields = [
            ("Transaction type", self.kind_var, ["Expense", "Income"]),
            ("Category", self.category_var, ["Food", "Travel", "Shopping", "Bills",
                                             "Education", "Health", "Salary", "Other"]),
        ]
        for r, (label, var, values) in enumerate(fields, start=1):
            tk.Label(box, text=label, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 10)).grid(row=r, column=0, sticky="w", pady=8)
            menu = ttk.Combobox(box, textvariable=var, values=values,
                                state="readonly", width=35)
            menu.grid(row=r, column=1, sticky="w", pady=8, ipady=5)

        entries = [
            ("Amount (₹)", self.amount_var),
            ("Date (YYYY-MM-DD)", self.date_var),
            ("Description", self.note_var),
        ]
        for r, (label, var) in enumerate(entries, start=3):
            tk.Label(box, text=label, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 10)).grid(row=r, column=0, sticky="w", pady=8)
            ent = tk.Entry(box, textvariable=var, bg=PANEL2, fg=TEXT,
                           insertbackground=TEXT, relief="flat", width=38,
                           font=("Segoe UI", 10))
            ent.grid(row=r, column=1, sticky="w", pady=8, ipady=8, padx=(0, 10))

        tk.Button(box, text="SAVE TRANSACTION", command=self.save_transaction,
                  bg=GREEN, fg="#07110b", activebackground="#63e39c",
                  font=("Segoe UI", 10, "bold"), bd=0, padx=22, pady=12,
                  cursor="hand2").grid(row=6, column=1, sticky="w", pady=(22, 0))

    def save_transaction(self):
        kind = self.kind_var.get()
        category = self.category_var.get()
        amount_text = self.amount_var.get().strip()
        txn_date = self.date_var.get().strip()
        note = self.note_var.get().strip()
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
            date.fromisoformat(txn_date)
        except ValueError:
            messagebox.showerror("Invalid details",
                                 "Enter an amount greater than zero and a valid date (YYYY-MM-DD).")
            return
        self.conn.execute(
            "INSERT INTO transactions(kind, amount, category, txn_date, note) VALUES(?,?,?,?,?)",
            (kind, amount, category, txn_date, note)
        )
        self.conn.commit()
        messagebox.showinfo("Saved", "Transaction saved successfully.")
        self.amount_var.set("")
        self.note_var.set("")
        self.refresh_all()
        self.show_page("Dashboard")

    def make_tree(self, parent, height=12):
        columns = ("id", "type", "amount", "category", "date", "note")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        headings = {"id": "ID", "type": "TYPE", "amount": "AMOUNT (₹)",
                    "category": "CATEGORY", "date": "DATE", "note": "DESCRIPTION"}
        widths = {"id": 45, "type": 90, "amount": 125, "category": 115,
                  "date": 115, "note": 220}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("Income", foreground=GREEN)
        self.tree.tag_configure("Expense", foreground="#ff9292")

    def load_tree(self, limit=None):
        if not hasattr(self, "tree") or not self.tree.winfo_exists():
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = "SELECT id, kind, amount, category, txn_date, note FROM transactions ORDER BY txn_date DESC, id DESC"
        params = ()
        if limit:
            query += " LIMIT ?"
            params = (limit,)
        for row in self.conn.execute(query, params).fetchall():
            rid, kind, amount, category, txn_date, note = row
            self.tree.insert("", "end", values=(rid, kind, f"{amount:,.2f}",
                                                category, txn_date, note or "-"),
                             tags=(kind,))

    def build_transactions_page(self):
        panel = tk.Frame(self.content, bg=PANEL, padx=18, pady=18,
                         highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        bar = tk.Frame(panel, bg=PANEL)
        bar.pack(fill="x", pady=(0, 14))
        tk.Label(bar, text="All recorded transactions", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Button(bar, text="Delete selected", command=self.delete_selected,
                  bg="#713b3b", fg="white", bd=0, padx=12, pady=8,
                  cursor="hand2").pack(side="right")
        self.make_tree(panel, height=14)
        self.load_tree()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a transaction", "Please select a row to delete.")
            return
        if not messagebox.askyesno("Confirm deletion", "Delete the selected transaction?"):
            return
        for item in selected:
            txn_id = self.tree.item(item, "values")[0]
            self.conn.execute("DELETE FROM transactions WHERE id=?", (txn_id,))
        self.conn.commit()
        self.refresh_all()

    def build_reports_page(self):
        income, expense, balance = self.totals()
        summary = tk.Frame(self.content, bg=PANEL, padx=18, pady=16)
        summary.pack(fill="x", pady=(0, 16))
        tk.Label(summary, text=f"Income: ₹{income:,.2f}     "
                              f"Expenses: ₹{expense:,.2f}     "
                              f"Balance: ₹{balance:,.2f}",
                 bg=PANEL, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        chart_area = tk.Frame(self.content, bg=PANEL, padx=12, pady=12)
        chart_area.pack(fill="both", expand=True)
        if HAS_MPL:
            data = self.conn.execute(
                "SELECT category, SUM(amount) FROM transactions "
                "WHERE kind='Expense' GROUP BY category ORDER BY SUM(amount) DESC"
            ).fetchall()
            if data:
                fig = Figure(figsize=(7, 4), dpi=100, facecolor=PANEL)
                ax = fig.add_subplot(111)
                ax.set_facecolor(PANEL)
                labels = [r[0] for r in data]
                values = [r[1] for r in data]
                ax.pie(values, labels=labels, autopct="%1.1f%%",
                       textprops={"color": TEXT}, startangle=90)
                ax.set_title("Expense distribution by category", color=TEXT)
                fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=chart_area)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                tk.Label(chart_area, text="No expense data yet. Add an expense to see your report.",
                         bg=PANEL, fg=MUTED, font=("Segoe UI", 12)).pack(expand=True)
        else:
            tk.Label(chart_area, text="Install Matplotlib to view charts:\n"
                                     "python -m pip install matplotlib",
                     bg=PANEL, fg=MUTED, font=("Segoe UI", 12)).pack(expand=True)

    def refresh_all(self):
        if self.current_page == "Dashboard":
            self.show_page("Dashboard")
        elif self.current_page == "Transactions":
            self.show_page("Transactions")
        elif self.current_page == "Reports":
            self.show_page("Reports")

    def close(self):
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenzApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
