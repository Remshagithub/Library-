import json
from datetime import datetime, timedelta

class Book:
    def __init__(self, book_id, title, author, is_available=True, borrower=None, due_date=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.is_available = is_available
        self.borrower = borrower
        self.due_date = due_date

class Member:
    def __init__(self, member_id, name, email, borrowed_books=None):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books = borrowed_books if borrowed_books else []

class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.fine_rate = 1.0  # $1 per day
        self.load_data()

    def save_data(self):
        data = {
            "books": {book_id: book.__dict__ for book_id, book in self.books.items()},
            "members": {member_id: member.__dict__ for member_id, member in self.members.items()}
        }
        with open("library_data.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open("library_data.json", "r") as f:
                data = json.load(f)
                # Handle books whether they're in list or dict format
                books_data = data.get("books", {})
                if isinstance(books_data, list):
                    self.books = {book["book_id"]: Book(**book) for book in books_data}
                else:
                    self.books = {book_id: Book(**book_data) for book_id, book_data in books_data.items()}
                
                # Handle members whether they're in list or dict format
                members_data = data.get("members", {})
                if isinstance(members_data, list):
                    self.members = {member["member_id"]: Member(**member) for member in members_data}
                else:
                    self.members = {member_id: Member(**member_data) for member_id, member_data in members_data.items()}
        except FileNotFoundError:
            print("No existing data found. Starting with empty library.")

    def add_book(self, book_id, title, author):
        if book_id not in self.books:
            self.books[book_id] = Book(book_id, title, author)
            self.save_data()
            return True
        return False

    def add_member(self, member_id, name, email):
        if member_id not in self.members:
            self.members[member_id] = Member(member_id, name, email)
            self.save_data()
            return True
        return False

    def borrow_book(self, book_id, member_id):
        if book_id in self.books and member_id in self.members:
            book = self.books[book_id]
            member = self.members[member_id]
            if book.is_available:
                book.is_available = False
                book.borrower = member_id
                book.due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                member.borrowed_books.append(book_id)
                self.save_data()
                return True
        return False

    def return_book(self, book_id):
        if book_id in self.books:
            book = self.books[book_id]
            if not book.is_available:
                fine = self.calculate_fine(book_id)
                member = self.members[book.borrower]
                member.borrowed_books.remove(book_id)
                book.is_available = True
                book.borrower = None
                book.due_date = None
                self.save_data()
                return True, fine
        return False, 0.0

    def display_books(self):
        print("\nLibrary Books:")
        print("-" * 80)  # Add separator line
        format_string = "{:<5} | {:<20} | {:<15} | {:<35}"
        print(format_string.format("ID", "Title", "Author", "Status"))
        print("-" * 80)  # Add separator line
        
        for book in self.books.values():
            if book.is_available:
                status = "Available"
            else:
                member_name = self.members[book.borrower].name
                status = f"Borrowed by {member_name} (Due: {book.due_date})"
            
            print(format_string.format(
                book.book_id,
                book.title[:18] + "..." if len(book.title) > 18 else book.title,
                book.author[:13] + "..." if len(book.author) > 13 else book.author,
                status[:33] + "..." if len(status) > 33 else status
            ))
        print("-" * 80)  # Add separator line

    def search_books(self, query):
        """Search books by title or author."""
        query = query.lower()
        results = []
        for book in self.books.values():
            if query in book.title.lower() or query in book.author.lower():
                results.append(book)
        return results

    def display_search_results(self, query):
        """Display search results in a formatted way."""
        results = self.search_books(query)
        if not results:
            print(f"\nNo books found matching '{query}'")
            return
        
        print(f"\nSearch results for '{query}':")
        print("-" * 80)
        format_string = "{:<5} | {:<20} | {:<15} | {:<35}"
        print(format_string.format("ID", "Title", "Author", "Status"))
        print("-" * 80)
        
        for book in results:
            if book.is_available:
                status = "Available"
            else:
                member_name = self.members[book.borrower].name
                status = f"Borrowed by {member_name} (Due: {book.due_date})"
            
            print(format_string.format(
                book.book_id,
                book.title[:18] + "..." if len(book.title) > 18 else book.title,
                book.author[:13] + "..." if len(book.author) > 13 else book.author,
                status[:33] + "..." if len(status) > 33 else status
            ))
        print("-" * 80)

    def calculate_fine(self, book_id):
        """Calculate fine for overdue book."""
        if book_id in self.books:
            book = self.books[book_id]
            if not book.is_available and book.due_date:
                due_date = datetime.strptime(book.due_date, "%Y-%m-%d")
                days_overdue = (datetime.now() - due_date).days
                if days_overdue > 0:
                    return days_overdue * self.fine_rate
        return 0.0

# Example usage
if __name__ == "__main__":
    library = Library()
    library.add_book("B1", "Python Programming", "John Smith")
    library.add_book("B2", "Data Structures", "Jane Doe")
    library.add_member("M1", "Alice Brown", "alice@email.com")
    library.borrow_book("B1", "M1")
    
    # Example of search functionality
    print("\nSearching for 'Python':")
    library.display_search_results("Python")
    
    # Example of return with fine calculation
    success, fine = library.return_book("B1")
    if success:
        if fine > 0:
            print(f"\nBook returned successfully. Fine due: ${fine:.2f}")
        else:
            print("\nBook returned successfully. No fine due.")
    
    library.display_books()
