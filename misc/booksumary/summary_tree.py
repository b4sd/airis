import pickle
import json
from openai import OpenAI



GROQ_API = "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"

import os

from groq import Groq

api_key = 'da7862c3-43f5-49ae-bad5-19ce3fbf4139'
client = OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=api_key,
        )

model = "Qwen2.5-72B-Instruct"


requirements = """
Hãy bỏ các kí hiệu đặc biệt như #, *, _, hoặc các kí hiệu đặc biệt khác. Đừng thêm xuống dòng không cần thiết. Loại bỏ các heading và viết thành đoạn văn văn nói.
Khi bạn đọc và gặp dấu hiệu này, hãy hiểu rằng đó là một phần mới trong văn bản. Các dấu hiệu này chỉ để giúp bạn hiểu cấu trúc của văn bản, không phải là phần của văn bản gốc.
Chỉ trả về đoạn văn bản đã được xử lí, không được nói gì khác.
Không bao gồm bài tập, ví dụ hoặc thông tin không cần thiết khác, chỉ bao gồm các khái niệm, ý chính và thông tin cần thiết, cô đọng và dễ hiểu.
Output của bạn không được quá 2000 từ, và phải là tiếng Việt chuẩn, không sai chính tả, ngữ pháp.
"""


prompt_adding_summary_template = """
Bạn là một trợ lý ảo giúp người mù đọc sách. Nhiệm vụ của bạn là kết hợp hai đoạn văn bản: một đoạn văn bản mới chưa được tóm tắt và một đoạn văn bản đã được tóm tắt trước đó. Đoạn kết hợp cuối cùng phải bao gồm đầy đủ các thông tin quan trọng từ cả hai đoạn bằng cách sử dụng bất kỳ phương pháp nào, như tóm tắt, tổng hợp hoặc sắp xếp lại, miễn là đảm bảo giữ nguyên ý nghĩa và nội dung cốt lõi.

Bạn hãy trả về bản tóm tắt cuối cùng dưới dạng văn bản. Bạn không nói những thứ không liên quan. Bạn cũng không cần phải tạo ra một tóm tắt hoàn chỉnh, nhưng hãy chắc chắn rằng bản tóm tắt của bạn chứa đầy đủ thông tin quan trọng từ cả hai đoạn văn bản.

Bạn đừng nói lặp ý, cũng đừng tóm tắt quá dài. Hãy tập trung vào việc truyền đạt. Bạn không nói những thứ không có trong văn bản.

Nếu văn bản quá dài, bạn có thể không cần đi vào chi tiết.

{requirements}

Dưới đây là đoạn văn bản đã được tóm tắt trước đó:
{summary}

Dưới đây là đoạn văn bản mới chưa được tóm tắt:
{text}
"""

prompt_combine_summaries_template = """ Bạn là một trợ lý ảo giúp người mù đọc sách. Nhiệm vụ của bạn là kết hợp hai đoạn văn bản đã được tóm tắt: một đoạn văn bản tóm tắt trước đó và một đoạn văn bản tóm tắt mới. Đoạn kết hợp cuối cùng phải bao gồm đầy đủ các thông tin quan trọng từ cả hai đoạn tóm tắt bằng cách sử dụng bất kỳ phương pháp nào, như tổng hợp hoặc sắp xếp lại, miễn là đảm bảo giữ nguyên ý nghĩa và nội dung cốt lõi.

Bạn hãy trả về bản tóm tắt cuối cùng dưới dạng văn bản. Bạn không nói những thứ không liên quan. Bạn cũng không cần phải tạo ra một bản tóm tắt quá dài, nhưng hãy chắc chắn rằng bản tóm tắt của bạn chứa đầy đủ thông tin quan trọng từ cả hai đoạn tóm tắt.

Bạn đừng nói lặp ý, cũng đừng làm bản kết hợp quá chi tiết hoặc dư thừa. Hãy tập trung vào việc truyền đạt thông tin cốt lõi.

{requirements}

Dưới đây là đoạn văn bản đã được tóm tắt trước đó:
{summary}

Dưới đây là đoạn văn bản tóm tắt mới:
{new_summary}
"""

prompt_sumary = """
Bạn là một trợ lý ảo giúp người mù đọc sách. Nhiệm vụ của bạn là tóm tắt một đoạn văn bản.

Bạn hãy trả về bản tóm tắt cuối cùng dưới dạng văn bản. Bạn không nói những thứ không liên quan. Bạn cũng không cần phải tạo ra một bản tóm tắt quá dài, nhưng hãy chắc chắn rằng bản tóm tắt của bạn chứa đầy đủ thông tin quan trọng từ cả hai đoạn tóm tắt.

Bạn đừng nói lặp ý, cũng đừng làm bản kết hợp quá chi tiết hoặc dư thừa. Hãy tập trung vào việc truyền đạt thông tin cốt lõi.

{requirements}

Dưới đây là đoạn văn bản cần được tóm tắt:
{text}
"""

