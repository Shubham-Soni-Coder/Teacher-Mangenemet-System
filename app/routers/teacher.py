from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import calendar

from app.database.session import get_db
from app.models import Batches, Student, Teacher, ClassSchedule
from app.services import teacher_service
from app.utils.helpers import initials
from app.utils.timezone import now_ist
from app.core.config import Settings
from app.core.dependencies import get_current_teacher

# Initialize templates
templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/dashboard", name="teacher_dashboard")
def show_teacher_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_teacher),
):
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    teacher_data = {
        "full_name": teacher.full_name,
        "department": teacher.department,
        "initials": initials(teacher.full_name),
    }

    # Use Service Layer for Data
    now = now_ist()
    upcoming_classes_data = teacher_service.get_formatted_upcoming_classes(
        db, teacher.id, now.weekday() + 1, now.time()
    )
    stats = teacher_service.get_teacher_dashboard_stats(db, teacher.id)

    return templates.TemplateResponse(
        "teacher_dashboard.html",
        {
            "request": request,
            "teacher": teacher_data,
            "upcoming_classes": upcoming_classes_data,
            "stats": stats,
        },
    )


@router.get("/classes", name="teacher_classes")
def show_teacher_classes(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_teacher),
):
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    teacher_data = {
        "full_name": teacher.full_name,
        "department": teacher.department,
        "initials": initials(teacher.full_name),
    }

    return templates.TemplateResponse(
        "teacher_classes.html", {"request": request, "teacher": teacher_data}
    )


@router.get("/classes/details", name="teacher_class_details")
def show_teacher_class_details(
    request: Request,
    batch_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_teacher),
):
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    if not teacher_service.is_teacher_authorized(db, teacher.id, batch_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this batch")

    # Fetch batch info
    class_obj = db.query(Batches).filter(Batches.id == batch_id).first()

    # Get student list
    result = (
        db.query(Student.id, Student.name)
        .filter(Student.batch_id == batch_id)
        .order_by(Student.name.asc())
        .all()
    )
    student_data = [
        {
            "roll_no": i + 1,
            "student_id": row[0],
            "name": row[1],
            "initials": initials(row[1]),
        }
        for i, row in enumerate(result)
    ]

    return templates.TemplateResponse(
        "teacher_class_details.html",
        {
            "request": request,
            "students": student_data,
            "batch_id": batch_id,
            "batch_name": class_obj.batch_name if class_obj else "Unknown",
            "mode": "start",
            "teacher": {
                "full_name": teacher.full_name,
                "department": teacher.department,
                "initials": initials(teacher.full_name),
            },
        },
    )


@router.get("/students/data", name="get_student_data")
def get_student_data(
    request: Request,
    month: str,
    batch_id: int,
    search: str = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_teacher),
):
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher or not teacher_service.is_teacher_authorized(
        db, teacher.id, batch_id
    ):
        return []

    try:
        month_num = datetime.strptime(month, "%B").month
    except ValueError:
        return []

    return teacher_service.get_students_for_batch(
        db, batch_id, month_num, now_ist().year, search=search
    )


@router.get("/students", name="teacher_students")
def show_teacher_students(
    request: Request,
    batch_id: int = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_teacher),
):
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    batches_list, teacher_batches = teacher_service.get_teacher_batches_list(
        db, teacher.id
    )

    if not batch_id and batches_list:
        batch_id = batches_list[0]["id"]

    if batch_id and not teacher_service.is_teacher_authorized(db, teacher.id, batch_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this batch")

    current_batch_name = teacher_batches.get(batch_id, "No Batch Selected")
    now = now_ist()
    students_data = (
        teacher_service.get_students_for_batch(db, batch_id, now.month, now.year)
        if batch_id
        else []
    )

    return templates.TemplateResponse(
        "teacher_students.html",
        {
            "request": request,
            "students": students_data,
            "current_month_name": now.strftime("%B"),
            "teacher": {
                "full_name": teacher.full_name,
                "department": teacher.department,
                "initials": initials(teacher.full_name),
            },
            "batches": batches_list,
            "current_batch_id": batch_id,
            "current_batch_name": current_batch_name,
        },
    )


@router.get("/api/classes-list", name="get_all_classes_data")
def get_all_classes_data(
    search: str = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_teacher),
):
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        return []
    return teacher_service.get_all_classes_formatted(db, teacher.id, search=search)


@router.get("/api/global-search", name="get_global_search")
def get_global_search(
    search: str = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_teacher),
):
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        return {"students": [], "classes": []}
    return teacher_service.global_search(db, teacher.id, search=search)
