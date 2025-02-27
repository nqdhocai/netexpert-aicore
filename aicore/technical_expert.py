from components.database.database import get_blog_by_query
from .model import model

def technical_chat(question):
    blog_ids, chunk_contents = get_blog_by_query(question)
    context = "/n/n ".join(chunk_contents)
    prompt = f"""
    Answer the technical questions in the field of networking and network devices below, using the information provided below (if no information is provided, use your knowledge)
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
