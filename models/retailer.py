from typing import List, Optional
from pydantic import BaseModel

class RetailerInfo(BaseModel):
    retailer: str
    location: str
    retailer_url: str

class RetailerList(BaseModel):
    retailers: List[RetailerInfo]

class RetailerRequest(BaseModel):
    device_id: str