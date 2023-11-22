import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Database initialization
conn = sqlite3.connect('library.db')
c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL
          )
          ''')
c.execute('''
          CREATE TABLE IF NOT EXISTS books (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              author TEXT NOT NULL,
              available INTEGER DEFAULT 1
          )
          ''')
conn.commit()

# Function to create tables for book rental history
def create_rental_table(username):
    table_name = f'rentals_{username}'
    c.execute(f'''
              CREATE TABLE IF NOT EXISTS {table_name} (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  book_id INTEGER,
                  rental_date DATE,
                  return_date DATE,
                  FOREIGN KEY (book_id) REFERENCES books(id)
              )
              ''')
    conn.commit()

# Function to check if a user exists
def user_exists(username):
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    return c.fetchone() is not None

# Function to check if a book is available
def is_book_available(book_id):
    c.execute('SELECT available FROM books WHERE id = ?', (book_id,))
    return c.fetchone()[0] == 1

# Function to handle signup
def signup():
    username = signup_username.get()
    password = signup_password.get()

    if user_exists(username):
        messagebox.showerror("Error", "Username already exists.")
        return

    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    create_rental_table(username)
    messagebox.showinfo("Success", "Account created successfully. You can now log in.")
    switch_frame()

# Function to handle login
def login():
    username = login_username.get()
    password = login_password.get()

    if not user_exists(username):
        messagebox.showerror("Error", "Username does not exist.")
        return

    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()

    if user is None:
        messagebox.showerror("Error", "Incorrect password.")
    else:
        messagebox.showinfo("Success", "Login successful.")
        open_book_rental_page(username)

# Function to switch between login and signup frames
def switch_frame():
    if login_frame.winfo_ismapped():
        login_frame.grid_forget()
        signup_frame.grid()
        root.title("Sign Up")
    else:
        signup_frame.grid_forget()
        login_frame.grid()
        root.title("Login")

# Function to open the book rental page
def open_book_rental_page(username):
    root.withdraw()  # Hide the main window

    book_rental_window = tk.Toplevel(root)
    book_rental_window.title("Book Rental System")

    def search_books():
        search_term = search_entry.get().lower()
        available_books.delete(0, tk.END)

        for row in c.execute('SELECT id, title FROM books WHERE available = 1'):
            book_id, title = row
            if str(search_term) in str(book_id) or str(search_term) in title.lower():
                available_books.insert(tk.END, f"{book_id}: {title}")

    def load_books():
        available_books.delete(0, tk.END)

        for row in c.execute('SELECT id, title FROM books '):
            book_id, title = row
            available_books.insert(tk.END, f"{book_id}: {title}")

    def rent_book():
        selected_book = available_books.get(available_books.curselection())
        if not selected_book:
            messagebox.showerror("Error", "Please select a book.")
            return

        book_id = int(selected_book.split(':')[0])
        if not is_book_available(book_id):
            messagebox.showerror("Error", "Book is not available for rent.")
            return

        c.execute('UPDATE books SET available = 0 WHERE id = ?', (book_id,))
        conn.commit()

        c.execute(f'INSERT INTO rentals_{username} (book_id, rental_date) VALUES (?, CURRENT_DATE)', (book_id,))
        conn.commit()

        messagebox.showinfo("Success", "Book rented successfully.")

    def return_book():
        selected_book = available_books.get(available_books.curselection())
        if not selected_book:
            messagebox.showerror("Error", "Please select a book.")
            return

        book_id = int(selected_book.split(':')[0])

        c.execute('UPDATE books SET available = 1 WHERE id = ?', (book_id,))
        conn.commit()

        c.execute(f'UPDATE rentals_{username} SET return_date = CURRENT_DATE WHERE book_id = ? AND return_date IS NULL',
                  (book_id,))
        conn.commit()

        messagebox.showinfo("Success", "Book returned successfully.")

        search_books()  # Refresh the available books list after returning a book

    def logout():
        root.deiconify()  # Show the main window
        book_rental_window.destroy()  # Close the book rental window

    # GUI for book rental page
    book_label = tk.Label(book_rental_window, text="Book Rental System", font=("Helvetica", 16))
    book_label.grid(row=0, column=0, columnspan=3, pady=10)

    search_label = tk.Label(book_rental_window, text="Search:")
    search_label.grid(row=1, column=0, pady=5)

    search_entry = tk.Entry(book_rental_window)
    search_entry.grid(row=1, column=1, pady=5)

    search_button = tk.Button(book_rental_window, text="Search", command=search_books)
    search_button.grid(row=1, column=2, pady=5)

    load_books_button = tk.Button(book_rental_window, text="Load Books", command=load_books)
    load_books_button.grid(row=1, column=3, pady=5)

    available_books = tk.Listbox(book_rental_window, selectmode=tk.SINGLE, height=10, width=40)
    available_books.grid(row=2, column=0, columnspan=3, pady=10)

    rent_button = tk.Button(book_rental_window, text="Rent Book", command=rent_book)
    rent_button.grid(row=3, column=0, pady=5)

    return_button = tk.Button(book_rental_window, text="Return Book", command=return_book)
    return_button.grid(row=3, column=1, pady=5)

    logout_button = tk.Button(book_rental_window, text="Logout", command=logout)
    logout_button.grid(row=3, column=2, pady=5)

    # Populate the available books list initially
    load_books()

# GUI for login and signup
root = tk.Tk()
root.title("Library Management System")

login_frame = tk.Frame(root)
login_frame.grid()

login_label = tk.Label(login_frame, text="Login", font=("Helvetica", 16))
login_label.grid(row=0, column=0, columnspan=2, pady=10)

login_username_label = tk.Label(login_frame, text="Username:")
login_username_label.grid(row=1, column=0, pady=5)

login_username = tk.Entry(login_frame)
login_username.grid(row=1, column=1, pady=5)

login_password_label = tk.Label(login_frame, text="Password:")
login_password_label.grid(row=2, column=0, pady=5)

login_password = tk.Entry(login_frame, show="*")
login_password.grid(row=2, column=1, pady=5)

login_button = tk.Button(login_frame, text="Login", command=login)
login_button.grid(row=3, column=0, columnspan=2, pady=10)

signup_frame = tk.Frame(root)
signup_frame.grid_forget()

signup_label = tk.Label(signup_frame, text="Sign Up", font=("Helvetica", 16))
signup_label.grid(row=0, column=0, columnspan=2, pady=10)

signup_username_label = tk.Label(signup_frame, text="Username:")
signup_username_label.grid(row=1, column=0, pady=5)

signup_username = tk.Entry(signup_frame)
signup_username.grid(row=1, column=1, pady=5)

signup_password_label = tk.Label(signup_frame, text="Password:")
signup_password_label.grid(row=2, column=0, pady=5)

signup_password = tk.Entry(signup_frame, show="*")
signup_password.grid(row=2, column=1, pady=5)

signup_button = tk.Button(signup_frame, text="Sign Up", command=signup)
signup_button.grid(row=3, column=0, columnspan=2, pady=10)

switch_button = tk.Button(root, text="Switch", command=switch_frame)
switch_button.grid(pady=10)

root.mainloop()

# Close the database connection when the application is closed
conn.close()