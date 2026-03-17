from __future__ import annotations

import gradio as gr

from .languages import LANGUAGE_OPTIONS, REWRITE_STYLES
from .services import process_audio


OUTPUT_KEYS = [
    "transcript",
    "rewritten",
    "translated",
    "translated_audio",
    "status",
]


def _empty_result(status: str):
    return {
        "transcript": "",
        "rewritten": "",
        "translated": "",
        "translated_audio": None,
        "status": status,
    }


def _run_pipeline(audio_path, source_label, rewrite_label, target_label, create_audio):
    if not audio_path:
        return _empty_result("Envie ou grave um audio para continuar.")

    transcript, rewritten, translated, translated_audio = process_audio(
        audio_path=audio_path,
        source_language=LANGUAGE_OPTIONS[source_label],
        rewrite_style=REWRITE_STYLES[rewrite_label],
        target_language=LANGUAGE_OPTIONS[target_label],
        generate_audio=create_audio,
    )

    status = "Processamento concluido com sucesso."
    if create_audio and not translated_audio:
        status += " O audio traduzido nao foi gerado porque gTTS nao esta disponivel."

    return {
        "transcript": transcript,
        "rewritten": rewritten,
        "translated": translated,
        "translated_audio": translated_audio,
        "status": status,
    }


def _result_to_tuple(result: dict[str, object]):
    return tuple(result[key] for key in OUTPUT_KEYS)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AudioIA") as app:
        gr.Markdown(
            "# AudioIA\n"
            "Transforme sua fala em texto, reescreva com mais clareza e traduza para outros idiomas."
        )

        last_live_audio = gr.State("")

        with gr.Row():
            audio_input = gr.Audio(
                sources=["upload", "microphone"],
                type="filepath",
                label="Audio de entrada",
            )

            with gr.Column():
                source_language = gr.Dropdown(
                    choices=list(LANGUAGE_OPTIONS.keys()),
                    value="Auto detectar",
                    label="Idioma de origem",
                )
                rewrite_style = gr.Dropdown(
                    choices=list(REWRITE_STYLES.keys()),
                    value="Natural",
                    label="Estilo da reescrita",
                )
                target_language = gr.Dropdown(
                    choices=[item for item in LANGUAGE_OPTIONS.keys() if item != "Auto detectar"],
                    value="Ingles",
                    label="Idioma de destino",
                )
                generate_audio = gr.Checkbox(
                    value=True,
                    label="Gerar audio traduzido",
                )
                live_mode = gr.Checkbox(
                    value=True,
                    label="Modo ao vivo",
                    info="Processa automaticamente cada nova gravacao do microfone.",
                )
                run_button = gr.Button("Processar audio", variant="primary")

        transcript_output = gr.Textbox(label="Transcricao", lines=6)
        rewritten_output = gr.Textbox(label="Texto reescrito", lines=6)
        translated_output = gr.Textbox(label="Traducao", lines=6)
        translated_audio_output = gr.Audio(label="Audio traduzido")
        status_output = gr.Markdown()

        def run_pipeline(audio_path, source_label, rewrite_label, target_label, create_audio):
            try:
                result = _run_pipeline(
                    audio_path,
                    source_label,
                    rewrite_label,
                    target_label,
                    create_audio,
                )
            except Exception as exc:
                raise gr.Error(str(exc)) from exc

            return _result_to_tuple(result)

        def auto_process(audio_path, source_label, rewrite_label, target_label, create_audio, enabled, last_path):
            if not enabled:
                return (
                    gr.skip(),
                    gr.skip(),
                    gr.skip(),
                    gr.skip(),
                    "Modo ao vivo desativado. Use o botao Processar audio.",
                    last_path,
                )

            if not audio_path:
                return gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), last_path

            if audio_path == last_path:
                return gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), last_path

            try:
                result = _run_pipeline(
                    audio_path,
                    source_label,
                    rewrite_label,
                    target_label,
                    create_audio,
                )
            except Exception as exc:
                raise gr.Error(str(exc)) from exc

            result["status"] = "Modo ao vivo: nova gravacao processada. " + str(result["status"])
            return (*_result_to_tuple(result), audio_path)

        run_button.click(
            fn=run_pipeline,
            inputs=[audio_input, source_language, rewrite_style, target_language, generate_audio],
            outputs=[
                transcript_output,
                rewritten_output,
                translated_output,
                translated_audio_output,
                status_output,
            ],
        )

        audio_input.change(
            fn=auto_process,
            inputs=[
                audio_input,
                source_language,
                rewrite_style,
                target_language,
                generate_audio,
                live_mode,
                last_live_audio,
            ],
            outputs=[
                transcript_output,
                rewritten_output,
                translated_output,
                translated_audio_output,
                status_output,
                last_live_audio,
            ],
        )

    return app
