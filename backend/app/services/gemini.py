import os
from google import genai
from google.genai import types
from fastapi import HTTPException
from dotenv import load_dotenv

# Load variables from the .env file into os.environ
load_dotenv()

class GeminiService:
    def __init__(self):
        # Read dynamically from the environment
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
        
        # Initialize the enterprise client engine
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash" 

    async def refine_medical_text(self, raw_text: str) -> str:
        system_prompt = (
            "You are the AI refinement engine for MediBridge, an AI-Based Multilingual and "
            "Sign Language Communication System for Healthcare. Your task is to take raw transcribed text—"
            "often derived from Ethiopian Sign Language (EthSL) gestures or speech recognition—and refine "
            "it into clear, medically accurate, and professional English. Ensure the original meaning is "
            "preserved for doctor-patient communication. Only return the refined sentence without any extra commentary."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=raw_text,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2, 
                )
            )
            
            if not response.text:
                raise HTTPException(status_code=500, detail="Gemini engine returned an empty response.")
                
            return response.text.strip()

        except Exception as e:
            print(f"[Internal Error] Gemini Generation Failure: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to communicate with AI generation engine.")