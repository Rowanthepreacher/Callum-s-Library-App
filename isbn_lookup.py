"""
ISBN lookup module using Open Library API
"""

import requests
from pathlib import Path
from io import BytesIO
from PIL import Image


def lookup_isbn(isbn):
    """
    Look up book information by ISBN using Open Library API
    
    Returns dict with:
        - title
        - year
        - author (comma-separated if multiple)
        - publisher
        - page_count
        - description
        - cover_url (for downloading)
    
    Returns None if ISBN not found
    """
    # Clean ISBN (remove hyphens/spaces)
    isbn_clean = isbn.replace("-", "").replace(" ", "")
    
    # Try Open Library Books API
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_clean}&jscmd=data&format=json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if we got results
        key = f"ISBN:{isbn_clean}"
        if key not in data:
            return None
        
        book_data = data[key]
        
        # Extract information
        result = {}
        
        # Title
        result['title'] = book_data.get('title', '')
        
        # Year - extract from publish_date if available
        result['year'] = ''
        if 'publish_date' in book_data:
            publish_date = book_data['publish_date']
            # Try to extract year (often in format like "2005" or "May 2005")
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', publish_date)
            if year_match:
                result['year'] = year_match.group(0)
        
        # Authors
        authors = []
        if 'authors' in book_data:
            for author in book_data['authors']:
                if 'name' in author:
                    authors.append(author['name'])
        result['author'] = ', '.join(authors)
        
        # Publishers
        publishers = []
        if 'publishers' in book_data:
            for publisher in book_data['publishers']:
                if 'name' in publisher:
                    publishers.append(publisher['name'])
        result['publisher'] = ', '.join(publishers)
        
        # Page count
        result['page_count'] = book_data.get('number_of_pages', None)
        
        # Description
        result['description'] = ''
        if 'description' in book_data:
            desc = book_data['description']
            if isinstance(desc, dict) and 'value' in desc:
                result['description'] = desc['value']
            elif isinstance(desc, str):
                result['description'] = desc
        
        # Cover URL
        result['cover_url'] = None
        if 'cover' in book_data:
            cover = book_data['cover']
            if 'large' in cover:
                result['cover_url'] = cover['large']
            elif 'medium' in cover:
                result['cover_url'] = cover['medium']
            elif 'small' in cover:
                result['cover_url'] = cover['small']
        
        return result
        
    except requests.RequestException as e:
        print(f"Error looking up ISBN: {e}")
        return None


def download_cover(cover_url, save_path):
    """
    Download a cover image from URL and save it locally
    
    Returns True if successful, False otherwise
    """
    if not cover_url:
        return False
    
    try:
        response = requests.get(cover_url, timeout=10)
        response.raise_for_status()
        
        # Open image and save
        img = Image.open(BytesIO(response.content))
        img.save(save_path)
        return True
        
    except Exception as e:
        print(f"Error downloading cover: {e}")
        return False


def get_cover_path(isbn):
    """Get the path where a cover image should be saved"""
    covers_dir = Path(__file__).parent / "covers"
    covers_dir.mkdir(exist_ok=True)
    
    isbn_clean = isbn.replace("-", "").replace(" ", "")
    return covers_dir / f"{isbn_clean}.jpg"


if __name__ == "__main__":
    # Test the lookup
    test_isbn = "9780451526538"  # 1984 by George Orwell
    print(f"Testing ISBN lookup for {test_isbn}...")
    
    result = lookup_isbn(test_isbn)
    if result:
        print("\nResults:")
        for key, value in result.items():
            if key == 'description':
                print(f"{key}: {value[:100]}..." if len(value) > 100 else f"{key}: {value}")
            else:
                print(f"{key}: {value}")
        
        # Test cover download
        if result['cover_url']:
            cover_path = get_cover_path(test_isbn)
            print(f"\nDownloading cover to {cover_path}...")
            success = download_cover(result['cover_url'], cover_path)
            print(f"Cover download: {'Success' if success else 'Failed'}")
    else:
        print("ISBN not found")
