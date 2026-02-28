import tkinter as tk
from tkinter import ttk, messagebox
import database
import re

# Modern Color Palette
COLORS = {
    "bg":         "#1e2124",   # Dark grey
    "sidebar":    "#282b30",   # Slightly lighter grey
    "accent":     "#7289da",   # Discord-like blurple
    "text":       "#ffffff",   # White
    "text_dim":   "#b9bbbe",   # Muted grey
    "success":    "#43b581",   # Green
    "danger":     "#f04747",   # Red
    "entry_bg":   "#40444b",   # Dark input field
    "view_btn":   "#4f545c",   # Neutral grey for View button
}

FORBIDDEN_CHARS = set('"\'')  # both double and single quotes are forbidden


def validate_inputs(website, username, password):
    """
    Validate all three fields.
    Returns (True, "") on success, or (False, error_message) on failure.
    """
    if not website.strip():
        return False, "Website field is required."
    if not username.strip():
        return False, "Email/Username field is required."
    if not password.strip():
        return False, "Password field is required."

    # Check forbidden characters (quotes)
    for field_name, value in [("Website", website), ("Email/Username", username), ("Password", password)]:
        for ch in value:
            if ch in FORBIDDEN_CHARS:
                return False, f"{field_name} must not contain quotation marks (' or \")."

    # Require '@' in the username (email)
    if "@" not in username:
        return False, "Email/Username must contain '@'."

    return True, ""


