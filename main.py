from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import os

app = FastAPI()

# Allow extension access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translation_cache = {}

class TextRequest(BaseModel):
    text: str
    target: str = "en"

@app.get("/")
def root():
    return {"message": "WhatsApp Translator API Running"}

@app.post("/translate")
def translate_text(request: TextRequest):
    text = request.text.strip()

    if not text:
        return {"translated": "", "language": "unknown"}

    cache_key = f"{text}_{request.target}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]

    detected_language = "unknown"
    is_fallback_used = False

    # --- Pass 1: Language Detection ---
    try:
        detected_language = detect(text)
    except LangDetectException:
        is_fallback_used = True

    try:
        # Build translation client
        translator = GoogleTranslator(source='auto', target=request.target)

        # Skip translation if langdetect confidently knows it's already the target language
        if not is_fallback_used and detected_language == request.target:
            return {"translated": text, "language": detected_language, "skipped": True}

        # Execute translation request
        translated = translator.translate(text)

        # --- Pass 2: Post-Translation Identification ---
        if is_fallback_used or detected_language == "unknown":
            detected_language = "auto"

        # FIXED: Corrected Python lowercasing syntax rule
        if translated.strip().lower() == text.strip().lower():
            response_data = {"translated": text, "language": request.target}
        else:
            response_data = {"translated": translated, "language": detected_language}

        translation_cache[cache_key] = response_data
        return response_data

    except Exception as e:
        print(f"Backend processing failure: {e}")
        return {"translated": text, "language": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)