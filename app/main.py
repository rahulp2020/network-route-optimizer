from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import APIError
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.database import Base, engine
from app.routers import edges, nodes, routes
from app.services.graph import GraphCache
from app.settings import get_settings

settings = get_settings()
logger = configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    app.state.graph_cache = GraphCache()
    yield


app = FastAPI(title=settings.title, version=settings.version, lifespan=lifespan)

app.add_middleware(RequestContextMiddleware)


@app.exception_handler(APIError)
async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    first_error = exc.errors()[0]
    loc = first_error["loc"]
    field = loc[-1] if len(loc) > 1 and isinstance(loc[-1], str) else None
    message = first_error["msg"].removeprefix("Value error, ")
    return JSONResponse(status_code=400, content={"error": f"{field}: {message}" if field else message})


app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(routes.router)
