from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine

from app.database import get_db, engine
from app import models, schemas, database
from app.models import ChangeoverStatus
from app.routers.auth import get_current_user, require_admin, require_leader, require_tool, require_user, require_role, require_leader_or_admin, require_tool_or_admin, require_user_or_leader  # assumes this returns current_user dict with role
from app.routers.auth import verify_password
import pytz, os

from app.email_utils import send_changeover_email, concur_done_email

malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")

router = APIRouter(prefix="/changeovers", tags=["Changeover"])

# ----- LIST ALL REQUESTS (Everyone) -----
@router.get("/", response_model=List[schemas.ChangeoverResponse])
def get_all_changeover_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Changeover).order_by(models.Changeover.id).all()

# ----- SEE REEQUST DETAILS (Everyone) -----
@router.get("/{changeover_id}", response_model=schemas.ChangeoverResponse)
def get_changeover_by_id(
    changeover_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    changeover = db.query(models.Changeover).filter(models.Changeover.id == changeover_id).first()
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    return changeover


# ----- Delete ALL Request (Admin) -----
@router.delete("/purge")
def purge_changeovers(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    if not verify_password(payload["password"], current_user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid password")
    
    dialect = engine.dialect.name

    if dialect == "sqlite":
        db.query(models.Changeover).delete()
    else:
        db.execute(text("TRUNCATE TABLE changeovers RESTART IDENTITY CASCADE"))

    db.commit()


# DELETE request (Admin)
@router.delete("/{changeover_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_changeover(
    changeover_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    request = db.query(models.Changeover).get(changeover_id)
    if not request:
        raise HTTPException(status_code=404, detail="request not found")
    db.delete(request)
    db.commit()
    return


# ----- CREATE REQUEST (User/Leader) -----
@router.post("/", response_model=schemas.ChangeoverResponse)
def create_changeover_request(
    background_tasks: BackgroundTasks,
    request: schemas.ChangeoverCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user_or_leader),
    
):
    new_request = models.Changeover(
        production_line=request.production_line,
        machine_no=request.machine_no,
        current_part_no=request.current_part_no,
        next_part_no=request.next_part_no,
        time_for_changeover=request.time_for_changeover,
        requested_by=current_user.username,  # username instead of ID
        time_requested=datetime.now(malaysia_tz).replace(tzinfo=None),  # Ensure timezone-naive datetime
        remark_request = request.remark_request
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    background_tasks.add_task(
        send_changeover_email,
        changeover_id=new_request.id,
        machine_name=request.machine_no,
        created_by=current_user.username
    )
    return new_request


# ----- CONCUR REQUEST (Leader/Admin) -----
@router.put("/{changeover_id}/concur", response_model=schemas.ChangeoverResponse)
def concur_changeover_request(
    background_tasks: BackgroundTasks,
    changeover_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_leader_or_admin)  # Admin/Leader only
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.concurred_by = current_user.username
    changeover.time_concurred = datetime.now(malaysia_tz).replace(tzinfo=None)

    db.commit()
    db.refresh(changeover)

    background_tasks.add_task(
        concur_done_email,
        changeover_id=changeover_id,
        machine_name=changeover.machine_no,
        concur_by=current_user.username
    )
    return changeover

# ----- Acknowledge REQUEST (Tool) -----
@router.put("/{changeover_id}/acknowledge", response_model=schemas.ChangeoverResponse)
def acknowledge_changeover_request(
    changeover_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_tool_or_admin)  # Admin/Leader only
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.acknowledged_by = current_user.username
    changeover.time_acknowledged = datetime.now(malaysia_tz).replace(tzinfo=None)
    changeover.status = ChangeoverStatus.IN_PROGRESS
    db.commit()
    db.refresh(changeover)
    return changeover

# ----- Tool Return (User) -----
@router.put("/{changeover_id}/toolreturn", response_model=schemas.ChangeoverResponse)
def tool_return_request(
    changeover_id: int,
    request: schemas.ChangeoverUpdate,  # <-- Accept remark here
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user_or_leader)
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.tool_return_by = current_user.username
    changeover.time_return = datetime.now(malaysia_tz).replace(tzinfo=None)
    # Save remark if provided
    if request.remark_return:
        changeover.remark_return = request.remark_return

    db.commit()
    db.refresh(changeover)
    return changeover

# ----- Tool Received (TOol) -----
@router.put("/{changeover_id}/toolreceived", response_model=schemas.ChangeoverResponse)
def tool_received_request(
    changeover_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_tool_or_admin)  # Admin/Leader only
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.confirm_and_received_by = current_user.username
    changeover.time_received = datetime.now(malaysia_tz).replace(tzinfo=None)
    changeover.status = ChangeoverStatus.RETURNED
    db.commit()
    db.refresh(changeover)
    return changeover

# ----- Tool Prepare (Tool) -----
@router.put("/{changeover_id}/toolprepare", response_model=schemas.ChangeoverResponse)
def tool_prepare_request(
    changeover_id: int,
    request: schemas.ChangeoverToolPrepare,  # <-- Accept remark here
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_tool_or_admin)  # User role
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.new_tool_by = current_user.username
    changeover.time_prepared = datetime.now(malaysia_tz).replace(tzinfo=None)

    # Save remark if provided
    if request.remark:
        changeover.remark = request.remark

    db.commit()
    db.refresh(changeover)
    return changeover

# ----- Request Completed (User) -----
@router.put("/{changeover_id}/toolcomplete", response_model=schemas.ChangeoverResponse)
def tool_complete_request(
    changeover_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user_or_leader) 
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.completed_and_received_by = current_user.username
    changeover.time_completed = datetime.now(malaysia_tz).replace(tzinfo=None)

    if changeover.concurred_by:
        changeover.status = ChangeoverStatus.COMPLETED
        
    db.commit()
    db.refresh(changeover)
    return changeover