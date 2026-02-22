from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.work_code import WorkCode
from app.models.user import User
from app.schemas.work_code import WorkCodeCreate, WorkCodeUpdate, WorkCodeOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/workcodes", tags=["workcodes"])


@router.get("", response_model=list[WorkCodeOut])
def list_work_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(WorkCode)
        .filter((WorkCode.user_id == None) | (WorkCode.user_id == current_user.id))
        .order_by(WorkCode.code)
        .all()
    )


@router.post("", response_model=WorkCodeOut, status_code=status.HTTP_201_CREATED)
def create_work_code(
    payload: WorkCodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wc = WorkCode(
        code=payload.code,
        description=payload.description,
        user_id=current_user.id,
    )
    db.add(wc)
    db.commit()
    db.refresh(wc)
    return wc


@router.put("/{wc_id}", response_model=WorkCodeOut)
def update_work_code(
    wc_id: int,
    payload: WorkCodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wc = (
        db.query(WorkCode)
        .filter(WorkCode.id == wc_id, WorkCode.user_id == current_user.id)
        .first()
    )
    if not wc:
        raise HTTPException(status_code=404, detail="Work code not found")
    if payload.code is not None:
        wc.code = payload.code
    if payload.description is not None:
        wc.description = payload.description
    db.commit()
    db.refresh(wc)
    return wc


@router.delete("/{wc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_code(
    wc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wc = (
        db.query(WorkCode)
        .filter(WorkCode.id == wc_id, WorkCode.user_id == current_user.id)
        .first()
    )
    if not wc:
        raise HTTPException(status_code=404, detail="Work code not found")
    db.delete(wc)
    db.commit()
