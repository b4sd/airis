# from misc.booksumary.summary_tree import SparseTableSummarizer
from summary_tree import SparseTableSummarizer
from unstructured.partition.auto import partition

# Extract text from the PDF
import os
root = os.getcwd()
file_path = root + r"\\misc\booksumary\book-stat_first_5_pages.pdf"
print(os.path.exists(file_path)) 
elements = partition(file_path)
print("extracted")
# Combine extracted elements into a single text
text = "\n\n".join([str(el) for el in elements])

print("n elements:", len(elements))

# Initial placeholder summary
summary = "Chưa có gì được tóm tắt"

# Chunk size limit (in characters)
limit = 2000

# Combine elements into chunks and map pages
temp = ""
new_elements = []
page_to_block_map = {}  # Mapping from page numbers to block indices
current_block_index = 0

for page_number, el in enumerate(elements, start=1):
    el_text = str(el).strip()  # Trim whitespace
    if len(el_text) <= 2:      # Skip empty/short elements
        continue
    if len(temp) + len(el_text) > limit:
        # Save the chunk and increment block index
        new_elements.append(temp.strip())
        temp = ""
        current_block_index += 1
    temp += el_text + "\n\n"
    page_to_block_map[page_number] = current_block_index  # Map page to current block

print("n blocks:", current_block_index)

# Append the final chunk if it's non-empty
if temp.strip():
    new_elements.append(temp.strip())

# Replace original elements with new chunks
elements = new_elements

# Summarize using SparseTableSummarizer
ST = SparseTableSummarizer(elements, "book-stat_first_5_pages")
ST.process()
ST.local_save()

# Print page-to-block mapping
print("Page to Block Mapping:")
for page, block in page_to_block_map.items():
    print(f"Page {page}: Block {block}")
