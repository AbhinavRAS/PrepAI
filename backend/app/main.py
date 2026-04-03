from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.interview.router import router as interview_router

app = FastAPI(title="AI Smart Interview Agent")

# Add CORS middleware with proper OPTIONS handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Add explicit OPTIONS handler for preflight requests
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"status": "OK"}

app.include_router(interview_router, prefix="/interview")

@app.get("/")
def root():
    return {"status": "AI Interview Agent Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )