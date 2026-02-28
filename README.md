# JebWine Password Manager

A modern, secure, and intuitive desktop application for managing your credentials. Built with Python using Tkinter for the GUI and SQLite for local data storage.

## ✨ Features

- **Modern Dark UI**: A sleek, Discord-inspired interface designed for clarity and ease of use.
- **Secure Local Storage**: Your passwords stay on your machine in a local SQLite database.
- **Full CRUD Support**: Add, view, update, and delete password records seamlessly.
- **Password Masking in Table**: Passwords are always hidden as `••••••••` in the credentials table by default. Click **View** to reveal a password for a specific row, and **Hide** to mask it again.
- **Eye Toggle in Sidebar**: A 👁 button next to the password input lets you show or hide what you're typing before saving.
- **No Duplicate Email per Website**: Each website can only have one entry per email/username. Attempting to add or update a duplicate will be blocked with a warning.
- **Strict Input Validation**:
  - All fields (Website, Email/Username, Password) are **required**.
  - The Email/Username field **must contain `@`**.
  - **Quotation marks** (`"` and `'`) are **not allowed** in any field.
  - Underscores (`_`) and dashes (`-`) are accepted.

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Tkinter (usually comes bundled with Python)

### Installation

1. Clone the repository or download the project files.
2. Ensure you have the following files in the same directory:
   - `main.py` — Application logic and UI
   - `database.py` — Database operations

### Running the App

```bash
python main.py
```

## 🛠️ Built With

- **Python** — Core programming language.
- **Tkinter** — Standard GUI library for modern desktop layouts.
- **SQLite** — Lightweight, serverless database for persistent storage.

## 📋 How to Use

| Action | Steps |
|---|---|
| **Add a record** | Fill in Website, Email/Username, and Password → click **ADD RECORD** |
| **View a password** | Click **View** in the Action column of the desired row |
| **Hide a password** | Click **Hide** in the Action column |
| **Edit a record** | Click a row to load it into the form → make changes → click **UPDATE RECORD** |
| **Delete a record** | Click a row → click **DELETE RECORD** → confirm |
| **Clear the form** | Click **Clear Fields** |

## 📸 Preview

The application features a dedicated sidebar for data entry and an expanded credential table on the right. Passwords are always masked in the table and can only be revealed on demand per row.

---
*Created as part of the BSIT 2 C project.*
