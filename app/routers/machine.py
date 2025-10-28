# machine.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.routers.auth import require_admin
from typing import List

router = APIRouter(prefix="/machines", tags=["Machines"])

@router.get("/", response_model=List[schemas.MachineResponse])
def list_machines(db: Session = Depends(database.get_db)):
    return db.query(models.Machine).order_by(
        models.Machine.production_line.asc(),  # Groups by production line
        #models.Machine.status.desc(),          # Active first
        models.Machine.machine_no.asc()        # Optional: sort by machine number inside line
    ).all()

@router.post("/", response_model=schemas.MachineResponse)
def add_machine(
    machine: schemas.MachineCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    new_machine = models.Machine(**machine.dict())
    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)
    return new_machine


@router.put("/{machine_id}/status", response_model=schemas.MachineResponse)
def update_machine_status(
    machine_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    machine = db.get(models.Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    if status not in ["Active", "Offline"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    machine.status = status
    db.commit()
    db.refresh(machine)
    return machine


@router.delete("/{machine_id}")
def delete_machine(
    machine_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    machine = db.get(models.Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(machine)
    db.commit()
    return {"message": "Machine deleted"}
