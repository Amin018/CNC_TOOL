from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app import models, schemas, database
from app.models import ToolStatus
from app.routers.auth import get_current_user, require_admin, require_leader, require_tool, require_user, require_user_or_leader, require_leader_or_admin, require_tool_or_admin  # assumes this returns current_user dict with role
import pytz


router = APIRouter(prefix="/tools", tags=["Tools"])
malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")

# ----- LIST ALL REQUESTS (Everyone) -----
@router.get("/", response_model=List[schemas.ToolRequestResponse])
def get_all_tool_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.ToolRequest).order_by(models.ToolRequest.id).all()



# ----- SEE REEQUST DETAILS (Everyone) -----
@router.get("/{tool_id}", response_model=schemas.ToolRequestResponse)
def get_changeover_by_id(
    tool_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ToolRequestDetail = db.query(models.ToolRequest).filter(models.ToolRequest.id == tool_id).first()
    if not ToolRequestDetail:
        raise HTTPException(status_code=404, detail="Request not found")
    return ToolRequestDetail



# ----- CREATE REQUEST (User) -----
@router.post("/", response_model=schemas.ToolRequestResponse)
def create_tool_request(
    request: schemas.ToolRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user_or_leader)
):
    new_request = models.ToolRequest(
        production_line=request.production_line,
        machine_no=request.machine_no,
        tool_name=request.tool_name,
        part_no=request.part_no,
        quantity=request.quantity,
        requested_by=current_user.username,  # username instead of ID
        time_requested=datetime.now(malaysia_tz),
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request



# ----- CONCUR REQUEST (Leader/Admin) -----
@router.put("/{tool_id}/concur", response_model=schemas.ToolRequestResponse)
def concur_tool_request(
    tool_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_leader_or_admin)  # Admin/Leader only
):
    Tool_Request = db.get(models.ToolRequest, tool_id)
    if not Tool_Request:
        raise HTTPException(status_code=404, detail="Tool Request not found")
    
    Tool_Request.concurred_by = current_user.username
    Tool_Request.time_concurred = datetime.now(malaysia_tz)
    Tool_Request.status = ToolStatus.IN_PROGRESS
    db.commit()
    db.refresh(Tool_Request)
    return Tool_Request



# ----- Tool Replace (TOol) -----
@router.put("/{tool_id}/toolreplace", response_model=schemas.ToolRequestResponse)
def tool_received_request(
    tool_id: int,
    request: schemas.ToolRequestUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_leader_or_admin)  # Admin/Leader only
):
    Tool_Request = db.get(models.ToolRequest, tool_id)
    if not Tool_Request:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    Tool_Request.prepared_by = current_user.username
    Tool_Request.time_prepared = datetime.now(malaysia_tz)
    Tool_Request.remark = request.remark
    db.commit()
    db.refresh(Tool_Request)
    return Tool_Request



# ----- Tool Complete (User) -----
@router.put("/{tool_id}/toolcomplete", response_model=schemas.ToolRequestResponse)
def tool_complete_request(
    tool_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user_or_leader)
):
    Tool_Request = db.get(models.ToolRequest, tool_id)
    if not Tool_Request:
        raise HTTPException(status_code=404, detail="Changeover not found")
    
    Tool_Request.received_and_completed_by = current_user.username
    Tool_Request.time_completed = datetime.now(malaysia_tz)
    Tool_Request.status = ToolStatus.COMPLETED
    db.commit()
    db.refresh(Tool_Request)
    return Tool_Request


# ----- DELETE request (Admin) -----
@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool_request(
    tool_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    request = db.query(models.ToolRequest).get(tool_id)
    if not request:
        raise HTTPException(status_code=404, detail="request not found")
    db.delete(request)
    db.commit()
    return