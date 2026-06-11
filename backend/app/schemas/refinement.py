from pydantic import BaseModel

class RefinementRequest(BaseModel):
    sentence: str

class RefinementResponse(BaseModel):
    refined_sentence: str