from pydantic import BaseModel
from typing import List

class BlogViewedModel(BaseModel):
    blog_id: int
    user_id: str
    viewed_blogs: List[int]

class RelatedBlog(BaseModel):
    blog_id: int
    similarity_score: float

class RelatedBlogResponse(BaseModel):
    related_blogs: List[RelatedBlog]