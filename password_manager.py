import tkinter as tk
from tkinter import ttk, messagebox
import csv
from pathlib import Path


# -------------------------
# File setup
# -------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILE_PATH = DATA_DIR / "passwords.csv"


# Create CSV file if it does not exist
if not FILE_PATH.exists():
    with open(FILE_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Website", "Username", "Password"])


# -------------------------
# Simple password obfuscation
# -------------------------
def encode_password(text):
    """Simple reversible obfuscation for demonstration purposes."""
    return "".join(chr(ord(char) + 3) for char in text)


def decode_password(text):
    """Reverse the simple password obfuscation."""
    return "".join(chr(ord(char) - 3) for char in text)


# -------------------------
# Save password
# -------------------------
def save_password():
    website = entry_website.get().strip()
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not website or not username or not password:
        messagebox.showerror(
            "Error",
            "All fields must be filled."
        )
        return

    encoded_password = encode_password(password)

    with open(FILE_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            website,
            username,
            encoded_password
        ])

    entry_website.delete(0, tk.END)
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

    messagebox.showinfo(
        "Saved",
        "Password entry saved."
    )


# -------------------------
# Load passwords
# -------------------------
def load_passwords():
    """Load stored password entries from the CSV file."""

    if not FILE_PATH.exists():
        return []

    rows = []

    with open(
        FILE_PATH,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            website = row.get("Website", "").strip()
            username = row.get("Username", "").strip()
            encoded = row.get("Password", "").strip()

            try:
                password = decode_password(encoded)
            except Exception:
                password = ""

            rows.append({
                "Website": website,
                "Username": username,
                "PasswordEncoded": encoded,
                "Password": password
            })

    return rows


# -------------------------
# Show stored passwords
# -------------------------
def show_passwords():
    data = load_passwords()

    if not data:
        messagebox.showinfo(
            "Empty",
            "No passwords stored yet."
        )
        return

    window = tk.Toplevel(root)
    window.title("Stored Passwords")
    window.geometry("700x420")
    window.resizable(False, False)

    columns = (
        "Website",
        "Username",
        "Password",
        "Encoded"
    )

    tree = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    tree.heading("Website", text="Website")
    tree.heading("Username", text="Username")
    tree.heading("Password", text="Password")

    tree.column("Website", width=220)
    tree.column("Username", width=200)
    tree.column("Password", width=200)

    # Hidden column used when deleting an entry
    tree.column(
        "Encoded",
        width=0,
        stretch=False
    )

    tree.pack(
        fill=tk.BOTH,
        expand=True,
        padx=8,
        pady=8
    )

    # Add stored entries
    for row in data:
        tree.insert(
            "",
            tk.END,
            values=(
                row["Website"],
                row["Username"],
                row["Password"],
                row["PasswordEncoded"]
            )
        )

    # -------------------------
    # Copy password
    # -------------------------
    def copy_password():
        selected = tree.focus()

        if not selected:
            messagebox.showerror(
                "Error",
                "Select an entry first."
            )
            return

        values = tree.item(selected)["values"]
        password = values[2]

        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()

        messagebox.showinfo(
            "Copied",
            "Password copied to clipboard."
        )

    # -------------------------
    # Delete entry
    # -------------------------
    def delete_entry():
        selected = tree.focus()

        if not selected:
            messagebox.showerror(
                "Error",
                "Select an entry first."
            )
            return

        values = tree.item(selected)["values"]

        website = str(values[0]).strip()
        username = str(values[1]).strip()
        encoded_password = str(values[3]).strip()

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete entry for {website} / {username}?"
        )

        if not confirm:
            return

        kept_rows = []

        with open(
            FILE_PATH,
            "r",
            encoding="utf-8",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                same_entry = (
                    row.get("Website", "").strip() == website
                    and row.get("Username", "").strip() == username
                    and row.get("Password", "").strip() == encoded_password
                )

                if not same_entry:
                    kept_rows.append(row)

        # Rewrite CSV without deleted entry
        with open(
            FILE_PATH,
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            fieldnames = [
                "Website",
                "Username",
                "Password"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(kept_rows)

        tree.delete(selected)

        messagebox.showinfo(
            "Deleted",
            "Password entry deleted."
        )

    # Buttons
    button_frame = ttk.Frame(window)
    button_frame.pack(pady=6)

    ttk.Button(
        button_frame,
        text="Copy Password",
        command=copy_password,
        width=18
    ).grid(row=0, column=0, padx=8)

    ttk.Button(
        button_frame,
        text="Delete Entry",
        command=delete_entry,
        width=18
    ).grid(row=0, column=1, padx=8)


# -------------------------
# Main window
# -------------------------
root = tk.Tk()
root.title("Password Manager")
root.geometry("460x300")
root.resizable(False, False)

frame = ttk.Frame(
    root,
    padding=15
)
frame.pack(
    fill="both",
    expand=True
)


# Website
ttk.Label(
    frame,
    text="Website:"
).grid(
    row=0,
    column=0,
    sticky="w"
)

entry_website = ttk.Entry(
    frame,
    width=40
)
entry_website.grid(
    row=0,
    column=1,
    pady=4
)


# Username
ttk.Label(
    frame,
    text="Username:"
).grid(
    row=1,
    column=0,
    sticky="w"
)

entry_username = ttk.Entry(
    frame,
    width=40
)
entry_username.grid(
    row=1,
    column=1,
    pady=4
)


# Password
ttk.Label(
    frame,
    text="Password:"
).grid(
    row=2,
    column=0,
    sticky="w"
)

entry_password = ttk.Entry(
    frame,
    width=40,
    show="*"
)
entry_password.grid(
    row=2,
    column=1,
    pady=4
)


# Add password
ttk.Button(
    frame,
    text="Add Password",
    command=save_password,
    width=20
).grid(
    row=3,
    column=0,
    columnspan=2,
    pady=12
)


# Show passwords
ttk.Button(
    frame,
    text="Show Passwords",
    command=show_passwords,
    width=20
).grid(
    row=4,
    column=0,
    columnspan=2,
    pady=4
)


# Exit
ttk.Button(
    frame,
    text="Exit",
    command=root.destroy,
    width=20
).grid(
    row=5,
    column=0,
    columnspan=2,
    pady=8
)


root.mainloop()