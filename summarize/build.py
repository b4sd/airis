import os
from groq import Groq
import dotenv


dotenv.load_dotenv()
# Initialize the Groq client with the API key


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")  # Correct environment variable key
)

def summarize_text(input_text: str, model: str = "llama3-8b-8192") -> str:
    """
    Summarizes the given input text using the Groq API.

    Args:
        input_text (str): The text to summarize.
        model (str): The model to use for summarization.

    Returns:
        str: The summarized text.
    """
    try:
        # Use the Groq API for summarization
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                    """Bạn là một trợ lý tóm tắt văn bản, giúp cô đọng nội dung từ câu truy vấn của người dùng thành một bản tóm tắt ngắn gọn và rõ ràng. 
                    Tập trung vào các khái niệm, nội dung chính và ý tưởng cốt lõi trong văn bản. Bỏ qua các chi tiết không cần thiết như bài tập, ví dụ minh họa, hoặc thông tin kém quan trọng.
                    
                    Đầu vào của người dùng sẽ là một văn bản hoặc câu truy vấn cần được tóm tắt. Hãy trả về kết quả dưới dạng văn bản ngắn gọn, trực tiếp truyền tải nội dung chính của văn bản đó.

                    Ví dụ:
                    Câu truy vấn của người dùng: Bạn có thể tóm tắt cuốn sách "Tư duy nhanh và chậm" không?
                    Kết quả: "Cuốn sách 'Tư duy nhanh và chậm' thảo luận về hai hệ thống tư duy: tư duy nhanh, trực giác và cảm tính; và tư duy chậm, logic và phân tích. Tác giả nhấn mạnh cách mà các sai lệch nhận thức và cảm xúc ảnh hưởng đến quyết định của con người."
                    """
                    )
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            model=model,
            stream=False,
        )

        # Extract and return the summary
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred during summarization: {e}"

# Example usage
if __name__ == "__main__":
    text_to_summarize = """
    Artificial intelligence (AI) is a branch of computer science that aims to create machines 
    that can perform tasks that would typically require human intelligence. These tasks include 
    learning, reasoning, problem-solving, perception, and language understanding.
    """
    summary = summarize_text(text_to_summarize)
    print("Original Text:", text_to_summarize)
    print("\nSummary:", summary)
