from sqlalchemy.orm import Session
from datetime import datetime, date, time
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.schemas import (
    UserCreate,
    TeacherCreate,
    SubjectCreate,
    BatchesCreate,
    StudentCreate,
    BatchesSubjectCreate,
    FeesStructureCreate,
    FeesComponentCreate,
    FeesPaymentCreate,
    StudentFeesDueCreate,
    ClassScheduleCreate,
)
from app.models import (
    User,
    Teacher,
    Subject,
    Batches,
    Student,
    BatchSubject,
    FeesStructure,
    FeesComponent,
    StudentFeesDue,
    FeesPayment,
    ClassSchedule,
)
from app.core.security import hash_password
from app.utils.json_loader import load_json
from app.utils.helpers import normalize
from datetime import datetime

"""
All table : 
1. User : complet
2. Teachers : complet
3. subjects : complet
11. batches : complet
12. batch_subjects : complet
5. student_fes_due :complet
6. fees_structure : complet
7. fees_components : complet
8. fee_payments : complet
9. class_scheddules : complet
10. class_instances : complet
13. attendance_session
14. attendance_records
"""

# load the json data
Data = load_json()

# store in database
Base.metadata.create_all(bind=engine)

database = SessionLocal()


# create user table
class DataBaseCreate:
    def __init__(self, db: Session = database, JSON_DATA=Data) -> None:
        self.JSON_DATA = JSON_DATA
        self.db = db

    def CreateUser(self) -> None:
        data = {
            "student": {
                self.JSON_DATA["students"][i]["gmail"]: self.JSON_DATA["students"][i][
                    "password"
                ]
                for i in range(len(self.JSON_DATA["students"]))
            },
            "teacher": {
                self.JSON_DATA["teacher"][i]["gmail"]: self.JSON_DATA["teacher"][i][
                    "password"
                ]
                for i in range(len(self.JSON_DATA["teacher"]))
            },
        }

        for role, user in data.items():
            for email, password in user.items():
                # Check if user already exists
                existing_user = (
                    self.db.query(User).filter(User.gmail_id == email).first()
                )
                if not existing_user:
                    schems = UserCreate(
                        gmail_id=email,
                        hashed_password=hash_password(password),
                        is_active=True,
                        role=role,
                    )
                    model = User(**schems.model_dump())
                    self.db.add(model)
                    print(f"Adding user: {email} ({role})")
                else:
                    print(f"User {email} already exists.")
            self.db.commit()

    def CreateTeacher(self) -> None:
        teachers_data = self.JSON_DATA.get("teacher", [])

        # Debug print
        print(f"Found {len(teachers_data)} teachers in JSON")

        for teacher_info in teachers_data:
            email = teacher_info.get("gmail")
            name = teacher_info.get("name")
            department = teacher_info.get("department_name")

            # Find user by email to ensure correct mapping
            user = self.db.query(User).filter(User.gmail_id == email).first()

            if user:
                # Check if teacher profile already exists
                existing = (
                    self.db.query(Teacher).filter(Teacher.user_id == user.id).first()
                )
                if not existing:
                    try:
                        schems = TeacherCreate(
                            user_id=user.id,
                            full_name=name,
                            department=department,
                            is_active=True,
                            created_at=datetime.now(),
                        )
                        model = Teacher(**schems.model_dump())
                        self.db.add(model)
                        print(f"Adding teacher: {name}")
                    except Exception as e:
                        print(f"Error creating teacher {name}: {e}")
                else:
                    print(f"Teacher {name} already exists.")
            else:
                print(f"User with email {email} not found.")

        self.db.commit()

    def CreateStudent(self) -> None:
        student_data = self.JSON_DATA.get("students", [])
        batches = self.db.query(Batches).all()

        if not batches:
            print("No batches found. Please create batches first.")
            return

        for i, user_info in enumerate(student_data):
            batch_obj = batches[i % len(batches)]
            email = user_info.get("gmail")

            # Find user by email to get user_id
            user_rec = self.db.query(User).filter(User.gmail_id == email).first()

            if user_rec:
                # Check if student profile already exists
                existing_student = (
                    self.db.query(Student)
                    .filter(Student.user_id == user_rec.id)
                    .first()
                )
                if not existing_student:
                    try:
                        schems = StudentCreate(
                            user_id=user_rec.id,
                            name=user_info["name"],
                            father_name=user_info["father_name"],
                            mother_name=user_info["mother_name"],
                            roll_no=str(user_info["roll_no"]),
                            batch_id=batch_obj.id,
                        )
                        model = Student(**schems.model_dump())
                        self.db.add(model)
                        print(f"Adding student: {user_info['name']}")
                    except Exception as e:
                        print(f"Error creating student {user_info['name']}: {e}")
                else:
                    print(f"Student {user_info['name']} already exists.")
            else:
                print(f"User with email {email} not found for student profiling.")

        self.db.commit()

    def add_subject(self, name: str) -> None:
        # Check if subject already exists
        name = normalize(name)
        existing_subject = self.db.query(Subject).filter(Subject.name == name).first()
        if not existing_subject:
            try:
                schems = SubjectCreate(name=name)
                model = Subject(**schems.model_dump())
                self.db.add(model)
                print(f"Adding subject: {name}")
            except Exception as e:
                print(f"Error creating subject {name}: {e}")
        else:
            print(f"Subject {name} already exists.")

    def insert(
        self,
        batch_id: int,
        subject_name: str,
        category: str,
        stream: str | None,
        compulsory: bool,
        main: bool,
        batch_name: str = None,
    ) -> None:
        # Get subject
        subject = self.db.query(Subject).filter(Subject.name == subject_name).first()
        if not subject:
            # print(f"Subject '{subject_name}' not found. Skipping link.")
            return

        exists = (
            self.db.query(BatchSubject)
            .filter_by(batch_id=batch_id, subject_id=subject.id)
            .first()
        )

        if exists:
            print(
                f"Subject '{subject_name}' already linked to batch {batch_name or batch_id}."
            )
            return

        try:
            schems = BatchesSubjectCreate(
                batch_id=batch_id,
                subject_id=subject.id,
                category=category,
                stream=stream,
                is_compulsory=compulsory,
                is_main=main,
            )

            self.db.add(BatchSubject(**schems.model_dump()))
            self.db.flush()
            print(
                f"Linked subject {subject_name} to batch {batch_name or batch_id} ({category})"
            )
        except Exception as e:
            print(f"Error linking {subject_name} to batch {batch_id}: {e}")

    def CreateSubject(self) -> None:
        Subject_data = self.JSON_DATA["Subjects"]

        unique_subjects = set()

        # common
        for subject_name in Subject_data.get("Common", []):
            unique_subjects.add(subject_name)

        # optional
        for subject_name in Subject_data.get("Optional", []):
            unique_subjects.add(subject_name)

        # Stream
        for stream_subject in Subject_data.get("Streams", {}).values():
            for subject_name in stream_subject:
                unique_subjects.add(subject_name)

        # Add at once
        for name in unique_subjects:
            self.add_subject(normalize(name))
        self.db.commit()

    def CreateBatch(self) -> None:
        starting = ["1st", "2nd", "3rd"]
        after = [f"{i}th" for i in range(4, 13)]
        streams = ["non-medical", "medical", "arts", "commerce"]

        batches = starting + after

        for batch_name_label in batches:
            batch_level = int(batch_name_label[:-2])  # remove suffix
            # If <= 10, only one batch with stream=None, else multiple streams
            for stream in [None] if batch_level <= 10 else streams:
                # Check if batch already exists
                existing_batch = (
                    self.db.query(Batches)
                    .filter(
                        Batches.batch_name == batch_name_label, Batches.stream == stream
                    )
                    .first()
                )

                if not existing_batch:
                    schema = BatchesCreate(batch_name=batch_name_label, stream=stream)
                    self.db.add(Batches(**schema.model_dump()))
                    print(
                        f"Adding batch: {batch_name_label} ({stream if stream else 'No Stream'})"
                    )
                else:
                    print(
                        f"Batch {batch_name_label} ({stream if stream else 'No Stream'}) already exists."
                    )

        self.db.commit()

    def CreateBatchSubjects(self) -> None:
        subjects_json = self.JSON_DATA["Subjects"]
        batches = self.db.query(Batches).all()

        # Data mapping between data.json and our internal stream labels
        stream_map = {
            "medical": ("Science", "Medical"),
            "non-medical": ("Science", "Non-Medical"),
            "commerce": ("Commerce", "Core"),
            "arts": ("Humanities", "Core"),
        }

        for cls in batches:
            batch_label = f"{cls.batch_name} {cls.stream or ''}"

            # 1. Common subjects for all classes (1 to 12)
            for s in subjects_json.get("Common", []):
                self.insert(
                    cls.id, normalize(s), "common", cls.stream, True, True, batch_label
                )

            # 2. Optional Subjects for 6th to 12th
            batch_level = int(cls.batch_name[:-2])
            if batch_level >= 6:
                for s in subjects_json.get("Optional", []):
                    self.insert(
                        cls.id,
                        normalize(s),
                        "optional",
                        cls.stream,
                        False,
                        False,
                        batch_label,
                    )

            # 3. Stream-specific subjects for 11th and 12th
            if cls.stream and cls.stream in stream_map:
                top_key, sub_key = stream_map[cls.stream]

                # Add Main Stream Subjects
                stream_subjects = (
                    subjects_json.get("Streams", {}).get(top_key, {}).get(sub_key, [])
                )
                for s in stream_subjects:
                    self.insert(
                        cls.id,
                        normalize(s),
                        "stream",
                        cls.stream,
                        True,
                        True,
                        batch_label,
                    )

                # Add Stream-specific Optional Subjects (if any)
                stream_optional = (
                    subjects_json.get("Streams", {})
                    .get(top_key, {})
                    .get("Optional", [])
                )
                for s in stream_optional:
                    self.insert(
                        cls.id,
                        normalize(s),
                        "optional",
                        cls.stream,
                        False,
                        False,
                        batch_label,
                    )

        self.db.commit()

    def CreateFeesStructure(self) -> None:
        batches = self.db.query(Batches).all()
        academic_year = "2025-26"
        for cls in batches:
            # Check if fees structure already exists
            existing = (
                self.db.query(FeesStructure)
                .filter(
                    FeesStructure.batch_id == cls.id,
                    FeesStructure.academic_year == academic_year,
                )
                .first()
            )

            if not existing:
                try:
                    schesm = FeesStructureCreate(
                        batch_id=cls.id, academic_year=academic_year, is_active=True
                    )
                    model = FeesStructure(**schesm.model_dump())
                    self.db.add(model)
                    print(f"Adding fees structure for batch {cls.batch_name}")
                except Exception as e:
                    print(
                        f"Error creating fees structure for batch {cls.batch_name}: {e}"
                    )
            else:
                print(f"Fees structure for batch {cls.batch_name} already exists.")
        self.db.commit()

    def CreateFeesComponent(self) -> None:
        fees_json = self.JSON_DATA.get("fees_by_class", {})

        for raw_key, components in fees_json.items():
            parts = raw_key.split("_")
            level_val = parts[0]
            stream_val = parts[1] if len(parts) > 1 else None

            # Robust matching: try with suffixes (1st, 2nd, etc.)
            possible_names = [level_val]
            if not level_val.endswith(("st", "nd", "rd", "th")):
                if level_val == "1":
                    possible_names.append("1st")
                elif level_val == "2":
                    possible_names.append("2nd")
                elif level_val == "3":
                    possible_names.append("3rd")
                else:
                    possible_names.append(f"{level_val}th")

            batch = (
                self.db.query(Batches)
                .filter(
                    Batches.batch_name.in_(possible_names), Batches.stream == stream_val
                )
                .first()
            )

            if not batch:
                continue

            structure = (
                self.db.query(FeesStructure)
                .filter(
                    FeesStructure.batch_id == batch.id,
                    FeesStructure.academic_year == "2025-26",
                )
                .first()
            )

            if not structure:
                try:
                    schema = FeesStructureCreate(
                        batch_id=batch.id, academic_year="2025-26", is_active=True
                    )
                    structure = FeesStructure(**schema.model_dump())
                    self.db.add(structure)
                    self.db.flush()
                except Exception as e:
                    print(f"Error creating structure for {batch.batch_name}: {e}")
                    continue

            for comp in components:
                name = comp["component_name"]
                amount = comp["amount"]

                existing = (
                    self.db.query(FeesComponent)
                    .filter(
                        FeesComponent.fees_structure_id == structure.id,
                        FeesComponent.component_name == name,
                    )
                    .first()
                )

                if not existing:
                    try:
                        schema = FeesComponentCreate(
                            fees_structure_id=structure.id,
                            component_name=name,
                            amount=amount,
                        )
                        self.db.add(FeesComponent(**schema.model_dump()))
                        print(f"Added component {name} to {batch.batch_name}")
                    except Exception as e:
                        print(f"Error adding component {name}: {e}")
        self.db.commit()

    def CreateStudentFeesDue(self) -> None:
        from sqlalchemy import func

        students = self.db.query(Student).all()
        month = datetime.now().month
        year = datetime.now().year

        for student in students:
            fee_structure = (
                self.db.query(FeesStructure)
                .filter(
                    FeesStructure.batch_id == student.batch_id,
                    FeesStructure.academic_year == "2025-26",
                )
                .first()
            )

            if not fee_structure:
                continue

            total_amount = (
                self.db.query(func.sum(FeesComponent.amount))
                .filter(FeesComponent.fees_structure_id == fee_structure.id)
                .scalar()
                or 0
            )

            existing = (
                self.db.query(StudentFeesDue)
                .filter(
                    StudentFeesDue.student_id == student.id,
                    StudentFeesDue.month == month,
                    StudentFeesDue.year == year,
                )
                .first()
            )

            if not existing:
                try:
                    schema = StudentFeesDueCreate(
                        student_id=student.id,
                        month=month,
                        year=year,
                        total_amount=float(total_amount),
                        status="pending",
                    )
                    self.db.add(StudentFeesDue(**schema.model_dump()))
                    print(f"Created fee due for student {student.name}")
                except Exception as e:
                    print(f"Error creating fee due for student {student.id}: {e}")
        self.db.commit()

    def CreateFeesPayment(self) -> None:
        # Note: Student IDs are logic-dependent.
        # Using a safer approach: pay for any existing dues if needed,
        # but here we follow the user's list idea.
        student_ids = [21, 22, 23, 24, 25]

        due_records = (
            self.db.query(StudentFeesDue)
            .filter(StudentFeesDue.student_id.in_(student_ids))
            .all()
        )

        for due in due_records:
            existing = (
                self.db.query(FeesPayment).filter(FeesPayment.due_id == due.id).first()
            )
            if not existing:
                try:
                    schema = FeesPaymentCreate(
                        due_id=due.id,
                        amount_paid=4000.0,
                        discount_amount=0.0,
                        fine_amount=0.0,
                        method="online",
                        is_late=False,
                    )
                    self.db.add(FeesPayment(**schema.model_dump()))
                    print(f"Recorded payment for Due ID {due.id}")
                except Exception as e:
                    print(f"Error recording payment for due {due.id}: {e}")
            else:
                print(f"Payment for Due ID {due.id} already exists.")
        self.db.commit()

    def CreateClassSchedule(self) -> None:
        schedules_template = self.JSON_DATA["class_schedules"]

        # Clear old schedules to prevent duplicates/overlaps from previous runs
        self.db.query(ClassSchedule).delete()
        self.db.commit()
        print("Old class schedules cleared.")

        for data in schedules_template:
            # Loop for Monday (1) to Saturday (6)
            for day in range(1, 7):
                subject = (
                    self.db.query(Subject)
                    .filter(Subject.name == data["subject"])
                    .first()
                )

                if subject is None:
                    print(f"Subject '{data['subject']}' not found, skipping...")
                    continue

                start_t = datetime.strptime(data["start_time"], "%I:%M %p").time()
                end_t = datetime.strptime(data["end_time"], "%I:%M %p").time()

                schems = ClassScheduleCreate(
                    batch_id=data["batch_id"],
                    teacher_id=data["teacher_id"],
                    subject_id=subject.id,
                    day_of_week=day,
                    name=data["name"],
                    start_time=start_t,
                    end_time=end_t,
                )
                model = ClassSchedule(**schems.model_dump())
                self.db.add(model)
            self.db.commit()

    def Create(self) -> None:
        print("Starting Database Seeding...")
        self.CreateUser()
        self.CreateTeacher()
        self.CreateSubject()
        self.CreateBatch()
        self.CreateBatchSubjects()
        self.CreateFeesStructure()
        self.CreateFeesComponent()
        self.CreateStudent()
        self.CreateStudentFeesDue()
        self.CreateFeesPayment()
        self.CreateClassSchedule()
        print("Seeding Complete!")
