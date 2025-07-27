from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.api import videos, comments, prompts_simple as prompts

load_dotenv()

app = FastAPI(
    title="コメント審判 API",
    description="YouTube動画のコメント分析API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "comment-umpire-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)