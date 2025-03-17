import streamlit as st
import pandas as pd
import json
import os

LIBRARY_FILE = "library.json"

# --- Load Library from File on Startup ---
if "library" not in st.session_state:
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "r") as f:
            st.session_state.library = json.load(f)
        st.success("Library loaded from file successfully!")
    else:
        st.session_state.library = []

# --- Utility Functions ---
def save_library_to_file(filename=LIBRARY_FILE):
    """Saves the current library to a JSON file."""
    with open(filename, "w") as f:
        json.dump(st.session_state.library, f, indent=4)

def add_book(title, author, publication_year, genre, read_status):
    """Adds a new book to the library and saves to file."""
    book_id = len(st.session_state.library) + 1
    st.session_state.library.append({
        "id": book_id,
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status
    })
    save_library_to_file()

def remove_book(book_id):
    """Removes a book from the library by its ID and saves to file."""
    st.session_state.library = [book for book in st.session_state.library if book["id"] != book_id]
    save_library_to_file()

def search_books(books, search_term, genre_filter, read_status_filter):
    """Searches books by multiple fields and applies genre/read status filters."""
    filtered = books
    term = search_term.lower()

    if search_term:
        filtered = [book for book in filtered if 
                    term in book["title"].lower() or 
                    term in book["author"].lower() or 
                    term in book["genre"].lower() or 
                    term in str(book["publication_year"])]

    if genre_filter != "All":
        filtered = [book for book in filtered if book["genre"].lower() == genre_filter.lower()]

    if read_status_filter != "All":
        read_status_bool = read_status_filter == "Read"
        filtered = [book for book in filtered if book["read_status"] == read_status_bool]

    return filtered

def get_statistics():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    return total_books, percentage_read

# --- Streamlit Interface ---
st.title("📚 Personal Library Manager")

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", 
    ["Add a Book", "Remove a Book", "Search Books", "Display All Books", "Library Statistics"])

# --- Add Book ---
if menu == "Add a Book":
    st.header("➕ Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=0, max_value=3000, step=1)
        genre = st.text_input("Genre")
        read_status = st.checkbox("Read")
        submitted = st.form_submit_button("Add Book")
        if submitted:
            add_book(title, author, int(publication_year), genre, read_status)
            st.success("Book added successfully!")

# --- Remove Book ---
elif menu == "Remove a Book":
    st.header("🗑️ Remove a Book")
    if st.session_state.library:
        book_options = {f"{book['id']} - {book['title']}": book['id'] for book in st.session_state.library}
        selected = st.selectbox("Select a book to remove", list(book_options.keys()))
        if st.button("Remove Book"):
            remove_book(book_options[selected])
            st.success("Book removed successfully!")
    else:
        st.info("No books available to remove.")

# --- Search Books ---
elif menu == "Search Books":
    st.header("🔍 Advanced Book Search")
    search_term = st.text_input("Search (Title, Author, Genre, Year)")
    
    genres = list({book["genre"] for book in st.session_state.library if book["genre"]})
    genre_filter = st.selectbox("Filter by Genre", ["All"] + genres)

    read_status_filter = st.selectbox("Filter by Read Status", ["All", "Read", "Unread"])
    
    sort_by = st.selectbox("Sort by", ["Title A-Z", "Publication Year ↑", "Publication Year ↓"])
    
    if st.button("Search"):
        results = search_books(st.session_state.library, search_term, genre_filter, read_status_filter)
        
        if results:
            df = pd.DataFrame(results)
            if sort_by == "Title A-Z":
                df = df.sort_values("title")
            elif sort_by == "Publication Year ↑":
                df = df.sort_values("publication_year")
            elif sort_by == "Publication Year ↓":
                df = df.sort_values("publication_year", ascending=False)
            st.write(df)
        else:
            st.info("No matching books found.")

# --- Display All Books ---
elif menu == "Display All Books":
    st.header("📖 All Books in Library")
    if st.session_state.library:
        df = pd.DataFrame(st.session_state.library)
        st.write(df)
    else:
        st.info("Library is empty.")

# --- Library Statistics ---
elif menu == "Library Statistics":
    st.header("📊 Library Statistics")
    total_books, percentage_read = get_statistics()
    st.write(f"**Total Books:** {total_books}")
    st.write(f"**Books Read:** {percentage_read:.2f}%")
