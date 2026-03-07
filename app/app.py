"""
Main Application Module
=======================

This module initializes the FastAPI application and defines the route handlers.
It includes routes for authentication (login, register), dashboard views, and teacher functionalities.
"""

from fastapi import FastAPI, status, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.middleware import setup_middleware
from app.utils.auth_checker import redirect_by_user
from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.models import *  # Import all models to ensure they are registered with Base
from app.routers import attendance, auth, dashboard, teacher
from app.core.config import Settings


# load the data
JSON_DATA = Settings.JSON_DATA

app = FastAPI()

# make database
db = SessionLocal()

# Include Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(teacher.router)
app.include_router(attendance.router)

# Static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


# Templates
templates = Jinja2Templates(directory="templates")


from app.core.dependencies import NotAuthenticatedException, NotAuthorizedException

# add security
setup_middleware(app)


@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.exception_handler(NotAuthorizedException)
def permission_exception_handler(request: Request, exc: NotAuthorizedException):
    role = request.session.get("role")
    return redirect_by_user(role)


@app.on_event("startup")
def startup():
    from app.utils.seeder import DataBaseCreate

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    # Automatically seed the database if it's empty
    db = SessionLocal()
    try:
        start = DataBaseCreate(db)
        start.Create()
    finally:
        db.close()


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="/static/images/favicon.ico")
