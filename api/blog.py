from fastapi import APIRouter
from models.blog import BlogViewedModel, RelatedBlogResponse
from components.database.database import get_related_blogs

router = APIRouter()

@router.post("/api/v1/blog/related")
def related_blogs(request: BlogViewedModel):
    blog_id = request.blog_id
    viewed_blogs = request.viewed_blogs
    viewed_blogs.append(blog_id)

    related_blogs = get_related_blogs(viewed_blogs)
    if len(related_blogs) > 5:
        related_blogs = related_blogs[:5]
    related_blogs = [
        {
            "blog_id": i[0],
            "similarity_score": i[1]
        } for i in related_blogs
    ]
    response = {
        "related_blogs": related_blogs
    }
    return RelatedBlogResponse(**response)