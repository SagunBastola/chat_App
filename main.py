from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, Base
from routers import auth, chat, websockets
import models.user
import models.message
from fastapi.responses import JSONResponse
import traceback

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Chat Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc().split("\n")
        }
    )

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(websockets.router)
@app.get("/")
def root():
    return {"Message":"Welcome to the chat app"}
