# Quick Start Guide - Callum's Library App

## For Rowan (Testing & Building)

### Step 1: Install Dependencies
```bash
cd "C:\Users\Rowan\Git\Callum's Library App"
pip install -r requirements.txt
```

### Step 2: Test Components
```bash
python test_components.py
```
This will verify that:
- Database creation works
- ISBN lookup works (requires internet)
- All GUI modules are available

### Step 3: Run the Application
```bash
python library_app.py
```

### Step 4: Build Executable for Callum
```bash
python build_exe.py
```

The executable will be created at: `dist/CallumsLibrary.exe`

You can then copy this single file to Callum - no Python installation required!

---

## For Callum (Using the Application)

### First Time Setup
1. Double-click `CallumsLibrary.exe`
2. The application will create:
   - `library.db` (your database)
   - `covers/` folder (for book cover images)

### Adding Books by ISBN

1. **Enter ISBN**: Type or paste the ISBN in the ISBN field
   - Works with ISBN-10 or ISBN-13
   - Hyphens optional (e.g., both "9780451526538" and "978-0-451-52653-8" work)

2. **Click "Look Up"**: The app will fetch:
   - Title and publication year
   - Author(s)
   - Publisher
   - Page count
   - Description
   - Cover image

3. **Review & Edit**: 
   - All fields are editable! Fix any errors or add missing info
   - Add series information manually (e.g., "Harry Potter" series, book #1)

4. **Click "Add New Book"**: Saves to your library

### Adding Books Manually (Without ISBN)

1. Click "Add New Book" (with ISBN field empty)
2. Fill in whatever details you have
3. Click "Save Changes"

### Lending Books

1. **Select a book** from the list at the bottom
2. **Click "Loan Out"**
3. **Enter borrower's name**
4. The book is tracked with a 30-day due date

### Returning Books

Go to the **"Current Loans"** tab:
1. Select the loan from the list
2. Click "Mark as Returned"

### Finding Overdue Books

The **"⚠ Overdue"** tab shows:
- All books on loan for more than 30 days
- How many days overdue each book is
- Who has the book

### Searching Your Library

**Quick Search (Library Tab):**
- Use the search box at the bottom of the Library tab
- Searches: Title, Author, and ISBN
- Updates as you type

**Advanced Search (Search Tab):**
- Go to the "Search" tab for more powerful searching
- Search by any combination of:
  - ISBN
  - Title
  - Series name
  - Author
  - Publisher
- Case-insensitive and typo-tolerant (partial matches work)
- Example: Searching "potter" in Title will find "Harry Potter"
- Click "Show All Books" to see your entire library
- Double-click any result to view the book details
- Results are always alphabetised by title

### Editing Book Details

1. Select a book from the list
2. Edit any fields (all are editable!)
3. Click "Save Changes"

### Deleting Books

1. Select a book
2. Click "Delete Book"
3. Confirm deletion

---

## Tips & Notes

### ISBN Sources
- Look on the back cover near the barcode
- Check the copyright page inside the book
- For comics, may be on the first page or inside back cover

### Series Information
- Not auto-filled (API doesn't reliably provide this)
- Add manually: Series name + book number
- Example: "The Lord of the Rings" #1

### Cover Images
- Downloaded automatically during ISBN lookup
- Stored in `covers/` folder
- Won't download twice for the same ISBN

### Comics & Graphic Novels
- Use the Format dropdown to mark as "Comic" or "Graphic Novel"
- ISBN lookup works for most modern comics
- Older comics may need manual entry

### Backing Up Your Library
Your entire library is stored in:
- `library.db` (database file)
- `covers/` (folder with images)

To backup, simply copy these to a safe location!

---

## Troubleshooting

### "ISBN not found"
- Check the ISBN is correct (no typos)
- Some older books aren't in the Open Library database
- Solution: Add the book manually

### Application Won't Start
- Make sure `library.db` file isn't open in another program
- Try moving the .exe to a new folder

### Cover Images Not Showing
- Requires internet connection during ISBN lookup
- Some books don't have cover images available
- Not essential - everything else works fine

### Slow ISBN Lookup
- The Open Library API can sometimes be slow
- Wait up to 10 seconds for a response
- The application will show a wait cursor

---

## Questions?

Contact Rowan if you run into any issues!
