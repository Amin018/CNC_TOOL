# app/models.py
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .database import Base
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Enum, Integer, func
import enum
import pytz

malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")


# ---------- USERS ----------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)  # user, leader, tool, admin
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(malaysia_tz))


# ---------- MACHINES ----------
class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    machine_no: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    production_line: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


# ---------- PARTS  ----------
class Part(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    part_no: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    package: Mapped[str | None] = mapped_column(String, nullable=True)



# ---------- CHANGEOVER REQUESTS ----------

# --- Enum for status ---
class ChangeoverStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"  # <-- match Enum name
    RETURNED = "Returned"
    COMPLETED = "Completed"

# --- Changeover model ---
class Changeover(Base):
    __tablename__ = "changeovers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    production_line: Mapped[str] = mapped_column(String(100))
    machine_no: Mapped[str] = mapped_column(String(100))
    time_for_changeover: Mapped[datetime] = mapped_column(DateTime)

    current_part_no: Mapped[str] = mapped_column(String(100))
    next_part_no: Mapped[str] = mapped_column(String(100))

    # Step tracking (by username)
    requested_by: Mapped[str] = mapped_column(String(100))
    time_requested: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(malaysia_tz))

    concurred_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_concurred: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    acknowledged_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_acknowledged: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tool_return_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_return: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    confirm_and_received_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_received: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    new_tool_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_prepared: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    completed_and_received_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_completed: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    remark_return: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ChangeoverStatus] = mapped_column(Enum(ChangeoverStatus), default=ChangeoverStatus.PENDING)


# ---------- TOOL REQUESTS ----------

# --- Enum for status ---
class ToolStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"  
    COMPLETED = "Completed"

# --- Tool Request model ---
class ToolRequest(Base):
    __tablename__ = "tool_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    machine_no: Mapped[str] = mapped_column(String(100))
    part_no: Mapped[str] = mapped_column(String(100))
    tool_name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer)

    requested_by: Mapped[str] = mapped_column(String(100))
    time_requested: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(malaysia_tz))

    concurred_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_concurred: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    prepared_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_prepared: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    received_and_completed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_completed: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ToolStatus] = mapped_column(Enum(ToolStatus), default=ToolStatus.PENDING)


# ---------- AUDIT LOGS ----------
"""class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "created_request"
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)"""
