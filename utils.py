import os
import fitz  # PyMuPDF

def load_books_from_folder(folder_path):
    """ Load PDF books from the specified folder """
    books = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            book_title = filename[:-4]  # Remove ".pdf" from the filename to get the title
            book_path = os.path.join(folder_path, filename)

            # Extract a cover image from the first page of the PDF
            cover_image = extract_cover_image(book_path, dpi=160)  # Extract with higher resolution

            # Placeholder content (for simplicity, we'll just create a list of placeholder text)
            content = extract_pdf_content(book_path, dpi=160)  # Extract pages with higher resolution

            books[book_title] = {
                "cover": cover_image,
                "content": content
            }
    return books

def extract_cover_image(pdf_path, dpi=300):
    """ Extract the cover image from the first page of the PDF with higher resolution """
    doc = fitz.open(pdf_path)
    page = doc[0]  # First page
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))  # Increase DPI
    image_path = pdf_path[:-4] + "_cover.png"  # Save the cover image as PNG
    pix.save(image_path)
    return image_path  # Return the path to the saved image

def extract_pdf_content(pdf_path, dpi=300):
    """ Extract the pages content (as images) from the PDF with higher resolution """
    doc = fitz.open(pdf_path)
    content = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load each page
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))  # Increase DPI
        image_path = f"{pdf_path[:-4]}_page_{page_num + 1}.png"  # Save each page as PNG
        pix.save(image_path)
        content.append(image_path)  # Store the path to the saved page image
    return content

from fuzzywuzzy import process

def find_most_similar_book(input_book, book_list, threshold=80):
    # Use fuzzywuzzy's process.extractOne to find the most similar book
    best_match = process.extractOne(input_book, book_list)
    best_match_name, best_match_score = best_match[0], best_match[1]
    
    # Check if the best match score exceeds the threshold
    if best_match_score >= threshold:
        return best_match_name, best_match_score  # Return the most similar book name
    else:
        return "Not sure", best_match_score  # Return "Not sure" if similarity score is below threshold

def get_book_list():
    """Return a list of book names"""
    ## temporary list of books
    book_list = [
        "Tâm lí học tội phạm",
        "Cây cam ngọt của tôi",
        "Ngày xưa có một chuyện tình",
        "Còn chút gì để nhớ",
        "Cắn khớp cơ sở",
        "Trên đường băng",
        "Tôi tài giỏi bạn cũng thế",
        "Không gia đình",
        "Call me by your name",
        "Mật mã Da Vinci",
        "Kẻ ăn hồn",
        "Tết ở làng địa ngục",
        "Dế mèn phiêu lưu ký",
        "Tôi là Bêtô",
        "Chuyện con mèo dạy hải âu bay",
        "Giải trí đến chết",
        "Gánh gánh gồng gồng",
        "Hai số phận",
        "Khoa học loài người",
        "25 độ âm",
        "Chí phèo",
        "Dạy con làm giàu",
        "Mỗi lần vấp ngã là mỗi lần trưởng thành",
        "Cô gái đan mạch",
        "Số đỏ",
        "Once upon a broken heart",
        "Binh pháp tôn tử",
        "Từ câu sai đến câu hay",
        "Harry Potter",
        "Hành tinh của một kẻ nghĩ nhiều",
        "Bên trong chúng ta đã vụn vỡ như thế nào?",
        "Đắc nhân tâm",
        "Nhà giả kim",
        "Chú chó nhỏ mang giỏ hoa hồng",
        "Thép đã tôi thế đấy",
        "Giáo trình tư tưởng HCM",
        "MINDSET",
        "The Three-body Problem",
        "Dám Ước Mơ",
        "Biết Thực Hiện",
        "Hạt giống tâm hồn",
        "Quà tặng cuộc sống",
        "Không gia đình",
        "Tiếng gọi nơi hoang dã",
        "Normal People",
        "Hai Số Phận",
        "Bốn thoả ước",
        "Hoàng tử bé",
        "Tuổi trẻ đánh giá bao nhiêu",
        "Cây cam ngọt của tôi và Harry Potter",
        "Chiến tranh và hoà bình",
        "Túp lều của bác Tom",
        "Giáo sư và công thức toán"
    ]
    return book_list

def get_most_similar_book(input_book, threshold=80):
    if input_book == "" or input_book is None:
        return "No input book provided"
    book_list = get_book_list()
    book_name, score =  find_most_similar_book(input_book, book_list, threshold)
    return book_name