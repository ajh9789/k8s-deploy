from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery import Celery
from fastapi.middleware.cors import CORSMiddleware
import os

# FastAPI 인스턴스 생성
app = FastAPI()

# CORS 설정 (브라우저에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포에선 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Celery 설정
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("model-api", broker=CELERY_BROKER_URL)
celery_app.conf.result_backend = CELERY_BROKER_URL

# 입력값 정의 (prompt + image_url 동시 수신)
class PromptRequest(BaseModel):
    prompt: str
    image_url: str | None = None

# 이미지 생성 요청 → 비동기 Task로 전달
@app.post("/api/generate-image")
async def generate_image(request: PromptRequest):
    task = celery_app.send_task("generate_image", args=[request.prompt, request.image_url])
    return {"task_id": task.id}

# 이미지 생성 상태 확인
@app.get("/api/result/{task_id}")
async def get_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "PENDING"}
    elif result.state == "SUCCESS":
        return {
            "status": "SUCCESS",
            "png_url": result.result.get("png_url"),
            "psd_url": result.result.get("psd_url")
        }
    elif result.state == "FAILURE":
        raise HTTPException(status_code=500, detail="Task failed")
    else:
        return {"status": result.state}
