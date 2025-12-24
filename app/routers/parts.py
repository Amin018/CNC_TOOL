# app/routers/parts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas, database
from app.routers.auth import require_admin

router = APIRouter(prefix="/parts", tags=["Parts"])

# Create part (Admin only)
@router.post("/", response_model=schemas.PartResponse, status_code=status.HTTP_201_CREATED)
def create_part(
    part: schemas.PartCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    db_part = db.query(models.Part).filter(models.Part.part_no == part.part_no).first()
    if db_part:
        raise HTTPException(status_code=400, detail="Part number already exists")

    new_part = models.Part(part_no=part.part_no, description=part.description, package=part.package)
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return new_part

# List all parts
@router.get("/", response_model=list[schemas.PartResponse])
def list_parts(db: Session = Depends(database.get_db)):
    return db.query(models.Part).order_by(models.Part.id).all()


@router.get("/search")
def search_parts(query: str, db: Session = Depends(database.get_db)):
    stmt = select(models.Part).where(models.Part.part_no.ilike(f"%{query}%"))
    results = db.execute(stmt).scalars().all()
    return [{"id": p.id, "part_no": p.part_no, "description": p.description} for p in results]


# List part details
@router.get("/{part_id}", response_model=schemas.PartResponse)
def get_part(
    part_id: int,
    db: Session = Depends(database.get_db)
    ):
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part


@router.put("/{part_id}", response_model=schemas.PartResponse)
def update_part(
    request: schemas.PartUpdate,
    part_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    part.description = request.description
    part.package = request.package

    db.commit()
    db.refresh(part)
    return part

# Delete part (Admin only)
@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(
    part_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_admin),
):
    part = db.get(models.Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    db.delete(part)
    db.commit()
    return

