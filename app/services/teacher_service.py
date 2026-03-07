from sqlalchemy import and_, func, extract, or_
from sqlalchemy.orm import Session
from app.models import (
    Student,
    StudentFeesDue,
    Batches,
    ClassSchedule,
    Teacher,
    Subject,
    AttendanceRecord,
    AttendanceSession,
)
from app.utils.helpers import initials
from app.utils.data_utils import get_total_days_in_month
from app.services.attendance_service import count_student_present_day
from datetime import time, datetime


def get_students_for_batch(
    db: Session, batch_id: int, month: int, year: int, search: str = None
):
    total_days = get_total_days_in_month(year, month)

    query = (
        db.query(Student, StudentFeesDue)
        .join(Batches, Student.batch_id == Batches.id)
        .outerjoin(
            StudentFeesDue,
            and_(
                Student.id == StudentFeesDue.student_id,
                StudentFeesDue.month == month,
                StudentFeesDue.year == year,
            ),
        )
        .filter(Batches.id == batch_id)
    )

    if search:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{search}%"),
                Student.father_name.ilike(f"%{search}%"),
            )
        )

    students = query.order_by(Student.name.asc()).all()
    if not students:
        return []

    student_ids = [s.id for s, _ in students]

    attendance_counts = (
        db.query(
            AttendanceRecord.student_id,
            func.count(AttendanceRecord.id).label("days_present"),
        )
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(
            AttendanceRecord.student_id.in_(student_ids),
            extract("year", AttendanceSession.date) == year,
            extract("month", AttendanceSession.date) == month,
            AttendanceRecord.status == "present",
        )
        .group_by(AttendanceRecord.student_id)
        .all()
    )

    attendance_map = {row.student_id: row.days_present for row in attendance_counts}

    students_data = []

    for index, (student, fees) in enumerate(students, start=1):
        days_present = attendance_map.get(student.id, 0)
        attendance_percentage = (
            round((days_present / total_days) * 100) if total_days > 0 else 0
        )

        students_data.append(
            {
                "serial_no": index,  # NOT roll_no (don’t lie)
                "name": student.name,
                "initials": initials(student.name),
                "father_name": student.father_name,
                "fees_paid": bool(fees and fees.status == "paid"),
                "days_present": days_present,
                "total_days": total_days,
                "attendance": attendance_percentage,
            }
        )

    return students_data


def get_teacher_dashboard_stats(db: Session, teacher_id: int):
    """Calculate dynamic stats for teacher dashboard"""
    total_classes = (
        db.query(func.count(ClassSchedule.id))
        .filter(ClassSchedule.teacher_id == teacher_id)
        .scalar()
    )

    # Get teacher's unique batches
    batch_ids = (
        db.query(ClassSchedule.batch_id)
        .filter(ClassSchedule.teacher_id == teacher_id)
        .distinct()
        .all()
    )
    batch_ids = [r[0] for r in batch_ids]

    total_students = (
        db.query(func.count(Student.id))
        .filter(Student.batch_id.in_(batch_ids))
        .scalar()
        if batch_ids
        else 0
    )

    return {
        "total_students": total_students,
        "active_classes": total_classes,
        "pending_review": 12,  # Placeholder
        "rating": 4.8,  # Placeholder
    }


def is_teacher_authorized(db: Session, teacher_id: int, batch_id: int) -> bool:
    """Verify if a teacher is assigned to a specific batch"""
    return (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.teacher_id == teacher_id, ClassSchedule.batch_id == batch_id
        )
        .first()
        is not None
    )


def get_teacher_batches_list(db: Session, teacher_id: int):
    """Get unique list of batches for a teacher"""
    schedules = (
        db.query(ClassSchedule).filter(ClassSchedule.teacher_id == teacher_id).all()
    )

    unique_batches = {}
    for s in schedules:
        if s.batch_id not in unique_batches:
            unique_batches[s.batch_id] = (
                f"{s.batch.batch_name} ({s.batch.stream})"
                if s.batch.stream
                else s.batch.batch_name
            )

    return [
        {"id": bid, "name": bname} for bid, bname in unique_batches.items()
    ], unique_batches