class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JebWine Password Manager")
        self.root.geometry("970x600")
        self.root.configure(bg=COLORS["bg"])

        # Track which rows have their password revealed {item_id: bool}
        self._revealed = {}

        # Store raw records so we can show/hide passwords without re-querying
        self._records = []

        # Initialize Database
        database.init_db()

        self.setup_styles()
        self.create_widgets()
        self.load_data()

    # ------------------------------------------------------------------ #
    #  Styles                                                              #
    # ------------------------------------------------------------------ #
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background=COLORS["sidebar"],
                        foreground=COLORS["text"],
                        fieldbackground=COLORS["sidebar"],
                        rowheight=35,
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", COLORS["accent"])])

        style.configure("Treeview.Heading",
                        background=COLORS["accent"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0)

        style.configure("Modern.TButton",
                        background=COLORS["accent"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=10,
                        borderwidth=0)
        style.map("Modern.TButton",
                  background=[("active", "#5b6eae")])

        style.configure("Danger.TButton",
                        background=COLORS["danger"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=10)
        style.map("Danger.TButton",
                  background=[("active", "#d83c3e")])

        style.configure("View.TButton",
                        background=COLORS["view_btn"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 9, "bold"),
                        padding=6,
                        borderwidth=0)
        style.map("View.TButton",
                  background=[("active", "#686d73")])

    # ------------------------------------------------------------------ #
    #  Widget creation                                                     #
    # ------------------------------------------------------------------ #
    def create_widgets(self):
        # ── Sidebar / Input Frame ──────────────────────────────────────
        self.input_frame = tk.Frame(self.root, bg=COLORS["sidebar"], width=300, padx=20, pady=20)
        self.input_frame.pack(side="left", fill="y")

        tk.Label(self.input_frame, text="SECURE VAULT", fg=COLORS["accent"], bg=COLORS["sidebar"],
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 30))

        # Form Fields
        self.create_label_entry("Website", "website_entry")
        self.create_label_entry("Email / Username", "username_entry")

        # Password field + show/hide toggle inside the sidebar
        tk.Label(self.input_frame, text="Password", fg=COLORS["text_dim"], bg=COLORS["sidebar"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 5))

        pw_row = tk.Frame(self.input_frame, bg=COLORS["sidebar"])
        pw_row.pack(fill="x")

        self.password_entry = tk.Entry(pw_row, bg=COLORS["entry_bg"], fg=COLORS["text"],
                                       insertbackground="white", font=("Segoe UI", 11),
                                       borderwidth=0, relief="flat", highlightthickness=1,
                                       highlightbackground="#4f545c", highlightcolor=COLORS["accent"],
                                       show="*")
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=8)

        self._pw_visible = False
        self.toggle_btn = tk.Button(pw_row, text="👁", bg=COLORS["entry_bg"], fg=COLORS["text_dim"],
                                    activebackground=COLORS["entry_bg"], activeforeground=COLORS["text"],
                                    borderwidth=0, cursor="hand2", font=("Segoe UI", 11),
                                    command=self._toggle_pw_entry)
        self.toggle_btn.pack(side="left", padx=(4, 0), ipadx=4, ipady=4)

        # Buttons
        self.add_btn = ttk.Button(self.input_frame, text="ADD RECORD",
                                  style="Modern.TButton", command=self.add_record)
        self.add_btn.pack(fill="x", pady=(20, 10))

        self.update_btn = ttk.Button(self.input_frame, text="UPDATE RECORD",
                                     style="Modern.TButton", command=self.update_record)
        self.update_btn.pack(fill="x", pady=5)

        self.delete_btn = ttk.Button(self.input_frame, text="DELETE RECORD",
                                     style="Danger.TButton", command=self.delete_record)
        self.delete_btn.pack(fill="x", pady=5)

        self.clear_btn = tk.Button(self.input_frame, text="Clear Fields",
                                   bg=COLORS["sidebar"], fg=COLORS["text_dim"],
                                   borderwidth=0, cursor="hand2", command=self.clear_entries)
        self.clear_btn.pack(pady=20)

        # ── Main Content Area ─────────────────────────────────────────
        self.content_frame = tk.Frame(self.root, bg=COLORS["bg"], padx=20, pady=20)
        self.content_frame.pack(side="right", expand=True, fill="both")

        tk.Label(self.content_frame, text="Stored Credentials",
                 fg=COLORS["text"], bg=COLORS["bg"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # Treeview — Password column shows "••••••••" by default
        columns = ("ID", "Website", "Email/Username", "Password", "Action")
        self.tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", style="Treeview")

        col_widths = {"ID": 50, "Website": 160, "Email/Username": 180, "Password": 160, "Action": 80}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 120), anchor="center")

        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #
    def create_label_entry(self, label_text, attr_name, show=None):
        tk.Label(self.input_frame, text=label_text, fg=COLORS["text_dim"], bg=COLORS["sidebar"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 5))
        entry = tk.Entry(self.input_frame, bg=COLORS["entry_bg"], fg=COLORS["text"],
                         insertbackground="white", font=("Segoe UI", 11),
                         borderwidth=0, relief="flat", highlightthickness=1,
                         highlightbackground="#4f545c", highlightcolor=COLORS["accent"])
        if show:
            entry.config(show=show)
        entry.pack(fill="x", ipady=8)
        setattr(self, attr_name, entry)

    def _toggle_pw_entry(self):
        """Show/hide the password inside the sidebar entry."""
        self._pw_visible = not self._pw_visible
        self.password_entry.config(show="" if self._pw_visible else "*")

    def _masked(self, password):
        return "••••••••"

    # ------------------------------------------------------------------ #
    #  Data loading                                                        #
    # ------------------------------------------------------------------ #
    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self._revealed.clear()
        self._records = database.get_all_passwords()
        for record in self._records:
            # record = (id, website, username, password)
            row_id = self.tree.insert("", "end",
                                      values=(record[0], record[1], record[2],
                                              self._masked(record[3]), "View"))
            self._revealed[row_id] = False

    # ------------------------------------------------------------------ #
    #  View button click                                                   #
    # ------------------------------------------------------------------ #
    def _on_tree_click(self, event):
        """Toggle password visibility when the 'View' / 'Hide' cell is clicked."""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        # Column #5 is the "Action" column (1-indexed)
        if col != "#5":
            return
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self._toggle_row_password(item)

    def _toggle_row_password(self, item):
        currently_revealed = self._revealed.get(item, False)
        # Find the matching record
        row_values = self.tree.item(item, "values")
        record_id = int(row_values[0])
        record = next((r for r in self._records if r[0] == record_id), None)
        if record is None:
            return

        if currently_revealed:
            # Hide it
            self.tree.item(item, values=(record[0], record[1], record[2],
                                         self._masked(record[3]), "View"))
            self._revealed[item] = False
        else:
            # Reveal it
            self.tree.item(item, values=(record[0], record[1], record[2],
                                         record[3], "Hide"))
            self._revealed[item] = True

    # ------------------------------------------------------------------ #
    #  CRUD operations                                                     #
    # ------------------------------------------------------------------ #
    def add_record(self):
        website  = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        valid, msg = validate_inputs(website, username, password)
        if not valid:
            messagebox.showwarning("Validation Error", msg)
            return

        if database.check_duplicate(website, username):
            messagebox.showwarning("Duplicate Entry",
                                   f"'{username}' is already registered for '{website}'.")
            return

        database.add_password(website, username, password)
        self.load_data()
        self.clear_entries()
        messagebox.showinfo("Success", "Record added successfully!")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            record_id = int(values[0])
            # Get actual (unmasked) password from our cached records
            record = next((r for r in self._records if r[0] == record_id), None)
            self.clear_entries()
            self.website_entry.insert(0, values[1])
            self.username_entry.insert(0, values[2])
            if record:
                self.password_entry.insert(0, record[3])

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to update.")
            return

        record_id = self.tree.item(selected[0], "values")[0]
        website   = self.website_entry.get().strip()
        username  = self.username_entry.get().strip()
        password  = self.password_entry.get().strip()

        valid, msg = validate_inputs(website, username, password)
        if not valid:
            messagebox.showwarning("Validation Error", msg)
            return

        if database.check_duplicate(website, username, exclude_id=int(record_id)):
            messagebox.showwarning("Duplicate Entry",
                                   f"'{username}' is already registered for '{website}'.")
            return

        database.update_password(record_id, website, username, password)
        self.load_data()
        self.clear_entries()
        messagebox.showinfo("Success", "Record updated successfully!")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return

        record_id = self.tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            database.delete_password(record_id)
            self.load_data()
            self.clear_entries()

    def clear_entries(self):
        self.website_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        # Reset password entry to hidden after clearing
        self._pw_visible = False
        self.password_entry.config(show="*")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
