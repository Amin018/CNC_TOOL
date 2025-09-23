from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app import models, schemas, database
from app.models import ChangeoverStatus
from app.routers.auth import get_current_user, require_admin, require_leader, require_tool, require_user  # assumes this returns current_user dict with role
import pytz

malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")

router = APIRouter(prefix="/changeovers", tags=["Changeover"])

# ----- LIST ALL REQUESTS (Everyone) -----
@router.get("/", response_model=List[schemas.ChangeoverResponse])
def get_all_changeover_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Changeover).all()

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

# DELETE request (Admin)
@router.delete("/{changeover_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
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


# ----- CREATE REQUEST (User) -----
@router.post("/", response_model=schemas.ChangeoverResponse)
def create_changeover_request(
    request: schemas.ChangeoverCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user)
):
    new_request = models.Changeover(
        production_line=request.production_line,
        machine_no=request.machine_no,
        current_part_no=request.current_part_no,
        next_part_no=request.next_part_no,
        time_for_changeover=request.time_for_changeover,
        requested_by=current_user.username,  # username instead of ID
        time_requested=datetime.now(malaysia_tz),
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


# ----- CONCUR REQUEST (Leader/Admin) -----
@router.put("/{changeover_id}/concur", response_model=schemas.ChangeoverResponse)
def concur_changeover_request(
    changeover_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin or require_leader)  # Admin/Leader only
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.concurred_by = current_user.username
    changeover.time_concurred = datetime.now(malaysia_tz)
    db.commit()
    db.refresh(changeover)
    return changeover

# ----- Acknowledge REQUEST (Tool) -----
@router.put("/{changeover_id}/acknowledge", response_model=schemas.ChangeoverResponse)
def acknowledge_changeover_request(
    changeover_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_tool)  # Admin/Leader only
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.acknowledged_by = current_user.username
    changeover.time_acknowledged = datetime.now(malaysia_tz)
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
    current_user: models.User = Depends(require_user)  # User role
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.tool_return_by = current_user.username
    changeover.time_return = datetime.now(malaysia_tz)

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
    current_user: models.User = Depends(require_tool)  # Admin/Leader only
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.confirm_and_received_by = current_user.username
    changeover.time_received = datetime.now(malaysia_tz)
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
    current_user: models.User = Depends(require_tool)  # User role
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.new_tool_by = current_user.username
    changeover.time_prepared = datetime.now(malaysia_tz)

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
    current_user: models.User = Depends(require_user) 
):
    changeover = db.get(models.Changeover, changeover_id)
    if not changeover:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    changeover.completed_and_received_by = current_user.username
    changeover.time_completed = datetime.now(malaysia_tz)
    changeover.status = ChangeoverStatus.COMPLETED
    db.commit()
    db.refresh(changeover)
    return changeover