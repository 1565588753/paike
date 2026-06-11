from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["系统"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "school-scheduling-backend"}


@router.get("/info")
def info():
    return {
        "name": "智慧教务与智能排课管理平台",
        "version": "1.0.0",
        "api_prefix": "/api/v1"
    }
