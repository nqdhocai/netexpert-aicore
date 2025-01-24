from components.database.database import get_blog_by_query
import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
genai.configure(api_key=os.getenv('GEMINI_API'))

# Create the model
generation_config = {
  "temperature": 0.95,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)
def technical_chat(question):
    blog_ids, chunk_contents = get_blog_by_query(question)
    context = "/n/n ".join(chunk_contents)
    prompt = f"""
    Trả lời câu hỏi về kĩ thuật trong lĩnh vực mạng và thiết bị mạng dưới đây, sử dung thông tin được cung cấp dưới đây (nếu không có thông tin thì sử dụng kiến thức của bạn)
    ### Question
    {question}
    ### Contexts
    {context}
    """
    response = model.generate_content(prompt).text
    return {
        "response": response,
        "blogs": blog_ids
    }