def get_formatted_upcoming_classes(
    db: Session, teacher_id: int, day: int, current_time: time
):
    schedules = (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.teacher_id == teacher_id,
            ClassSchedule.day_of_week == day,
            ClassSchedule.start_time > current_time,
        )
        .order_by(ClassSchedule.start_time.asc())
        .all()
    )

    formatted = []
    for cls in schedules:
        student_count = (
            db.query(func.count(Student.id))
            .filter(Student.batch_id == cls.batch_id)
            .scalar()
        )
        formatted.append(
            {
                "batch_id": cls.batch_id,
                "batch_name": cls.batch.batch_name if cls.batch else "Class",
                "subject": cls.subject.name if cls.subject else "N/A",
                "time": cls.start_time.strftime("%I:%M %p"),
                "student_count": student_count,
            }
        )
    return formatted


def get_all_classes_formatted(db: Session, teacher_id: int, search: str = None):
    query = (
        db.query(ClassSchedule)
        .join(Subject, ClassSchedule.subject_id == Subject.id)
        .filter(ClassSchedule.teacher_id == teacher_id)
    )

    if search:
        query = query.filter(
            or_(
                ClassSchedule.name.ilike(f"%{search}%"),
                Subject.name.ilike(f"%{search}%"),
            )
        )

    classes = query.all()

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    results = []

    for cls in classes:
        student_count = (
            db.query(func.count(Student.id))
            .filter(Student.batch_id == cls.batch_id)
            .scalar()
        )
        day_name = days[cls.day_of_week - 1] if 1 <= cls.day_of_week <= 7 else "Unknown"

        results.append(
            {
                "id": cls.batch_id,
                "name": cls.name,
                "subject": cls.subject.name if cls.subject else "N/A",
                "students": student_count,
                "time": (
                    f"{day_name} {cls.start_time.strftime('%I:%M %p')}"
                    if cls.start_time
                    else "N/A"
                ),
                "day_code": cls.day_of_week,
            }
        )
    return results


def get_active_classes(db: Session, teacher_id: int, day: int, current_time: time):
    """Get classes that are currently happening"""
    return (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.teacher_id == teacher_id,
            ClassSchedule.day_of_week == day,
            ClassSchedule.start_time <= current_time,
            ClassSchedule.end_time >= current_time,
        )
        .all()
    )


def get_upcoming_classes(db: Session, teacher_id: int, day: int, current_time: time):
    """Raw upcoming classes"""
    return (
        db.query(ClassSchedule)
        .filter(
            ClassSchedule.teacher_id == teacher_id,
            or_(
                ClassSchedule.day_of_week > day,
                and_(
                    ClassSchedule.day_of_week == day,
                    ClassSchedule.start_time > current_time,
                ),
            ),
        )
        .order_by(ClassSchedule.day_of_week.asc(), ClassSchedule.start_time.asc())
        .all()
    )


def global_search(db: Session, teacher_id: int, search: str):
    if not search:
        return {"students": [], "classes": []}

    # Search Classes/Batches
    classes_query = (
        db.query(ClassSchedule)
        .join(Subject, ClassSchedule.subject_id == Subject.id)
        .filter(ClassSchedule.teacher_id == teacher_id)
        .filter(
            or_(
                ClassSchedule.name.ilike(f"%{search}%"),
                Subject.name.ilike(f"%{search}%"),
            )
        )
        .limit(5)
        .all()
    )

    # Search Students (Only in batches this teacher teaches)
    students_query = (
        db.query(Student)
        .join(Batches, Student.batch_id == Batches.id)
        .join(ClassSchedule, ClassSchedule.batch_id == Batches.id)
        .filter(ClassSchedule.teacher_id == teacher_id)
        .filter(
            or_(
                Student.name.ilike(f"%{search}%"),
                Student.father_name.ilike(f"%{search}%"),
            )
        )
        .distinct()
        .limit(5)
        .all()
    )

    return {
        "classes": [
            {
                "id": c.batch_id,
                "name": c.name,
                "subject": c.subject.name if c.subject else "N/A",
                "type": "class",
            }
            for c in classes_query
        ],
        "students": [
            {
                "id": s.id,
                "name": s.name,
                "batch_id": s.batch_id,
                "initials": initials(s.name),
                "type": "student",
            }
            for s in students_query
        ],
    }
