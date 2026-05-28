from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

app = FastAPI()

# Allow Chrome extension access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache translations
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

    # Empty or purely numerical/special character message check
    if not text or len(text) <= 1:
        return {"translated": text}

    # Cache check
    cache_key = f"{text}_{request.target}"
    if cache_key in translation_cache:
        return {"translated": translation_cache[cache_key]}

    try:
        # Detect language with a fallback for short text/emojis
        try:
            detected_language = detect(text)
        except LangDetectException:
            detected_language = "unknown"

        # Skip translation if it's already in our target language
        if detected_language == request.target:
            return {"translated": text}

        # Translate text safely
        translated = GoogleTranslator(
            source='auto',
            target=request.target
        ).translate(text)

        # Save to cache
        translation_cache[cache_key] = translated

        return {"translated": translated}

    except Exception as e:
        print(f"Server-side translation error: {e}")
        # Return the original text back so the extension doesn't break
        return {"translated": text}
    
    if __name__ == "__main__":

     import uvicorn
    import os
    # Render automatically sets the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    # Bind to 0.0.0.0 so it is accessible externally on the web
    uvicorn.run("main:app", host="0.0.0.0", port=port)