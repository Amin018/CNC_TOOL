from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

# ======================================================
# USER SCHEMAS
# ======================================================

# Input schema for admin when creating a user
class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    full_name: str

class UserUpdate(BaseModel):
    # what admin is allowed to change (keep it minimal for now)
    role: str
    full_name: Optional[str]

# Output schema for returning user details
class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    full_name: Optional[str]

    class Config:
        orm_mode = True   # This allows SQLAlchemy objects to work with Pydantic

# ======================================================
# AUTHENTICATION SCHEMAS
# ======================================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# ======================================================
# CHANGEOVER REQUEST SCHEMAS
# ======================================================


class ChangeoverStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    RETURNED = "Returned"
    COMPLETED = "Completed"
    

class ChangeoverBase(BaseModel):
    production_line: str
    machine_no: str
    time_for_changeover: datetime
    current_part_no: str
    next_part_no: str

class ChangeoverCreate(ChangeoverBase):
    remark_request: Optional[str]

# ------------------------------
# Response Schema
# ------------------------------
class ChangeoverResponse(ChangeoverCreate):
    
    # Step tracking
    id: int
    requested_by: str
    time_requested: datetime

    concurred_by: Optional[str]
    time_concurred: Optional[datetime]

    acknowledged_by: Optional[str]
    time_acknowledged: Optional[datetime]

    tool_return_by: Optional[str]
    time_return: Optional[datetime]

    confirm_and_received_by: Optional[str]
    time_received: Optional[datetime]

    new_tool_by: Optional[str]
    time_prepared: Optional[datetime]

    completed_and_received_by: Optional[str]
    time_completed: Optional[datetime]

    remark_return: Optional[str]
    remark: Optional[str]

    status: ChangeoverStatus

    class Config:
        from_attributes = True  # ORM mode

class ChangeoverUpdate(BaseModel):
    remark_return: Optional[str] = None

class ChangeoverToolPrepare(BaseModel):
    remark: Optional[str] = None

class ChangeoverOut(ChangeoverBase):
    id: int
    time_requested: datetime

    class Config:
        orm_mode = True


# ======================================================
# Part SCHEMAS
# ======================================================

class PartBase(BaseModel):
    part_no: str
    description: Optional[str] = None
    package: Optional[str] = None

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    description: Optional[str] = None
    package: Optional[str] = None

class PartResponse(PartBase):
    id: int

    class Config:
        orm_mode = True

# ======================================================
# TOOL REQUEST SCHEMAS
# ======================================================

class ToolStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    COMPLETED = "Completed"

class ToolRequestBase(BaseModel):
    production_line: str
    machine_no: str
    part_no: str
    tool_name: str
    quantity: int

class ToolRequestCreate(ToolRequestBase):
    pass

class ToolRequestResponse(ToolRequestBase):
    id: int
    requested_by: str
    time_requested: datetime

    concurred_by: Optional[str]
    time_concurred: Optional[datetime]

    prepared_by: Optional[str]
    time_prepared: Optional[datetime]

    received_and_completed_by: Optional[str]
    time_completed: Optional[datetime]

    remark: Optional[str]

    status: ToolStatus

    class Config:
        from_attributes = True  # ORM mode

class ToolRequestUpdate(BaseModel):
    remark: Optional[str] = None


# ======================================================
# MACHINE SCHEMAS
# ======================================================

class MachineBase(BaseModel):
    production_line: str
    machine_no: str
    status: Optional[str] = "Active"

class MachineCreate(MachineBase):
    pass

class MachineResponse(MachineBase):
    id: int

    class Config:
        from_attributes = True

# ======================================================
# GENERIC RESPONSE / MESSAGE (optional)
# ======================================================

class Message(BaseModel):
    detail: str
