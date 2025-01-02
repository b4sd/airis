from unstructured.partition.auto import partition_auto
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text

# Extract text from a PDF
pdf_content = partition_auto("book-stat.pdf")
for element in pdf_content:
    print(element)

# # Extract text from a DOCX file
# docx_content = partition_docx("example.docx")
# for element in docx_content:
#     print(element)

# # Extract text from a plain text file
# text_content = partition_text("example.txt")
# for element in text_content:
#     print(element)
