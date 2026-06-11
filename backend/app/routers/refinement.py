from fastapi import APIRouter, Depends, HTTPException
from app.schemas.refinement import RefinementRequest, RefinementResponse
from app.services.gemini import GeminiService

router = APIRouter(
    prefix="/ai",
    tags=["AI Refinement"]
)

# Dependency Injection for service instance
def get_gemini_service():
    return GeminiService()

@router.post("/refine", response_model=RefinementResponse)
async def refine_sentence(
    payload: RefinementRequest, 
    service: GeminiService = Depends(get_gemini_service)
):
    if not payload.sentence.strip():
        raise HTTPException(status_code=400, detail="Input sentence cannot be empty.")
        
    refined_text = await service.refine_medical_text(payload.sentence)
    return RefinementResponse(refined_sentence=refined_text)