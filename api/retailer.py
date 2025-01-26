from fastapi import APIRouter, HTTPException
from models.retailer import RetailerList
from components.database.database import get_device_retailer_by_id

router = APIRouter()

@router.get("/api/v1/retailer")
def get_retailer(device_id: str):
    retailers = get_device_retailer_by_id(device_id)
    return RetailerList(retailers= retailers)