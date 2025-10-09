from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app import models, schemas, database
from app.utils import hash_password
from app.routers.auth import get_current_user, require_admin  # import auth dependency

import pandas as pd
from fastapi.responses import FileResponse
import os

from fastapi import BackgroundTasks


router = APIRouter(prefix="/admin", tags=["Admin"])


# Dependency: Only allow admins
'''def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return user'''


# CREATE user
@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# LIST users
@router.get("/users", response_model=List[schemas.UserResponse])
def list_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    return db.query(models.User).all()


# GET user by id
@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# UPDATE user (role only)
@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


# DELETE user
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return


from datetime import datetime, timedelta
from fastapi import Query

from datetime import datetime, timedelta
from fastapi import Query

@router.get("/export/changeovers")
def export_changeovers_to_csv(
    background_tasks: BackgroundTasks,
    period: str = Query("all", enum=["daily", "weekly", "monthly", "all"]),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    # Base query
    query = db.query(models.Changeover)

    # Get current time
    now = datetime.now()

    # Filter by period
    if period == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(models.Changeover.time_requested >= start_date)
    elif period == "weekly":
        start_date = now - timedelta(days=7)
        query = query.filter(models.Changeover.time_requested >= start_date)
    elif period == "monthly":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(models.Changeover.time_requested >= start_date)

    changeovers = query.all()

    # Convert to list of dicts
    data = [
        {
            "id": c.id,
            "status": c.status,
            "production_line": c.production_line,
            "machine_no": c.machine_no,
            "time_for_changeover": c.time_for_changeover.strftime("%Y-%m-%d %H:%M:%S") if c.time_for_changeover else None,
            "current_part_no": c.current_part_no,
            "next_part_no": c.next_part_no,

            "requested_by": c.requested_by,
            "time_requested": c.time_requested.strftime("%Y-%m-%d %H:%M:%S") if c.time_requested else None,
            "concurred_by": c.concurred_by,
            "time_concurred": c.time_concurred.strftime("%Y-%m-%d %H:%M:%S") if c.time_concurred else None,
            "acknowledged_by": c.acknowledged_by,
            "time_acknowledged": c.time_acknowledged.strftime("%Y-%m-%d %H:%M:%S") if c.time_acknowledged else None,

            "returned_by": c.tool_return_by,
            "time_return": c.time_return.strftime("%Y-%m-%d %H:%M:%S") if c.time_return else None,
            "confirm_and_received_by": c.confirm_and_received_by,
            "tool_return_by": c.tool_return_by,

            "new_tool_by": c.new_tool_by,
            "time_prepared": c.time_prepared.strftime("%Y-%m-%d %H:%M:%S") if c.time_prepared else None,
            "completed_and_received_by": c.completed_and_received_by,
            "time_completed": c.time_completed.strftime("%Y-%m-%d %H:%M:%S") if c.time_completed else None,

            "remark_return": c.remark_return,
            "remark": c.remark
        }
        for c in changeovers
    ]

    # Save to CSV
    file_path = f"changeovers_export_{period}.csv"
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    #print(f"Saving CSV at {file_path}")
    #background_tasks.add_task(lambda: print(f"Deleting {file_path}"))
    background_tasks.add_task(os.remove, file_path)

    # Return file with delete after response
    return FileResponse(
        path=file_path,
        filename=file_path,
        media_type="text/csv",
        background=background_tasks
    )

@router.get("/export/tools")
def export_tool_to_csv(
    background_tasks: BackgroundTasks,
    period: str = Query("all", enum=["daily", "weekly", "monthly", "all"]),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    # Base query
    query = db.query(models.ToolRequest)

    # Get current time
    now = datetime.now()

    # Filter by period
    if period == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(models.ToolRequest.time_requested >= start_date)
    elif period == "weekly":
        start_date = now - timedelta(days=7)
        query = query.filter(models.ToolRequest.time_requested >= start_date)
    elif period == "monthly":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(models.ToolRequest.time_requested >= start_date)

    tools = query.all()

    # Convert to list of dicts
    data = [
        {
            "id": c.id,
            "status": c.status,
            "production_line": c.production_line,
            "machine_no": c.machine_no,
            "part_no": c.part_no,
            "tool_name": c.tool_name,
            "quantity": c.quantity,


            "requested_by": c.requested_by,
            "time_requested": c.time_requested.strftime("%Y-%m-%d %H:%M:%S") if c.time_requested else None,
            "concurred_by": c.concurred_by,
            "time_concurred": c.time_concurred.strftime("%Y-%m-%d %H:%M:%S") if c.time_concurred else None,

            "prepared_by": c.prepared_by,
            "time_prepared": c.time_prepared.strftime("%Y-%m-%d %H:%M:%S") if c.time_prepared else None,
            "completed_and_received_by": c.received_and_completed_by,
            "time_completed": c.time_completed.strftime("%Y-%m-%d %H:%M:%S") if c.time_completed else None,

            "remark": c.remark
        }
        for c in tools
    ]

    # Save to CSV
    file_path = f"toolsRequest_export_{period}.csv"
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    #print(f"Saving CSV at {file_path}")
    #background_tasks.add_task(lambda: print(f"Deleting {file_path}"))
    background_tasks.add_task(os.remove, file_path)

    # Return file with delete after response
    return FileResponse(
        path=file_path,
        filename=file_path,
        media_type="text/csv",
        background=background_tasks
    )
