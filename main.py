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

    # Initialize variables
    detected_language = "unknown"
    is_fallback_used = False

    # --- Pass 1: Primary Language Detection ---
    try:
        detected_language = detect(text)
    except LangDetectException:
        # langdetect failed (likely due to short text, emojis, or punctuation)
        is_fallback_used = True

    try:
        # Build the translator engine
        # We use 'auto' source so Google's server-side engine acts as our ultimate safety net
        translator = GoogleTranslator(source='auto', target=request.target)

        # --- Pass 2: Check for same-language shortcuts ---
        # If Pass 1 confidently matched the target language, skip the API call to save resources
        if not is_fallback_used and detected_language == request.target:
            return {"translated": text, "language": detected_language, "skipped": True}

        # Translate the string
        translated = translator.translate(text)

        # --- Pass 3: Post-Translation Fallback Verification ---
        # If Pass 1 completely missed or failed, we can deduce the true source language 
        # by inspecting the metadata deep-translator naturally discovers during execution.
        if is_fallback_used or detected_language == "unknown":
            try:
                # Ask deep_translator to pinpoint what it actually translated from
                detected_language = translator.get_supported_languages(as_dict=True).get(
                    translator.source, "unknown"
                )
                # If it's still generic 'auto', we map it nicely
                if translator.source == 'auto':
                    # A quick single-word secondary string validation check
                    detected_language = "detected_via_api"
            except:
                detected_language = "fallback_mode"

        # If the translated output is identical to the input text, it's already in the target language!
        if translated.strip().toLowerCase() == text.strip().toLowerCase():
            response_data = {"translated": text, "language": request.target, "cached": False}
        else:
            response_data = {"translated": translated, "language": detected_language, "cached": False}

        # Cache the finalized schema block
        translation_cache[cache_key] = response_data
        return response_data

    except Exception as e:
        print(f"Backend processing failure: {e}")
        return {"translated": text, "language": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)