from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services import auth_service
from app.core.exceptions import CustomException
from app.utils.auth_checker import redirect_by_user

# Initialize templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/", name="login_page")
def show_form(request: Request):
    # Security check: exist session
    if request.session.get("auth") is True:
        role = request.session.get("role")
        return redirect_by_user(role)

    return templates.TemplateResponse("login_page.html", {"request": request})


@router.post("/login", name="login")
def login(
    request: Request,
    usergmail: str = Form(...),
    userpassword: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = auth_service.login_user(db, usergmail, userpassword, request.session)

        # Save user info in session
        request.session["user_id"] = user.id
        request.session["role"] = user.role
        request.session["auth"] = True

        if not user.role:
            raise CustomException("Invalid user role")

        return redirect_by_user(user.role)

    except CustomException as e:
        return templates.TemplateResponse(
            "login_page.html",
            {"request": request, "error": e.detail},
        )


@router.get("/logout", name="logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
