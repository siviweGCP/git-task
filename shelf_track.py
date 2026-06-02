"""
Shelf Track - Bookstore Inventory System.

This program allows a bookstore clerk to manage book inventory using
a SQLite database. The clerk can add, update, delete, search, and view
book details.
"""

import sqlite3


DATABASE_NAME = "ebookstore.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.

    Returns:
        sqlite3.Connection: Connection object for ebookstore.db.
    """
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    """
    Create the author and book tables if they do not already exist.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS author (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                authorID INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                FOREIGN KEY (authorID) REFERENCES author(id)
            )
        """)

        conn.commit()


def insert_initial_data():
    """
    Insert the required initial authors and books into the database.

    INSERT OR IGNORE prevents duplicate records from being inserted every
    time the program runs.
    """
    authors = [
        (1290, "Charles Dickens", "England"),
        (8937, "J.K. Rowling", "England"),
        (2356, "C.S. Lewis", "Ireland"),
        (6380, "J.R.R. Tolkien", "South Africa"),
        (5620, "Lewis Carroll", "England"),
    ]

    books = [
        (3001, "A Tale of Two Cities", 1290, 30),
        (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
        (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
        (3004, "The Lord of the Rings", 6380, 37),
        (3005, "Alice's Adventures in Wonderland", 5620, 12),
    ]

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.executemany("""
            INSERT OR IGNORE INTO author (id, name, country)
            VALUES (?, ?, ?)
        """, authors)

        cursor.executemany("""
            INSERT OR IGNORE INTO book (id, title, authorID, qty)
            VALUES (?, ?, ?, ?)
        """, books)

        conn.commit()


def get_valid_four_digit_id(prompt):
    """
    Ask the user for a valid four-digit integer ID.

    Args:
        prompt (str): The input message shown to the user.

    Returns:
        int: A valid four-digit integer.
    """
    while True:
        user_input = input(prompt).strip()

        if user_input.isdigit() and len(user_input) == 4:
            return int(user_input)

        print("Error: ID must be exactly four digits.")


def get_valid_integer(prompt):
    """
    Ask the user for a valid integer.

    Args:
        prompt (str): The input message shown to the user.

    Returns:
        int: A valid integer.
    """
    while True:
        user_input = input(prompt).strip()

        if user_input.isdigit():
            return int(user_input)

        print("Error: Please enter a valid number.")


def get_non_empty_text(prompt):
    """
    Ask the user for text that is not empty.

    Args:
        prompt (str): The input message shown to the user.

    Returns:
        str: A non-empty string.
    """
    while True:
        user_input = input(prompt).strip()

        if user_input:
            return user_input

        print("Error: This field cannot be empty.")


def add_book():
    """
    Add a new book and its author details to the database.
    """
    print("\n--- Enter New Book ---")

    book_id = get_valid_four_digit_id("Enter book ID: ")
    title = get_non_empty_text("Enter book title: ")
    author_id = get_valid_four_digit_id("Enter author ID: ")
    author_name = get_non_empty_text("Enter author's name: ")
    author_country = get_non_empty_text("Enter author's country: ")
    qty = get_valid_integer("Enter quantity: ")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO author (id, name, country)
                VALUES (?, ?, ?)
            """, (author_id, author_name, author_country))

            cursor.execute("""
                INSERT INTO book (id, title, authorID, qty)
                VALUES (?, ?, ?, ?)
            """, (book_id, title, author_id, qty))

            conn.commit()
            print("Book added successfully.")

    except sqlite3.IntegrityError:
        print("Error: A book with this ID already exists.")
    except sqlite3.Error as error:
        print(f"Database error: {error}")


