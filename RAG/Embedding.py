import psycopg2
from psycopg2.extras import execute_values
from openai import OpenAI
import os
from dotenv import load_dotenv

class EmbeddingDatabase:
    def __init__(self, conn_string, collection_name):
        load_dotenv()
        self.conn_string = conn_string
        self.collection_name = collection_name
        self.conn, self.cur = self.__get_db_connection()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def __get_db_connection(self):
        """Establishes a connection to PostgreSQL and returns the connection and cursor."""
        print(f"Connecting to database: {self.conn_string}")
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        return conn, cur

    def encode_text(self, texts):
        """Encodes text into embeddings using the OpenAI API."""
        results = []
        try:
            for text in texts:
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",  # Adjust model as needed
                    input=text
                )
                results.append(response.data[0].embedding)
            return results
        except Exception as e:
            print(f"Error during embedding generation: {e}")
            return []

    def create_embeddings_table(self):
        """Creates a table to store text chunks and their embeddings."""
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.collection_name} (
                id SERIAL PRIMARY KEY,
                book_title TEXT,
                block_id TEXT,
                text_chunk TEXT,
                embedding VECTOR(1536)  -- OpenAI small model returns 1536 dimensions
            );
        """)
        self.conn.commit()

    def delete_embeddings_table(self):
        """Deletes the embeddings table if it exists."""
        self.cur.execute(f"DROP TABLE IF EXISTS {self.collection_name};")
        self.conn.commit()
        print(f"{self.collection_name} table deleted successfully.")

    def store_embeddings(self, text_chunks, embeddings, book_title="", block_id=""):
        """Stores embeddings in the database using batch insert."""
        values = [(book_title, block_id, chunk, embedding) 
                  for chunk, embedding in zip(text_chunks, embeddings)]
        insert_query = f"""
            INSERT INTO {self.collection_name} (book_title, block_id, text_chunk, embedding) 
            VALUES %s;
        """
        execute_values(self.cur, insert_query, values)
        self.conn.commit()

    def close_connection(self):
        """Closes the database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()