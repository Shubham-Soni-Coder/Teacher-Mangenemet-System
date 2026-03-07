from fastapi import APIRouter, Depends, HTTPException
from app.schemas import (
    AttendanceSubmitCreate,
    AttendanceItemCreate,
    AttendanceSessionCreate,
    AttendanceRecordCreate,
)
from app.models import AttendanceSession, AttendanceRecord, Student
from app.database.session import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api")


@router.post("/attendance")
def save_attendance(payload: AttendanceSubmitCreate, db: Session = Depends(get_db)):
    # 1. Find or create session
    session = (
        db.query(AttendanceSession)
        .filter(
            AttendanceSession.batch_id == payload.batch_id,
            AttendanceSession.date == payload.date,
            AttendanceSession.session_name == payload.session_type,
        )
        .first()
    )

    # check for session
    if not session:
        session_create = AttendanceSessionCreate(
            batch_id=payload.batch_id,
            date=payload.date,
            session_name=payload.session_type,
        )
        session = AttendanceSession(**session_create.model_dump())
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2. Save/Update attendance records
    for item in payload.attendance:
        # optional safety : check for the student beylong to class
        student = (
            db.query(Student)
            .filter(Student.id == item.student_id, Student.batch_id == payload.batch_id)
            .first()
        )

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        record = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_id == session.id,
                AttendanceRecord.student_id == item.student_id,
            )
            .first()
        )
        status = "present" if item.is_present else "absent"

        if record:
            record.status = status
        else:
            record_create = AttendanceRecordCreate(
                session_id=session.id, student_id=item.student_id, status=status
            )
            record = AttendanceRecord(**record_create.model_dump())
            db.add(record)
    db.commit()

    return {"message": "Attendance saved successfully", "session_id": session.id}
