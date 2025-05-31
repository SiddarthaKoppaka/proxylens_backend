from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.app import router as api_router

app = FastAPI(title="RAG Backend API", version="1.0.0")

# Enable CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"message": "RAG Backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
