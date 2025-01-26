import os
import sys
from fastapi import FastAPI
import uvicorn
from api.chat import router as chat_router
from api.retailer import router as retailer_router
from api.blog import router as blog_router

# Add the root directory to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Include routers
app.include_router(chat_router)
app.include_router(retailer_router)
app.include_router(blog_router)

@app.get('/')
def root():
    return {"message": "Wellcome to NetExpert!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1585))
    uvicorn.run(app, host="0.0.0.0", port=port)