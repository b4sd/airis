# Display the tree
import json
from summary_tree import SparseTableSummarizer


# "command": "tóm tắt", 
#         "parameters": {
#             "tên sách": "'?'",
#             "trang bắt đầu": "'?' || 'STARTPAGE' || 'PREVIOUS_STOPPAGE'",
#             "trang kết thúc": "'?' || 'ENDPAGE'",
#             "chương bắt đầu": "'?' || 'STARTCHAPTER' || 'PREVIOUS_STOPCHAPTER'",
#             "chương kết thúc": "'?' || 'ENDCHAPTER'",
#         }},

def query_summary_page(book_name, start_page, end_page, start_chapter, end_chapter):
    ST = SparseTableSummarizer.local_load('misc/booksumary/book')
    block_mapping = {}
    with open("misc/booksumary/block_mapping_book.json", "r") as f:
        block_mapping = json.load(f)

    # start block is min block of start page
    start_block = block_mapping.get(str(start_page), [0])[0]
    
    # end block is max block of end page
    end_block = block_mapping.get(str(end_page), [0])[-1]

    return ST.query(start_block, end_block)

def query_summary_block(book_name, start_block, end_block):
    ST = SparseTableSummarizer.local_load('misc/booksumary/book')
    return ST.query(start_block, end_block)


# print(query_summary("niggest", 10, 10, 1, 2))

