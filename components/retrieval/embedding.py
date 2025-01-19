import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GEMINI_API'))
embedding_model = "models/text-embedding-004"


def get_embedding_doc(content: str):
    result = genai.embed_content(
        model=embedding_model,
        content=content,
        task_type="retrieval_document",
    )
    return result['embedding']


def get_embedding_query(query: str):
    result = genai.embed_content(
        model=embedding_model,
        content=query,
        task_type="retrieval_query",
    )
    return result['embedding']