def update_book():
    """
    Update book information.

    The user can update quantity, title, author ID, author name, or
    author country.
    """
    print("\n--- Update Book ---")

    book_id = get_valid_four_digit_id("Enter the book ID to update: ")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT book.id, book.title, book.authorID, book.qty,
                       author.name, author.country
                FROM book
                INNER JOIN author ON book.authorID = author.id
                WHERE book.id = ?
            """, (book_id,))

            book = cursor.fetchone()

            if not book:
                print("Book not found.")
                return

            current_book_id, title, author_id, qty, author_name, country = book

            print("\nCurrent Book Details")
            print("-" * 50)
            print(f"Book ID: {current_book_id}")
            print(f"Title: {title}")
            print(f"Author ID: {author_id}")
            print(f"Author's Name: {author_name}")
            print(f"Author's Country: {country}")
            print(f"Quantity: {qty}")
            print("-" * 50)

            print("\nWhat do you want to update?")
            print("1. Quantity")
            print("2. Title")
            print("3. Author ID")
            print("4. Author name")
            print("5. Author country")

            choice = input("Enter your choice. Press Enter for Quantity: ").strip()

            if choice == "" or choice == "1":
                new_qty = get_valid_integer("Enter new quantity: ")

                cursor.execute("""
                    UPDATE book
                    SET qty = ?
                    WHERE id = ?
                """, (new_qty, book_id))

                print("Quantity updated successfully.")

            elif choice == "2":
                new_title = get_non_empty_text("Enter new title: ")

                cursor.execute("""
                    UPDATE book
                    SET title = ?
                    WHERE id = ?
                """, (new_title, book_id))

                print("Title updated successfully.")

            elif choice == "3":
                new_author_id = get_valid_four_digit_id("Enter new author ID: ")
                new_author_name = get_non_empty_text("Enter new author's name: ")
                new_country = get_non_empty_text("Enter new author's country: ")

                cursor.execute("""
                    INSERT OR IGNORE INTO author (id, name, country)
                    VALUES (?, ?, ?)
                """, (new_author_id, new_author_name, new_country))

                cursor.execute("""
                    UPDATE book
                    SET authorID = ?
                    WHERE id = ?
                """, (new_author_id, book_id))

                print("Author ID updated successfully.")

            elif choice == "4":
                new_author_name = get_non_empty_text("Enter new author's name: ")

                cursor.execute("""
                    UPDATE author
                    SET name = ?
                    WHERE id = ?
                """, (new_author_name, author_id))

                print("Author name updated successfully.")

            elif choice == "5":
                new_country = get_non_empty_text("Enter new author's country: ")

                cursor.execute("""
                    UPDATE author
                    SET country = ?
                    WHERE id = ?
                """, (new_country, author_id))

                print("Author country updated successfully.")

            else:
                print("Invalid choice. No changes made.")

            conn.commit()

    except sqlite3.Error as error:
        print(f"Database error: {error}")


def delete_book():
    """
    Delete a book from the database using the book ID.
    """
    print("\n--- Delete Book ---")

    book_id = get_valid_four_digit_id("Enter the book ID to delete: ")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT title
                FROM book
                WHERE id = ?
            """, (book_id,))

            book = cursor.fetchone()

            if not book:
                print("Book not found.")
                return

            confirm = input(
                f"Are you sure you want to delete '{book[0]}'? (yes/no): "
            ).strip().lower()

            if confirm == "yes":
                cursor.execute("""
                    DELETE FROM book
                    WHERE id = ?
                """, (book_id,))

                conn.commit()
                print("Book deleted successfully.")
            else:
                print("Delete cancelled.")

    except sqlite3.Error as error:
        print(f"Database error: {error}")


def search_books():
    """
    Search for books by book ID, title, or author name.
    """
    print("\n--- Search Books ---")
    search_term = input("Enter book ID, title, or author name: ").strip()

    if not search_term:
        print("Error: Search term cannot be empty.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT book.id, book.title, author.name, author.country, book.qty
                FROM book
                INNER JOIN author ON book.authorID = author.id
                WHERE CAST(book.id AS TEXT) LIKE ?
                   OR book.title LIKE ?
                   OR author.name LIKE ?
            """, (
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%"
            ))

            results = cursor.fetchall()

            if results:
                print("\nSearch Results")
                print("-" * 50)

                for book_id, title, author_name, country, qty in results:
                    print(f"Book ID: {book_id}")
                    print(f"Title: {title}")
                    print(f"Author: {author_name}")
                    print(f"Country: {country}")
                    print(f"Quantity: {qty}")
                    print("-" * 50)
            else:
                print("No matching books found.")

    except sqlite3.Error as error:
        print(f"Database error: {error}")


def view_all_book_details():
    """
    Display the title, author's name, author's country, and quantity
    for all books in the database.
    """
    print("\nDetails")
    print("-" * 50)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT book.title, author.name, author.country, book.qty
                FROM book
                INNER JOIN author ON book.authorID = author.id
                ORDER BY book.id
            """)

            books = cursor.fetchall()

            if books:
                for title, author_name, country, qty in books:
                    print(f"Title: {title}")
                    print(f"Author's Name: {author_name}")
                    print(f"Author's Country: {country}")
                    print(f"Quantity: {qty}")
                    print("-" * 50)
            else:
                print("No books found.")

    except sqlite3.Error as error:
        print(f"Database error: {error}")


def display_menu():
    """
    Display the main menu options.
    """
    print("\nShelf Track - Bookstore Inventory System")
    print("-" * 50)
    print("1. Enter book")
    print("2. Update book")
    print("3. Delete book")
    print("4. Search books")
    print("5. View details of all books")
    print("0. Exit")


def main():
    """
    Run the Shelf Track bookstore inventory program.
    """
    create_tables()
    insert_initial_data()

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_book()
        elif choice == "2":
            update_book()
        elif choice == "3":
            delete_book()
        elif choice == "4":
            search_books()
        elif choice == "5":
            view_all_book_details()
        elif choice == "0":
            print("Thank you for using Shelf Track. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid menu option.")


if __name__ == "__main__":
    main()