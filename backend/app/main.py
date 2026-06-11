from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from .core.config import settings
from .api.v1.endpoints import auth, teachers, basic, years, hr, timetable, swap, stats, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="智慧教务与智能排课管理平台 - 后端 API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/")
def root():
    return {"message": settings.APP_NAME, "docs": "/docs"}


# 路由注册
prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix)
app.include_router(teachers.router, prefix=prefix)
app.include_router(basic.router, prefix=prefix)
app.include_router(years.router, prefix=prefix + "/years")
app.include_router(hr.router, prefix=prefix)
app.include_router(timetable.router, prefix=prefix + "/timetable")
app.include_router(swap.router, prefix=prefix + "/swaps")
app.include_router(stats.router, prefix=prefix)
app.include_router(system.router, prefix=prefix)
