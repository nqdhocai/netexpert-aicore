import sys
import os

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI, HTTPException
from model.chat import ChatRequest
from chat import get_response
import os

app = FastAPI()

@app.get('/')
def root():
    return {"message": "Hello World"}

@app.post("/api/v1/chat")
def get_recommendation(request: ChatRequest):
    try:
        # Xử lý logic đề xuất dựa trên request
        user_id = request.user_id
        location = request.location
        history = [i.model_dump() for i in request.history]

        response = get_response(history)
        if user_id:
            response['user_id'] = user_id
        # Trả về kết quả
        return response

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

if __name__ == '__main__':
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 15085))
        uvicorn.run(app, host="0.0.0.0", port=port)
