import re
import pdfplumber
from groq import Groq


import os
root = os.getcwd()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def fix_typo(text):
    # Prompt initial notes
    query = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content":  "Bạn là một trợ lý ảo giúp sửa lỗi chính tả. Hãy sửa lỗi chính tả cho đoạn văn bản được đưa vào."
                            "Chỉ được sửa lỗi chính tả với những từ không đúng chính tả. Sửa lỗi dựa vào ngữ cảnh đoạn văn."
                            "Nếu một từ sai chính tả, thử sắp xếp lại các chữ để tạo ra từ có nghĩa. Nếu không, hãy sửa theo cách bạn muốn."
                            "Không thêm, không bớt, không thay đổi câu văn."
                            "Không giải thích, không dài dòng. Trả lời cả những phần không bị sửa."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return query.choices[0].message.content

def process_plumber(file_path):
    sections = []
    current_section = {"header": None, "content": "", "page_numbers": set()}

    def is_header_footer(text, page_number):
        return re.match(r"^\d+$", text.strip()) or "Header" in text or "Footer" in text

    def is_section_header(text, page):
        """Identify section headers based on uppercase text, patterns, or boldness."""
        return (text.strip().isupper() or  # Check for full uppercase text
            re.match(r"^(Section|Chapter|Part|\d+(\.\d+)*)", text.strip(), re.IGNORECASE)) # Check for patterns

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            max_font_size = 0
            lines = []

            for char in page.chars:
                font_size = char.get("size", 0)
                max_font_size = max(max_font_size, font_size)
                lines.append({"text": char["text"], "size": font_size})
            
            lines = page.extract_text().splitlines()
            for line in lines:
                if is_header_footer(line, page_number):
                    continue
                if is_section_header(line, page):
                    if current_section["content"].strip():
                        sections.append(current_section)
                    current_section = {"header": line.strip(), "content": "", "page_numbers": {page_number}}
                else:
                    current_section["content"] += f" {line.strip()}"
                    current_section["page_numbers"].add(page_number)

    if current_section["content"].strip():
        sections.append(current_section)
    
    return sections

def blockify(partitions):
    """
    Group partitions into blocks and create a page-block mapping.
    
    Parameters:
        partitions (list): A list of partitions, each with 'header', 'content', and 'page_number'.
    
    Returns:
        blocks (list): List of blocks, each a dictionary with 'header', 'content', and 'page_numbers'.
        page_block (list): List of lists, where each element contains block indices for that page.
    """
    limit = 5000
    blocks = []
    page_block_map = {}

    current_block = None
    current_char_count = 0
    
    for section in sections:
        header = section['header']
        content = section['content']
        pages = section['page_numbers']
        part_length = (len(header) if header else 0) + len(content)
        
        # If the partition has a header, start a new block
        if header:
            # Finalize the previous block
            if current_block is not None:
                blocks.append(current_block)
            
            # Start a new block
            current_block = {
                'header': header,
                'content': content,
                'page_numbers': pages
            }
            current_char_count = part_length
        else:
            # Add to the current block if within limit
            if current_block and current_char_count + part_length <= 5000:
                current_block['content'] += '\n' + content
                current_block['page_numbers'] = sorted(set(current_block['page_numbers'] + pages))
                current_char_count += part_length
            else:
                # Finalize the current block
                if current_block is not None:
                    blocks.append(current_block)
                
                # Start a new block
                current_block = {
                    'header': None,
                    'content': content,
                    'page_numbers': pages
                }
                current_char_count = part_length
        
        # Update page-block mapping
        for page in pages:
            if page not in page_block_map:
                page_block_map[page] = []
            page_block_map[page].append(len(blocks))  # Add current block index
    
    # Add the last block
    if current_block is not None:
        blocks.append(current_block)
    
    # Convert page-block mapping to a sorted list of lists
    page_block = [page_block_map[page] for page in sorted(page_block_map)]
    
    return blocks, page_block


file_path = root + r"\\misc\booksumary\pl-18-23.pdf"
sections = process_plumber(file_path)

# Print the output
for i, section in enumerate(sections):
    print(f"Section {i + 1}", len(section['content']))
    print(f"Header: {section['header']}")
    print(f"Content: {section['content']}")
    print(f"Page Numbers: {sorted(section['page_numbers'])}")
    print("-" * 50)

blocks, page_block = blockify(sections)

# Output results
print("Blocks:")
for i, block in enumerate(blocks):
    print(i, len(block['content']))
    print(block['content'])
    print()

print("\nPage-Block Mapping:")
print(page_block)