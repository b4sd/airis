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
    ST = SparseTableSummarizer.local_load(f'assets/summarize/{book_name}')
    block_mapping = {}
    with open(f"assets/mapping/{book_name}.json", "r") as f:
        block_mapping = json.load(f)

    # start block is min block of start page
    start_block = block_mapping.get(str(start_page), [0])[0]
    
    # end block is max block of end page
    end_block = block_mapping.get(str(end_page), [0])[-1]



    return ST.query(start_block, end_block)

def query_summary_block(book_name, start_block, end_block):
    ST = SparseTableSummarizer.local_load(f'assets/summarize/{book_name}')
    print(ST)
    return ST.query(start_block, end_block)



