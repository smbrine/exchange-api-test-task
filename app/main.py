from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import settings
from app.v1 import router as v1_router
from app.dependencies import r


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    print(f"Starting FastAPI version: {fastapi_app.version}")
    await r.check_connection()
    yield


app = FastAPI(
    root_path="/api", version=settings.APP_VERSION, lifespan=lifespan
)


@app.get("/", include_in_schema=False)
async def handle_get_root():
    return RedirectResponse(url="/api/docs")


app.include_router(
    v1_router,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.BIND_HOST,
        port=settings.BIND_PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
