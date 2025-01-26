from pydantic import BaseModel

class Device(BaseModel):
    quantity: float
    id: str
    device_type: str
    name: str
    img_url: str