from typing import List
from pydantic import BaseModel

from models.network import Network


class ResponseModel(BaseModel):
    status: str
    response: str
    devices: List[str]  # Replace with List[Device] if needed
    networks: List[Network]
    blogs: List  # Replace with List[Blog] if needed