# Callum's Library Management System

A desktop application for managing a personal library of books and comics with lending tracking.

## Features

- **ISBN Lookup**: Automatically fetch book details from Open Library API
- **Complete Book Management**: Track title, author, publisher, year, page count, series info, and more
- **Cover Images**: Download and display book covers
- **Lending System**: Track who has borrowed books and when they're due back
- **Overdue Warnings**: Separate tab for books on loan longer than 30 days
- **Quick Search**: Find books instantly by title, author, or ISBN
- **Advanced Search**: Dedicated search tab with multiple criteria (ISBN, Title, Series, Author, Artist, Publisher)
- **Flexible Searching**: Case-insensitive with partial matching (typo-tolerant)
- **Manual Cover Upload**: Upload custom cover images for any book
- **Alphabetical Sorting**: All book lists automatically sorted by title
- **Fully Editable**: All fields can be manually edited even after API lookup

## Layout

**Left Panel:**
- Title with year
- Series information (name and number)
- Author
- Artist (for comics/graphic novels)
- Publisher
- Format and page count
- Personal notes

**Right Panel:**
- Cover image preview
- Manual cover upload button
- Scrollable book description

**Bottom:**
- Searchable list of all books in library

## Installation

### For Development

1. Install Python 3.9 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python library_app.py
   ```

### Creating an Executable

To package as a standalone executable that doesn't require Python:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   python build_exe.py
   ```

3. The executable will be created in the `dist` folder

## Usage

### Adding a Book

1. Enter an ISBN in the ISBN field
2. Click "Look Up" to fetch details from Open Library
3. Review and edit any fields as needed
4. Add series information if applicable
5. Click "Add New Book"

### Lending a Book

1. Select a book from the list
2. Click "Loan Out"
3. Enter the borrower's name
4. The book is automatically tracked with a 30-day due date

### Returning a Book

1. Go to the "Current Loans" or "⚠ Overdue" tab
2. Select the loan
3. Click "Mark as Returned"

### Viewing Overdue Books

Books on loan for more than 30 days automatically appear in the "⚠ Overdue" tab with the number of days overdue.

## Data Storage

- **Database**: SQLite database (`library.db`)
- **Cover Images**: Stored in `covers/` folder
- Both are created automatically in the application directory

## Technical Details

- **GUI**: tkinter (built into Python)
- **Database**: SQLite3
- **API**: Open Library Books API
- **Images**: PIL/Pillow for image handling

## Notes

- All book fields are editable even after auto-fill from ISBN lookup
- ISBN field is optional (books can be added manually without ISBN)
- Series information must be entered manually as it's not reliably available from the API
- Artist field must be entered manually (ISBN lookup provides authors only)
- Cover images are downloaded once and stored locally, or can be uploaded manually
- All notifications are silent (no system beeps)
