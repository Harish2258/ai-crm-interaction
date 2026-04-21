from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Interaction
from app.schemas import InteractionCreate, InteractionResponse
from app.ai.langgraph_agent import run_agent

router = APIRouter()


@router.post("/interaction/log", response_model=InteractionResponse)
def log_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    if not payload.text:
        raise HTTPException(status_code=400, detail="Text is required")

    response = run_agent(payload.text)

    if isinstance(response, dict) and "data" in response:
        data = response["data"]
    else:
        data = response

    new_entry = Interaction(
        hcp_name=data.get("hcp_name") or "Unknown Doctor",
        drug=data.get("drug") or "Unknown Drug",
        notes=data.get("notes") or payload.text,
        sentiment=data.get("sentiment") or "Neutral",
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


@router.get("/interaction/search")
def search_interactions(
    doctor: Optional[str] = None,
    drug: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Interaction)

    if doctor:
        query = query.filter(Interaction.hcp_name.ilike(f"%{doctor}%"))

    if drug:
        query = query.filter(Interaction.drug.ilike(f"%{drug}%"))

    return query.all()


@router.get("/interaction/all")
def get_all(db: Session = Depends(get_db)):
    return db.query(Interaction).all()