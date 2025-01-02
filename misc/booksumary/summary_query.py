# Display the tree
import json
from misc.booksumary.summary_tree import SparseTableSummarizer


# "command": "tóm tắt", 
#         "parameters": {
#             "tên sách": "'?'",
#             "trang bắt đầu": "'?' || 'STARTPAGE' || 'PREVIOUS_STOPPAGE'",
#             "trang kết thúc": "'?' || 'ENDPAGE'",
#             "chương bắt đầu": "'?' || 'STARTCHAPTER' || 'PREVIOUS_STOPCHAPTER'",
#             "chương kết thúc": "'?' || 'ENDCHAPTER'",
#         }},

def query_summary_page(book_name, start_page, end_page, start_chapter, end_chapter):
    if end_page == "":
        end_page = start_page
    if end_chapter == "":
        end_chapter = start_chapter

    if start_chapter == "":
        start_chapter = end_chapter
    if start_page == "":
        start_page = end_page

    ST = SparseTableSummarizer.local_load('misc/booksumary/book')
    block_mapping = {}
    with open("misc/booksumary/block_mapping_book.json", "r") as f:
        block_mapping = json.load(f)

    # start block is min block of start page
    start_block = block_mapping.get(str(start_page), [0])[0]
    
    # end block is max block of end page
    end_block = block_mapping.get(str(end_page), [0])[-1]

    res = ST.query(start_block, end_block)

    print(f"start_block: {start_block}, end_block: {end_block}")
    print(f"res: {res}")

    return res

def query_summary_block(book_name, start_block, end_block):
    ST = SparseTableSummarizer.local_load('misc/booksumary/book')
    res =  ST.query(start_block, end_block)

    print(f"start_block: {start_block}, end_block: {end_block}")
    print(f"res: {res}")
    return res


# print(query_summary("niggest", 10, 10, 1, 2))

