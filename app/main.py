# File: app/main.py (UPDATED WITH ALL FEATURES)
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime, timedelta
from starlette.middleware.sessions import SessionMiddleware
import os
from pathlib import Path

from app.database import get_db, init_db, User, UserPreferences, DigestHistory
from app.services.user_service import UserService
from app.services.scheduler_service import SchedulerService
from app.services.digest_generator import DigestGenerator
from app.services.email_service import EmailService

# Create FastAPI app
app = FastAPI(title="Dev Digest", version="1.0.0")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key-here"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize services
user_service = UserService()
scheduler_service = SchedulerService()
email_service = EmailService()

# Authentication dependency
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return user_service.get_user_by_id(db, user_id)

def require_auth(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# Admin authentication
def require_admin(request: Request):
    if not request.session.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return True

@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler"""
    init_db()
    scheduler_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on shutdown"""
    scheduler_service.stop()

# Health endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Routes with explicit names
@app.get("/", response_class=HTMLResponse, name="index")
async def home(request: Request):
    """Landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", name="login")
async def login(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login user"""
    try:
        user = user_service.login_user(db, email)
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    except ValueError as e:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": str(e)
        })

@app.get("/signup", response_class=HTMLResponse, name="signup_page")
async def signup_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", name="signup")
async def signup(
    request: Request,
    name: str = Form(...),
    github_username: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create new user"""
    try:
        user = user_service.create_user(db, name, github_username, email)
        
        # Send welcome email
        try:
            email_service.send_welcome_email(user.email, user.name)
        except Exception as e:
            print(f"Error sending welcome email: {e}")
        
        # Generate and send first digest
        try:
            digest_generator = DigestGenerator()
            await digest_generator.generate_and_send_digest(db, user.id, is_welcome=True)
        except Exception as e:
            print(f"Error sending welcome digest: {e}")
        
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    except ValueError as e:
        return templates.TemplateResponse("signup.html", {
            "request": request, 
            "error": str(e)
        })

@app.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard(request: Request, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """User dashboard"""
    history = user_service.get_digest_history(db, user.id, limit=5)
    stats = user_service.get_user_stats(db, user.id)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "history": history,
        "stats": stats
    })

@app.get("/settings", response_class=HTMLResponse, name="settings_page")
async def settings_page(request: Request, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """User settings page"""
    preferences = user_service.get_user_preferences(db, user.id)
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": user,
        "preferences": preferences
    })

@app.post("/settings", name="settings")
async def update_settings(
    request: Request,
    repositories: str = Form(""),
    languages: str = Form(""),
    stackoverflow_tags: str = Form(""),
    digest_time: str = Form("20:00"),
    timezone: str = Form("UTC"),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    try:
        user_service.update_preferences(
            db, user.id, repositories, languages, 
            stackoverflow_tags, digest_time, timezone
        )
        return RedirectResponse(url="/settings?success=1", status_code=status.HTTP_302_FOUND)
    except ValueError as e:
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "user": user,
            "error": str(e)
        })

@app.post("/toggle-service", name="toggle_service")
async def toggle_service(request: Request, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Toggle user service active/inactive"""
    user_service.toggle_user_status(db, user.id)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.get("/logout", name="logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# Unsubscribe functionality
@app.get("/unsubscribe/{token}", name="unsubscribe")
async def unsubscribe(token: str, db: Session = Depends(get_db)):
    """Unsubscribe user via token"""
    try:
        user = user_service.unsubscribe_user(db, token)
        return templates.TemplateResponse("unsubscribe.html", {
            "request": None,
            "success": True,
            "user_name": user.name
        })
    except ValueError as e:
        return templates.TemplateResponse("unsubscribe.html", {
            "request": None,
            "success": False,
            "error": str(e)
        })

# Admin routes
@app.get("/admin/login", response_class=HTMLResponse, name="admin_login_page")
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})

@app.post("/admin/login", name="admin_login")
async def admin_login(
    request: Request,
    password: str = Form(...)
):
    """Admin login"""
    if password == os.getenv("ADMIN_PASSWORD", "admin123"):
        request.session["is_admin"] = True
        return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    else:
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Invalid password"
        })

@app.get("/admin", response_class=HTMLResponse, name="admin_dashboard")
async def admin_dashboard(request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """Admin dashboard"""
    users = user_service.get_all_users(db)
    system_health = scheduler_service.get_system_health()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "users": users,
        "system_health": system_health
    })

@app.get("/admin/logout", name="admin_logout")
async def admin_logout(request: Request):
    """Admin logout"""
    request.session.pop("is_admin", None)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# API endpoints
@app.post("/api/trigger-digest/{user_id}")
async def trigger_digest(user_id: int, db: Session = Depends(get_db)):
    """Manually trigger digest for user"""
    digest_generator = DigestGenerator()
    result = await digest_generator.generate_and_send_digest(db, user_id)
    return {"success": result, "user_id": user_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)