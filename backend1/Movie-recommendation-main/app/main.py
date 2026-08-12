import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.connection import engine
from app.database.base import Base
from app.routes import movies, theaters, shows, seats, bookings, payments, ai, chat, group_recommend

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cinemate")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CineMate AI: Complete AI + Backend System for Smart Movie Ticket Booking",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(movies.router)
app.include_router(theaters.router)
app.include_router(shows.router)
app.include_router(seats.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(ai.router)
app.include_router(chat.router)
app.include_router(group_recommend.router)

@app.on_event("startup")
def startup_db_check():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified successfully on startup.")
    except Exception as e:
        logger.error(f"Error initializing DB tables: {e}")

@app.get("/health", tags=["Health"])
def health_check():
    """
    Service health check endpoint.
    """
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred. Please try again later."}
    )
