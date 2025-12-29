from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/partlinks", tags=["Part Links"])

@router.post("/{part_id}/{linked_id}")
def add_link(part_id: int, linked_id: int, db: Session = Depends(get_db)):

    if part_id == linked_id:
        raise HTTPException(400, "A part cannot link to itself")

    # ensure both exist
    part = db.get(models.Part, part_id)
    linked = db.get(models.Part, linked_id)

    if not part or not linked:
        raise HTTPException(404, "Part not found")

    def create_pair(a, b):
        exists = db.query(models.PartLink).filter_by(
            part_id=a, linked_part_id=b
        ).first()

        if not exists:
            db.add(models.PartLink(part_id=a, linked_part_id=b))
        else:
            raise HTTPException(400, "Link already exists")

    # main pair
    create_pair(part_id, linked_id)

    # mirror pair
    create_pair(linked_id, part_id)

    db.commit()
    return {"message": "Linked successfully"}


@router.delete("/{part_id}/{linked_id}")
def remove_link(part_id: int, linked_id: int, db: Session = Depends(get_db)):

    db.query(models.PartLink).filter_by(
        part_id=part_id, linked_part_id=linked_id
    ).delete()

    db.query(models.PartLink).filter_by(
        part_id=linked_id, linked_part_id=part_id
    ).delete()

    db.commit()
    return {"message": "Link removed"}



@router.get("/{part_id}")
def get_links(part_id: int, db: Session = Depends(get_db)):
    part = db.get(models.Part, part_id)
    if not part:
        raise HTTPException(404, "Part not found")

    return [
        {"id": p.id, "part_no": p.part_no, "description": p.description}
        for p in part.linked_parts
    ]
