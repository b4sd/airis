from misc.booksumary.summary_tree import SparseTableSummarizer
from unstructured.partition.auto import partition

# Extract text from the PDF
elements = partition(r"book-stat_first_5_pages.pdf")

# Combine extracted elements into a single text
text = "\n\n".join([str(el) for el in elements])

print(len(elements))

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

# Append the final chunk if it's non-empty
if temp.strip():
    new_elements.append(temp.strip())

# Replace original elements with new chunks
elements = new_elements

# write to el.json in utf-8
for i, el in enumerate(elements):
    with open(f"el_{i}.json", "w", encoding="utf-8") as f:
        f.write(el)

# Summarize using SparseTableSummarizer
# ST = SparseTableSummarizer(elements, "book-stat_first_5_pages")
# ST.process()
# ST.local_save()

# Print page-to-block mapping
print("Page to Block Mapping:")
for page, block in page_to_block_map.items():
    print(f"Page {page}: Block {block}")
