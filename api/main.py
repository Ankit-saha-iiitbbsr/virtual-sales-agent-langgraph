from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routers import chat, history
import logging
import time
from typing import Callable
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Virtual Sales Agent API",
    description="API for virtual sales agent chat and history management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log the request
        logger.info(
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"Process Time: {process_time:.4f}s"
        )
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        process_time = time.time() - start_time
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={"X-Process-Time": str(process_time)}
        )

# Include routers
app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["chat"]
)
app.include_router(
    history.router,
    prefix="/api/chat",
    tags=["chat"]
)

# Root endpoint
@app.get("/", tags=["health"])
async def root():
    """Root endpoint for API health check"""
    return {
        "status": "healthy",
        "service": "Virtual Sales Agent API",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint"""
    try:
        # Add any additional health checks here (e.g., database connection)
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "api": "up",
                # Add other service statuses as needed
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": request.url.path
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute startup tasks"""
    logger.info("Starting up Virtual Sales Agent API")
    # Add any startup tasks here (e.g., initialize connections)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute shutdown tasks"""
    logger.info("Shutting down Virtual Sales Agent API")
    # Add any cleanup tasks here

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("API_PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload during development
        workers=1     # Number of worker processes
    )