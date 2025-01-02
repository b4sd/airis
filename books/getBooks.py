import os

def getBooks():
    books = []
    for book in os.listdir('books'):
        if book.endswith('.txt') or book.endswith('.pdf'):
            book_name = book.split('.')[0]
            books.append(book_name)
    return books

if __name__ == '__main__':
    print(getBooks())