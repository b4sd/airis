import re
import pdfplumber
# import pytesseract
from collections import defaultdict
from groq import Groq
from openai import OpenAI
from time import sleep
import json
# from dotenv import load_dotenv
# load_dotenv()

import os
root = os.getcwd()

api_key = 'da7862c3-43f5-49ae-bad5-19ce3fbf4139'
client = OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=api_key,
        )

def fix_typo(text):
    # Prompt initial notes
    query = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content":  """Bạn là một trợ lý ảo giúp sửa lỗi chính tả. Hãy sửa lỗi chính tả cho đoạn văn bản được đưa vào.
                            Chỉ được sửa lỗi chính tả với những từ không đúng chính tả. Sửa lỗi dựa vào ngữ cảnh đoạn văn.
                            Nếu một từ sai chính tả, thử sắp xếp lại các chữ để tạo ra từ có nghĩa. Nếu không, hãy sửa theo cách bạn muốn.
                            Không thêm, không bớt, không thay đổi câu văn.
                            Không giải thích, không dài dòng. Trả lời cả những phần không bị sửa.
                            Ví dụ: input: mãgn xà. output: mãng xà."""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model="Qwen2.5-72B-Instruct",
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
            if len(lines) == 0:
                continue
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
                if is_section_header(line, page):
                    continue
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
            # print("new page")
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

def blockify(partitions, char_limit=2000):
    blocks = []
    current_block = {"content": "", "page_numbers": set()}
    page_to_block = {}

    previous_type = None  # Track the type of the previous partition
    def add_block():
        """Finalize the current block and add it to the blocks list."""
        # print("add block")
        if len(current_block["content"]) == 0:
            return
        while True:
            try:
                current_block["content"] = fix_typo(current_block["content"])
                break
            except:
                sleep(2)
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
    if page_number >= len(page_to_block):
        return
    return page_to_block[page_number]

def pages_to_block_query(start_page, end_page, page_to_block):
    mp = set()
    for page_idx in range(start_page, end_page + 1):
        blocks = page_to_block_query(page_idx, page_to_block)
        if blocks:
            for block in blocks:
                mp.add(block)
    return mp

def write_blocks_to_file(blocks, book_name):
    """
    Writes block information to a text file.

    Args:
        blocks (list): A list of blocks, each containing 'content' and 'page_numbers'.
        file_path (str): Path to the output text file.
    """
    file_path = root + r"\\misc\booksumary\block-" + book_name + ".txt"
    with open(file_path, "w", encoding="utf-8") as file:
        for idx, block in enumerate(blocks):
            # Write block header
            file.write(f"Block {idx + 1}:\n")
            # Write block content
            file.write(f"Content:\n{block['content']}\n")
            # Write page numbers
            pages = ", ".join(map(str, sorted(block["page_numbers"])))
            file.write(f"Page Numbers: {pages}\n")
            # Separator for readability
            file.write("\n" + "=" * 40 + "\n\n")

# def write_page_to_block(book_name, page_to_block_map):
#     file_path = root + r"\\misc\booksumary\block-mapping" + book_name + ".json"
#     """
#     Writes the page-to-block mapping to a file in JSON-like format.

#     Args:
#         file_path (str): The path to the output file.
#         page_to_block_map (dict): A dictionary where the keys are page indices (int)
#                                   and the values are lists of block indices (int).
#     """
#     # Convert page indices and block lists to the desired string format
#     formatted_map = {
#         str(page_index): block_indices
#         for page_index, block_indices in page_to_block_map.items()
#     }
    
#     # Write to the file in a readable format
#     with open(file_path, "w", encoding="utf-8") as file:
#         json.dump(formatted_map, file, indent=4)

def write_page_to_block(book_name, page_to_block_map):
    file_path = root + f"\\assets\\mapping\\{book_name}.json"
    """
    Writes the page-to-block mapping to a file in JSON-like format where each list of blocks is on the same line.

    Args:
        file_path (str): The path to the output file.
        page_to_block_map (dict): A dictionary where the keys are page indices (int)
                                  and the values are lists of block indices (int).
    """

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("{\n")
        total_items = len(page_to_block_map)
        for idx, (page_index, block_indices) in enumerate(page_to_block_map.items(), start=1):
            blocks = ", ".join(map(str, block_indices))
            comma = "," if idx < total_items else ""  # Add a comma unless it's the last item
            file.write(f'    "{page_index}": [{blocks}]{comma}\n')
        file.write("}\n")

def get_block_content(block_index, book_name):
    """
    Retrieves the content of a specific block by its index from a file, excluding page number information.

    Args:
        file_path (str): Path to the file containing block information.
        block_index (int): The index of the block to retrieve (1-based).

    Returns:
        str: The content of the block without page numbers, or None if the block is not found.
    """
    file_path = root + r"\\misc\booksumary\block-" + book_name + ".txt"
    block_header = f"Block {block_index}:"
    in_block = False
    content_lines = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Check if we're entering the desired block
            if line.strip() == block_header:
                in_block = True
                continue
            
            # If we're in the block, collect its content
            if in_block:
                # Stop collecting if we hit the next block or a separator
                if line.strip().startswith("Block ") or line.strip() == "=" * 40:
                    break
                if line.strip().startswith("Page Numbers:"):
                    continue
            
                content_lines.append(line.strip())
    return "\n".join(content_lines) if content_lines else None

def write_each_block_to_file(blocks, book_name):
    for idx, block in enumerate(blocks):
        file_path = root + f"\\assets\\book\\{book_name}\\block_{idx}.txt"
        # create folder if not exist
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(block['content'])

