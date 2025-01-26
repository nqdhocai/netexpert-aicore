from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest
from models.response import ResponseModel
from chat import get_response

router = APIRouter()

@router.post("/api/v1/chat")
def get_recommendation(request: ChatRequest):
    try:
        location = request.location
        history = [i.model_dump() for i in request.history]
        response = get_response(history)
        return ResponseModel(**response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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