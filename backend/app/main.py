from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.character import character_router
from app.api.routes import router
from app.api.websocket import ws_router
from app.api.world_builder import world_builder_router
from app.graph.connection import get_driver, close_driver
from app.graph.schema import ensure_schema
from app.utils.llm import close_client
from app.utils.logger import get_logger

log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting_up")
    driver = get_driver()
    await ensure_schema(driver)
    log.info("schema_ready")
    yield
    log.info("shutting_down")
    await close_client()
    await close_driver()


app = FastAPI(
    title="Living World Engine",
    description="AI Dungeon Master with living world simulation",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(ws_router)
app.include_router(world_builder_router)
app.include_router(character_router)
