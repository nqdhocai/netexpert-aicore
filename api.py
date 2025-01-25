import os
import sys

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI, HTTPException
from model.chat import ChatRequest
from chat import get_response
import os
from pydantic import BaseModel
from typing import List

from components.database.database import get_related_blogs
# Model cho thiết bị (device)
class Device(BaseModel):
    quantity: float
    id: str
    device_type: str
    name: str
    img_url: str


# Model cho kết nối trong sơ đồ mạng (network diagram)
class NetworkDiagram(BaseModel):
    connection_to: List[str]
    device_id: str


# Model cho mạng (network)
class Network(BaseModel):
    type: str
    devices: List[Device]
    network_diagram: List[NetworkDiagram]
    cost: float


# Model chính cho response
class ResponseModel(BaseModel):
    status: str
    response: str
    devices: List  # Có thể thay thế bằng List[Device] nếu có dữ liệu cụ thể
    networks: List[Network]
    blogs: List  # Có thể thay thế bằng List[Blog] nếu có dữ liệu cụ thể

class BlogViewedModel(BaseModel):
    blog_id: int
    user_id: str
    viewed_blogs: List[int]

class RelatedBlog(BaseModel):
    blog_id: int
    similarity_score: float

class RelatedBlogResponse(BaseModel):
    related_blogs: List[RelatedBlog]

app = FastAPI()


@app.get('/')
def root():
    return {"message": "Hello World"}


@app.post("/api/v1/chat")
def get_recommendation(request: ChatRequest, response_model=ResponseModel):
    try:
        # Xử lý logic đề xuất dựa trên request
        location = request.location
        history = [i.model_dump() for i in request.history]

        response = get_response(history)
        # Trả về kết quả
        print(response)
        return ResponseModel(**response)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": "Lỗi xử lý từ AI-CORE"
            }
        )

@app.post("/api/v1/blog/related")
def related_blogs(request: BlogViewedModel, response_model=RelatedBlogResponse):
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

if __name__ == '__main__':
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 15085))
        uvicorn.run(app, host="0.0.0.0", port=port)

