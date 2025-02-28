from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest
from models.response import ResponseModel
from chat import get_response, get_report_response

router = APIRouter()

@router.post("/api/v1/chat")
def get_recommendation(request: ChatRequest):
    try:
        location = request.location
        try:
            province, nation = location.split(", ")
        except:
            province = ""
            nation = "Global"
        history = [i.model_dump() for i in request.history]
        response = get_response(history, nation, province)
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

@router.post("/api/v1/chat/report")
def get_network_report(request: ChatRequest):
    try:
        history = [i.model_dump() for i in request.history]
        response = get_report_response(history)
        return response
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