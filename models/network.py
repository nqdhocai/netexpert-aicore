from typing import List
from pydantic import BaseModel
from models.device import Device

class NetworkDiagram(BaseModel):
    connection_to: List[str]
    device_id: str

class Network(BaseModel):
    type: str
    devices: List[Device]
    network_diagram: List[NetworkDiagram]
    cost: float