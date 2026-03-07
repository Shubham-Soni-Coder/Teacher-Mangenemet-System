from fastapi import APIRouter, Request, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.core.dependencies import get_current_student
from app.database.session import get_db
from app.models import Student
from sqlalchemy.orm import Session
from app.utils.helpers import initials
import fastapi


# Initialize templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/dashboard", name="dashboard")
def show_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_student),
):
    student = db.query(Student).filter(Student.user_id == current_user).first()
    if not student:
        raise fastapi.HTTPException(status_code=404, detail="Student profile not found")

    student_data = {
        "name": student.name,
        "initials": initials(student.name),
    }

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "student": student_data}
    )
