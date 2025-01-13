import psycopg2
from openai import OpenAI
import os

class Retriever:
    def __init__(self, conn_string, collection_name):
        """
        Initializes the Retriever with a database connection and OpenAI client.

        Args:
            conn_string (str): PostgreSQL connection string.
            collection_name (str): Name of the table storing embeddings.
        """
        self.conn_string = conn_string
        self.collection_name = collection_name
        self.conn, self.cur = self.__get_db_connection()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def __get_db_connection(self):
        """
        Establishes a connection to PostgreSQL and returns the connection and cursor.

        Returns:
            tuple: (connection, cursor)
        """
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        return conn, cur

    def encode_text(self, texts):
        """
        Encodes a list of texts into embeddings using the OpenAI API.

        Args:
            texts (list): List of text strings to encode.

        Returns:
            list: List of embeddings (1536-dimensional vectors).
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # OpenAI's small embedding model
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Error during embedding generation: {e}")
            return []

    def query_similar_texts(self, query_text, top_n=5):
        """
        Retrieves the most similar text chunks based on cosine similarity.

        Args:
            query_text (str): The query text to compare against stored embeddings.
            top_n (int): Number of similar texts to retrieve.

        Returns:
            list: List of dictionaries containing id, book_title, block_id, text_chunk, and similarity score.
        """
        try:
            # Encode the query text
            query_embedding = self.encode_text([query_text])[0]
            query_embedding_vector = f'[{",".join(map(str, query_embedding))}]'

            # Query the database for similar texts
            self.cur.execute(f"""
                SELECT id, book_title, block_id, text_chunk, embedding <=> %s::vector AS similarity
                FROM {self.collection_name}
                ORDER BY similarity ASC
                LIMIT %s;
            """, (query_embedding_vector, top_n))

            # Fetch and format results
            results = self.cur.fetchall()
            return [{"id": row[0], "book_title": row[1], "block_id": row[2], "text_chunk": row[3], "similarity": row[4]} for row in results]
        except Exception as e:
            print(f"Error querying similar texts: {e}")
            return []

    def query_similar_texts_by_title(self, query_text, book_title, top_n=5):
        """
        Retrieves the most similar text chunks based on cosine similarity for a specific book title.

        Args:
            query_text (str): The query text to compare against stored embeddings.
            book_title (str): The title of the book to filter the results.
            top_n (int): Number of similar texts to retrieve.

        Returns:
            list: List of dictionaries containing id, book_title, block_id, text_chunk, and similarity score.
        """
        try:
            # Encode the query text
            query_embedding = self.encode_text([query_text])[0]
            query_embedding_vector = f'[{",".join(map(str, query_embedding))}]'

            # Query the database for similar texts within the specified book title
            self.cur.execute(f"""
                SELECT id, book_title, block_id, text_chunk, embedding <=> %s::vector AS similarity
                FROM {self.collection_name}
                WHERE book_title = %s
                ORDER BY similarity ASC
                LIMIT %s;
            """, (query_embedding_vector, book_title, top_n))

            # Fetch and format results
            results = self.cur.fetchall()
            return [{"id": row[0], "book_title": row[1], "block_id": row[2], "text_chunk": row[3], "similarity": row[4]} for row in results]
        except Exception as e:
            print(f"Error querying similar texts by title: {e}")
            return []

    def get_text_chunks_by_title(self, book_title):
        """
        Retrieves and merges all text chunks for a given book title, ordered by ID.

        Args:
            book_title (str): The title of the book to retrieve text chunks for.

        Returns:
            str: Merged text chunks as a single string.
        """
        try:
            self.cur.execute(f"""
                SELECT text_chunk
                FROM {self.collection_name}
                WHERE book_title = %s
                ORDER BY id ASC;
            """, (book_title,))

            # Fetch and merge text chunks
            rows = self.cur.fetchall()
            merged_text = " ".join([row[0] for row in rows])
            return merged_text
        except Exception as e:
            print(f"Error retrieving text chunks by title: {e}")
            return ""

    def get_nearby_text_chunks(self, chunk_id, book_title, near=1):
        """
        Retrieves nearby text chunks for a given chunk ID and book title.

        Args:
            chunk_id (int): The ID of the reference text chunk.
            book_title (str): The title of the book.
            near (int): Number of chunks to retrieve on either side of the reference chunk.

        Returns:
            str: Merged nearby text chunks as a single string.
        """
        try:
            # Calculate the range of chunks to retrieve
            left_bound = max(chunk_id - near, 1)
            right_bound = chunk_id + near

            # Query nearby text chunks
            self.cur.execute(f"""
                SELECT text_chunk
                FROM {self.collection_name}
                WHERE book_title = %s AND id BETWEEN %s AND %s
                ORDER BY id ASC;
            """, (book_title, left_bound, right_bound))

            # Fetch and merge nearby text chunks
            rows = self.cur.fetchall()
            merged_text = " ".join([row[0] for row in rows])
            return merged_text
        except Exception as e:
            print(f"Error retrieving nearby text chunks: {e}")
            return ""

    def close_connection(self):
        """Closes the database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()