import sqlite3

def init_db():
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_password(website, username, password):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)',
                   (website, username, password))
    conn.commit()
    conn.close()

def get_all_passwords():
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM passwords')
    records = cursor.fetchall()
    conn.close()
    return records

def update_password(id, website, username, password):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE passwords 
        SET website = ?, username = ?, password = ? 
        WHERE id = ?
    ''', (website, username, password, id))
    conn.commit()
    conn.close()

def delete_password(id):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM passwords WHERE id = ?', (id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
