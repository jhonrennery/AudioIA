from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from .config import get_settings


def transcribe_audio(audio_path: str, source_language: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "Defina OPENAI_API_KEY para transcrever audio. O prototipo ja esta pronto para usar a API."
        )

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=settings.openai_audio_model,
            file=audio_file,
            language=None if source_language == "auto" else source_language,
        )

    return transcript.text.strip()


def _style_instruction(style: str) -> str:
    mapping = {
        "natural": "Mantenha um tom natural, claro e fiel ao sentido original.",
        "professional": "Reescreva com tom profissional, direto e bem organizado.",
        "short": "Reescreva de forma curta, objetiva e sem perder a ideia principal.",
        "didactic": "Reescreva de forma didatica, clara e facil de entender.",
    }
    return mapping.get(style, mapping["natural"])


def rewrite_text(text: str, style: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return " ".join(text.split())

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = (
        "Voce recebe a transcricao de uma fala. "
        "Reescreva o texto sem inventar fatos. "
        f"{_style_instruction(style)}"
    )
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
    )
    return response.output_text.strip()


def translate_text(text: str, source_language: str, target_language: str) -> str:
    if not text:
        return ""
    if target_language in {"", source_language, "auto"}:
        return text

    settings = get_settings()
    if settings.openai_api_key:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        response = client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Traduza o texto para o idioma solicitado. "
                        "Preserve sentido, tom e nomes proprios."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Idioma de destino: {target_language}\n\nTexto:\n{text}",
                },
            ],
        )
        return response.output_text.strip()

    from deep_translator import GoogleTranslator

    translator = GoogleTranslator(
        source="auto" if source_language == "auto" else source_language,
        target=target_language,
    )
    return translator.translate(text)


def synthesize_speech(text: str, target_language: str) -> str | None:
    if not text:
        return None

    try:
        from gtts import gTTS
    except ImportError:
        return None

    safe_language = target_language if target_language != "auto" else "pt"
    output_dir = Path(tempfile.mkdtemp(prefix="audioia_"))
    output_path = output_dir / "translated_audio.mp3"
    tts = gTTS(text=text, lang=safe_language)
    tts.save(str(output_path))
    return str(output_path)


def process_audio(
    audio_path: str,
    source_language: str,
    rewrite_style: str,
    target_language: str,
    generate_audio: bool,
):
    transcript = transcribe_audio(audio_path, source_language)
    rewritten = rewrite_text(transcript, rewrite_style)
    translated = translate_text(rewritten, source_language, target_language)
    translated_audio_path = None

    if generate_audio:
        translated_audio_path = synthesize_speech(translated, target_language)

    return transcript, rewritten, translated, translated_audio_path


def create_download_bundle(
    transcript: str,
    rewritten: str,
    translated: str,
    translated_audio_path: str | None,
) -> str | None:
    if not any([transcript, rewritten, translated, translated_audio_path]):
        return None

    bundle_dir = Path(tempfile.mkdtemp(prefix="audioia_bundle_"))
    bundle_path = bundle_dir / "audioia_resultados.zip"

    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("transcricao.txt", transcript or "")
        archive.writestr("texto_reescrito.txt", rewritten or "")
        archive.writestr("traducao.txt", translated or "")

        if translated_audio_path:
            audio_file = Path(translated_audio_path)
            if audio_file.exists():
                archive.write(audio_file, arcname=audio_file.name)

    return str(bundle_path)
