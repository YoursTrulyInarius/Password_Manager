import tkinter as tk
from tkinter import ttk, messagebox
import database

# Modern Color Palette
COLORS = {
    "bg": "#1e2124",        # Dark grey
    "sidebar": "#282b30",   # Slightly lighter grey
    "accent": "#7289da",    # Discord-like blurple
    "text": "#ffffff",      # White
    "text_dim": "#b9bbbe",  # Muted grey
    "success": "#43b581",   # Green
    "danger": "#f04747",    # Red
    "entry_bg": "#40444b"   # Dark input field
}

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JebWine Password Manager")
        self.root.geometry("900x600")
        self.root.configure(bg=COLORS["bg"])
        
        # Initialize Database
        database.init_db()
        
        self.setup_styles()
        self.create_widgets()
        self.load_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Treeview Style
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
        
        # Button Styles
        style.configure("Modern.TButton",
                        background=COLORS["accent"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=10,
                        borderwidth=0)
        style.map("Modern.TButton",
                  background=[("active", "#5b6eae")]) # Darker blurple on hover

        style.configure("Danger.TButton",
                        background=COLORS["danger"],
                        foreground=COLORS["text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=10)
        style.map("Danger.TButton",
                  background=[("active", "#d83c3e")])

    def create_widgets(self):
        # Sidebar/Input Frame
        self.input_frame = tk.Frame(self.root, bg=COLORS["sidebar"], width=300, padx=20, pady=20)
        self.input_frame.pack(side="left", fill="y")
        
        tk.Label(self.input_frame, text="SECURE VAULT", fg=COLORS["accent"], bg=COLORS["sidebar"], 
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 30))
        
        # Form Fields
        self.create_label_entry("Website", "website_entry")
        self.create_label_entry("Username", "username_entry")
        self.create_label_entry("Password", "password_entry", show="*")
        
        # Buttons
        self.add_btn = ttk.Button(self.input_frame, text="ADD RECORD", style="Modern.TButton", command=self.add_record)
        self.add_btn.pack(fill="x", pady=(20, 10))
        
        self.update_btn = ttk.Button(self.input_frame, text="UPDATE RECORD", style="Modern.TButton", command=self.update_record)
        self.update_btn.pack(fill="x", pady=5)
        
        self.delete_btn = ttk.Button(self.input_frame, text="DELETE RECORD", style="Danger.TButton", command=self.delete_record)
        self.delete_btn.pack(fill="x", pady=5)
        
        self.clear_btn = tk.Button(self.input_frame, text="Clear Fields", bg=COLORS["sidebar"], fg=COLORS["text_dim"], 
                                   borderwidth=0, cursor="hand2", command=self.clear_entries)
        self.clear_btn.pack(pady=20)

        # Main Content Area
        self.content_frame = tk.Frame(self.root, bg=COLORS["bg"], padx=20, pady=20)
        self.content_frame.pack(side="right", expand=True, fill="both")
        
        tk.Label(self.content_frame, text="Stored Credentials", fg=COLORS["text"], bg=COLORS["bg"], 
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Treeview
        columns = ("ID", "Website", "Username", "Password")
        self.tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", style="Treeview")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col == "ID" else 150, anchor="center")
        
        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def create_label_entry(self, label_text, attr_name, show=None):
        tk.Label(self.input_frame, text=label_text, fg=COLORS["text_dim"], bg=COLORS["sidebar"], 
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 5))
        entry = tk.Entry(self.input_frame, bg=COLORS["entry_bg"], fg=COLORS["text"], insertbackground="white",
                         font=("Segoe UI", 11), borderwidth=0, relief="flat", highlightthickness=1,
                         highlightbackground="#4f545c", highlightcolor=COLORS["accent"])
        if show:
            entry.config(show=show)
        entry.pack(fill="x", ipady=8)
        setattr(self, attr_name, entry)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        records = database.get_all_passwords()
        for record in records:
            self.tree.insert("", "end", values=record)

    def add_record(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if website and username and password:
            database.add_password(website, username, password)
            self.load_data()
            self.clear_entries()
            messagebox.showinfo("Success", "Record added successfully!")
        else:
            messagebox.showwarning("Incomplete", "Please fill in all fields.")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_entries()
            self.website_entry.insert(0, values[1])
            self.username_entry.insert(0, values[2])
            self.password_entry.insert(0, values[3])

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to update.")
            return
            
        id = self.tree.item(selected[0], "values")[0]
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if website and username and password:
            database.update_password(id, website, username, password)
            self.load_data()
            self.clear_entries()
            messagebox.showinfo("Success", "Record updated successfully!")
        else:
            messagebox.showwarning("Incomplete", "Please fill in all fields.")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return
            
        id = self.tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            database.delete_password(id)
            self.load_data()
            self.clear_entries()

    def clear_entries(self):
        self.website_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
