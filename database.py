"""
Database module for Callum's Library App
Handles SQLite database creation and operations
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "library.db"


def init_database():
    """Create the database and tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT UNIQUE,
            title TEXT NOT NULL,
            year TEXT,
            author TEXT,
            artist TEXT,
            publisher TEXT,
            page_count INTEGER,
            description TEXT,
            series_name TEXT,
            series_number INTEGER,
            format TEXT DEFAULT 'Book',
            cover_path TEXT,
            notes TEXT,
            date_added TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add artist column to existing databases (migration)
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN artist TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Loans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            borrower_name TEXT NOT NULL,
            date_loaned TEXT NOT NULL,
            date_due TEXT NOT NULL,
            date_returned TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def add_book(isbn, title, year, author, artist=None, publisher=None, page_count=None, 
             description=None, series_name=None, series_number=None,
             format_type='Book', cover_path=None, notes=None):
    """Add a new book to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO books (isbn, title, year, author, artist, publisher, page_count,
                             description, series_name, series_number, format, 
                             cover_path, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (isbn, title, year, author, artist, publisher, page_count, description,
              series_name, series_number, format_type, cover_path, notes))
        
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        return book_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("A book with this ISBN already exists")


def update_book(book_id, **kwargs):
    """Update book details"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided kwargs
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    
    if fields:
        query = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
        values.append(book_id)
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()


def get_book(book_id):
    """Get a book by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    
    return dict(book) if book else None


def get_all_books():
    """Get all books"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM books ORDER BY title COLLATE NOCASE")
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return books


def search_books(query):
    """Search books by title, author, artist, or ISBN (quick search)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ? OR artist LIKE ? OR isbn LIKE ?
        ORDER BY title COLLATE NOCASE
    """, (search_pattern, search_pattern, search_pattern, search_pattern))
    
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return books


def advanced_search(isbn=None, title=None, series=None, author=None, artist=None, publisher=None):
    """Advanced search with multiple criteria (case-insensitive, partial matching)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query dynamically based on provided criteria
    conditions = []
    params = []
    
    if isbn:
        conditions.append("isbn LIKE ?")
        params.append(f"%{isbn}%")
    
    if title:
        conditions.append("title LIKE ?")
        params.append(f"%{title}%")
    
    if series:
        conditions.append("series_name LIKE ?")
        params.append(f"%{series}%")
    
    if author:
        conditions.append("author LIKE ?")
        params.append(f"%{author}%")
    
    if artist:
        conditions.append("artist LIKE ?")
        params.append(f"%{artist}%")
    
    if publisher:
        conditions.append("publisher LIKE ?")
        params.append(f"%{publisher}%")
    
    # If no criteria provided, return all books
    if not conditions:
        cursor.execute("SELECT * FROM books ORDER BY title COLLATE NOCASE")
    else:
        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM books WHERE {where_clause} ORDER BY title COLLATE NOCASE"
        cursor.execute(query, params)
    
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return books


def loan_book(book_id, borrower_name, loan_days=30):
    """Record a book loan"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    date_loaned = datetime.now().isoformat()
    date_due = (datetime.now() + timedelta(days=loan_days)).isoformat()
    
    cursor.execute("""
        INSERT INTO loans (book_id, borrower_name, date_loaned, date_due)
        VALUES (?, ?, ?, ?)
    """, (book_id, borrower_name, date_loaned, date_due))
    
    conn.commit()
    loan_id = cursor.lastrowid
    conn.close()
    
    return loan_id


def return_book(loan_id):
    """Mark a book as returned"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    date_returned = datetime.now().isoformat()
    cursor.execute("""
        UPDATE loans SET date_returned = ? WHERE id = ?
    """, (date_returned, loan_id))
    
    conn.commit()
    conn.close()


def get_current_loan(book_id):
    """Get the current active loan for a book (if any)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM loans 
        WHERE book_id = ? AND date_returned IS NULL
        ORDER BY date_loaned DESC
        LIMIT 1
    """, (book_id,))
    
    loan = cursor.fetchone()
    conn.close()
    
    return dict(loan) if loan else None


def get_all_loans():
    """Get all active loans"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT loans.*, books.title, books.author
        FROM loans
        JOIN books ON loans.book_id = books.id
        WHERE loans.date_returned IS NULL
        ORDER BY loans.date_due
    """)
    
    loans = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return loans


def get_overdue_loans():
    """Get all overdue loans (> 30 days)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute("""
        SELECT loans.*, books.title, books.author
        FROM loans
        JOIN books ON loans.book_id = books.id
        WHERE loans.date_returned IS NULL AND loans.date_due < ?
        ORDER BY loans.date_due
    """, (now,))
    
    loans = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return loans


def get_loan_history(book_id):
    """Get loan history for a specific book"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM loans 
        WHERE book_id = ?
        ORDER BY date_loaned DESC
    """, (book_id,))
    
    loans = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return loans


def delete_book(book_id):
    """Delete a book from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Initialise database when run directly
    init_database()
    print(f"Database initialised at {DB_PATH}")
