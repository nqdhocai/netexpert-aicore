from components.database.database import get_all_blog, insert_blog_chunk
from components.retrieval.embedding import get_embedding_doc
import re

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import google.generativeai as genai 
from google.ai.generativelanguage_v1beta.types import content

# from dotenv import load_dotenv
# load_dotenv()
import os 

print(os.getenv('GEMINI_API'))

genai.configure(api_key=os.getenv('GEMINI_API'))
generation_config = {
  "temperature": 0.95,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

# Function to create function declarations
def create_function_declaration(name, description, required, properties):
    return genai.protos.FunctionDeclaration(
        name=name,
        description=description,
        parameters=content.Schema(
            type=content.Type.OBJECT,
            required=required,
            properties=properties,
        ),
    )

tools = [
    create_function_declaration(
        "get_blog_content",
        "clean the content from a blog markdown file, only stripping out special characters while preserving readability",
        ["content"],
        {"content": content.Schema(type=content.Type.STRING)}
    )
]

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    generation_config=generation_config,
    tools=[genai.protos.Tool(function_declarations=tools)],
    tool_config={'function_calling_config': 'ANY'},
)

def get_action(content):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(content)
    return (response.parts[0].function_call.name, dict(response.parts[0].function_call.args)) if response.parts[0].function_call else None

def chunk_text(text, chunk_size=200, overlap=20):
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start += chunk_size - overlap  # Dịch chuyển có overlap
    return chunks
def split_chunk(chunk, max_chunk_size=256, overlap=50):
    """ Chia chunk lớn thành các chunk nhỏ hơn với overlap """
    words = chunk.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = start + max_chunk_size
        chunk_part = words[start:end]
        chunks.append(" ".join(chunk_part))
        start += max_chunk_size - overlap  # Dịch chuyển với overlap
    
    return chunks
def combine_chunks(chunks, similarity_threshold=0.9, max_chunk_size=850, overlap=30):
    """
    Kết hợp các chunk có độ tương đồng cao thành một chunk duy nhất.
    Nếu chunk sau khi gộp quá lớn, nó sẽ bị chia lại.
    
    :param chunks: Danh sách các chunk văn bản
    :param similarity_threshold: Ngưỡng tương đồng (mặc định 0.85)
    :param max_chunk_size: Kích thước tối đa của một chunk sau khi gộp
    :param overlap: Số từ trùng lặp khi chia lại chunk lớn
    :return: Danh sách các chunk mới đã được gộp và tối ưu hóa
    """
    if not chunks:
        return []

    chunk_embs = [get_embedding_doc(chunk) for chunk in chunks]  # Tính embedding
    similarity_matrix = cosine_similarity(chunk_embs)  # Tính ma trận cosine similarity
    merged = set()  # Lưu các index đã gộp
    combined_chunks = []

    for i in range(len(chunks)):
        if i in merged:
            continue

        new_chunk = [chunks[i]]
        merged.add(i)

        for j in range(i + 1, len(chunks)):
            if j in merged:
                continue

            if similarity_matrix[i][j] >= similarity_threshold:
                new_chunk.append(chunks[j])
                merged.add(j)

        merged_chunk = " ".join(new_chunk)

        # Nếu chunk quá lớn, chia lại
        if len(merged_chunk.split()) > max_chunk_size:
            combined_chunks.extend(split_chunk(merged_chunk, max_chunk_size, overlap))
        else:
            combined_chunks.append(merged_chunk)

    return combined_chunks
def truncate_text(text, max_tokens=900):
    """ Giới hạn văn bản dưới ngưỡng cho phép của API (tối đa 10000 bytes) """
    words = text.split()
    if len(words) > max_tokens:
        return " ".join(words[:max_tokens])
    return text
def clean_text(text):
    """Loại bỏ ký tự đặc biệt, dấu xuống dòng thừa, và khoảng trắng"""
    text = re.sub(r'\s+', ' ', text)  # Xóa khoảng trắng thừa
    text = re.sub(r'[^\w\s]', '', text)  # Xóa ký tự đặc biệt
    return text.strip()

def insert_chunk(blog_id, title, content):
    chunks = chunk_text(content)
    print(len(chunks))
    combined_chunks = combine_chunks(chunks)
    print(len(combined_chunks))
    for chunk in combined_chunks:
        text = truncate_text(clean_text(f"###title \n {title} ###chunk content \n {chunk}"))
        try:
            emb = get_embedding_doc(text)
            insert_blog_chunk(blog_id, chunk, emb)
        except:
            print(len(text))

blogs = get_all_blog()
for blog in blogs:
    insert_chunk(blog[0], blog[1], blog[2])
    print(f"Done {blog[0]} !!!")