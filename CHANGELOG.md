# Version 1.1 Update Summary

## Changes Made

### Bug Fixes

1. **Cover Image Clearing**: Fixed issue where old cover images would persist when looking up a new book that doesn't have a cover
   - Now clears all fields (including cover) before populating with new ISBN lookup data
   - Ensures clean slate for each lookup

### New Features

2. **Advanced Search Tab**: Added dedicated "Search" tab with multiple search criteria
   - Search by ISBN, Title, Series, Author, or Publisher
   - Can use any combination of criteria
   - Case-insensitive searching
   - Partial matching (typo-tolerant) - e.g., "potter" finds "Harry Potter"
   - Results displayed in sortable table format
   - Double-click or "View Selected Book" button to load book details
   - "Show All Books" button to view entire library
   - "Clear Criteria" to reset search fields

3. **Improved Sorting**: All book lists now alphabetised case-insensitively
   - Library list alphabetised
   - Search results alphabetised
   - Uppercase/lowercase doesn't affect sort order

### Technical Improvements

4. **Database Enhancements**:
   - Added `advanced_search()` function for multi-criteria searches
   - All ORDER BY clauses now use `COLLATE NOCASE` for proper alphabetisation
   - Flexible query building based on provided criteria

5. **Build Script Fix**:
   - Fixed PyInstaller PATH issue
   - Now uses `python -m PyInstaller` instead of direct command
   - Should work on all systems regardless of PATH configuration

## Files Modified

- `library_app.py`: Added search tab UI and functionality, fixed cover clearing
- `database.py`: Added advanced_search() function, improved sorting
- `build_exe.py`: Fixed PyInstaller invocation
- `README.md`: Updated feature list
- `QUICK_START.md`: Added search documentation

## Testing Checklist

- [ ] ISBN lookup clears old cover images
- [ ] Search tab accessible from notebook
- [ ] Search by ISBN works
- [ ] Search by Title works (case-insensitive)
- [ ] Search by Series works
- [ ] Search by Author works
- [ ] Search by Publisher works
- [ ] Partial matching works (typo tolerance)
- [ ] Multiple criteria combine with AND logic
- [ ] "Show All Books" displays entire library
- [ ] Double-click loads book and switches to Library tab
- [ ] "View Selected Book" button works
- [ ] Results sorted alphabetically
- [ ] Build script creates executable successfully

## User-Facing Changes

**For Callum:**
- New "Search" tab in the main window
- Can now search by series name
- Searches are more forgiving (don't need exact spelling)
- Capital letters no longer matter in searches
- All book lists now properly alphabetised
