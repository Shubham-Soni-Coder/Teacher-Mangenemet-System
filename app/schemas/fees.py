from pydantic import BaseModel


class FeesStructureCreate(BaseModel):
    batch_id: int
    academic_year: str
    is_active: bool


class FeesComponentCreate(BaseModel):
    fees_structure_id: int
    component_name: str
    amount: int


class StudentFeesDueCreate(BaseModel):
    student_id: int
    month: int
    year: int
    total_amount: float
    status: str


class FeesPaymentCreate(BaseModel):
    due_id: int
    amount_paid: float
    discount_amount: float
    fine_amount: float
    method: str
    is_late: bool
