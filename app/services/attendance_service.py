from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models import AttendanceSession, AttendanceRecord

def count_student_present_day(db: Session, student_id: int, year: int, month: int) -> int:
    present_day = (
        db.query(func.count(distinct(AttendanceSession.date)))
        .join(AttendanceRecord, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.status == "present",
            func.strftime("%Y", AttendanceSession.date) == str(year),
            func.strftime("%m", AttendanceSession.date) == f"{month:02d}",
        )
        .scalar()
    )
    return present_day
