from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.ai.agent import extract_interaction
from app.models import Interaction
from app.database import SessionLocal


class AgentState(TypedDict):
    input: str
    output: dict


def log_interaction_tool(text: str):
    data = extract_interaction(text)

    db = SessionLocal()
    try:
        new_entry = Interaction(
            hcp_name=data.get("hcp_name") or "Unknown Doctor",
            drug=data.get("drug") or "Unknown Drug",
            notes=data.get("notes") or text,
            sentiment=data.get("sentiment") or "Neutral",
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return {
            "message": "Logged successfully",
            "data": {
                "id": new_entry.id,
                "hcp_name": new_entry.hcp_name,
                "drug": new_entry.drug,
                "notes": new_entry.notes,
                "sentiment": new_entry.sentiment,
            },
        }
    finally:
        db.close()


def search_interaction_tool(text: str):
    import re

    db = SessionLocal()
    try:
        query = db.query(Interaction)

        match = re.search(r"doctor\s*(\w+)", text, re.I)
        if match:
            query = query.filter(Interaction.hcp_name.ilike(f"%{match.group(1)}%"))

        match = re.search(r"drug\s*(\w+)", text, re.I)
        if match:
            query = query.filter(Interaction.drug.ilike(f"%{match.group(1)}%"))

        results = query.all()

        return {
            "results": [
                {
                    "id": r.id,
                    "hcp_name": r.hcp_name,
                    "drug": r.drug,
                    "notes": r.notes,
                    "sentiment": r.sentiment,
                }
                for r in results
            ]
        }
    finally:
        db.close()


def edit_interaction_tool(text: str):
    import re

    db = SessionLocal()
    try:
        id_match = re.search(r"id\s*(\d+)", text)
        if not id_match:
            return {"error": "ID required"}

        record = db.query(Interaction).filter(
            Interaction.id == int(id_match.group(1))
        ).first()

        if not record:
            return {"error": "Not found"}

        drug_match = re.search(r"drug\s*to\s*(\w+)", text, re.I)
        if drug_match:
            record.drug = drug_match.group(1).capitalize()

        doc_match = re.search(r"doctor\s*to\s*(dr\.?\s*\w+)", text, re.I)
        if doc_match:
            record.hcp_name = doc_match.group(1)

        db.commit()
        db.refresh(record)

        return {
            "message": "Updated successfully",
            "data": {
                "id": record.id,
                "hcp_name": record.hcp_name,
                "drug": record.drug,
                "notes": record.notes,
                "sentiment": record.sentiment,
            },
        }
    finally:
        db.close()


def summarize_tool(text: str):
    return {"summary": text[:100]}


def followup_tool(text: str):
    return {"suggestion": "Follow-up in 2 weeks"}


def agent_node(state: AgentState):
    text = state["input"].lower()

    if "edit" in text:
        result = edit_interaction_tool(state["input"])
    elif "search" in text:
        result = search_interaction_tool(state["input"])
    elif "summary" in text:
        result = summarize_tool(state["input"])
    elif "follow" in text:
        result = followup_tool(state["input"])
    else:
        result = log_interaction_tool(state["input"])

    return {"output": result}


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_edge("agent", END)

graph = builder.compile()


def run_agent(text: str):
    result = graph.invoke({"input": text})
    return result.get("output", {})