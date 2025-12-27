"""
Callum's Library Management System
Main GUI Application
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from PIL import Image, ImageTk
from pathlib import Path
import shutil
import database
import isbn_lookup


class SilentDialog:
    """Custom dialog boxes that don't make system beeps"""
    
    @staticmethod
    def showinfo(title, message, parent=None):
        """Show info dialog without beep"""
        dialog = tk.Toplevel(parent) if parent else tk.Toplevel()
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        if parent:
            dialog.transient(parent)
            dialog.grab_set()
        
        # Centre on parent
        if parent:
            dialog.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text=message, wraplength=350, justify='left').pack(pady=20, padx=20)
        ttk.Button(dialog, text="OK", command=dialog.destroy, width=10).pack(pady=10)
        
        dialog.focus_set()
        dialog.wait_window()
    
    @staticmethod
    def showwarning(title, message, parent=None):
        """Show warning dialog without beep"""
        dialog = tk.Toplevel(parent) if parent else tk.Toplevel()
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        if parent:
            dialog.transient(parent)
            dialog.grab_set()
        
        if parent:
            dialog.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text=message, wraplength=350, justify='left').pack(pady=20, padx=20)
        ttk.Button(dialog, text="OK", command=dialog.destroy, width=10).pack(pady=10)
        
        dialog.focus_set()
        dialog.wait_window()
    
    @staticmethod
    def showerror(title, message, parent=None):
        """Show error dialog without beep"""
        dialog = tk.Toplevel(parent) if parent else tk.Toplevel()
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        if parent:
            dialog.transient(parent)
            dialog.grab_set()
        
        if parent:
            dialog.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text=message, wraplength=350, justify='left', foreground='red').pack(pady=20, padx=20)
        ttk.Button(dialog, text="OK", command=dialog.destroy, width=10).pack(pady=10)
        
        dialog.focus_set()
        dialog.wait_window()
    
    @staticmethod
    def askyesno(title, message, parent=None):
        """Show yes/no dialog without beep"""
        dialog = tk.Toplevel(parent) if parent else tk.Toplevel()
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        if parent:
            dialog.transient(parent)
            dialog.grab_set()
        
        if parent:
            dialog.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
        
        result = [False]
        
        ttk.Label(dialog, text=message, wraplength=350, justify='left').pack(pady=20, padx=20)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def on_yes():
            result[0] = True
            dialog.destroy()
        
        def on_no():
            result[0] = False
            dialog.destroy()
        
        ttk.Button(button_frame, text="Yes", command=on_yes, width=10).pack(side='left', padx=5)
        ttk.Button(button_frame, text="No", command=on_no, width=10).pack(side='left', padx=5)
        
        dialog.focus_set()
        dialog.wait_window()
        
        return result[0]


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Callum's Library")
        self.root.geometry("1000x700")
        
        # Initialise database
        database.init_database()
        
        # Current book being viewed/edited
        self.current_book_id = None
        self.cover_image = None
        
        # Debounce timer for listbox selection
        self.selection_timer = None
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_library_tab()
        self.create_search_tab()
        self.create_loans_tab()
        self.create_overdue_tab()
        
        # Load initial data
        self.refresh_library_list()
        self.refresh_loans_list()
        self.refresh_overdue_list()
    
    def create_library_tab(self):
        """Main library tab for browsing and adding books"""
        library_frame = ttk.Frame(self.notebook)
        self.notebook.add(library_frame, text='Library')
        
        # Top section: ISBN lookup and add book
        top_frame = ttk.Frame(library_frame)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="ISBN:").pack(side='left', padx=5)
        self.isbn_entry = ttk.Entry(top_frame, width=20)
        self.isbn_entry.pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="Look Up", command=self.lookup_isbn).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Add New Book", command=self.add_new_book).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Clear", command=self.clear_form).pack(side='left', padx=5)
        
        # Main content area
        content_frame = ttk.Frame(library_frame)
        content_frame.pack(fill='both', expand=True, padx=10)
        
        # Left side: Book details
        left_frame = ttk.Frame(content_frame, width=500)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Title and Year
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(fill='x', pady=5)
        ttk.Label(title_frame, text="Title:").pack(anchor='w')
        self.title_entry = ttk.Entry(title_frame, font=('TkDefaultFont', 10, 'bold'))
        self.title_entry.pack(fill='x')
        
        year_frame = ttk.Frame(title_frame)
        year_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(year_frame, text="Year:").pack(side='left')
        self.year_entry = ttk.Entry(year_frame, width=10)
        self.year_entry.pack(side='left', padx=5)
        
        # Series info
        series_frame = ttk.LabelFrame(left_frame, text="Series Information", padding=5)
        series_frame.pack(fill='x', pady=5)
        
        series_name_frame = ttk.Frame(series_frame)
        series_name_frame.pack(fill='x')
        ttk.Label(series_name_frame, text="Series:").pack(side='left')
        self.series_name_entry = ttk.Entry(series_name_frame)
        self.series_name_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        ttk.Label(series_name_frame, text="#:").pack(side='left')
        self.series_number_entry = ttk.Entry(series_name_frame, width=5)
        self.series_number_entry.pack(side='left', padx=5)
        
        # Author and Artist
        author_frame = ttk.Frame(left_frame)
        author_frame.pack(fill='x', pady=5)
        ttk.Label(author_frame, text="Author:").pack(anchor='w')
        self.author_entry = ttk.Entry(author_frame)
        self.author_entry.pack(fill='x')
        
        artist_frame = ttk.Frame(left_frame)
        artist_frame.pack(fill='x', pady=5)
        ttk.Label(artist_frame, text="Artist:").pack(anchor='w')
        self.artist_entry = ttk.Entry(artist_frame)
        self.artist_entry.pack(fill='x')
        
        # Publisher
        publisher_frame = ttk.Frame(left_frame)
        publisher_frame.pack(fill='x', pady=5)
        ttk.Label(publisher_frame, text="Publisher:").pack(anchor='w')
        self.publisher_entry = ttk.Entry(publisher_frame)
        self.publisher_entry.pack(fill='x')
        
        # Format and Page Count
        meta_frame = ttk.Frame(left_frame)
        meta_frame.pack(fill='x', pady=5)
        
        ttk.Label(meta_frame, text="Format:").pack(side='left')
        self.format_var = tk.StringVar(value='Book')
        format_combo = ttk.Combobox(meta_frame, textvariable=self.format_var, 
                                     values=['Book', 'Comic', 'Graphic Novel', 'Magazine'], 
                                     width=15, state='readonly')
        format_combo.pack(side='left', padx=5)
        
        ttk.Label(meta_frame, text="Pages:").pack(side='left', padx=(20, 0))
        self.page_count_entry = ttk.Entry(meta_frame, width=8)
        self.page_count_entry.pack(side='left', padx=5)
        
        # Notes
        notes_frame = ttk.LabelFrame(left_frame, text="Notes", padding=5)
        notes_frame.pack(fill='both', expand=True, pady=5)
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=4)
        self.notes_text.pack(fill='both', expand=True)
        
        # Save and action buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill='x', pady=10)
        ttk.Button(button_frame, text="Save Changes", command=self.save_book).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Loan Out", command=self.loan_out_book).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Book", command=self.delete_book).pack(side='left', padx=5)
        
        # Right side: Cover and Description
        right_frame = ttk.Frame(content_frame, width=350)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Cover image with upload button
        cover_container = ttk.Frame(right_frame)
        cover_container.pack(pady=10)
        
        self.cover_label = ttk.Label(cover_container, text="No cover image")
        self.cover_label.pack()
        
        ttk.Button(cover_container, text="Upload Cover Image", 
                   command=self.upload_cover_image).pack(pady=5)
        
        # Description
        desc_frame = ttk.LabelFrame(right_frame, text="Description", padding=5)
        desc_frame.pack(fill='both', expand=True)
        self.description_text = scrolledtext.ScrolledText(desc_frame, wrap='word', height=10)
        self.description_text.pack(fill='both', expand=True)
        
        # Bottom section: Book list
        list_frame = ttk.LabelFrame(library_frame, text="All Books", padding=5)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Search box
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.refresh_library_list())
        
        # Book list with debounced selection
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side='right', fill='y')
        
        self.book_list = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, height=8)
        self.book_list.pack(side='left', fill='both', expand=True)
        list_scroll.config(command=self.book_list.yview)
        
        self.book_list.bind('<<ListboxSelect>>', self.on_book_selected_debounced)
    
    def create_search_tab(self):
        """Dedicated search tab with multiple criteria"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text='Search')
        
        # Search criteria frame
        criteria_frame = ttk.LabelFrame(search_frame, text="Search Criteria", padding=10)
        criteria_frame.pack(fill='x', padx=10, pady=10)
        
        # ISBN search
        isbn_row = ttk.Frame(criteria_frame)
        isbn_row.pack(fill='x', pady=5)
        ttk.Label(isbn_row, text="ISBN:", width=12).pack(side='left')
        self.search_isbn_entry = ttk.Entry(isbn_row)
        self.search_isbn_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Title search
        title_row = ttk.Frame(criteria_frame)
        title_row.pack(fill='x', pady=5)
        ttk.Label(title_row, text="Title:", width=12).pack(side='left')
        self.search_title_entry = ttk.Entry(title_row)
        self.search_title_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Series search
        series_row = ttk.Frame(criteria_frame)
        series_row.pack(fill='x', pady=5)
        ttk.Label(series_row, text="Series:", width=12).pack(side='left')
        self.search_series_entry = ttk.Entry(series_row)
        self.search_series_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Author search
        author_row = ttk.Frame(criteria_frame)
        author_row.pack(fill='x', pady=5)
        ttk.Label(author_row, text="Author:", width=12).pack(side='left')
        self.search_author_entry = ttk.Entry(author_row)
        self.search_author_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Artist search
        artist_row = ttk.Frame(criteria_frame)
        artist_row.pack(fill='x', pady=5)
        ttk.Label(artist_row, text="Artist:", width=12).pack(side='left')
        self.search_artist_entry = ttk.Entry(artist_row)
        self.search_artist_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Publisher search
        publisher_row = ttk.Frame(criteria_frame)
        publisher_row.pack(fill='x', pady=5)
        ttk.Label(publisher_row, text="Publisher:", width=12).pack(side='left')
        self.search_publisher_entry = ttk.Entry(publisher_row)
        self.search_publisher_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Search buttons
        button_row = ttk.Frame(criteria_frame)
        button_row.pack(fill='x', pady=10)
        ttk.Button(button_row, text="Search", command=self.do_advanced_search).pack(side='left', padx=5)
        ttk.Button(button_row, text="Clear Criteria", command=self.clear_search_criteria).pack(side='left', padx=5)
        ttk.Button(button_row, text="Show All Books", command=self.show_all_in_search).pack(side='left', padx=5)
        
        # Results info
        self.search_results_label = ttk.Label(search_frame, text="Enter search criteria and click Search")
        self.search_results_label.pack(pady=5)
        
        # Results treeview
        results_frame = ttk.Frame(search_frame)
        results_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(results_frame, orient='vertical')
        v_scroll.pack(side='right', fill='y')
        
        h_scroll = ttk.Scrollbar(results_frame, orient='horizontal')
        h_scroll.pack(side='bottom', fill='x')
        
        # Treeview
        columns = ('Title', 'Author', 'Artist', 'Series', 'Publisher', 'Year')
        self.search_results_tree = ttk.Treeview(results_frame, columns=columns, show='tree headings',
                                                yscrollcommand=v_scroll.set,
                                                xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=self.search_results_tree.yview)
        h_scroll.config(command=self.search_results_tree.xview)
        
        self.search_results_tree.heading('#0', text='ID')
        self.search_results_tree.column('#0', width=50)
        
        self.search_results_tree.heading('Title', text='Title')
        self.search_results_tree.column('Title', width=200)
        
        self.search_results_tree.heading('Author', text='Author')
        self.search_results_tree.column('Author', width=130)
        
        self.search_results_tree.heading('Artist', text='Artist')
        self.search_results_tree.column('Artist', width=130)
        
        self.search_results_tree.heading('Series', text='Series')
        self.search_results_tree.column('Series', width=130)
        
        self.search_results_tree.heading('Publisher', text='Publisher')
        self.search_results_tree.column('Publisher', width=130)
        
        self.search_results_tree.heading('Year', text='Year')
        self.search_results_tree.column('Year', width=60)
        
        self.search_results_tree.pack(side='left', fill='both', expand=True)
        
        # Bind double-click to load book
        self.search_results_tree.bind('<Double-Button-1>', self.load_book_from_search)
        
        # Button to load selected book
        load_button_frame = ttk.Frame(search_frame)
        load_button_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(load_button_frame, text="View Selected Book", 
                  command=self.view_book_from_search).pack(side='left', padx=5)
    
    def create_loans_tab(self):
        """Tab for viewing all active loans"""
        loans_frame = ttk.Frame(self.notebook)
        self.notebook.add(loans_frame, text='Current Loans')
        
        # Treeview for loans
        columns = ('Title', 'Author', 'Borrower', 'Loaned', 'Due')
        self.loans_tree = ttk.Treeview(loans_frame, columns=columns, show='tree headings')
        
        self.loans_tree.heading('#0', text='ID')
        self.loans_tree.column('#0', width=50)
        
        for col in columns:
            self.loans_tree.heading(col, text=col)
            if col == 'Title':
                self.loans_tree.column(col, width=250)
            elif col == 'Author':
                self.loans_tree.column(col, width=150)
            else:
                self.loans_tree.column(col, width=120)
        
        self.loans_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Return button
        button_frame = ttk.Frame(loans_frame)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(button_frame, text="Mark as Returned", 
                   command=self.return_selected_loan).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh", 
                   command=self.refresh_loans_list).pack(side='left', padx=5)
    
    def create_overdue_tab(self):
        """Tab for viewing overdue books"""
        overdue_frame = ttk.Frame(self.notebook)
        self.notebook.add(overdue_frame, text='⚠ Overdue')
        
        # Warning label
        warning_label = ttk.Label(overdue_frame, 
                                  text="Books on loan for more than 30 days", 
                                  foreground='red',
                                  font=('TkDefaultFont', 10, 'bold'))
        warning_label.pack(pady=10)
        
        # Treeview for overdue loans
        columns = ('Title', 'Author', 'Borrower', 'Loaned', 'Due', 'Days Overdue')
        self.overdue_tree = ttk.Treeview(overdue_frame, columns=columns, show='tree headings')
        
        self.overdue_tree.heading('#0', text='ID')
        self.overdue_tree.column('#0', width=50)
        
        for col in columns:
            self.overdue_tree.heading(col, text=col)
            if col == 'Title':
                self.overdue_tree.column(col, width=200)
            elif col in ['Author', 'Borrower']:
                self.overdue_tree.column(col, width=130)
            else:
                self.overdue_tree.column(col, width=100)
        
        self.overdue_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Return button
        button_frame = ttk.Frame(overdue_frame)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(button_frame, text="Mark as Returned", 
                   command=self.return_selected_overdue).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh", 
                   command=self.refresh_overdue_list).pack(side='left', padx=5)
    
    def upload_cover_image(self):
        """Allow manual upload of cover image"""
        if not self.current_book_id:
            SilentDialog.showwarning("No Book Selected", 
                                    "Please select or add a book before uploading a cover image",
                                    self.root)
            return
        
        # Open file picker
        file_path = filedialog.askopenfilename(
            parent=self.root,
            title="Select Cover Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Create covers directory if it doesn't exist
            covers_dir = Path(__file__).parent / "covers"
            covers_dir.mkdir(exist_ok=True)
            
            # Generate filename based on book ID
            file_ext = Path(file_path).suffix
            new_filename = f"manual_{self.current_book_id}{file_ext}"
            new_path = covers_dir / new_filename
            
            # Copy image to covers directory
            shutil.copy2(file_path, new_path)
            
            # Update database
            database.update_book(self.current_book_id, cover_path=str(new_path))
            
            # Display the cover
            self.display_cover(new_path)
            
            SilentDialog.showinfo("Success", "Cover image uploaded successfully!", self.root)
            
        except Exception as e:
            SilentDialog.showerror("Error", f"Failed to upload cover image: {e}", self.root)
    
    def lookup_isbn(self):
        """Look up book information by ISBN"""
        isbn = self.isbn_entry.get().strip()
        if not isbn:
            SilentDialog.showwarning("No ISBN", "Please enter an ISBN", self.root)
            return
        
        # Clear all fields first
        self.clear_form()
        self.isbn_entry.insert(0, isbn)
        
        # Show loading message
        self.root.config(cursor="wait")
        self.root.update()
        
        try:
            result = isbn_lookup.lookup_isbn(isbn)
            
            if result:
                # Fill in the fields
                self.title_entry.delete(0, 'end')
                self.title_entry.insert(0, result.get('title', ''))
                
                self.year_entry.delete(0, 'end')
                self.year_entry.insert(0, result.get('year', ''))
                
                self.author_entry.delete(0, 'end')
                self.author_entry.insert(0, result.get('author', ''))
                
                self.publisher_entry.delete(0, 'end')
                self.publisher_entry.insert(0, result.get('publisher', ''))
                
                self.page_count_entry.delete(0, 'end')
                if result.get('page_count'):
                    self.page_count_entry.insert(0, str(result['page_count']))
                
                self.description_text.delete('1.0', 'end')
                self.description_text.insert('1.0', result.get('description', ''))
                
                # Download cover if available
                if result.get('cover_url'):
                    cover_path = isbn_lookup.get_cover_path(isbn)
                    if isbn_lookup.download_cover(result['cover_url'], cover_path):
                        self.display_cover(cover_path)
                
                SilentDialog.showinfo("Success", "Book information loaded! Please review and save.", self.root)
            else:
                SilentDialog.showwarning("Not Found", 
                                       "ISBN not found in Open Library. You can still add the book manually.",
                                       self.root)
        finally:
            self.root.config(cursor="")
    
    def display_cover(self, image_path):
        """Display a cover image"""
        try:
            img = Image.open(image_path)
            img.thumbnail((200, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.cover_image = photo
            self.cover_label.config(image=photo, text='')
        except Exception as e:
            print(f"Error displaying cover: {e}")
            self.cover_label.config(text="Cover unavailable")
    
    def clear_form(self):
        """Clear all form fields"""
        self.current_book_id = None
        self.isbn_entry.delete(0, 'end')
        self.title_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')
        self.author_entry.delete(0, 'end')
        self.artist_entry.delete(0, 'end')
        self.publisher_entry.delete(0, 'end')
        self.page_count_entry.delete(0, 'end')
        self.series_name_entry.delete(0, 'end')
        self.series_number_entry.delete(0, 'end')
        self.notes_text.delete('1.0', 'end')
        self.description_text.delete('1.0', 'end')
        self.format_var.set('Book')
        self.cover_label.config(image='', text='No cover image')
        self.cover_image = None
    
    def add_new_book(self):
        """Add a new book to the database"""
        isbn = self.isbn_entry.get().strip()
        title = self.title_entry.get().strip()
        
        if not title:
            SilentDialog.showwarning("Missing Information", "Title is required", self.root)
            return
        
        try:
            year = self.year_entry.get().strip()
            author = self.author_entry.get().strip()
            artist = self.artist_entry.get().strip()
            publisher = self.publisher_entry.get().strip()
            
            page_count = self.page_count_entry.get().strip()
            page_count = int(page_count) if page_count else None
            
            description = self.description_text.get('1.0', 'end-1c').strip()
            series_name = self.series_name_entry.get().strip() or None
            
            series_number = self.series_number_entry.get().strip()
            series_number = int(series_number) if series_number else None
            
            format_type = self.format_var.get()
            notes = self.notes_text.get('1.0', 'end-1c').strip()
            
            # Get cover path if exists
            cover_path = None
            if isbn:
                potential_cover = isbn_lookup.get_cover_path(isbn)
                if potential_cover.exists():
                    cover_path = str(potential_cover)
            
            # Add to database
            book_id = database.add_book(
                isbn=isbn or None,
                title=title,
                year=year,
                author=author,
                artist=artist or None,
                publisher=publisher,
                page_count=page_count,
                description=description,
                series_name=series_name,
                series_number=series_number,
                format_type=format_type,
                cover_path=cover_path,
                notes=notes
            )
            
            SilentDialog.showinfo("Success", "Book added to library!", self.root)
            self.clear_form()
            self.refresh_library_list()
            
        except ValueError as e:
            SilentDialog.showerror("Error", str(e), self.root)
        except Exception as e:
            SilentDialog.showerror("Error", f"Failed to add book: {e}", self.root)
    
    def save_book(self):
        """Save changes to current book"""
        if not self.current_book_id:
            SilentDialog.showwarning("No Book Selected", "Please select a book to update", self.root)
            return
        
        try:
            updates = {
                'isbn': self.isbn_entry.get().strip() or None,
                'title': self.title_entry.get().strip(),
                'year': self.year_entry.get().strip(),
                'author': self.author_entry.get().strip(),
                'artist': self.artist_entry.get().strip() or None,
                'publisher': self.publisher_entry.get().strip(),
                'description': self.description_text.get('1.0', 'end-1c').strip(),
                'series_name': self.series_name_entry.get().strip() or None,
                'format': self.format_var.get(),
                'notes': self.notes_text.get('1.0', 'end-1c').strip()
            }
            
            page_count = self.page_count_entry.get().strip()
            updates['page_count'] = int(page_count) if page_count else None
            
            series_number = self.series_number_entry.get().strip()
            updates['series_number'] = int(series_number) if series_number else None
            
            database.update_book(self.current_book_id, **updates)
            
            SilentDialog.showinfo("Success", "Book updated!", self.root)
            self.refresh_library_list()
            
        except Exception as e:
            SilentDialog.showerror("Error", f"Failed to save changes: {e}", self.root)
    
    def delete_book(self):
        """Delete the current book"""
        if not self.current_book_id:
            SilentDialog.showwarning("No Book Selected", "Please select a book to delete", self.root)
            return
        
        title = self.title_entry.get()
        if not SilentDialog.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete '{title}'?",
                                   self.root):
            return
        
        try:
            database.delete_book(self.current_book_id)
            SilentDialog.showinfo("Success", "Book deleted", self.root)
            self.clear_form()
            self.refresh_library_list()
        except Exception as e:
            SilentDialog.showerror("Error", f"Failed to delete book: {e}", self.root)
    
    def loan_out_book(self):
        """Loan out the current book"""
        if not self.current_book_id:
            SilentDialog.showwarning("No Book Selected", "Please select a book to loan out", self.root)
            return
        
        current_loan = database.get_current_loan(self.current_book_id)
        if current_loan:
            SilentDialog.showwarning("Already On Loan", 
                                   f"This book is currently loaned to {current_loan['borrower_name']}",
                                   self.root)
            return
        
        # Dialog for borrower name
        dialog = tk.Toplevel(self.root)
        dialog.title("Loan Book")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Borrower Name:").pack(pady=10)
        borrower_entry = ttk.Entry(dialog, width=30)
        borrower_entry.pack(pady=5)
        borrower_entry.focus()
        
        def do_loan():
            borrower = borrower_entry.get().strip()
            if not borrower:
                SilentDialog.showwarning("Missing Information", "Please enter borrower name", dialog)
                return
            
            try:
                database.loan_book(self.current_book_id, borrower)
                SilentDialog.showinfo("Success", f"Book loaned to {borrower}", self.root)
                dialog.destroy()
                self.refresh_loans_list()
                self.refresh_overdue_list()
            except Exception as e:
                SilentDialog.showerror("Error", f"Failed to record loan: {e}", dialog)
        
        ttk.Button(dialog, text="Loan Out", command=do_loan).pack(pady=10)
        borrower_entry.bind('<Return>', lambda e: do_loan())
    
    def on_book_selected_debounced(self, event):
        """Debounced book selection handler to prevent juddering"""
        # Cancel any existing timer
        if self.selection_timer:
            self.root.after_cancel(self.selection_timer)
        
        # Set new timer for 300ms delay
        self.selection_timer = self.root.after(300, self.on_book_selected, event)
    
    def on_book_selected(self, event):
        """Handle book selection from list"""
        selection = self.book_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        book_info = self.book_list.get(index)
        
        try:
            book_id = int(book_info.split(':')[0])
            self.load_book(book_id)
        except:
            pass
    
    def load_book(self, book_id):
        """Load a book's details into the form"""
        book = database.get_book(book_id)
        if not book:
            return
        
        self.current_book_id = book_id
        
        # Fill in fields
        self.isbn_entry.delete(0, 'end')
        if book['isbn']:
            self.isbn_entry.insert(0, book['isbn'])
        
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, book['title'] or '')
        
        self.year_entry.delete(0, 'end')
        self.year_entry.insert(0, book['year'] or '')
        
        self.author_entry.delete(0, 'end')
        self.author_entry.insert(0, book['author'] or '')
        
        self.artist_entry.delete(0, 'end')
        self.artist_entry.insert(0, book.get('artist', '') or '')
        
        self.publisher_entry.delete(0, 'end')
        self.publisher_entry.insert(0, book['publisher'] or '')
        
        self.page_count_entry.delete(0, 'end')
        if book['page_count']:
            self.page_count_entry.insert(0, str(book['page_count']))
        
        self.series_name_entry.delete(0, 'end')
        self.series_name_entry.insert(0, book['series_name'] or '')
        
        self.series_number_entry.delete(0, 'end')
        if book['series_number']:
            self.series_number_entry.insert(0, str(book['series_number']))
        
        self.format_var.set(book['format'] or 'Book')
        
        self.description_text.delete('1.0', 'end')
        self.description_text.insert('1.0', book['description'] or '')
        
        self.notes_text.delete('1.0', 'end')
        self.notes_text.insert('1.0', book['notes'] or '')
        
        # Load cover if exists
        if book['cover_path'] and Path(book['cover_path']).exists():
            self.display_cover(book['cover_path'])
        else:
            self.cover_label.config(image='', text='No cover image')
            self.cover_image = None
    
    def refresh_library_list(self):
        """Refresh the library book list"""
        self.book_list.delete(0, 'end')
        
        query = self.search_entry.get().strip()
        
        if query:
            books = database.search_books(query)
        else:
            books = database.get_all_books()
        
        for book in books:
            display = f"{book['id']}: {book['title']}"
            if book['author']:
                display += f" by {book['author']}"
            self.book_list.insert('end', display)
    
    def refresh_loans_list(self):
        """Refresh the current loans list"""
        for item in self.loans_tree.get_children():
            self.loans_tree.delete(item)
        
        loans = database.get_all_loans()
        
        for loan in loans:
            loaned = loan['date_loaned'][:10]
            due = loan['date_due'][:10]
            
            self.loans_tree.insert('', 'end', text=str(loan['id']),
                                   values=(loan['title'], loan['author'], 
                                          loan['borrower_name'], loaned, due))
    
    def refresh_overdue_list(self):
        """Refresh the overdue loans list"""
        for item in self.overdue_tree.get_children():
            self.overdue_tree.delete(item)
        
        loans = database.get_overdue_loans()
        
        from datetime import datetime
        now = datetime.now()
        
        for loan in loans:
            loaned = loan['date_loaned'][:10]
            due = loan['date_due'][:10]
            
            due_date = datetime.fromisoformat(loan['date_due'])
            days_overdue = (now - due_date).days
            
            self.overdue_tree.insert('', 'end', text=str(loan['id']),
                                     values=(loan['title'], loan['author'],
                                            loan['borrower_name'], loaned, due,
                                            str(days_overdue)))
    
    def return_selected_loan(self):
        """Mark selected loan as returned"""
        selection = self.loans_tree.selection()
        if not selection:
            SilentDialog.showwarning("No Selection", "Please select a loan to return", self.root)
            return
        
        loan_id = int(self.loans_tree.item(selection[0])['text'])
        
        try:
            database.return_book(loan_id)
            SilentDialog.showinfo("Success", "Book marked as returned", self.root)
            self.refresh_loans_list()
            self.refresh_overdue_list()
        except Exception as e:
            SilentDialog.showerror("Error", f"Failed to return book: {e}", self.root)
    
    def return_selected_overdue(self):
        """Mark selected overdue loan as returned"""
        selection = self.overdue_tree.selection()
        if not selection:
            SilentDialog.showwarning("No Selection", "Please select a loan to return", self.root)
            return
        
        loan_id = int(self.overdue_tree.item(selection[0])['text'])
        
        try:
            database.return_book(loan_id)
            SilentDialog.showinfo("Success", "Book marked as returned", self.root)
            self.refresh_loans_list()
            self.refresh_overdue_list()
        except Exception as e:
            SilentDialog.showerror("Error", f"Failed to return book: {e}", self.root)
    
    def do_advanced_search(self):
        """Perform advanced search with multiple criteria"""
        isbn = self.search_isbn_entry.get().strip()
        title = self.search_title_entry.get().strip()
        series = self.search_series_entry.get().strip()
        author = self.search_author_entry.get().strip()
        artist = self.search_artist_entry.get().strip()
        publisher = self.search_publisher_entry.get().strip()
        
        if not any([isbn, title, series, author, artist, publisher]):
            SilentDialog.showinfo("No Criteria", "Please enter at least one search criterion", self.root)
            return
        
        results = database.advanced_search(isbn=isbn or None, 
                                          title=title or None,
                                          series=series or None, 
                                          author=author or None,
                                          artist=artist or None,
                                          publisher=publisher or None)
        
        self.display_search_results(results)
    
    def clear_search_criteria(self):
        """Clear all search criteria fields"""
        self.search_isbn_entry.delete(0, 'end')
        self.search_title_entry.delete(0, 'end')
        self.search_series_entry.delete(0, 'end')
        self.search_author_entry.delete(0, 'end')
        self.search_artist_entry.delete(0, 'end')
        self.search_publisher_entry.delete(0, 'end')
        
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        
        self.search_results_label.config(text="Enter search criteria and click Search")
    
    def show_all_in_search(self):
        """Show all books in search results"""
        results = database.get_all_books()
        self.display_search_results(results)
    
    def display_search_results(self, results):
        """Display search results in the treeview"""
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        
        for book in results:
            series_info = ''
            if book['series_name']:
                series_info = book['series_name']
                if book['series_number']:
                    series_info += f" #{book['series_number']}"
            
            self.search_results_tree.insert('', 'end', text=str(book['id']),
                                           values=(book['title'] or '',
                                                  book['author'] or '',
                                                  book.get('artist', '') or '',
                                                  series_info,
                                                  book['publisher'] or '',
                                                  book['year'] or ''))
        
        count = len(results)
        if count == 0:
            self.search_results_label.config(text="No books found matching criteria")
        elif count == 1:
            self.search_results_label.config(text="Found 1 book")
        else:
            self.search_results_label.config(text=f"Found {count} books")
    
    def load_book_from_search(self, event):
        """Load book when double-clicked in search results"""
        selection = self.search_results_tree.selection()
        if not selection:
            return
        
        book_id = int(self.search_results_tree.item(selection[0])['text'])
        self.load_book(book_id)
        self.notebook.select(0)
    
    def view_book_from_search(self):
        """Load selected book from search results via button"""
        selection = self.search_results_tree.selection()
        if not selection:
            SilentDialog.showwarning("No Selection", "Please select a book to view", self.root)
            return
        
        book_id = int(self.search_results_tree.item(selection[0])['text'])
        self.load_book(book_id)
        self.notebook.select(0)


def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
