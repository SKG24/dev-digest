# File: app/middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
from typing import Callable

logger = logging.getLogger("dev_digest.middleware")

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request timing"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log slow requests
        if process_time > 1.0:
            logger.warning(f"Slow request: {request.method} {request.url} took {process_time:.2f}s")
        
        response.headers["X-Process-Time"] = str(process_time)
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: times for ip, times in self.clients.items()
            if any(t > current_time - self.period for t in times)
        }
        
        # Check rate limit
        if client_ip in self.clients:
            recent_calls = [t for t in self.clients[client_ip] if t > current_time - self.period]
            if len(recent_calls) >= self.calls:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
            self.clients[client_ip] = recent_calls + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)