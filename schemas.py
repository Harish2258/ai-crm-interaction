from pydantic import BaseModel

class InteractionCreate(BaseModel):
    text: str

class InteractionResponse(BaseModel):
    id: int
    hcp_name: str
    drug: str
    notes: str
    sentiment: str