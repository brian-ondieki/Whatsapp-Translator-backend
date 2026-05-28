from deep_translator import GoogleTranslator


def translate_text(text):

    try:

        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)

        return translated

    except Exception as e:

        print("Translation error:", e)

        return None