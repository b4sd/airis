from block_preprocess import process_plumber, blockify, write_blocks_to_file, write_page_to_block, get_block_content, write_each_block_to_file
import os
root = os.getcwd()

book_name = "Thạch Sanh"

file_path = root + r"\\assets\pdf" + "\\" + book_name + ".pdf"
sections = process_plumber(file_path)

# create blocks for file
blocks, page_to_block = blockify(sections)

# write content of each block to file
write_page_to_block(book_name, page_to_block) # assets/mapping/book_name.json

# write mapping of page to block to file
write_each_block_to_file(blocks, book_name) # assets/book/book_name/blocks_i.txt

# create summarized blocks
from summary_tree import SparseTableSummarizer
import os

# take elements from the booktext from assets/book/{name}/block_{index}.txt
elements = []
for i in range(len(os.listdir(f"assets/book/{book_name}"))):
    with open(f"assets/book/{book_name}/block_{i}.txt", "r", encoding="utf-8") as f:
        elements.append(f.read())

# Summarize using SparseTableSummarizer
ST = SparseTableSummarizer(elements, book_name)
ST.process()
ST.local_save()