prompt_normalize = """
Bạn là một trợ lý ảo giúp người mù đọc sách. Nhiệm vụ của bạn là chuẩn hóa một đoạn văn bản.

Bạn hãy trả về bản văn bản cuối cùng dưới dạng văn bản. Bạn không nói những thứ không liên quan. Bạn cũng không cần phải tạo ra một bản văn bản quá dài, nhưng hãy chắc chắn rằng bản văn bản của bạn chứa đầy đủ thông tin cần thiết.

Đây là tính chất của văn bản cần chuẩn hóa:
{requirements}

Bạn hãy chuyển nó về dạng bình thường để người bình thường hiểu, không cần phải tóm tắt hoặc thêm thông tin. Bỏ đi các phần dấu hiệu, chú thích, hoặc thông tin không cần thiết.
Hãy loại bỏ những dấu hiệu của heading bắt đầu bằng "###" và kết thúc bằng "###". Ví dụ: "###Chương 1###" hoặc "###1.1###".
Đừng thêm xuống dòng không cần thiết. Loại bỏ các heading và viết thành đoạn văn bình thường.

Dưới đây là đoạn văn bản cần được chuẩn hóa:
{text}

"""


import time

def add_summarize(text, summary):
    sleep_timer = 2
    while True:
        try:
            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_adding_summary_template.format(text=text, summary=summary, requirements=requirements),
                    }
                ],
                model=model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            print("Sleeping for", sleep_timer, "seconds")
            time.sleep(sleep_timer)
            sleep_timer *= 2

def combine_summaries(summary, new_summary):
    sleep_timer = 2
    while True:
        try:
            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_combine_summaries_template.format(summary=summary, new_summary=new_summary, requirements=requirements),
                    }
                ],
                model=model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            print("Sleeping for", sleep_timer, "seconds")
            time.sleep(sleep_timer)
            sleep_timer *= 2

def summarize(text):
    sleep_timer = 2
    while True:
        try:
            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_sumary.format(text=text, requirements=requirements),
                    }
                ],
                model=model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            print("Sleeping for", sleep_timer, "seconds")
            time.sleep(sleep_timer)
            sleep_timer *= 2

def normalize(text):
    sleep_timer = 2
    while True:
        try:
            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_normalize.format(text=text, requirements=requirements),
                    }
                ],
                model=model,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            print("Sleeping for", sleep_timer, "seconds")
            time.sleep(sleep_timer)
            sleep_timer *= 2


import math

class SparseTableSummarizer:
    def __init__(self, elements, name):
        self.elements = elements
        self.name = name
        self.summaries = []
        self.n = len(elements)
        print("Number of elements: ", self.n)
        self.k = 10
        self.st = [["" for i in range(self.k)] for j in range(self.n)]
    
    
        
    def to_dict(self):
        """Convert the object state to a JSON-serializable dictionary."""
        return {
            "elements": self.elements,
            "name": self.name,
            "summaries": self.summaries,
            "n": self.n,
            "k": self.k,
            "st": self.st
        }
    
    @staticmethod
    def from_dict(data):
        """Reconstruct the object from a dictionary."""
        obj = SparseTableSummarizer(data["elements"], data["name"])
        obj.summaries = data["summaries"]
        obj.n = data["n"]
        obj.k = data["k"]
        obj.st = data["st"]
        return obj
    
    def local_save(self):
        """Save the object state using JSON."""
        with open(f"{self.name}.json", "w") as f:
            json.dump(self.to_dict(), f)
        print(f"Object saved to {self.name}.json")
    
    @staticmethod
    def local_load(name):
        """Load the object state using JSON."""
        with open(f"{name}.json", "r") as f:
            data = json.load(f)
        print(f"Object loaded from {name}.json")
        return SparseTableSummarizer.from_dict(data)
    
    def process(self):

        print("process method called")

        for i in range(self.n):
            summary = summarize(self.elements[i])
            print(" len element:", len(self.elements[i]))
            self.summaries.append(summary)
            print("-------------Done adding summary for element: ", i)
            self.st[i][0] = summary
            
        for j in range(1, self.k):
            for i in range(self.n):
                if i + (1 << j) <= self.n:
                    self.st[i][j] = combine_summaries(self.st[i][j-1], self.st[i + (1 << (j-1))][j-1])
                    print(f"-------------Done combining summary for element: {i} and {j}")
                    
    def query(self, l, r, pretext = None, postText = None):
        print("-------------Query: ", end="")

        if (l == r):
            return self.st[l][0]
        
        len = r - l + 1
        k = 0
        while (1 << (k+1)) <= len:
            k += 1
            
        summarize = self.st[l][k]
        
        summarize = combine_summaries(summarize, self.st[r - (1 << k) + 1][k])
        
        if pretext is not None:
            summarize = add_summarize(pretext, summarize)
            print("-------------Done with element: ", "text")
            
        if postText is not None:
            summarize = add_summarize(summarize, postText)
            print("-------------Done with element: ", "text")
        return summarize
    
