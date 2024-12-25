from openai import OpenAI
import os
import dotenv
from unitTest.commands_unittest import testlist
import time
import json

dotenv.load_dotenv()


def command_mapping(user_query):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
        )
    
    with open("outputformat.json", "r", encoding='utf-8') as f:
        json_schema = json.load(f)

    # Send the query to the LLM for intent recognition and parameter extraction
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                """Bạn là một trợ lý giúp ánh xạ câu truy vấn bằng ngôn ngữ tự nhiên của người dùng thành một lệnh JSON dựa trên cấu trúc sau:""")
            },
            {
                "role": "user",
                "content": user_query
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": json_schema
        }
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
    correct_outputs = 0
    for user_query in testlist:
        query = user_query['Query']
        try:
            begin = time.time()
            mapped_json = command_mapping(query)
            end = time.time()
        except Exception as e:
            print("ERROR at query: ", query)
            print(f"Error: {e}")
            print(f"Sleeping for {time_sleep} seconds")
            time.sleep(time_sleep)
            time_sleep *= 2
            time_sleep = min(60, time_sleep)
            testlist.insert(i, user_query)
            continue
            
        is_matching = False
        if mapped_json['command'].lower() in ["thoát chương trình", "tắt chương trình", "ngừng chương trình"] and user_query['Output']["command"].lower() in ["thoát chương trình", "tắt chương trình", "ngừng chương trình"]:
            is_matching = True
        elif mapped_json['command'].lower() == user_query['Output']["command"].lower():
            if mapped_json['command'].lower() in ["đọc sách", "tóm tắt"]:
                if mapped_json['parameters']['tên sách'].lower() == user_query['Output']["parameters"]["tên sách"].lower():
                    is_matching = True
            elif mapped_json['command'].lower() in ["tiếp tục", 'hỏi đáp']:
                is_matching = True

        
        if is_matching:
            print("Correct output ✅")
            correct_outputs += 1
        else:
            print("Incorrect output ❌")
        
        print(f"Correct outputs: {correct_outputs}/{len(testlist)}")
        
        i += 1
        total_time += end - begin
        print(f"User query: {query}")
        print(f"Output: {mapped_json}")
        print(f"Time: {end - begin}")
        print("\n")
        
        # sleep for 1 second to avoid rate limiting
        time.sleep(2)