from openai import OpenAI
import os
import dotenv
# from requests import requests
from unitTest.commands_unittest import testlist
import time
import json

dotenv.load_dotenv()

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("OPENAI_API_KEY_GITHUB")
    )

# Problems: If Query = "Hãy tóm tắt chương 1" -> what should i do?
# Cố định Prompt -> code theo output của Llm
commands = [
    {
        "command": "đọc sách",
        "parameters": {
            "tên sách": "'?'",
            "trang bắt đầu": "'?' || 'STARTPAGE' || 'PREVIOUS_STOPPAGE'",
            "trang kết thúc": "'?' || 'ENDPAGE'",
            "chương bắt đầu": "'?' || 'STARTCHAPTER' || 'PREVIOUS_STOPCHAPTER'",
            "chương kết thúc": "'?' || 'ENDCHAPTER'",
        }
    },
    # {"command": "ghi chú", "parameters": {"tiêu đề": "?", "nội dung": "?"}},
    {
        "command": "tóm tắt", 
        "parameters": {
            "tên sách": "'?'",
            "trang bắt đầu": "'?' || 'STARTPAGE' || 'PREVIOUS_STOPPAGE'",
            "trang kết thúc": "'?' || 'ENDPAGE'",
            "chương bắt đầu": "'?' || 'STARTCHAPTER' || 'PREVIOUS_STOPCHAPTER'",
            "chương kết thúc": "'?' || 'ENDCHAPTER'",
        }},
    {"command": "tiếp tục", "parameters": {}},
    {"command": "dừng", "parameters": {}},
    {"command": "hỏi đáp", "parameters": {"câu hỏi": "'?'"}},
    
    {"command": "thoát chương trình", "parameters": {}},
    {"command": "tắt chương trình", "parameters": {}},
    {"command": "ngừng chương trình", "parameters": {}},
    
    {"command": "không có", "parameters": {}},
]

def command_mapping(user_query):
    # Send the query to the LLM for intent recognition and parameter extraction
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                """Bạn là một trợ lý giúp ánh xạ câu truy vấn bằng ngôn ngữ tự nhiên của người dùng thành một lệnh JSON dựa trên cấu trúc sau:
                {commands}
                Hãy đối chiếu lệnh và điền các tham số dựa trên đầu vào của người dùng. Nếu câu truy vấn của người dùng không khớp với bất kỳ lệnh nào, hãy trả về lệnh 'không có' với một đối tượng tham số trống. Không trả về dưới dạng một mảng đối tượng.
                Câu truy vấn của người dùng: Bạn có thể cô đọng thông tin cả cuốn sách Tư duy nhanh và chậm không?
                Kết quả: {'command': 'tóm tắt', 'parameters': {'tên sách': 'Tư duy nhanh và chậm', 'trang bắt đầu': 'STARTPAGE', 'trang kết thúc': 'ENDPAGE', 'chương bắt đầu': '?', 'chương kết thúc': '?'}}
                Câu truy vấn của người dùng: Hãy đọc sách chương đầu cuốn sách Tư duy nhanh và chậm không?
                Kết quả: {'command': 'tóm tắt', 'parameters': {'tên sách': 'Tư duy nhanh và chậm', 'trang bắt đầu': 'STARTPAGE', 'trang kết thúc': 'ENDPAGE', 'chương bắt đầu': 'STARTCHAPTER', 'chương kết thúc': '?'}}
                Note: STARTPAGE, ENDPAGE, PREVIOUS_STOPPAGE, STARTCHAPTER, ENDCHAPTER là các tham số đặc biệt để biểu diễn "trang bắt đầu", "trang kết thúc", "trang dừng lại lần trước", "bắt đầu chương", "kết thúc chương" của cuốn sách.
                """)
            },
            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    # Parse and handle the response to ensure it is a consistent format
    result = response.choices[0].message.content
    result = result.replace("\'", "\"")

    while result[0] == "[":
        result = result[1:-1]

    return json.loads(result)
    
if __name__ == "__main__":
    correct_outputs = 0

    total_time = 0
    time_sleep = 2
    i = 0
    for user_query in testlist:
        query = user_query['Query']
        try:
            begin = time.time()
            mapped_json = command_mapping(query)
            end = time.time()
        except Exception as e:
            print("ERROR")
            print(f"Sleeping for {time_sleep} seconds")
            time.sleep(time_sleep)
            time_sleep *= 2
            time_sleep = max(60, time_sleep)
            testlist.insert(i, user_query)
            continue
            
        i += 1
        total_time += end - begin
        print(f"User query: {query}")
        print(f"Output: {mapped_json}")
        print(f"Time: {end - begin}")
        print("\n")
        
        # sleep for 1 second to avoid rate limiting
        time.sleep(2)