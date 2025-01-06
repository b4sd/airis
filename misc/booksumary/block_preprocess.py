import re
import pdfplumber
# import pytesseract
from collections import defaultdict
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
    current_section = {"type": None, "content": "", "page_numbers": set()}
    
    def is_header_footer(text, page_number):
        return re.match(r"^\d+$", text.strip()) or "Header" in text or "Footer" in text

    def is_section_header(text, page):
        """Identify section headers based on uppercase text, patterns, or boldness."""
        return (text.strip().isupper() or
                re.match(r"^(Section|Chapter|Part|\d+(\.\d+)*)", text.strip(), re.IGNORECASE))

    def is_bullet_point(text):
        """Identify if the line is a bullet point based on common symbols."""
        return re.match(r"^\s*[-•*·→‣⦾●○◦▪▶]", text.strip())

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            lines = page.extract_text().splitlines()
            chars = sorted(page.chars, key=lambda c: (c["top"], c["x0"]))  

            line_positions = []
            current_line_chars = []
            line_top = None

            for char in chars:
                char_top = char["top"]

                # Group characters into lines based on vertical position (top)
                if line_top is None or abs(char_top - line_top) < 2:
                    if line_top is None:
                        line_top = char_top
                    current_line_chars.append(char)
                else:
                    # Process the current line
                    if current_line_chars:
                        # Sort characters horizontally (x0) and join their text
                        current_line = "".join(c["text"] for c in sorted(current_line_chars, key=lambda c: c["x0"]))
                        line_positions.append((current_line.strip(), line_top))
                    # Start a new line
                    current_line_chars = [char]
                    line_top = char_top

            # Add the last line
            if current_line_chars:
                current_line = "".join(c["text"] for c in sorted(current_line_chars, key=lambda c: c["x0"]))
                line_positions.append((current_line.strip(), line_top))
            
            if current_line.strip():
                line_positions.append((current_line.strip(), line_top))
            # for line, pos in line_positions:
            #     print("line:", line)
            top_positions = [pos[1] for pos in line_positions]
            line_gaps = [top_positions[i + 1] - top_positions[i] for i in range(len(top_positions) - 1)]
            average_gap = sum(line_gaps) / len(line_gaps) if line_gaps else 0
            gap_threshold = average_gap * 1.2
            total_end_gap = 0
            line_count = 0
            for line, current_top in line_positions:
                end_gap = page.width - max(
                    [char for char in chars if abs(char["top"] - current_top) < 2],
                    key=lambda c: c["x1"]
                )["x1"]
                
                total_end_gap += end_gap
                line_count += 1
            average_end_gap = total_end_gap / line_count if line_count > 0 else 0
            end_gap_threshold = average_end_gap * 1.2 # Adjust this threshold based on your PDF layout

            previous_top = None
            end_gap = 0
            print("new page")
            for line, current_top in line_positions:
                if is_header_footer(line, page_number):
                    continue

                # print("     cur:", f" {line}")
                if is_section_header(line, page):
                    if current_section["content"].strip():
                        sections.append(current_section)
                    current_section = {
                        "type": "header",
                        "content": line,
                        "page_numbers": {page_number}
                    }
                    previous_top = current_top
                    end_gap = page.width - max(
                        [char for char in chars if abs(char["top"] - current_top) < 2],
                        key=lambda c: c["x1"]
                    )["x1"]

                elif is_bullet_point(line):
                    if current_section["type"] != "bullet point" and current_section["content"].strip():
                        sections.append(current_section)
                    current_section = {
                        "type": "bullet point",
                        "content": line,
                        "page_numbers": {page_number}
                    }
                    previous_top = current_top
                    end_gap = page.width - max(
                        [char for char in chars if abs(char["top"] - current_top) < 2],
                        key=lambda c: c["x1"]
                    )["x1"]

                elif line:
                    if (
                        (previous_top is not None and
                        current_top - previous_top > gap_threshold) 
                        or end_gap > end_gap_threshold
                    ):
                        # if current_section["type"] == "narrative text" and current_section["content"].strip():
                        sections.append(current_section)
                        current_section = {
                            "type": "narrative text",
                            "content": line,
                            "page_numbers": {page_number}
                        }

                    else:
                        if current_section["type"] == "narrative text":
                            current_section["content"] += f" {line}"
                        else:
                            sections.append(current_section)
                            current_section = {
                                "type": "narrative text",
                                "content": line,
                                "page_numbers": {page_number}
                            }
                end_gap = page.width - max(
                    [char for char in chars if abs(char["top"] - current_top) < 2],
                    key=lambda c: c["x1"]
                )["x1"]
                previous_top = current_top

    if current_section["content"].strip():
        sections.append(current_section)

    return sections

def blockify(partitions, char_limit=1000):
    blocks = []
    current_block = {"content": "", "page_numbers": set()}
    page_to_block = {}

    previous_type = None  # Track the type of the previous partition

    def add_block():
        """Finalize the current block and add it to the blocks list."""
        if current_block["content"].strip():
            blocks.append(current_block.copy())
            for page in current_block["page_numbers"]:
                if page not in page_to_block:
                    page_to_block[page] = []
                page_to_block[page].append(len(blocks) - 1)  # Map page number to block index
            current_block["content"] = ""
            current_block["page_numbers"] = set()

    for partition in partitions:
        partition_length = len(partition["content"])

        # Check if the current partition is a header
        if partition["type"] == "header":
            # If the previous partition was not a header, finalize the current block
            if previous_type != "header":
                add_block()

            # Add the header content to the current block
            current_block["content"] += (current_block["content"] and " ") + partition["content"]
            current_block["page_numbers"].update(partition["page_numbers"])

        else:
            # For non-header partitions, check if adding it exceeds the char limit
            if partition_length + len(current_block["content"]) > char_limit:
                # Finalize the current block if it exceeds the limit
                add_block()

            # Add the partition to the current block
            current_block["content"] += (current_block["content"] and " ") + partition["content"]
            current_block["page_numbers"].update(partition["page_numbers"])

        # Update the previous_type tracker
        previous_type = partition["type"]

    # Finalize the last block
    add_block()

    return blocks, page_to_block

def page_to_block_query(page_number, page_to_block):
    return page_to_block[page_number]

file_path = root + r"\\misc\booksumary\pl-18-23.pdf"
sections = process_plumber(file_path)

# Print the output
for i, section in enumerate(sections):
    print(f"Section {i + 1}", len(section['content']))
    print(f"Type: {section['type']}")
    print(f"Content: {section['content']}")
    print(f"Page Numbers: {sorted(section['page_numbers'])}")
    print("-" * 50)

blocks, page_to_block = blockify(sections)

# Output results
print("Blocks:")
for i, block in enumerate(blocks):
    print(i, len(block['content']))
    print(block['content'])
    print(block['page_numbers'])
    print()

print("\nPage-Block Mapping:")
print(page_to_block)

print("\nquery:", page_to_block_query(3, page_to_block))