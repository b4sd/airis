from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI
from RAG.Retriever import Retriever

load_dotenv()

# Fetch environment variables
embedding_model_name = os.getenv('EMBEDDING_MODEL')
connection_string = os.getenv('CONNECTION_STRING')
openai_api_key = os.getenv('OPENAI_API_KEY')
SAMBANOVA_api_key = os.getenv('SAMBANOVA_API_KEY')

# Pydantic model to define the request body structure
class UserQuery(BaseModel):
    query: str

class RAGModel():
    def __init__(self):
        self.template_query = """
            Bạn là một trợ lý hữu ích đang giúp tôi trả lời các câu hỏi và yêu cầu cho người dùng.
            Hãy đưa ra câu trả lời với độ dài vừa phải — không quá ngắn, không quá dài — và điều chỉnh theo từng câu hỏi.
            Cố gắng tự trả lời trực tiếp nếu có thể. Chỉ đưa ra câu trả lời liên quan và chính xác.
            Nếu bạn không biết câu trả lời, hãy trả lời "Tôi không biết."
        """
        self.message_history = [{"role": "system", "content": self.template_query}]
        self.retriever = Retriever(connection_string, "AIrisBooks")
        self.client = OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=os.environ.get("SAMBANOVA_API_KEY"),
        )

    def _retrieve_top_document(self, user_query_text, top_n=5, top_k=5):
        top_documents = []
        results = self.retriever.query_similar_texts(user_query_text, top_n=top_n)
        
        # handle the retrieved documents with the same title, keep the one with the highest similarity and highest frequency
        results.sort(key=lambda x: x['similarity'], reverse=True)
        top_title = []
        for result in results:
            if result['title'] not in top_title:
                top_title.append((result['title'], 0))
            else:
                for i in range(len(top_title)):
                    if top_title[i][0] == result['title']:
                        top_title[i] = (result['title'], top_title[i][1] + 1)
        top_title.sort(key=lambda x: x[1], reverse=True)
        top_title = [title[0] for title in top_title]
        top_title = list(dict.fromkeys(top_title))
        
        # retrieved top documents based on the title, if the document is too long, get the nearby text chunks only
        for title in top_title:
            document = self.retriever.get_text_chunks_by_title(title=title)
            if len(document.split()) > 6000:
                idx = -1
                for result in results:
                    if result['title'] == title:
                        idx = result['id']
                        break
                if idx != -1:
                    document = self.retriever.get_nearby_text_chunks(title=title, id=idx)
            top_documents.append(document)
            
        return top_documents[:min(top_k+1, len(top_documents))]


    def _create_prompt(self, results, user_query_text):
        template_query_retrieval = """
            Hãy tham khảo vào thông tin sau để trả lời câu hỏi của người dùng nếu nội dung liên quan:
            {document}
            Câu hỏi của người dùng: {question}
        """
        document=""
        for i in range(len(results)):
            result = results[i]
            document += f"{i + 1}) {result}\n\n"
            
        prompt = template_query_retrieval.format(
            document=document,
            question=user_query_text
        )
        return prompt
    
    def get_completion(self, messages, model="Qwen2.5-72B-Instruct"):
        print(f"Messages: {messages}")
        user_query_text = messages.query
        results = self._retrieve_top_document(user_query_text, top_n=3, top_k = 1)
        prompt = self._create_prompt(results, messages)
        self.message_history.append({"role": "user", "content": prompt})
        print(f"Prompt: {prompt}")
        response = self.client.chat.completions.create(
            model=model,
            messages=self.message_history
        )
        return response.choices[0].message.content

if __name__ == "__main__":
    rag_model = RAGModel()
    user_query = UserQuery(query="Tư tưởng hồ chí minh là gì")
    response = rag_model.get_completion(messages = user_query)
    print(response)