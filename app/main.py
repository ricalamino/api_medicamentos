from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import init_db, settings
from app.routes import medicamentos, auth, stats

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="API de Medicamentos do Brasil",
    description="API REST autenticada para consulta de medicamentos brasileiros registrados na ANVISA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Ensure UTF-8 encoding for JSON responses
@app.middleware("http")
async def ensure_utf8_middleware(request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(medicamentos.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(stats.router, prefix=settings.api_prefix)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    """Landing page: API info and self-service API key generation."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return {
        "message": "API de Medicamentos do Brasil",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
