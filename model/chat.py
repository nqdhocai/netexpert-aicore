from typing import List, Optional
from pydantic import BaseModel

# Model cho mỗi phần trong lịch sử
class HistoryItem(BaseModel):
    role: str
    parts: List[str]

# Model cho request body
class ChatRequest(BaseModel):
    user_id: Optional[int] = None
    location: str
    history: List[HistoryItem]