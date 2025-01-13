from RAG.RAG import *
from RAG.Embedding import *
from RAG.Retriever import *
from RAG.TextSplitter import *
from RAG.utils import find_txt_files, find_folders
load_dotenv()

def embedding():
    # Load environment variables
    connection_string = os.getenv('CONNECTION_STRING')
    print(f"Connection string: {connection_string}")
    

    # Initialize components
    textsplitter = TextSplitter(chunk_size=500)
    embedding_db = EmbeddingDatabase(connection_string, "AIrisBooks")
    

    # Optional: Reset the table
    # !!! Warning: This will delete the whole AIrisBooks collection !!!
    # embedding_db.delete_embeddings_table()
    # embedding_db.create_embeddings_table()


    # Embedding all txt files in the folder
    folder_path = "assets/book"
    folders = find_folders(folder_path)
    for book_name in folders:
        folder_path = os.path.join("assets/book", book_name)
        txt_files = find_txt_files(folder_path, include_subfolders=False)
        for file_name in txt_files:
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                text_chunks = textsplitter.get_text_chunks(text)
                embeddings_text = embedding_db.encode_text(text_chunks)
                embedding_db.store_embeddings(text_chunks, embeddings_text, book_title=book_name, block_id=file_name)
            print("\n")

    # Close connection
    embedding_db.close_connection()

def retriever(query="The quick brown fox jumps over the lazy dog"):
    # Load environment variables
    connection_string = os.getenv('CONNECTION_STRING')
    print(f"Connection string: {connection_string}")
    
    retriever = Retriever(connection_string, "AIrisBooks")
    # results = retriever.query_similar_texts(query, top_n=5)
    results = retriever.query_similar_texts_by_title(query, book_title="Thạch Sanh", top_n=5)
    for result in results:
        print(result)
        print("\n" + "-"*50 + "\n")
    
if __name__ == "__main__":
    # embedding()
    retriever("Thạch sanh giết chằn tinh")