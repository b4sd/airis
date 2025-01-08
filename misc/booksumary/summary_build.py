from summary_tree import SparseTableSummarizer
from unstructured.partition.auto import partition
import os

# take elements from the booktext from assets/book/{name}/block_{index}.txt
elements = []
book_name = "thanh-giong"
for i in range(len(os.listdir(f"assets/book/{book_name}"))):
    with open(f"assets/book/{book_name}/block_{i}.txt", "r", encoding="utf-8") as f:
        elements.append(f.read())

# print(elements)
for element in elements:
    print(element)


# Summarize using SparseTableSummarizer
ST = SparseTableSummarizer(elements, book_name)
ST.process()
ST.local_save()

# # Print page-to-block mapping
# print("Page to Block Mapping:")
# for page, block in page_to_block_map.items():
#     print(f"Page {page}: Block {block}")

